#!/usr/bin/env python3
"""Stop hook for odoo-dev-skill: status-aware context_session.xml enforcement.

Optional, Claude-Code-specific — nothing else in this skill depends on it.
Wire it into the consuming project's .claude/settings.json using the
ABSOLUTE path to wherever this skill was installed:

    {
      "hooks": {
        "Stop": [
          {"hooks": [{"type": "command", "command": "python3 /absolute/path/to/odoo-dev-skill/hooks/context_session_guard.py"}]}
        ]
      }
    }

Behavior driven by the status= attribute in context_session.xml:

  status="in_progress"  Task is active, more prompts expected.
                        - Block if file exceeds ~12,000 char budget.
                        - Block if project files changed more recently than
                          context_session.xml (stale state), asking the agent
                          to write a checkpoint before stopping.

  status="checkpoint"   Agent just finished a logical block and wrote state.
                        - Allow stop cleanly — no stale-file check needed.
                        - Switch status back to in_progress on next agent turn
                          (the agent does this automatically).

  status="completed"    User signalled end of task (natural phrases like
                        "terminamos", "listo", "abre el PR", etc.).
                        - Archive a <session> entry into history_context.xml.
                        - Reset context_session.xml to blank template state.
                        - Allow stop.

  missing / unreadable  Fails open — exit 0, never blocks on infrastructure
                        it cannot verify.

Stdlib only.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MAX_CHARS = 12000
CONTEXT_REL = os.path.join(".claude", "odoo-dev-skill")
CONTEXT_FILENAME = "context_session.xml"
HISTORY_FILENAME = "history_context.xml"

BLANK_TEMPLATE = """\
<!--
  context_session.xml — per-task working memory for odoo-dev-skill.

  Lives at .claude/odoo-dev-skill/context_session.xml inside the project.
  The agent creates and manages this file automatically — do not edit manually.
  Keep it under ~12,000 characters; the agent compresses it when needed.

  status lifecycle (read by context_session_guard.py Stop hook):
    in_progress → task active, more prompts expected; hook checks for stale files
    checkpoint  → logical block just written; hook lets the agent stop cleanly
    completed   → user signalled end of task; hook archives to history_context.xml
                  and resets this file to blank template state

  See SKILL.md ## Context management for the full lifecycle.
-->
<context_session id="" started="" odoo_version="" status="in_progress" max_chars="12000">

  <task>
    <description></description>
    <module></module>
    <models></models>
  </task>

  <state>
    <patterns_loaded>
      <!-- <pattern file="skills/odoo-model-patterns-18.md"/> -->
    </patterns_loaded>

    <files_touched>
      <!-- <file path="models/library_book.py" action="created"/> -->
    </files_touched>

    <decisions>
      <!-- <decision>Short, terse rationale for a choice made.</decision> -->
    </decisions>

    <open_questions>
      <!-- <question>Unresolved thing to confirm with the user.</question> -->
    </open_questions>
  </state>

</context_session>
"""


def read_cwd():
    try:
        payload = json.load(sys.stdin)
        return payload.get("cwd") or os.getcwd()
    except Exception:
        return os.getcwd()


def block(reason):
    sys.stderr.write(reason + "\n")
    sys.exit(2)


def extract_attr(content, attr):
    """Extract a single XML attribute value from the context_session root tag."""
    m = re.search(rf'{attr}="([^"]*)"', content[:500])
    return m.group(1).strip() if m else ""


def extract_tag(content, tag):
    """Extract inner text of a simple XML tag (first match)."""
    m = re.search(rf"<{tag}>(.*?)</{tag}>", content, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_list(content, outer, inner):
    """Extract a list of attribute values from repeated child tags."""
    block_m = re.search(rf"<{outer}>(.*?)</{outer}>", content, re.DOTALL)
    if not block_m:
        return []
    return re.findall(rf'<{inner}\s+[^/]*?/>', block_m.group(1))


def archive_session(cwd, content, session_file, history_file):
    """Append a <session> entry to history_context.xml from current context."""
    session_id   = extract_attr(content, "id") or "unknown"
    started      = extract_attr(content, "started") or ""
    odoo_version = extract_attr(content, "odoo_version") or ""
    ended        = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    summary      = extract_tag(content, "description") or "No description recorded."
    module       = extract_tag(content, "module") or ""

    # Collect patterns and files as raw XML snippets
    patterns_block = re.search(r"<patterns_loaded>(.*?)</patterns_loaded>", content, re.DOTALL)
    patterns_xml   = patterns_block.group(1).strip() if patterns_block else ""
    # Strip comment lines
    patterns_xml   = "\n      ".join(
        l for l in patterns_xml.splitlines() if l.strip() and not l.strip().startswith("<!--")
    )

    files_block = re.search(r"<files_touched>(.*?)</files_touched>", content, re.DOTALL)
    files_xml   = files_block.group(1).strip() if files_block else ""
    files_xml   = "\n      ".join(
        l for l in files_xml.splitlines() if l.strip() and not l.strip().startswith("<!--")
    )

    entry = f"""
  <session id="{session_id}" started="{started}" ended="{ended}" odoo_version="{odoo_version}">
    <summary>{summary}</summary>
    <module>{module}</module>
    <patterns_used>
      {patterns_xml or "<!-- none recorded -->"}
    </patterns_used>
    <files_changed>
      {files_xml or "<!-- none recorded -->"}
    </files_changed>
    <outcome status="completed"/>
  </session>
