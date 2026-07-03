#!/usr/bin/env bash
# scripts/link-skills.sh
# Links SKILL.md, agents/ and skills/ from this repo into ~/.claude/skills/odoo-dev-skill/
# and ~/.agents/skills/odoo-dev-skill/ for local development.
# Changes to the repo are reflected immediately without reinstalling.

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="odoo-dev-skill"

TARGETS=(
  "$HOME/.claude/skills/$SKILL_NAME"
  "$HOME/.agents/skills/$SKILL_NAME"
)

for DEST in "${TARGETS[@]}"; do

  # Guard against DEST itself being a symlink into this repo
  if [ -L "$DEST" ]; then
    resolved="$(readlink -f "$DEST")"
    case "$resolved" in
      "$REPO"|"$REPO"/*)
        echo "error: $DEST is a symlink into this repo ($resolved)." >&2
        echo "Remove it and re-run; the script will recreate it as a real directory." >&2
        exit 1
        ;;
    esac
  fi

  mkdir -p "$DEST"

  # Link SKILL.md
  ln -sfn "$REPO/SKILL.md" "$DEST/SKILL.md"
  echo "linked SKILL.md -> $DEST/SKILL.md"

  # Link agents/
  if [ -d "$REPO/agents" ]; then
    ln -sfn "$REPO/agents" "$DEST/agents"
    echo "linked agents/ -> $DEST/agents"
  fi

  # Link skills/
  if [ -d "$REPO/skills" ]; then
    ln -sfn "$REPO/skills" "$DEST/skills"
    echo "linked skills/ -> $DEST/skills"
  fi

  echo "done: $DEST"
  echo ""

done

echo "Restart or reload Claude Code so it picks up the linked skill."