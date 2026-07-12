# Odoo Module Generator — v19

Use only for modules targeting 19.0.

## v19 key changes from v18

- `_sql_constraints` → `models.Constraint()` (bare class attribute)
- Manual indexes → `models.Index()` (bare class attribute)
- `from odoo.tools.sql import SQL` → `from odoo.tools import SQL`
- `from odoo.fields import Command, Domain`
- `bypass_search_access=True` on M2O fields
- `from odoo.osv import expression` → `from odoo import expression`
- `record._cr/_context/_uid` → `self.env.cr/.context/.uid`

Views, chatter, `<list>`, `aggregator=` — same as v18.

---

## __manifest__.py

```python
{
    'name': '{Module Title}',
    'version': '19.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'author': '{Author}',
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

## Directory structure + security

Same as v17/v18. See `odoo-module-generator-17.md` for full tree and security templates.

For full model/view/constraint/index patterns → see `odoo-model-patterns-19.md`