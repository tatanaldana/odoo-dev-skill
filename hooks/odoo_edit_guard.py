#!/usr/bin/env python3
"""PostToolUse hook for odoo-dev-skill: real-time CRITICAL feedback on edits.

Optional, Claude-Code-specific — nothing else in this skill depends on it.
Wire it into the consuming project's .claude/settings.json:

    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Edit|Write",
            "hooks": [{"type": "command", "command": "python3 /absolute/path/to/odoo-dev-skill/hooks/odoo_edit_guard.py"}]
          }
        ]
      }
    }

Deliberately does NOT block on every edit — that would be constant friction
for HIGH/MEDIUM findings that are fine to catch at review time (see
agents/odoo-code-reviewer.md and odoo-coding-guidelines-validator.md, which
already run the full checks/odoo_lint.py before their analysis). This hook
only interrupts for CRITICAL findings ("breaks the module or causes data
loss" per SKILL.md's own severity definition) in the SINGLE file that was
just edited — the moment they're introduced, not batched up for later.

Behavior:
  - Only acts on Edit/Write of a .py or .xml file.
  - Runs checks/odoo_lint.py (this hook's own sibling script — located via
    __file__, not cwd, so it works regardless of where the skill was
    installed) against just that file.
  - CRITICAL finding(s) -> block (exit 2), surfacing them to Claude so they
    get fixed immediately.
  - Anything else (HIGH/MEDIUM, no findings, script missing, python3
    issues, unparseable JSON) -> fails open, exit 0, silent.
"""
import json
import os
import subprocess
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT_SCRIPT = os.path.join(SKILL_ROOT, "checks", "odoo_lint.py")


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def block(reason):
    sys.stderr.write(reason + "\n")
    sys.exit(2)


def main():
    payload = read_input()
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path")

    if not file_path or not file_path.endswith((".py", ".xml")):
        sys.exit(0)

    if not os.path.exists(file_path) or not os.path.exists(LINT_SCRIPT):
        sys.exit(0)

    try:
        result = subprocess.run(
            [sys.executable or "python3", LINT_SCRIPT, file_path, "--format", "json"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        findings = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        sys.exit(0)

    critical = [f for f in findings if f.get("severity") == "CRITICAL"]
    if not critical:
        sys.exit(0)

    lines = [f"{f['rule']} ({os.path.basename(f['file'])}:{f['line']}): {f['message']}" for f in critical]
    block(
        "checks/odoo_lint.py found CRITICAL issue(s) in the file you just edited "
        "— fix these before moving on:\n" + "\n".join(lines)
    )


if __name__ == "__main__":
    main()
