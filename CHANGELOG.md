# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-07-12

### Changed
- Compressed every file in `skills/` and `agents/`, plus `SKILL.md`, from the
  original XML-tagged format to plain markdown (headers, tables, fenced code
  blocks) — ~77% token reduction with no loss of content, so each `Read`
  costs a fraction of the tokens it used to.
- `README.md` "Design Principles" section rewritten to describe the new
  plain-markdown file shape instead of the retired XML tag vocabulary
  (`<pattern>`, `<agent>`, etc.).

### Fixed
- Restored the context-session lifecycle protocol that the compression pass
  had dropped from `SKILL.md` without moving it anywhere: added
  `skills/context-session-management.md` so the dangling reference in
  `SKILL.md`'s "Context session management" section resolves to real content
  again (hook verification steps, `status` lifecycle table, completion
  signals).
- Corrected several false or internally-contradictory Odoo v17→19 migration
  claims across `skills/` and `agents/`, verified against the real Odoo
  Community source (18.0/19.0 branches): `allowed_company_ids` does not
  replace `company_ids` in `ir.rule` domains; type hints and the `SQL()`
  builder are not mandatory in v19; `models.Constraint()`/`models.Index()`
  are bare class attributes, not wrapped in a list; `formattedReadGroup`'s
  count aggregate is the literal `"__count"`; `from odoo import _` remains
  valid in v19; bare `<chatter/>` is the dominant real-world form.
- `MAINTENANCE.md` refresh checklist updated to reference the current
  "Pattern index" / "Breaking changes" markdown tables in `SKILL.md` instead
  of the retired `<version_router>`/`<pattern_index>` XML tags.
- `examples/` files (`README.md`, `bad-vs-good-prompts.md`,
  `common-tasks.md`, `agent-skill-finder.md`, `agent-upgrade-analyzer.md`,
  `xml-structured-prompts.md`) updated to stop describing `SKILL.md` as
  XML-tag driven now that it and every `skills/`/`agents/` file are plain
  markdown.

## [1.2.0] - 2026-07-03

### Added
- `init` CLI subcommand (`bin/install.js`) that wires the odoo-dev-skill hooks
  into a project's `.claude/settings.json` automatically — resolves the
  absolute path to the globally installed hooks, creates the file or merges
  into it without touching other keys, supports `--dry-run`, and is a no-op
  if the hooks are already declared. Cross-platform (Linux/macOS/Windows).
- `context_session_guard.py` now implements the status-driven lifecycle
  already documented in `SKILL.md`: `status="completed"` archives a
  `<session>` entry into `history_context.xml` and resets
  `context_session.xml` to a blank template; `status="checkpoint"` allows a
  clean stop with no stale-file check; `status="in_progress"` keeps the
  existing char-budget and stale-file enforcement.
- `SKILL.md` gains two steps at the start of every task: resolve the skill's
  install path, and check whether `.claude/settings.json` already declares
  the hooks — warning the user once (without blocking or writing the file)
  if they're missing.

### Changed
- `README.md` installation instructions restructured into "Step 1 — install
  globally" and "Step 2 — run `init` per project", replacing the old
  instruction to manually edit `.claude/settings.json`.
- `examples/context-session-and-history.md` updated to show the `init`
  command instead of the manual hooks JSON snippet, with new sections on
  what happens without `init` and on setting up future projects.
- Local-dev symlink instructions in `README.md` corrected to the actual
  script name (`link_skills.sh`, not `scripts/link-skills.sh`).

## [1.1.0] - 2026-07-03

### Added
- Automatic `context_session.xml` lifecycle driven by a new `status` attribute
  (`in_progress` / `checkpoint` / `completed`), documented in a new
  "Context management" section in `SKILL.md` and reflected in the
  `templates/context_session.xml` template.
- `hooks/` and `templates/` are now bundled and installed: `package.json`'s
  `files` field includes them, `bin/install.js` copies both directories into
  the target install, and `scripts/link_skills.sh` symlinks them for local
  development.

### Changed
- `examples/context-session-and-history.md` rewritten (in Spanish) to describe
  the fully automatic, hook-driven session workflow — replacing the older
  manual "XML-structured request" prose examples.

### Fixed
- Missing trailing newline in `examples/common-tasks.md`.

## [1.0.0] - 2026-07-02

Initial release.

### Added
- Odoo module development skill for Claude Code (versions 17, 18, 19) with
  OCA-standard patterns and specialized agents.
- Deterministic checks (`checks/`), session context tracking
  (`context_session.xml` / `history_context.xml`), usage examples, and a
  version maintenance plan (`MAINTENANCE.md`).
- `npx` installer (`bin/install.js`) and a local-dev symlink script
  (`scripts/link_skills.sh`).
