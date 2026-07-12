# Model Patterns Migration — v18 → v19

## Breaking changes

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name = models.Constraint('sql', 'msg')` (bare attribute) |
| Indexes | `_auto_init()` + `create_index()` | `_name = models.Index("(cols)")` (bare attribute) |
| SQL import | `from odoo.tools.sql import SQL` | `from odoo.tools import SQL` |
| Domain class | `odoo.osv.expression` | `from odoo.fields import Command, Domain` |
| M2O bypass | — | `bypass_search_access=True` |

## NOT mandatory (common false claims)

- Type hints — only 2/3700 lines in account.move.line use them
- SQL() builder — raw parameterized `cr.execute()` still valid

## Quick examples

```python
# v18
_sql_constraints = [('name_uniq', 'unique(name)', 'Must be unique!')]
from odoo.tools.sql import SQL

# v19
_name_uniq = models.Constraint('unique(name)', 'Must be unique!')
_name_idx = models.Index("(name, company_id)")
from odoo.tools import SQL
from odoo.fields import Domain
combined = Domain.OR([domain_a, domain_b])
```

## Checklist

```
MUST FIX:
[ ] _sql_constraints → models.Constraint() bare attributes
[ ] create_index() → models.Index() bare attributes
[ ] from odoo.tools.sql → from odoo.tools (if using SQL())

ADOPT:
[ ] Domain class for domain manipulation
[ ] bypass_search_access=True on M2O where needed

NOT REQUIRED:
[ ] Type hints on all methods
[ ] SQL() on all raw queries
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Type hints NOT mandatory — don't flag absence |
| CRITICAL | Raw SQL NOT removed — parameterized `cr.execute()` still valid |
| HIGH | `models.Constraint()`/`models.Index()` never in list wrappers |
| HIGH | SQL import: `odoo.tools` not `odoo.tools.sql` in v19 |