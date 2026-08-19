# Security Guide Migration — v17 → v18

## Changes

| Component | v17 | v18 | Action |
|-----------|-----|-----|--------|
| SQL | `SQL()` builder already available (`odoo/tools/sql.py`), parameterized `cr.execute()` also common | `SQL()` builder more widely used/recommended | adopt |
| Aggregation | `group_operator=` | `aggregator=` (old still works, DeprecationWarning) | recommended |
| Type hints | optional | recommended | optional |
| `_check_company_auto` | available (long-standing, predates v17) | same | no change |
| Record rules | `company_ids` | same | no change |

## SQL migration

```python
# v17
self.env.cr.execute("SELECT id FROM %s WHERE company_id = %%s" % self._table, [company_id])

# v18
from odoo.tools.sql import SQL
self.env.cr.execute(SQL("SELECT id FROM %(t)s WHERE company_id = %(c)s",
    t=SQL.identifier(self._table), c=company_id))
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `allowed_company_ids` NOT valid in `domain_force` — use `company_ids` |
| CRITICAL | `_check_company_auto` is NOT new in v18 — long-standing, predates v17 (added ~Odoo 13) |
| HIGH | `group_operator=` deprecated (warning) in favor of `aggregator=` — old kwarg still functions, migrate but don't call it a hard break |