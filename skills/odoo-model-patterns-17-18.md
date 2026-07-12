# Model Patterns Migration — v17 → v18

## Three breaking changes

| Change | v17 | v18 |
|--------|-----|-----|
| `group_operator=` | yes | → `aggregator=` |
| `<tree>` | yes | → `<list>` |
| Chatter | `<div class="oe_chatter">` | → `<chatter/>` |

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
MUST FIX:
[ ] group_operator= → aggregator=
[ ] <tree> → <list> (all XML + view_mode)
[ ] oe_chatter → <chatter/>

NO CHANGE:
[ ] company_ids in domain_force (NOT allowed_company_ids)
[ ] _check_company_auto (not new in v18)

RECOMMENDED:
[ ] Adopt SQL() builder
[ ] Add type hints
[ ] Use SQL.identifier() for table names
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `group_operator=` in v18 |
| CRITICAL | `<tree>` in v18 |
| CRITICAL | `oe_chatter` div in v18 |
| CRITICAL | `allowed_company_ids` NOT valid in `domain_force` |
| HIGH | Raw SQL with string interpolation of table names |