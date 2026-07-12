# Module Generator Migration — v18 → v19

## Changes to apply

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name_uniq = models.Constraint(...)` |
| Indexes | manual | `_my_idx = models.Index("(col1, col2)")` |
| SQL import | `from odoo.tools.sql import SQL` | `from odoo.tools import SQL` |
| Domain class | not available | `from odoo.fields import Command, Domain` |
| M2O bypass | not available | `bypass_search_access=True` |
| ORM JS | `orm.readGroup()` | `orm.formattedReadGroup()` |

## Manifest

Change version prefix: `'version': '19.0.1.0.0'`

No other manifest changes — `web.assets_unit_tests`, `<list>`, `<chatter/>` are same as v18.

## Model migration checklist

1. Replace all `_sql_constraints` with `models.Constraint()` class attributes
2. Add `models.Index()` for frequently queried columns
3. Change `from odoo.tools.sql import SQL` → `from odoo.tools import SQL`
4. Add `bypass_search_access=True` on M2O fields that need cross-company search
5. Replace `from odoo.osv import expression` → `from odoo import expression` (if used)
6. Replace `record._cr`/`record._context`/`record._uid` → `self.env.cr`/`.context`/`.uid`

## OWL migration

- `orm.readGroup()` → `orm.formattedReadGroup()`
- New: `orm.cache()`, `orm.webSaveMulti()`, `orm.webResequence()`

For full v19 patterns → see `odoo-model-patterns-19.md`