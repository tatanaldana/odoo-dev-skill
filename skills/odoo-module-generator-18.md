# Odoo Module Generator — v18

Use only for modules targeting 18.0. Do not mix with other versions.

## v18 changes from v17

- `group_operator=` → `aggregator=`
- `<tree>` → `<list>`
- `<div class="oe_chatter">` → `<chatter/>`
- `@odoo-module` no longer required in JS
- New: `web.assets_unit_tests` key in manifest
- New: `export_string_translation=False` on fields
- Type hints recommended, not mandatory

---

## __manifest__.py

```python
{
    'name': '{Module Title}',
    'version': '18.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'author': '{Author}',
    'website': '{Website}',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/{module_name}_security.xml',
        'security/ir.model.access.csv',
        'views/{model_name}_views.xml',
        'views/menuitems.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '{module_name}/static/src/**/*.js',
            '{module_name}/static/src/**/*.xml',
            '{module_name}/static/src/**/*.scss',
        ],
        'web.assets_unit_tests': [
            '{module_name}/static/tests/**/*.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Directory structure

Same as v17. See `odoo-module-generator-17.md` for full tree.

## Security files

Same as v17 — `company_ids` in `domain_force` for multi-company rules.

For full model/view patterns → see `odoo-model-patterns-18.md`