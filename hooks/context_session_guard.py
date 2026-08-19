#!/usr/bin/env python3
"""Stop hook for odoo-dev-skill: status-aware context_session.md enforcement.

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

Behavior driven by the `- status:` field in context_session.md:

  status="in_progress"  Task is active, more prompts expected.
                        - Block if file exceeds ~12,000 char budget.
                        - Block if project files changed more recently than
                          context_session.md (stale state), asking the agent
                          to write a checkpoint before stopping.

  status="checkpoint"   Agent just finished a logical block and wrote state.
                        - Allow stop cleanly — no stale-file check needed.
                        - Switch status back to in_progress on next agent turn
                          (the agent does this automatically).

  status="completed"    User signalled end of task (natural phrases like
                        "terminamos", "listo", "abre el PR", etc.).
                        - Archive a session entry into history_context.md.
                        - Reset context_session.md to blank template state.
                        - Allow stop.

  missing / unreadable  Fails open — exit 0, never blocks on infrastructure
                        it cannot verify.

Plain markdown, not XML — cheaper for the agent to read/write and to parse
here (no tag balancing, just line-oriented "- key: value" fields and
"## Header" sections). Stdlib only.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MAX_CHARS = 12000
CONTEXT_REL = os.path.join(".claude", "odoo-dev-skill")
CONTEXT_FILENAME = "context_session.md"
HISTORY_FILENAME = "history_context.md"

BLANK_TEMPLATE = """\
<!--
  context_session.md — per-task working memory for odoo-dev-skill.

  Lives at .claude/odoo-dev-skill/context_session.md inside the project.
  The agent creates and manages this file automatically — do not edit manually.
  Keep it under ~12,000 characters; the agent compresses it when needed.

  status lifecycle (read by context_session_guard.py Stop hook):
    in_progress → task active, more prompts expected; hook checks for stale files
    checkpoint  → logical block just written; hook lets the agent stop cleanly
    completed   → user signalled end of task; hook archives to history_context.md
                  and resets this file to blank template state

  See SKILL.md ## Context management for the full lifecycle.
-->

- id:
- started:
- odoo_version:
- status: in_progress

## Task

- description:
- module:
- models:

## Patterns loaded

<!-- - skills/odoo-model-patterns-18.md -->

## Files touched

<!-- - models/library_book.py — created -->

## Decisions

<!-- - Short, terse rationale for a choice made. -->

## Open questions

<!-- - Unresolved thing to confirm with the user. -->
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


def extract_field(content, key):
    """Extract the value of a top-level '- key: value' line."""
    m = re.search(rf"^-\s*{re.escape(key)}:\s*(.*)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_section(content, header):
    """Return the raw text of a '## Header' section, up to the next '## ' or EOF."""
    m = re.search(
        rf"^##\s*{re.escape(header)}\s*$(.*?)(?=^##\s|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    return m.group(1) if m else ""


def extract_bullets(section_text):
    """Extract real '- item' bullets from a section, ignoring HTML-comment placeholders."""
    stripped = re.sub(r"<!--.*?-->", "", section_text, flags=re.DOTALL)
    return [
        line.strip()[2:].strip()
        for line in stripped.splitlines()
        if line.strip().startswith("- ")
    ]


def archive_session(cwd, content, session_file, history_file):
    """Append a session entry to history_context.md from current context."""
    session_id   = extract_field(content, "id") or "unknown"
    started      = extract_field(content, "started") or ""
    odoo_version = extract_field(content, "odoo_version") or ""
    ended        = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

    task_section = extract_section(content, "Task")
    summary      = extract_field(task_section, "description") or "No description recorded."
    module       = extract_field(task_section, "module") or ""

    patterns = extract_bullets(extract_section(content, "Patterns loaded"))
    files    = extract_bullets(extract_section(content, "Files touched"))

    patterns_md = "\n".join(f"- {p}" for p in patterns) or "- none recorded"
    files_md    = "\n".join(f"- {f}" for f in files) or "- none recorded"

    entry = f"""
## Session {session_id} — {started} → {ended} (Odoo {odoo_version})

- status: completed

**Summary:** {summary}

**Module:** {module}

**Patterns used:**
{patterns_md}

**Files changed:**
{files_md}
"""

    if os.path.exists(history_file):
        with open(history_file, encoding="utf-8") as f:
            history = f.read()
        history = history.rstrip("\n") + "\n" + entry
    else:
        history = f"""<!--
  history_context.md — append-only log of finished sessions for odoo-dev-skill.
  Never rewrite or delete past entries — this is the audit trail.
  See SKILL.md -> Context session management for the full lifecycle.
-->

# History Context
{entry}"""

    with open(history_file, "w", encoding="utf-8") as f:
        f.write(history)


def reset_session(session_file):
    """Reset context_session.md to blank template."""
    with open(session_file, "w", encoding="utf-8") as f:
        f.write(BLANK_TEMPLATE)


def check_stale_files(cwd, session_mtime):
    """Return list of project files modified after context_session.md."""
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

    status = extract_field(content, "status")

    # --- completed: archive and reset, then allow stop ---
    if status == "completed":
        try:
            os.makedirs(context_dir, exist_ok=True)
            archive_session(cwd, content, session_file, history_file)
            reset_session(session_file)
        except OSError as e:
            # Archive failed — block so the agent can retry manually
            block(
                f"Failed to archive session to history_context.md: {e}. "
                "Fix the issue and try again, or archive manually before stopping."
            )
        sys.exit(0)

    # --- checkpoint: agent wrote a clean block, allow stop ---
    if status == "checkpoint":
        sys.exit(0)

    # --- in_progress (default): enforce budget and stale-file checks ---

    if len(content) > MAX_CHARS:
        block(
            f"context_session.md is {len(content)} chars, over the ~{MAX_CHARS} "
            "budget. Compress the Decisions and Files touched sections into "
            "denser summaries before stopping."
        )

    session_mtime = os.path.getmtime(session_file)
    stale = check_stale_files(cwd, session_mtime)

    if stale is None:
        sys.exit(0)  # can't verify git state — fail open

    if stale:
        shown = ", ".join(stale[:10]) + (" ..." if len(stale) > 10 else "")
        block(
            f"Files changed after context_session.md was last updated: {shown}. "
            "Write a checkpoint (status: checkpoint) or mark the task done "
            "(status: completed) before stopping."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
