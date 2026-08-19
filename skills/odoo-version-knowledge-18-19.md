# Version Knowledge Migration — v18 → v19

## Breaking changes

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | arbitrary attribute = `models.Constraint(...)` (bare instance, never a list) — old form now just logs a warning and is non-functional |
| Indexes | `index=True` on fields | arbitrary attribute = `models.Index("(cols)")` (bare instance, never a list) |
| `odoo.osv.expression` | available, no warning | `DeprecationWarning` on instantiation ("Since 19.0") → use `from odoo.fields import Domain` instead |
| `record._cr/_context/_uid` | available | deprecated → `self.env.cr/.context/.uid` |
| OWL `readGroup()` | available | removed → `formattedReadGroup()` |

## Unchanged from v18

- `<list>`, `<chatter/>`, `aggregator=`, `invisible=`
- `@odoo-module` not required
- `from odoo import _` still valid
- Record rules: `company_ids` in `domain_force`
- `SQL()` — both `from odoo.tools import SQL` and `from odoo.tools.sql import SQL` work in v18 and v19 alike; NOT a breaking change
- OWL 2.x

## Migration checklist

```
CRITICAL:
[ ] _sql_constraints → models.Constraint() bare class attributes
[ ] record._cr/_context/_uid → self.env.cr/.context/.uid

HIGH:
[ ] OWL: readGroup() → formattedReadGroup()

MEDIUM:
[ ] odoo.osv.expression → Domain class (from odoo.fields import Domain) — old import still works but warns
[ ] SQL() import unchanged, no action needed (from odoo.tools import SQL works since v17)
[ ] Review _read_group usage — native GROUPING SETS support added in v19 ORM

INFO:
[ ] No OWL migration (still 2.x)
[ ] No tree/list/chatter migration (already done in 17→18)
[ ] Type hints still optional
```