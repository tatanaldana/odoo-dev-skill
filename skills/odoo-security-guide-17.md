# Security Guide — v17

## Key patterns

- `attrs=` removed — use `invisible=`/`readonly=`/`required=` directly
- `@api.model_create_multi` mandatory
- `_check_company_auto = True` + `check_company=True` (available since v15)
- Record rules: `company_ids` in `domain_force`
- SQL: parameterized `cr.execute(query, params)`

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

## Record rules + view security

```xml
<record id="rule_company" model="ir.rule">
    <field name="model_id" ref="model_my_model"/><field name="global" eval="True"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
</record>
```

```xml
<button name="action_approve" groups="my_module.group_manager" invisible="state != 'pending'"/>
<field name="cost_price" groups="account.group_account_user"/>
```

## Chatter (v17)

```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/><field name="activity_ids"/><field name="message_ids"/>
</div>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `attrs=` in v17 |
| CRITICAL | No string formatting in SQL — use parameterized |
| HIGH | `@api.model_create_multi` mandatory |