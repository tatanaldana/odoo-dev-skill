# Odoo Module Generator — v19

Use only for modules targeting 19.0.

## v19 key changes from v18

- `_sql_constraints` → `models.Constraint()` (bare class attribute). Old-style `_sql_constraints = [...]` now logs `_logger.warning("...no longer supported...")` (soft deprecation, not a hard crash), but the constraint is no longer actually applied — treat as MUST FIX in practice.
- Manual indexes → `models.Index()` (bare class attribute)
- `from odoo.tools import SQL` — this works in v17/v18/v19 already (`odoo/tools/__init__.py` does `from .sql import *` and `SQL` is exported in all three branches; core code uses both `odoo.tools.SQL` and `odoo.tools.sql.SQL` interchangeably since v17). Not a v19-only change — just the preferred import style going forward.
- `from odoo.fields import Command, Domain` — `Domain` is a new v19 query-builder class (`odoo/orm/domains.py`, re-exported via `odoo/fields/__init__.py`)
- `bypass_search_access=True` — new in v19, on relational fields generally (`Many2one`, `One2many`, `Many2many` — not just M2O; confirmed used on both in core, e.g. `res.partner.user_ids` One2many and `res.users.partner_id` Many2one)
- `odoo.osv` (incl. `odoo.osv.expression`) is fully deprecated in v19 (`odoo/osv/__init__.py` raises `DeprecationWarning: Since 19.0, odoo.osv is deprecated use odoo.fields.Domain` on import) — it still works but the replacement is **`from odoo.fields import Domain`**, NOT `from odoo import expression` (there is no `odoo.expression` module in v19)
- `record._cr/_context/_uid` → `self.env.cr/.context/.uid` — soft deprecation only (`@api.deprecated` decorator added in v19, still functional, just logs a warning). These shortcuts existed unchanged since v17.

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

Same as v17/v18. See `odoo-module-generator-17.md` for full tree.

## Security files — BREAKING CHANGE vs v17/v18

`res.groups` no longer has a `category_id` field in v19 (confirmed: `odoo/addons/base/models/res_groups.py` — the field is gone from the model). Groups now link to a new `res.groups.privilege` model (which itself carries `category_id`) via `privilege_id`. The v17/v18 security XML template (`<field name="category_id" ref="..."/>` directly on a `res.groups` record) will fail on v19 — do NOT copy it as-is.

```xml
<!-- security/{module_name}_security.xml (v19) -->
<odoo>
    <record id="privilege_{module_name}" model="res.groups.privilege">
        <field name="name">{Privilege Name}</field>
        <field name="category_id" ref="base.module_category_services"/>
    </record>
    <record id="group_user" model="res.groups">
        <field name="name">User</field>
        <field name="privilege_id" ref="{module_name}.privilege_{module_name}"/>
    </record>
    <record id="group_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="privilege_id" ref="{module_name}.privilege_{module_name}"/>
        <field name="implied_ids" eval="[(4, ref('{module_name}.group_user'))]"/>
    </record>
</odoo>
```

`ir.model.access.csv` and multi-company `domain_force` (`company_ids`) are unchanged from v17/v18.

For full model/view/constraint/index patterns → see `odoo-model-patterns-19.md`