# Odoo Version Knowledge — v18

Python 3.11+ | OWL 2.x

## Breaking changes from v17

| Area | v17 | v18 |
|------|-----|-----|
| Field aggregation | `group_operator='min'` | `aggregator='min'` |
| List view tag | `<tree>` | `<list>` |
| Chatter | `<div class="oe_chatter">` + 3 fields | `<chatter/>` (bare dominant; `reload_on_*` where needed) |
| `@odoo-module` JS | required | optional |
| `read_group()` | available | deprecated (v18.2) → `_read_group()` / `formatted_read_group()` |
| `name_get()` | deprecated since v16.4 | `_search_display_name` replaces it |

## New in v18

- `@api.private` — marks methods not exposed to RPC (v18.2)
- `check_access()`, `has_access()`, `_filtered_access()` — new access methods
- `odoo.Domain` API for domain manipulation (v18.1)
- `export_string_translation=False` on fields
- `web.assets_unit_tests` manifest key
- JS: `notification.add()` gains `autocloseDelay` option
- JS: `registry.category().addValidation()`
- JS: `useService("company")` new service

## NOT changed from v17

- `from odoo import _` — still valid
- `_check_company_auto` + `check_company=True` — available since v17
- Record rules: `company_ids` in `domain_force` (NOT `allowed_company_ids`)
- `SQL()` via `from odoo.tools.sql import SQL`
- OWL 2.x

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `group_operator=` → `aggregator=` |
| CRITICAL | `<tree>` → `<list>` |
| CRITICAL | `oe_chatter` → `<chatter/>` |
| CRITICAL | `allowed_company_ids` NOT valid in `domain_force` — use `company_ids` |
| HIGH | `@odoo-module` no longer required in JS |

Full model/view patterns → `odoo-model-patterns-18.md`