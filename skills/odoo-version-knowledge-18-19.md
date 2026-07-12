# Version Knowledge Migration — v18 → v19

## Breaking changes

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name = models.Constraint(...)` (bare attribute) |
| Indexes | `index=True` on fields | `_name = models.Index("(cols)")` (bare attribute) |
| SQL import | `from odoo.tools.sql import SQL` | `from odoo.tools import SQL` |
| `odoo.osv` | available | deprecated → `from odoo import expression` (or `Domain`) |
| `record._cr/_context/_uid` | available | deprecated → `self.env.cr/.context/.uid` |
| OWL `readGroup()` | available | removed → `formattedReadGroup()` |

## Unchanged from v18

- `<list>`, `<chatter/>`, `aggregator=`, `invisible=`
- `@odoo-module` not required
- `from odoo import _` still valid
- Record rules: `company_ids` in `domain_force`
- OWL 2.x

## Migration checklist

```
CRITICAL:
[ ] _sql_constraints → models.Constraint() bare class attributes
[ ] record._cr/_context/_uid → self.env.cr/.context/.uid

HIGH:
[ ] from odoo.tools.sql import SQL → from odoo.tools import SQL (if using SQL())
[ ] OWL: readGroup() → formattedReadGroup()

MEDIUM:
[ ] odoo.osv.expression → Domain class (from odoo.fields import Domain)
[ ] Review pivot views — GROUPING SETS now native

INFO:
[ ] No OWL migration (still 2.x)
[ ] No tree/list/chatter migration (already done in 17→18)
[ ] Type hints still optional
```