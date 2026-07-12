# Security Guide — v18

## Key patterns

- `SQL()` builder: `from odoo.tools.sql import SQL`
- Type hints recommended, not mandatory
- `_check_company_auto = True` + `check_company=True` (since v17)
- Record rules: `company_ids` in `domain_force`
- `aggregator=` replaces `group_operator=`

## Groups + access rights

```xml
<record id="group_user" model="res.groups">
    <field name="name">User</field><field name="category_id" ref="module_category"/>
</record>
<record id="group_manager" model="res.groups">
    <field name="name">Manager</field><field name="implied_ids" eval="[(4, ref('group_user'))]"/>
</record>
```

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_user,model.user,model_my_model,my_module.group_user,1,1,1,0
access_mgr,model.mgr,model_my_model,my_module.group_manager,1,1,1,1
```

## Record rules

```xml
<record id="rule_company" model="ir.rule">
    <field name="model_id" ref="model_my_model"/><field name="global" eval="True"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
</record>
```

## Secure SQL

```python
from odoo.tools.sql import SQL
query = SQL("SELECT id FROM %(t)s WHERE company_id = %(c)s",
    t=SQL.identifier(self._table), c=self.env.company.id)
self.env.cr.execute(query)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No string formatting in SQL |
| CRITICAL | `allowed_company_ids` NOT valid in `domain_force` |
| HIGH | `_check_company_auto` without `check_company=True` on fields does nothing |