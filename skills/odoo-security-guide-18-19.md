# Security Guide Migration — v18 → v19

## What changes

| Component | v18 | v19 | Action |
|-----------|-----|-----|--------|
| Constraints | `_sql_constraints` (fully functional) | `_sql_constraints` becomes a SILENT NO-OP (warning logged, constraint never created); use `models.Constraint()` bare attribute | REQUIRED — not cosmetic, leaving old attribute silently drops the DB constraint |
| Indexes | `index=` on fields (still works in v19) | `models.Index()` bare attribute also available | recommended (both work; `index=` on fields is not deprecated) |
| SQL import | `odoo.tools.sql` or `odoo.tools` (both work) | `odoo.tools.sql` or `odoo.tools` (both still work, no deprecation) | style preference only — prefer `odoo.tools`, but `.tools.sql` is NOT broken |
| Type hints | recommended | still recommended | optional |
| Raw SQL | valid | still valid | no change |
| `res.users.groups_id` | `groups_id` | renamed to `group_ids` | REQUIRED — writing `groups_id` raises `ValueError: Invalid field 'groups_id' in 'res.users'` |
| `res.groups.category_id` | `category_id` (Many2one to `ir.module.category`) | removed — replaced by `privilege_id` (Many2one to new `res.groups.privilege`, which now carries `category_id`) | REQUIRED — setting `category_id` directly on `res.groups` raises `ValueError` at install time |
| `res.groups.users` (reverse M2M) | `users` | renamed to `user_ids` | REQUIRED — writing `users` raises `ValueError: Invalid field 'users' in 'res.groups'` |

## What does NOT change

- Record rules: `company_ids` in `domain_force`
- `_check_company_auto` + `check_company=True`
- View syntax: `invisible=` expressions

## Constraint/Index migration

```python
# v18
_sql_constraints = [('name_uniq', 'UNIQUE(name, company_id)', 'Must be unique!')]

# v19 — bare attributes, never list-wrapped
_name_uniq = models.Constraint('UNIQUE(name, company_id)', 'Must be unique!')
_company_idx = models.Index("(company_id)")
```

## SQL import

```python
# v18 — still works unchanged in v19, not an error
from odoo.tools.sql import SQL
# v19 — preferred style (both re-export the same class from odoo/tools/sql.py)
from odoo.tools import SQL
```

## Groups/privileges migration (security-relevant, v19 only)

`res.groups`/`res.users` field renames in the v19 groups/privileges refactor.
Confirmed against `odoo/addons/base/models/res_users.py` (v18 defines `Groups`
inline, no separate `res_groups.py`) vs. v19's new
`odoo/addons/base/models/res_groups.py` + `res_groups_privilege.py`. Real core
example: `addons/fleet/security/fleet_security.xml` in 19.0 uses `privilege_id`
and `user_ids`.

```xml
<!-- v18 -->
<record id="group_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category"/>
</record>

<!-- v19 -->
<record id="group_privilege" model="res.groups.privilege">
    <field name="name">Custom</field>
    <field name="category_id" ref="module_category"/>
</record>
<record id="group_user" model="res.groups">
    <field name="name">User</field>
    <field name="privilege_id" ref="group_privilege"/>
</record>
```

```python
# v18: self.env.user.groups_id / group.users
# v19: self.env.user.group_ids / group.user_ids
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Type hints NOT mandatory — don't flag absence |
| CRITICAL | Raw parameterized `cr.execute()` still valid in v19 |
| CRITICAL | `_sql_constraints = [...]` left over from v18 is a SILENT NO-OP in v19 (log warning only, constraint never created) — migrate to `models.Constraint()` |
| CRITICAL | `res.users.groups_id` → `group_ids` in v19; `res.groups.category_id` → `privilege_id`; `res.groups.users` → `user_ids` |
| HIGH | `models.Constraint()`/`models.Index()` never in list wrapper |
| STYLE | `from odoo.tools.sql import SQL` is NOT wrong in v19 (still works) — prefer `from odoo.tools import SQL` but don't flag the old path as broken |