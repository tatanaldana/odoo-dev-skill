# Model Patterns Migration — v17 → v18

## Key changes (2 hard breaks + 1 deprecation)

| Change | v17 | v18 |
|--------|-----|-----|
| `group_operator=` | yes | deprecated → `aggregator=` (still works: `DeprecationWarning` + auto-conversion, not a hard break, verified still present in v19 too) |
| `<tree>` | yes | → `<list>` (hard break: RNG schema only defines `list`) |
| Chatter | `<div class="oe_chatter">` | → `<chatter/>` (old div doesn't error, but JS compiler no longer binds to it — chatter silently fails to render) |

## NOT changed (corrections)

- `_check_company_auto` + `check_company=True` — present since v17
- Record rules: `company_ids` in `domain_force` — unchanged (NOT `allowed_company_ids`)
- `SQL()` import: `from odoo.tools.sql import SQL` — same path

## Quick examples

```python
# v17
date = fields.Date(group_operator='min')
# v18
date = fields.Date(aggregator='min')
```

```xml
<!-- v17 -->
<tree editable="bottom"><field name="name"/></tree>
<!-- v18 -->
<list editable="bottom"><field name="name"/></list>
```

```xml
<!-- v17 -->
<div class="oe_chatter"><field name="message_follower_ids"/>...</div>
<!-- v18 — bare tag default -->
<chatter/>
```

## Migration checklist

```
MUST FIX (hard breaks):
[ ] <tree> → <list> (all XML + view_mode) — RNG schema rejects <tree>
[ ] oe_chatter → <chatter/> — old div silently fails to render, no error

NO CHANGE:
[ ] company_ids in domain_force (NOT allowed_company_ids)
[ ] _check_company_auto (not new in v18)
[ ] SQL import path (from odoo.tools import SQL / from odoo.tools.sql import SQL both work, v17-v19)

RECOMMENDED (not mandatory):
[ ] group_operator= → aggregator= (deprecated, still functional via compat shim + DeprecationWarning)
[ ] Adopt SQL() builder
[ ] Add type hints
[ ] Use SQL.identifier() for table names
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| MEDIUM | `group_operator=` in v18 — deprecated (warns, auto-converts), not a crash |
| CRITICAL | `<tree>` in v18 |
| CRITICAL | `oe_chatter` div in v18 |
| CRITICAL | `allowed_company_ids` NOT valid in `domain_force` |
| HIGH | Raw SQL with string interpolation of table names |