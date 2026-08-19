# Module Generator Migration — v17 → v18

## Breaking changes checklist

```
MUST FIX (hard breaks — confirmed against v18 source):
[ ] <tree> → <list> in all XML (views + inside One2many) — ir.ui.view `type` selection only accepts 'list' in v18, 'tree' is rejected
[ ] view_mode: tree,form → list,form
[ ] <div class="oe_chatter"> → <chatter/> (bare tag) — mail's form_compiler.js now looks for a `<chatter/>` tag, not `div.oe_chatter`; old markup silently loses the chatter
[ ] Do NOT rename existing ir.ui.view record ids (breaks inheritors)

SOFT DEPRECATION (still works in v18, only logs a warning — fix when convenient, not urgent):
[ ] group_operator= → aggregator= on all fields (auto-remapped internally with a DeprecationWarning; not a hard break in v18)

NO CHANGE NEEDED:
[ ] Record rules: company_ids unchanged (do NOT replace with allowed_company_ids)
[ ] _check_company_auto — already available in v17
[ ] read_group() — still fully available and NOT deprecated in v18 (it only gets @api.deprecated in v19 — see odoo-module-generator-18-19.md)
[ ] export_string_translation — already available since v17, not new in v18

RECOMMENDED:
[ ] Remove /** @odoo-module **/ from JS
[ ] Adopt SQL() builder for new raw SQL
[ ] Add type hints to new methods
[ ] Add export_string_translation=False on internal fields
[ ] Update manifest: version 17.0.x → 18.0.x, add web.assets_unit_tests key
```

## Quick diff

| Feature | v17 | v18 |
|---------|-----|-----|
| `group_operator=` | yes | deprecated (warning only) → `aggregator=` |
| `<tree>` | yes | removed → `<list>` (hard break) |
| `oe_chatter` div | yes | removed → `<chatter/>` (hard break) |
| `@odoo-module` JS | required | optional |
| `read_group()` | available | still available, not deprecated yet (deprecated only in v19) |
| `SQL` import | `from odoo.tools import SQL` or `from odoo.tools.sql import SQL` (both work) | same — no change; both still work in v19 too |

For full patterns → see `odoo-model-patterns-17-18.md`