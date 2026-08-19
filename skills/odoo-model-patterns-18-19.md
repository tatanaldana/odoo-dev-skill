# Model Patterns Migration — v18 → v19

## Breaking changes

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name = models.Constraint('sql', 'msg')` (bare attribute) |
| Indexes | `_auto_init()` + `create_index()` | `_name = models.Index("(cols)")` (bare attribute) |
| Domain class | `odoo.osv.expression` (functions, no class) | `from odoo.fields import Command, Domain` |
| M2O bypass | `auto_join=True` (SQL-join side effect; silently removed in v19 — no error/warning, just stops working) | `bypass_search_access=True` (explicit ir.rule bypass; not a literal rename of `auto_join`) |

## NOT changed (common false claims)

- SQL import — `from odoo.tools.sql import SQL` AND `from odoo.tools import SQL` have both been valid since v17; neither path changes in v19 (`odoo/tools/__init__.py` does `from .sql import *` in v17/v18/v19 alike)

## NOT mandatory (common false claims)

- Type hints — only a handful of lines (~3 of 3740) in account.move.line use them
- SQL() builder — raw parameterized `cr.execute()` still valid

## Quick examples

```python
# v18
_sql_constraints = [('name_uniq', 'unique(name)', 'Must be unique!')]
from odoo.tools.sql import SQL  # also works unchanged in v19

# v19
_name_uniq = models.Constraint('unique(name)', 'Must be unique!')
_name_idx = models.Index("(name, company_id)")
from odoo.tools import SQL  # equivalent short form, valid since v17
from odoo.fields import Domain
combined = Domain.OR([domain_a, domain_b])
```

## Checklist

```
MUST FIX:
[ ] _sql_constraints → models.Constraint() bare attributes
[ ] create_index() → models.Index() bare attributes
[ ] audit auto_join=True fields — silently ignored in v19, no error; replace with bypass_search_access=True if the intent was to bypass ir.rule access

ADOPT (optional, not breaking):
[ ] Domain class for domain manipulation
[ ] bypass_search_access=True on M2O where needed
[ ] from odoo.tools import SQL — shorter form, purely cosmetic (odoo.tools.sql path still valid)

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
| HIGH | `auto_join=True` silently ignored in v19 (no error/warning) — audit, don't assume it still works |
| LOW | SQL import: `odoo.tools` and `odoo.tools.sql` are BOTH valid in v19 — not a required change |