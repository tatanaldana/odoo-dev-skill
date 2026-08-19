# Odoo Version Knowledge — v18

Python 3.11+ | OWL 2.x

## Breaking changes from v17

| Area | v17 | v18 |
|------|-----|-----|
| Field aggregation | `group_operator='min'` | `aggregator='min'` |
| List view tag | `<tree>` | `<list>` |
| Chatter | `<div class="oe_chatter">` + 3 fields | `<chatter/>` (bare dominant; `reload_on_*` where needed) |
| `@odoo-module` JS | required | optional |
| `read_group()` | available, no deprecation warning | still available; only marked `@api.deprecated` starting v19.0 |
| `name_get()` | removed as a concrete method (deprecated since v17.0, not v16.4) | `_search_display_name` is the replacement mechanism |

## New in v18

- `check_access()`, `has_access()`, `_filtered_access()` — new access methods
- `export_string_translation=False` on fields (attribute existed since v17.0 — NOT new in v18)
- `web.assets_unit_tests` manifest key
- JS: `notification.add()` gains `autocloseDelay` option
- JS: `registry.category().addValidation()`

## NOT changed from v17

- `from odoo import _` — still valid
- `_check_company_auto` + `check_company=True` — available since v17
- `useService("company")` — already existed in v17 (not new in v18); **removed in v19**, replaced by `import { user } from "@web/core/user"` (see `odoo-version-knowledge-19.md`/`odoo-owl-components-19.md`)
- Record rules: `company_ids` in `domain_force` (NOT `allowed_company_ids`)
- `SQL()` — `from odoo.tools import SQL` (already the more common form since v17) or `from odoo.tools.sql import SQL` — both work
- `@api.private` — available since v17.0, NOT new in v18
- `odoo.fields.Domain` does NOT exist yet in v18 (introduced in v19 only)
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