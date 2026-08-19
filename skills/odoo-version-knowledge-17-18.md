# Version Knowledge Migration — v17 → v18

## Breaking changes

| Area | v17 | v18 |
|------|-----|-----|
| Field aggregation | `group_operator='min'` | `aggregator='min'` |
| List view | `<tree>` | `<list>` |
| Chatter | `<div class="oe_chatter">` | `<chatter/>` (bare tag dominant) |
| `@odoo-module` JS | required | optional |
| `read_group()` | available, no deprecation warning | still available; only marked `@api.deprecated` starting v19.0 (NOT v18.2) |
| `name_get()` | deprecated since v17.0 (not v16.4) | removed as concrete method → `_search_display_name` |

## New in v18

- `check_access()`, `has_access()`, `_filtered_access()`
- `web.assets_unit_tests` manifest key
- JS: `autocloseDelay` on notifications

## NOT changed (common mistakes)

- `_check_company_auto` — available since v17, NOT new
- Record rules: `company_ids` in `domain_force` — NOT replaced by `allowed_company_ids`
- `SQL()`: both `from odoo.tools import SQL` and `from odoo.tools.sql import SQL` work — same as v17 (the top-level form was already the more common one in v17)
- `@api.private` — available since v17.0, NOT new in v18
- `export_string_translation=False` — field attribute available since v17.0, NOT new in v18
- `odoo.Domain`/`odoo.fields.Domain` — does NOT exist in v18 at all (introduced only in v19)

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

MEDIUM:
[ ] Adopt SQL() builder for new code
[ ] Add type hints to new methods
[ ] read_group() still works in v18 (not deprecated until v19) — no urgent action needed
```