---
name: odoo-code-reviewer
description: Odoo module code review — quality, security, performance, and version compliance.
disable-model-invocation: true
---

Review Odoo module code systematically. Do not generate new code.

---

## Step 1 — Reasoning block

```
REVIEW ANALYSIS:
- Odoo version: [X]
- Files to review: [list]
- Version-specific checks active: [list]
```

## Step 2 — Systematic review

Check every category below. Mark each item OK or flag with file + line reference.

## Step 3 — Generate report using [Output format](#output-format).

---

## Review categories

**Manifest:** version format (`X.0.Y.Z.W`), depends complete, data order (security → data → views → menus), assets, license.

**Models:** correct `_inherit` vs `_name`, decorators per version, field naming (`_id`/`_ids`), computed fields optimized (`store=`), constraints, CRUD calls `super()`, `action_*` calls `ensure_one()`.

**Security:** `ir.model.access.csv` for every model, record rules use `company_ids` (not `allowed_company_ids`), no SQL injection, no unjustified `sudo()`, no hardcoded IDs.

**Views:** `invisible=`/`readonly=`/`required=` directly (no `attrs=`), always xpath inherit, group restrictions applied.

**Performance:** indexed search fields, no N+1 (`browse`/`search` in loops), `mapped()`/`filtered()` for batch ops.

**OWL/JS:** OWL 2.x all versions, `@odoo-module` only v17, services via `useService()`, registry registration present.

**Tests:** unit + security + edge cases present.

---

## Version-specific checks

For detailed breaking changes per version → load `skills/odoo-version-knowledge-{version}.md`

**v17:** `@odoo-module` required, no `attrs=`, `group_operator=`
**v18:** `aggregator=`, `<list>`, `<chatter/>`, no `@odoo-module`, `read_group()` deprecated
**v19:** `models.Constraint()`, `models.Index()`, `from odoo.tools import SQL`, `record._cr` deprecated

---

## SOLID — applied to Odoo

Review as judgment calls, not mechanical checks. Flag with specific method + suggestion.

**S — Single Responsibility:** Each `action_*` does one thing. Flag methods mixing validation + computation + side effects. Each concern in a separate method.

**O — Open/Closed:** Extend via `_inherit`, never patch/overwrite without inheritance.

**L — Liskov Substitution:** Overrides must fulfill the original contract. Flag: changed return type, skipped `super()`, unexpected side effects.

**I — Interface Segregation:** Mixins carry only needed methods. Flag bloated custom mixins.

**D — Dependency Inversion:** Use ORM (`self.env['model']`), not hardcoded IDs or reimplemented logic from dependencies.

---

## UI checks

- Smart buttons: `oe_stat_button` + `widget="statinfo"` + meaningful count
- Primary actions in header/statusbar, secondary in Action menu
- No `x_studio_` fields (Studio-generated logic outside version control)

---

## Logging checks

- `_logger` at module level (not inside methods)
- No empty `except` blocks — log or re-raise
- `UserError`/`ValidationError` messages in business language, no technical names/traces
- Flag `search()` + per-record access → suggest `search_read()`

---

## Output format

```
# Code Review: {module_name}
## Version: {odoo_version}

### Overall assessment
- Security:           ★★★★☆
- Code quality:       ★★★★★
- Performance:        ★★★☆☆
- Version compliance: ★★★★★
- Test coverage:      ★★☆☆☆

### Critical issues — fix immediately
1. [CATEGORY] file:line — Issue + Current + Fix

### Warnings — should fix
1. [CATEGORY] file:line — Issue + Fix

### Suggestions — nice to have

### Positive observations

### Files reviewed
| File | Issues |
|------|--------|
```