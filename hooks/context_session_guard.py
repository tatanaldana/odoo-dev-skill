#!/usr/bin/env python3
"""Stop hook for odoo-dev-skill: enforces context_session.xml upkeep.

Optional, Claude-Code-specific — nothing else in this skill depends on it.
Wire it into the consuming project's .claude/settings.json using the
ABSOLUTE path to wherever this skill was installed (global installs live
outside the project, so a bare relative path won't resolve):

    {
      "hooks": {
        "Stop": [
          {"hooks": [{"type": "command", "command": "python3 /absolute/path/to/odoo-dev-skill/hooks/context_session_guard.py"}]}
        ]
      }
    }

See SKILL.md <context_management> and examples/context-session-and-history.md
for the convention this hook enforces. Stdlib only.

Behavior:
  - No context_session.xml present -> nothing to guard, exit 0 (allow stop).
  - context_session.xml exceeds the ~12,000 char budget -> block (exit 2),
    asking Claude to compress <decisions>/<files_touched> before stopping.
  - Tracked/untracked files changed more recently than context_session.xml
    was last written -> block (exit 2), asking Claude to update it (and, if
    the task is actually finished, archive a <session> entry into
    history_context.xml) before stopping.
  - Anything unexpected (no git repo, git not installed, unreadable file)
    fails open — it exits 0 rather than blocking on infrastructure it can't
    verify.
"""
import json
import os
import subprocess
import sys

MAX_CHARS = 12000
CONTEXT_REL = os.path.join(".claude", "odoo-dev-skill")


def read_cwd():
    try:
        payload = json.load(sys.stdin)
        return payload.get("cwd") or os.getcwd()
    except Exception:
        return os.getcwd()


def block(reason):
    sys.stderr.write(reason + "\n")
    sys.exit(2)


def main():
    cwd = read_cwd()
    session_file = os.path.join(cwd, CONTEXT_REL, "context_session.xml")

    if not os.path.exists(session_file):
        sys.exit(0)

    try:
        with open(session_file, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        sys.exit(0)

    if len(content) > MAX_CHARS:
        block(
            f"context_session.xml is {len(content)} chars, over the ~{MAX_CHARS} "
            "budget defined in SKILL.md <context_management>. Compress "
            "<decisions> and <files_touched> into denser summaries before stopping."
        )

    session_mtime = os.path.getmtime(session_file)

    try:
        result = subprocess.run(
            ["git", "-C", cwd, "status", "--porcelain"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        sys.exit(0)

    if result.returncode != 0:
        sys.exit(0)

    stale = []
    for line in result.stdout.splitlines():
        rel_path = line[3:].strip().strip('"')
        if not rel_path or rel_path.startswith(CONTEXT_REL):
            continue
        full_path = os.path.join(cwd, rel_path)
        if os.path.exists(full_path) and os.path.getmtime(full_path) > session_mtime:
            stale.append(rel_path)

    if stale:
        shown = ", ".join(stale[:10]) + (" ..." if len(stale) > 10 else "")
        block(
            f"These files changed after context_session.xml was last updated: {shown}. "
            "Update context_session.xml (files_touched/decisions) — and if this task "
            "is done, archive a <session> entry into history_context.xml — before stopping."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