"""

    if os.path.exists(history_file):
        with open(history_file, encoding="utf-8") as f:
            history = f.read()
        # Insert before closing tag
        if "</history_context>" in history:
            history = history.replace("</history_context>", entry + "\n</history_context>")
        else:
            history += entry
    else:
        history = f"""<!--
  history_context.xml — append-only log of finished sessions for odoo-dev-skill.
  Never rewrite or delete past entries — this is the audit trail.
  See SKILL.md ## Context management for the full lifecycle.
-->
<history_context>
{entry}
</history_context>
"""

    with open(history_file, "w", encoding="utf-8") as f:
        f.write(history)


def reset_session(session_file):
    """Reset context_session.xml to blank template."""
    with open(session_file, "w", encoding="utf-8") as f:
        f.write(BLANK_TEMPLATE)


def check_stale_files(cwd, session_mtime):
    """Return list of project files modified after context_session.xml."""
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None  # can't verify — fail open

    if result.returncode != 0:
        return None

    stale = []
    for line in result.stdout.splitlines():
        rel_path = line[3:].strip().strip('"')
        if not rel_path or rel_path.startswith(CONTEXT_REL):
            continue
        full_path = os.path.join(cwd, rel_path)
        if os.path.exists(full_path) and os.path.getmtime(full_path) > session_mtime:
            stale.append(rel_path)
    return stale


def main():
    cwd          = read_cwd()
    context_dir  = os.path.join(cwd, CONTEXT_REL)
    session_file = os.path.join(context_dir, CONTEXT_FILENAME)
    history_file = os.path.join(context_dir, HISTORY_FILENAME)

    if not os.path.exists(session_file):
        sys.exit(0)

    try:
        with open(session_file, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        sys.exit(0)

    status = extract_attr(content, "status")

    # --- completed: archive and reset, then allow stop ---
    if status == "completed":
        try:
            os.makedirs(context_dir, exist_ok=True)
            archive_session(cwd, content, session_file, history_file)
            reset_session(session_file)
        except OSError as e:
            # Archive failed — block so the agent can retry manually
            block(
                f"Failed to archive session to history_context.xml: {e}. "
                "Fix the issue and try again, or archive manually before stopping."
            )
        sys.exit(0)

    # --- checkpoint: agent wrote a clean block, allow stop ---
    if status == "checkpoint":
        sys.exit(0)

    # --- in_progress (default): enforce budget and stale-file checks ---

    if len(content) > MAX_CHARS:
        block(
            f"context_session.xml is {len(content)} chars, over the ~{MAX_CHARS} "
            "budget. Compress <decisions> and <files_touched> into denser summaries "
            "before stopping."
        )

    session_mtime = os.path.getmtime(session_file)
    stale = check_stale_files(cwd, session_mtime)

    if stale is None:
        sys.exit(0)  # can't verify git state — fail open

    if stale:
        shown = ", ".join(stale[:10]) + (" ..." if len(stale) > 10 else "")
        block(
            f"Files changed after context_session.xml was last updated: {shown}. "
            "Write a checkpoint (status='checkpoint') or mark the task done "
            "(status='completed') before stopping."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()