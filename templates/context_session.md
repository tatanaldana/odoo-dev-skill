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
