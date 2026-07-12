---
name: odoo-dev-skill
description: >
  Odoo module development for versions 17, 18 and 19 following OCA standards.
  Use when the user asks to create, modify, review or migrate Odoo modules,
  models, views, controllers, wizards, reports, security, OWL components,
  or any task involving __manifest__.py, ORM fields, xpath, or ir.model.*.
versions: "17,18,19"
---

Read `__manifest__.py` first. Extract version (`X.0.Y.Z`) — first number
is Odoo major (17, 18 or 19). **If unknown, ask. Below 17, stop.**

Communicate with the user in their language. Code/variables/docstrings
in English.

---

## Task routing

**Simple** (single file/field/view fix) → check forbidden rules below,
read the matching pattern file, write code.

**Complex** (new module, new model, migration, multi-file) →
Read `agents/odoo-context-gatherer.md` and follow its workflow.

---

## Forbidden rules

CRITICAL:
- No `cr.commit()`/`cr.rollback()` unless you own the cursor.
- No raw SQL when ORM suffices — use `search()`, `read_group()`, `filtered()`.
- No `attrs=` in v17+ — use `invisible=` directly.
- No full view replacement — always xpath + inherit.
- No `# -*- coding: utf-8 -*-`.

HIGH:
- No `browse()`/`search()` inside loops — use `mapped()`/`filtered()`.
- No ORM calls in `@api.depends` without full dependency chain.
- No hardcoded IDs — `env.ref('xml_id')`.
- `self.ensure_one()` as first line of every `action_*`.
- No broad `except Exception` without savepoint.
- `_()` only on literals: `_('text %s', var)`.

MEDIUM:
- No `print()` — use `_logger`.
- Model attribute order: `_name/_inherit` → fields → constraints → compute → CRUD → actions → business.
- M2O → `_id`, O2M/M2M → `_ids`.
- Singular `_name` (`sale.order` not `sale.orders`).

---

## Pattern index

Read the file **before** writing code:

| Keywords | File |
|----------|------|
| owl, component, dashboard, frontend | `skills/odoo-owl-components.md` |
| qweb, template, t-if, t-foreach | `skills/qweb-template-patterns.md` |
| field widget, custom widget | `skills/widget-field-patterns.md` |
| computed, depends, inverse, stored | `skills/computed-field-patterns.md` |
| constraint, validation, _sql_constraints | `skills/constraint-patterns.md` |
| onchange, dynamic domain | `skills/onchange-dynamic-patterns.md` |
| view, form, list, kanban, search, pivot | `skills/xml-view-patterns.md` |
| workflow, state machine, statusbar | `skills/workflow-state-patterns.md` |
| wizard, transient, dialog | `skills/wizard-patterns.md` |
| cron, scheduled action | `skills/cron-automation-patterns.md` |
| mail, chatter, activity, message_post | `skills/mail-notification-patterns.md` |
| sequence, numbering | `skills/sequence-numbering-patterns.md` |
| controller, http route, json-rpc | `skills/controller-api-patterns.md` |
| external api, webhook, xml-rpc | `skills/external-api-patterns.md` |
| portal, token, share link | `skills/portal-access-patterns.md` |
| fastapi, pydantic, openapi | `skills/fastapi-patterns.md` |
| multi-company, company_ids | `skills/multi-company-patterns.md` |
| inherit, extend, override | `skills/inheritance-patterns.md` |
| assets, javascript, css, scss | `skills/assets-bundling-patterns.md` |
| context, env, sudo, with_context | `skills/context-environment-patterns.md` |
| performance, index, prefetch, N+1 | `skills/odoo-performance-guide.md` |
| exception, UserError, AccessError | `skills/error-handling-patterns.md` |
| test, unittest, TransactionCase | `skills/odoo-test-patterns.md` |
| report, pdf, QWeb report | `skills/report-patterns.md` |
| settings, res.config.settings | `skills/config-settings-patterns.md` |
| translation, i18n, _lt | `skills/translation-i18n-patterns.md` |
| domain, filter, search criteria | `skills/domain-filter-patterns.md` |

Versioned families: `odoo-version-knowledge`, `odoo-model-patterns`,
`odoo-module-generator`, `odoo-owl-components`, `odoo-security-guide`
→ append `-{version}.md` (e.g. `odoo-model-patterns-19.md`)
→ migration: append `-17-18.md` or `-18-19.md`

---

## Breaking changes (quick ref)

| Change | Versions |
|--------|----------|
| `group_operator=` → `aggregator=` | 17→18 |
| `<tree>` → `<list>` | 17→18 |
| `<div class="oe_chatter">` → `<chatter/>` | 17→18 |
| `@odoo-module` no longer required | 17→18 |
| `orm.readGroup()` → `orm.formattedReadGroup()` | 18→19 |
| `_sql_constraints` → `models.Constraint()` | 18→19 |
| SQL import: `odoo.tools.sql` → `odoo.tools` | 18→19 |

Full details → `skills/odoo-version-knowledge-{from}-{to}.md`

---

## Agents

| Task | File |
|------|------|
| Code review / security audit | `agents/odoo-code-reviewer.md` |
| Migration between versions | `agents/odoo-upgrade-analyzer.md` |
| Pattern lookup | `agents/odoo-skill-finder.md` |
| Guidelines validation | `agents/odoo-coding-guidelines-validator.md` |
| Complex task context | `agents/odoo-context-gatherer.md` |

---

## Context session management

See `skills/context-session-management.md` for the full protocol
(context_session.xml lifecycle, hooks verification, status transitions).