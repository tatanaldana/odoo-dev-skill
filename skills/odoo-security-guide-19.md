# Odoo Security Guide — v19

Access rights, record rules, model security, SQL builder.

---

## Key v19 notes

- `models.Constraint()` / `models.Index()` — bare class attributes (never list-wrapped)
- `from odoo.tools import SQL` recommended (the top-level package re-exports it). NOTE: `from odoo.tools.sql import SQL` still works unchanged in v19 too (no deprecation on the module/class) — prefer the top-level import for style, but don't flag the `.sql` path as an error.
- `_sql_constraints = [...]` is now a silent no-op: `odoo/orm/model_classes.py` only logs `"Model attribute '_sql_constraints' is no longer supported, please define models.Constraint on the model."` and never applies it. No exception is raised — the DB constraint simply isn't created. Migrating to `models.Constraint()` is REQUIRED to keep the constraint enforced, not just a style recommendation.
- Record rules: `company_ids` in `domain_force` (NOT `allowed_company_ids`)
- Type hints: optional (NOT mandatory)
- `_check_company_auto = True` + `check_company=True` — same as v17/v18
- `res.groups.category_id` **no longer exists** — replaced by `privilege_id` (Many2one to the new `res.groups.privilege` model, which is the one that now carries `category_id`). Setting `category_id` directly on a `res.groups` record raises `ValueError: Invalid field 'category_id' in 'res.groups'` at install time. Confirmed against `odoo/addons/base/models/{res_groups,res_groups_privilege}.py` and the real core example in `addons/fleet/security/fleet_security.xml`.
- `res.users.groups_id` **renamed to `group_ids`** (same v19 groups/privileges refactor as above). Writing/creating with `groups_id` raises `ValueError: Invalid field 'groups_id' in 'res.users'`. Confirmed against `odoo/addons/base/models/res_users.py` (17.0/18.0 define `groups_id`/`Groups`/`Users` inline in `res_users.py` — there is no separate `res_groups.py` in those versions; 19.0 splits `Groups` out into its own `res_groups.py`/`res_groups_privilege.py`).
- `res.groups`'s reverse users field **also renamed**: `users` (v17/v18) → `user_ids` (v19). Writing `users` on a v19 `res.groups` record raises `ValueError: Invalid field 'users' in 'res.groups'`. Confirmed against `odoo/addons/base/models/res_groups.py` and the real core example `addons/fleet/security/fleet_security.xml` (uses `user_ids`).

---

## Security groups

```xml
<record id="module_category_custom" model="ir.module.category">
    <field name="name">Custom Module</field>
    <field name="sequence">100</field>
</record>
<record id="res_groups_privilege_custom" model="res.groups.privilege">
    <field name="name">Custom Module</field>
    <field name="category_id" ref="module_category_custom"/>
</record>
<record id="group_custom_user" model="res.groups">
    <field name="name">User</field>
    <field name="privilege_id" ref="res_groups_privilege_custom"/>
</record>
<record id="group_custom_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="privilege_id" ref="res_groups_privilege_custom"/>
    <field name="implied_ids" eval="[(4, ref('group_custom_user'))]"/>
    <field name="user_ids" eval="[(4, ref('base.user_admin'))]"/>
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
| RECOMMENDED | SQL import: prefer `from odoo.tools import SQL` over `.tools.sql` for style — but the `.tools.sql` path still works, do not flag it as broken |
| CRITICAL | Leaving `_sql_constraints = [...]` on a model is a SILENT NO-OP in v19 (logged warning only, constraint never created) — must migrate to `models.Constraint()` |
| CRITICAL | `res.groups.category_id` removed in v19 — use `privilege_id` (Many2one to `res.groups.privilege`) |
| CRITICAL | `res.users.groups_id` renamed to `group_ids` in v19 |
| CRITICAL | `res.groups.users` renamed to `user_ids` in v19 |
| HIGH | `models.Constraint()`/`models.Index()` never in a list wrapper |