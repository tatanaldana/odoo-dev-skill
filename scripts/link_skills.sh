#!/usr/bin/env bash
# scripts/link_skills.sh
# Links SKILL.md, agents/, skills/, hooks/ and templates/ from this repo into
# ~/.claude/skills/odoo-dev-skill/ and ~/.agents/skills/odoo-dev-skill/
# for local development. Changes to the repo are reflected immediately without reinstalling.

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

  # ln -sfn only replaces an existing *symlink* atomically. If $2 is a real
  # file or (non-empty) directory — e.g. left over from a prior `npx`
  # install — plain `ln -sfn` on BSD/macOS creates the new symlink *inside*
  # it instead of replacing it, silently leaving the stale copy in place.
  # Remove any non-symlink leftover first so the link always lands cleanly.
  link_item() {
    local src="$1" dst="$2"
    if [ -e "$dst" ] || [ -L "$dst" ]; then
      if [ ! -L "$dst" ] || [ "$(readlink "$dst")" != "$src" ]; then
        rm -rf "$dst"
      fi
    fi
    ln -sfn "$src" "$dst"
  }

  # Link SKILL.md
  link_item "$REPO/SKILL.md" "$DEST/SKILL.md"
  echo "linked SKILL.md -> $DEST/SKILL.md"

  # Link agents/
  if [ -d "$REPO/agents" ]; then
    link_item "$REPO/agents" "$DEST/agents"
    echo "linked agents/ -> $DEST/agents"
  fi

  # Link skills/
  if [ -d "$REPO/skills" ]; then
    link_item "$REPO/skills" "$DEST/skills"
    echo "linked skills/ -> $DEST/skills"
  fi

  # Link hooks/
  if [ -d "$REPO/hooks" ]; then
    link_item "$REPO/hooks" "$DEST/hooks"
    echo "linked hooks/ -> $DEST/hooks"
  fi

  # Link templates/
  if [ -d "$REPO/templates" ]; then
    link_item "$REPO/templates" "$DEST/templates"
    echo "linked templates/ -> $DEST/templates"
  fi

  echo "done: $DEST"
  echo ""

done

echo "Restart or reload Claude Code so it picks up the linked skill."