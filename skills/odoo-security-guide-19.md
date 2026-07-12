# Odoo Security Guide — v19

Access rights, record rules, model security, SQL builder.

---

## Key v19 notes

- `models.Constraint()` / `models.Index()` — bare class attributes (never list-wrapped)
- `from odoo.tools import SQL` (not `odoo.tools.sql`)
- Record rules: `company_ids` in `domain_force` (NOT `allowed_company_ids`)
- Type hints: optional (NOT mandatory)
- `_check_company_auto = True` + `check_company=True` — same as v17/v18

---

## Security groups

```xml
<record id="module_category_custom" model="ir.module.category">
    <field name="name">Custom Module</field>
    <field name="sequence">100</field>
</record>
<record id="group_custom_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category_custom"/>
</record>
<record id="group_custom_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="category_id" ref="module_category_custom"/>
    <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
    <field name="users" eval="[(4, ref('base.user_admin'))]"/>
</record>
```

## Access rights (ir.model.access.csv)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_custom_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
access_custom_mgr,custom.model.mgr,model_custom_model,custom_module.group_custom_manager,1,1,1,1
```

## Multi-company record rule

```xml
<record id="rule_custom_company" model="ir.rule">
    <field name="name">Custom: Multi-Company</field>
    <field name="model_id" ref="model_custom_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
</record>
```

## Model with security patterns

```python
from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from odoo.tools import SQL

class SecureModel(models.Model):
    _name = 'custom.secure'
    _inherit = ['mail.thread']
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', check_company=True)

    _unique_name = models.Constraint('UNIQUE(name, company_id)', 'Name must be unique!')
    _company_state_idx = models.Index("(company_id, state)")

    def action_sensitive(self):
        if not self.env.user.has_group('custom_module.group_custom_manager'):
            raise AccessError(_("Only managers can do this."))
        self.check_access_rights('write')
        self.check_access_rule('write')
```

## Secure SQL

```python
from odoo.tools import SQL

query = SQL("""
    SELECT id, name FROM %(table)s
    WHERE company_id = %(company_id)s AND active = %(active)s
""", table=SQL.identifier(self._table), company_id=self.env.company.id, active=True)
self.env.cr.execute(query)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `allowed_company_ids` does NOT exist in `domain_force` — use `company_ids` |
| CRITICAL | Type hints NOT mandatory — don't flag absence |
| CRITICAL | SQL import: `from odoo.tools import SQL` (not `.sql`) |
| HIGH | `models.Constraint()`/`models.Index()` never in a list wrapper |