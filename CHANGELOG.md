# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
