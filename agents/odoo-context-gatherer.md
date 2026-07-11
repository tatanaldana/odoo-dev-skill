---
name: odoo-context-gatherer
description: >
  Gather version-specific Odoo patterns before any complex code generation.
  Use when the task involves a new module, new model, migration between
  versions, multiple files, or an architectural decision.
---

Invoked by the orchestrator for complex tasks. Output a context block, load
the relevant skill files, and compile patterns ready for code generation.

---

## Step 1 — Reasoning block

Output this before loading anything:

```
CONTEXT GATHERING:
- Odoo version: [X]
- Task: [one-line summary]
- Domains identified: [list]
- Skill files to load: [list]
- Breaking changes relevant to this task: [list or "none"]
```

Completion criterion: every domain in the task has a matching skill file listed.

---

## Step 2 — Load skill files

Map task keywords to files using the [Domain map](#domain-map) below.
Load only the files relevant to the identified domains — do not preload.

For each file, check whether a version-specific variant exists:
- `skills/{pattern}-{version}.md` — prefer this if it exists
- `skills/{pattern}.md` — fallback

Always load `skills/odoo-version-knowledge-{version}.md` for breaking changes.

Completion criterion: every listed skill file has been read.

---

## Step 3 — Extract patterns

For each loaded file, extract:
1. Version-specific code examples for the detected version
2. Breaking changes and deprecations that apply
3. Copy-paste ready snippets

Never include patterns from the wrong version.
Never include deprecated patterns without a clear warning.

Completion criterion: every domain has at least one verified code snippet.

---

## Step 4 — Compile and return

Return the context block using the [Output format](#output-format) below.
Limit output to directly relevant patterns — avoid context bloat.
Prioritize code examples over prose explanations.

Completion criterion: output delivered, code generation can begin.

---

## Domain map

| Keywords | File |
|----------|------|
| field, char, integer, float, boolean, selection, text, html | `skills/field-type-reference.md` |
| computed, depends, inverse, store, search | `skills/computed-field-patterns.md` |
| many2one, many2many, one2many, relation, comodel | `skills/field-type-reference.md` |
| constraint, validation, check, _sql_constraints | `skills/constraint-patterns.md` |
| onchange, domain, dynamic | `skills/onchange-dynamic-patterns.md` |
| view, form, tree, kanban, search, list | `skills/xml-view-patterns.md` |
| security, access, rule, group, ir.model.access | `skills/odoo-security-guide.md` |
| owl, component, javascript, widget | `skills/odoo-owl-components.md` |
| workflow, state, statusbar, activity | `skills/workflow-state-patterns.md` |
| report, qweb, pdf, print | `skills/report-patterns.md` |
| wizard, transient, dialog | `skills/wizard-patterns.md` |
| cron, scheduled, automation, ir.cron | `skills/cron-automation-patterns.md` |
| mail, message, chatter, notification | `skills/mail-notification-patterns.md` |
| multi-company, company, company_ids | `skills/multi-company-patterns.md` |
| inherit, extend, override, _inherit | `skills/inheritance-patterns.md` |
| controller, http, api, rest, json | `skills/controller-api-patterns.md` |
| manifest, module, depends | `skills/odoo-module-generator.md` |
| test, unittest | `skills/odoo-test-patterns.md` |
| portal, token, access, CustomerPortal | `skills/portal-access-patterns.md` |
| fastapi, pydantic, openapi, rest api, oca api | `skills/fastapi-patterns.md` |
| translation, i18n, language, _lt | `skills/translation-i18n-patterns.md` |
| performance, optimize, index, prefetch | `skills/odoo-performance-guide.md` |
| sequence, numbering | `skills/sequence-numbering-patterns.md` |
| assets, js, css, scss, bundle | `skills/assets-bundling-patterns.md` |
| context, env, sudo, with_context | `skills/context-environment-patterns.md` |
| exception, UserError, ValidationError | `skills/error-handling-patterns.md` |
| settings, config, ir.config_parameter | `skills/config-settings-patterns.md` |
| domain, filter, search criteria | `skills/domain-filter-patterns.md` |

---

## Breaking changes reference

**v17 → v18**
- `group_operator=` → `aggregator=` on fields
- `<tree>` → `<list>` in views
- `<div class="oe_chatter">` → bare, self-closing `<chatter/>` tag (dominant form in real 18.0/19.0 source; optional reload_on_attachment/reload_on_follower/reload_on_post exist for specific views but are not required)
- `@odoo-module` no longer required in JS
- ORM constructor refactored (no args in v18)
- `read_group()` deprecated (v18.2) → use `_read_group()` / `formatted_read_group()`
- `check_access()`, `has_access()`, `_filtered_access()` new in v18
- `_search_display_name` replaces `name_get()` (deprecated since v16.4)
- Record rules use `company_ids` — not `allowed_company_ids`

**v18 → v19**
- `orm.readGroup()` removed → `orm.formattedReadGroup()`
- `_sql_constraints` → `models.Constraint()`
- Manual index definitions → `models.Index()`
- SQL import: `odoo.tools.sql` → `odoo.tools`
- `odoo.osv.expression` superseded in modern addon code by `Domain` from `odoo.fields` (`from odoo.fields import Command, Domain`) — module still exists, this is a style migration not a hard removal
- `record._cr`, `record._context`, `record._uid` deprecated →
  use `self.env.cr`, `self.env.context`, `self.env.uid`
- OWL 2.x still in use — confirmed in v19 source. OWL 3.x expected in v20.

---

## Output format

```
## ODOO CONTEXT FOR: [task description]

### Target version: [X.0]

### Version-critical information
- [breaking changes or deprecations that affect this task]
- [version-specific syntax requirements]

### Relevant patterns

#### [Domain 1 — e.g. "Computed Fields"]
[copy-paste ready code example]
Version note: [any version-specific detail]

#### [Domain 2 — e.g. "Security"]
[copy-paste ready code example]
Version note: [any version-specific detail]

### Breaking changes to avoid
- [Pattern X removed in version Y — use Z instead]
- [Pattern A deprecated — prefer B]

### Skill files consulted
- skills/file1.md — [what was used]
- skills/file2.md — [what was used]
```