---
name: odoo-dev-skill
description: >
  Odoo module development for versions 17, 18 and 19 following OCA standards.
  Use when the user asks to create, modify, review or migrate Odoo modules,
  models, views, controllers, wizards, reports, security, OWL components,
  or any task involving __manifest__.py, ORM fields, xpath, or ir.model.*.
versions: "17,18,19"
---

Read `__manifest__.py` before anything else. Extract the version field
(`X.0.Y.Z`) — the first number is the Odoo major version (17, 18 or 19).
**If the version cannot be determined, stop and ask before proceeding.**
**If the version is below 17, stop — this skill covers 17, 18 and 19 only.**

Communicate with the user in their language. Code, variables, and docstrings
always in English.

---

## Classify the task

**Simple** — single file, single field, single view tweak, quick fix:
proceed directly to [Simple task workflow](#simple-task-workflow).

**Complex** — new module, new model, migration between versions, multiple
files, or architectural decision:
Read `agents/odoo-context-gatherer.md` and follow its workflow.

---

## Simple task workflow

1. Check the [Forbidden rules](#forbidden-rules) before writing any line.
2. Read the relevant file from the [Pattern index](#pattern-index) using
   the Read tool before writing any code.
3. Apply [Development standards](#development-standards).
4. Write the code.

---

## Forbidden rules

CRITICAL — break the module or cause data loss:

- Never call `cr.commit()` or `cr.rollback()` manually unless you created
  your own cursor.
- Never use raw SQL (`cr.execute`) when the ORM can do the same — use
  `search()`, `read_group()`, or `filtered()` instead.
- Never use `attrs=` for visibility in v17+ — use `invisible=` directly.
- Never replace XML views entirely — always use xpath + inherit.
- Never add `# -*- coding: utf-8 -*-` — Python 3 does not need it.

HIGH — silent bugs, hard to detect:

- Never call `browse()` or `search()` inside a loop — use `mapped()` or
  `filtered()`.
- Never make ORM calls inside `@api.depends` without listing the full
  dependency chain.
- Never hardcode database IDs — always use `xml_id` with `env.ref()`.
- Always call `self.ensure_one()` as the first line of every `action_*` method.
- Never catch broad exceptions (`except Exception`) without a savepoint.
- Never use `_()` on dynamic strings or concatenations — only
  `_('literal')` or `_('pattern %s', variable)`.

MEDIUM — standard violations:

- Never use `print()` — use `_logger.info / warning / error`.
- Declare model attributes in this order: `_name/_description/_inherit` →
  default methods → fields → SQL constraints → compute/search/inverse →
  `@api.constrains/@api.onchange` → CRUD overrides → `action_*` → business
  methods.
- Many2one fields require `_id` suffix; One2many/Many2many require `_ids`.
- Model `_name` must be singular (`sale.order` not `sale.orders`).
- Never include the word "wizard" in transient model names — use
  `base_model.action` pattern (e.g. `account.invoice.make`).
- Never name a controller file `main.py` — use `module_name.py`.

---

## Development standards

**Python:** PEP8, SOLID, DRY, KISS. Always `super()` without arguments.
Imports: stdlib → odoo core → odoo addons, alphabetical within each group.

**JavaScript:** ES6+, PascalCase classes, one component per file.
OWL 2.x for v17, v18, and v19. See `skills/odoo-owl-components-{version}.md`.

**XML:** `invisible=` only — `attrs=` was removed in v17.
Always inherit with xpath, never replace a view.

**Security:** `ir.model.access.csv` is required for every new model —
no exceptions.

**Performance:** No N+1 — never `search()` or `browse()` per record.
Use `mapped()`, `filtered()`, `read_group()`.

---

## Breaking changes

| From → To | Change |
|-----------|--------|
| 17 → 18 | `group_operator=` → `aggregator=` on fields |
| 17 → 18 | `<tree>` → `<list>` in views |
| 17 → 18 | `<div class="oe_chatter">` → `<chatter/>` tag |
| 17 → 18 | `@odoo-module` no longer required in JS |
| 17 → 18 | ORM constructor refactored (no args) |
| 18 → 19 | `orm.readGroup()` removed → `orm.formattedReadGroup()` |
| 18 → 19 | `_sql_constraints` → `models.Constraint()` |
| 18 → 19 | Manual index definitions → `models.Index()` |
| 18 → 19 | SQL import: `odoo.tools.sql` → `odoo.tools` |

Version-specific files: `skills/odoo-version-knowledge-{version}.md`
Migration guides: `skills/{pattern}-17-18.md`, `skills/{pattern}-18-19.md`

---

## Pattern index

Read the relevant file using the Read tool before writing any code.

| Keywords | File |
|----------|------|
| owl, component, client action, dashboard, frontend | `skills/odoo-owl-components.md` |
| qweb, template, t-if, t-foreach, t-call, t-slot | `skills/qweb-template-patterns.md` |
| field widget, custom widget, render field | `skills/widget-field-patterns.md` |
| computed, depends, inverse, stored compute | `skills/computed-field-patterns.md` |
| constraint, validation, check, _sql_constraints | `skills/constraint-patterns.md` |
| onchange, dynamic domain, conditional field | `skills/onchange-dynamic-patterns.md` |
| view, form, list, kanban, search, pivot | `skills/xml-view-patterns.md` |
| workflow, state machine, statusbar, button transition | `skills/workflow-state-patterns.md` |
| wizard, transient, dialog, popup | `skills/wizard-patterns.md` |
| cron, scheduled action, automation rule | `skills/cron-automation-patterns.md` |
| mail, email, chatter, activity, message_post | `skills/mail-notification-patterns.md` |
| sequence, numbering, auto-increment | `skills/sequence-numbering-patterns.md` |
| controller, http route, api endpoint, rest, json-rpc | `skills/controller-api-patterns.md` |
| external api, webhook, sync, xml-rpc | `skills/external-api-patterns.md` |
| portal, token, share link, CustomerPortal | `skills/portal-access-patterns.md` |
| fastapi, pydantic, openapi, swagger, oca api | `skills/fastapi-patterns.md` |
| multi-company, res.company, company_ids, with_company | `skills/multi-company-patterns.md` |
| inherit, extend, override, _inherit, _inherits | `skills/inheritance-patterns.md` |
| assets, javascript, css, scss, bundle | `skills/assets-bundling-patterns.md` |
| context, env, sudo, with_context, with_user | `skills/context-environment-patterns.md` |
| performance, optimization, index, prefetch, N+1 | `skills/odoo-performance-guide.md` |
| exception, UserError, ValidationError, AccessError | `skills/error-handling-patterns.md` |
| test, unittest, TransactionCase, HttpCase, mock | `skills/odoo-test-patterns.md` |
| report, pdf, QWeb report, print | `skills/report-patterns.md` |
| settings, res.config.settings, ir.config_parameter | `skills/config-settings-patterns.md` |
| translation, i18n, language, _lt, LazyTranslate | `skills/translation-i18n-patterns.md` |
| domain, filter, search criteria | `skills/domain-filter-patterns.md` |

Versioned families (prefer version-specific file when it exists):
`odoo-version-knowledge`, `odoo-model-patterns`, `odoo-module-generator`,
`odoo-owl-components`, `odoo-security-guide`

---

## Context management

This section defines the agent's automatic behavior — no special prompts
required from the user.

**At the start of every task**, check `.claude/odoo-dev-skill/context_session.xml`:
- Exists, same task → read once and resume; do not re-ask answered questions.
- Exists, different task → ask the user before overwriting.
- Does not exist → create it from `templates/context_session.xml`, filling
  `id` (short slug), `started` (ISO timestamp), and `odoo_version`.

**During the task**, hold state in memory. Write `context_session.xml` only
at **logical checkpoints** — a coherent unit of work complete (model + its
views, not file by file). Set `status="checkpoint"` on that write.
Never re-read the file between checkpoints; one read at session start is enough.

**Status lifecycle** — the Stop hook reads this attribute to decide what to do:

| status | When the agent sets it | What the Stop hook does |
|---|---|---|
| `in_progress` | Default; task active, more prompts expected | Checks budget + stale files; blocks if either fails |
| `checkpoint` | Just finished a logical block | Allows stop cleanly; no stale-file check |
| `completed` | User signalled end of task | Archives to `history_context.xml`, resets file, allows stop |

**Signals that indicate `completed`** — detect naturally without waiting for
an explicit command:
- Explicit: "terminamos", "listo", "perfecto así", "esto es todo", "abre el PR"
- Implicit: user requests a full module review, asks to generate the final
  `__manifest__.py` with all files listed, or asks to run the linter on the
  whole module.

Keep `context_session.xml` under ~12,000 characters. Compress `<decisions>`
and `<files_touched>` into denser summaries if it grows too large before
the next checkpoint write.

The Stop hook (`hooks/context_session_guard.py`) and PostToolUse hook
(`hooks/odoo_edit_guard.py`) enforce this mechanically in Claude Code.
Wire them in the project's `.claude/settings.json` using the **absolute path**
to the installed skill (e.g. `~/.claude/skills/odoo-dev-skill/hooks/`).

---

## Agents

To invoke an agent, Read its file and follow its workflow:

- Code review or security audit → Read `agents/odoo-code-reviewer.md`
- Migration between versions → Read `agents/odoo-upgrade-analyzer.md`
- Precise pattern lookup → Read `agents/odoo-skill-finder.md`
- Guidelines validation → Read `agents/odoo-coding-guidelines-validator.md`