# Module Generator Migration — v18 → v19

## Changes to apply

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name_uniq = models.Constraint(...)` — old style now logs a warning and the constraint is silently NOT applied (fix required) |
| Indexes | manual | `_my_idx = models.Index("(col1, col2)")` |
| SQL import | `from odoo.tools import SQL` (already works) | same — no real change; `from odoo.tools import SQL` has worked since v17 |
| Domain class | not available | `from odoo.fields import Command, Domain` (new query-builder class) |
| Relational field bypass | not available | `bypass_search_access=True` — on Many2one, One2many, AND Many2many (not just M2O) |
| `odoo.osv` / `odoo.osv.expression` | available, no warning | deprecated (`DeprecationWarning` on import of `odoo.osv`) — replace with `from odoo.fields import Domain`, NOT `from odoo import expression` (no such module exists) |
| `read_group()` (Python) | available, not deprecated | `@api.deprecated` — use `_read_group()` (backend) or the read_group JS service's `formattedReadGroup` |
| `record._cr/_context/_uid` | available, not deprecated | `@api.deprecated` (soft — still works) → use `self.env.cr/.context/.uid` |
| `res.groups.category_id` | field exists directly on res.groups | REMOVED — groups now link via `privilege_id` to a new `res.groups.privilege` model, which carries `category_id` |
| ORM JS | `orm.readGroup()` | `orm.formattedReadGroup()` |

## Manifest

Change version prefix: `'version': '19.0.1.0.0'`

No other manifest changes — `web.assets_unit_tests`, `<list>`, `<chatter/>` are same as v18.

## Model migration checklist

1. Replace all `_sql_constraints` with `models.Constraint()` class attributes (MUST FIX — old style no longer applies the constraint, only logs a warning)
2. Add `models.Index()` for frequently queried columns
3. `from odoo.tools import SQL` already works in v17/v18/v19 — no change needed here; if code still uses `from odoo.tools.sql import SQL`, both remain valid, this is a style preference only
4. Add `bypass_search_access=True` on relational fields (Many2one, One2many, Many2many) that need cross-company/cross-access search
5. `odoo.osv` (including `odoo.osv.expression`) is deprecated in v19 (DeprecationWarning, still functional) — replace with `from odoo.fields import Domain`. There is no `odoo.expression` module to import from.
6. Replace `record._cr`/`record._context`/`record._uid` → `self.env.cr`/`.context`/`.uid` (soft deprecation — old code still works, just warns)
7. Security groups: `res.groups.category_id` no longer exists — create a `res.groups.privilege` record and reference it via `privilege_id` on the group (see `odoo-module-generator-19.md` for the full XML template)

## OWL migration

- `orm.readGroup()` → `orm.formattedReadGroup()`
- New: `orm.cache()`, `orm.webSaveMulti()`, `orm.webResequence()`

For full v19 patterns → see `odoo-model-patterns-19.md`