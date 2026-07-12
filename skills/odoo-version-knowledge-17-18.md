# Version Knowledge Migration — v17 → v18

## Breaking changes

| Area | v17 | v18 |
|------|-----|-----|
| Field aggregation | `group_operator='min'` | `aggregator='min'` |
| List view | `<tree>` | `<list>` |
| Chatter | `<div class="oe_chatter">` | `<chatter/>` (bare tag dominant) |
| `@odoo-module` JS | required | optional |
| `read_group()` | available | deprecated (v18.2) → `_read_group()` |
| `name_get()` | deprecated | → `_search_display_name` |

## New in v18

- `@api.private` — not exposed to RPC
- `check_access()`, `has_access()`, `_filtered_access()`
- `odoo.Domain` API
- `export_string_translation=False`
- `web.assets_unit_tests` manifest key
- JS: `autocloseDelay` on notifications

## NOT changed (common mistakes)

- `_check_company_auto` — available since v17, NOT new
- Record rules: `company_ids` in `domain_force` — NOT replaced by `allowed_company_ids`
- `SQL()`: `from odoo.tools.sql import SQL` — same as v17

## Migration checklist

```
CRITICAL:
[ ] group_operator= → aggregator=
[ ] <tree> → <list> (all XML + view_mode values)
[ ] oe_chatter → <chatter/>
[ ] Do NOT rename existing view record ids

NO CHANGE:
[ ] Record rules: company_ids unchanged
[ ] _check_company_auto: no migration needed

HIGH:
[ ] Remove @odoo-module from JS
[ ] read_group() → _read_group()

MEDIUM:
[ ] Adopt SQL() builder for new code
[ ] Add type hints to new methods
```