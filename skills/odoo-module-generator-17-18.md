# Module Generator Migration — v17 → v18

## Breaking changes checklist

```
MUST FIX:
[ ] group_operator= → aggregator= on all fields
[ ] <tree> → <list> in all XML (views + inside One2many)
[ ] view_mode: tree,form → list,form
[ ] <div class="oe_chatter"> → <chatter/> (bare tag default)
[ ] Do NOT rename existing ir.ui.view record ids (breaks inheritors)

NO CHANGE NEEDED:
[ ] Record rules: company_ids unchanged (do NOT replace with allowed_company_ids)
[ ] _check_company_auto — already available in v17

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
| `group_operator=` | yes | → `aggregator=` |
| `<tree>` | yes | → `<list>` |
| `oe_chatter` div | yes | → `<chatter/>` |
| `@odoo-module` JS | required | optional |
| `read_group()` | available | deprecated → `_read_group()` |
| `SQL()` import | `odoo.tools.sql` | same (→ `odoo.tools` in v19) |

For full patterns → see `odoo-model-patterns-17-18.md`