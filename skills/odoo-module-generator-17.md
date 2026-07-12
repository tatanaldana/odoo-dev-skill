# Odoo Module Generator — v17

Use only for modules targeting 17.0. Do not mix with other versions.

## v17 key syntax

- `attrs=` removed — use `invisible=`/`readonly=`/`required=` as Python expressions
- `@api.model_create_multi` mandatory
- `group_operator=` on fields (→ `aggregator=` in v18)
- `<tree>` tag (→ `<list>` in v18)
- Chatter: `<div class="oe_chatter">` with child fields
- OWL: `/** @odoo-module **/` REQUIRED
- Multi-company rules: `company_ids` in `domain_force`

---

## __manifest__.py

```python
{
    'name': '{Module Title}',
    'version': '17.0.1.0.0',
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
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Directory structure

```
{module_name}/
├── __init__.py              → from . import models, wizard
├── __manifest__.py
├── models/
│   ├── __init__.py          → from . import {model_name}
│   └── {model_name}.py
├── wizard/
│   ├── __init__.py
│   └── {wizard_name}.py
├── security/
│   ├── {module_name}_security.xml   → groups
│   └── ir.model.access.csv
├── views/
│   ├── {model_name}_views.xml
│   └── menuitems.xml
├── data/                    → demo/seed data
├── static/src/              → JS/XML/SCSS
└── tests/
    ├── __init__.py
    └── test_{model_name}.py
```

## Security files

```xml
<!-- security/{module_name}_security.xml -->
<odoo>
    <record id="group_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="base.module_category_services"/>
    </record>
    <record id="group_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="base.module_category_services"/>
        <field name="implied_ids" eval="[(4, ref('{module_name}.group_user'))]"/>
    </record>
</odoo>
```

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model}_user,{model} user,model_{model_under},{module_name}.group_user,1,1,1,0
access_{model}_manager,{model} manager,model_{model_under},{module_name}.group_manager,1,1,1,1
```

## Multi-company record rule

```xml
<record id="rule_{model}_multi_company" model="ir.rule">
    <field name="name">{Model} multi-company</field>
    <field name="model_id" ref="model_{model_under}"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
</record>
```

For full model/view patterns → see `odoo-model-patterns-17.md`