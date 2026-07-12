# Security Guide Migration — v18 → v19

## What changes

| Component | v18 | v19 | Action |
|-----------|-----|-----|--------|
| Constraints | `_sql_constraints` | `models.Constraint()` bare attribute | recommended |
| Indexes | `index=` on fields | `models.Index()` bare attribute | recommended |
| SQL import | `odoo.tools.sql` | `odoo.tools` | required if using SQL() |
| Type hints | recommended | still recommended | optional |
| Raw SQL | valid | still valid | no change |

## What does NOT change

- Record rules: `company_ids` in `domain_force`
- `_check_company_auto` + `check_company=True`
- View syntax: `invisible=` expressions

## Constraint/Index migration

```python
# v18
_sql_constraints = [('name_uniq', 'UNIQUE(name, company_id)', 'Must be unique!')]

# v19 — bare attributes, never list-wrapped
_name_uniq = models.Constraint('UNIQUE(name, company_id)', 'Must be unique!')
_company_idx = models.Index("(company_id)")
```

## SQL import

```python
# v18
from odoo.tools.sql import SQL
# v19
from odoo.tools import SQL
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Type hints NOT mandatory — don't flag absence |
| CRITICAL | `from odoo.tools.sql import SQL` wrong in v19 |
| CRITICAL | Raw parameterized `cr.execute()` still valid in v19 |
| HIGH | `models.Constraint()`/`models.Index()` never in list wrapper |