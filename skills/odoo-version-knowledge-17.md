# Odoo Version Knowledge — v17

Python 3.10+ | OWL 2.x

## Breaking changes from v16

- `attrs=` removed from views — use `invisible=`/`readonly=`/`required=` directly
- `@api.model_create_multi` mandatory for all `create()` overrides

## v17 features

- `index='trigram'`, `index='btree'`, `index='btree_not_null'`
- `Command` class for x2many (mandatory convention)
- `_check_company_auto = True` + `check_company=True` (available since v15)
- `SQL()` via `from odoo.tools.sql import SQL`
- `group_operator=` on fields (→ `aggregator=` in v18)
- Chatter: `<div class="oe_chatter">` with child fields
- List views: `<tree>` tag (→ `<list>` in v18)
- OWL 2.x, `/** @odoo-module **/` REQUIRED in JS

## Record rules

`company_ids` in `domain_force` — same in v17/v18/v19.

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `attrs=` — crashes in v17 |
| CRITICAL | `@api.model_create_multi` mandatory on `create()` |

Full model/view patterns → `odoo-model-patterns-17.md`