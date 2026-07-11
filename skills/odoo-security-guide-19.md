# odoo-security-guide-19.md

<pattern>

  <description>
    Odoo 19.0 security patterns. Covers access rights, record rules, model-level
    security, field-level security, view security, SQL builder, type hints,
    models.Constraint(), and models.Index(). Use this file for v19 only.

    IMPORTANT: a previous version of this file claimed type hints and the SQL()
    builder are "mandatory" in v19, and showed models.Constraint()/models.Index()
    wrapped in _sql_constraints=[...] / _indexes=[...] lists. Both claims are FALSE —
    verified against real 19.0 source (account.move.line, 3700+ lines, has only 2
    type-hinted methods; account_journal.py/account_move_line.py use bare
    `_name = models.Constraint(...)` / `_name = models.Index(...)` class attributes,
    never a wrapping list). Corrected below — cross-reference odoo-model-patterns-18-19.md
    and odoo-model-patterns-19.md, which document this correctly with the same citations.
  </description>

  <version_notes>
    <version id="19">
      Type hints: recommended convention, NOT mandatory — confirmed 0 type hints across
      account.move.line's 3700+ lines in real source. Use from __future__ import
      annotations only where you choose to adopt them.
      SQL() builder: recommended, NOT mandatory — from odoo.tools import SQL (import
      path changed from v18). Raw parameterized cr.execute() remains valid and coexists
      with SQL() throughout real 19.0 addon code.
      models.Constraint() replaces _sql_constraints — as a BARE class attribute
      (`_my_constraint = models.Constraint(sql, message)`), never a list.
      models.Index() replaces index=True / index='btree' / index='trigram' on fields —
      also a bare class attribute (`_my_idx = models.Index("(col1, col2)")`), never a list.
      Record rules use company_ids in domain_force — same variable as v17/v18.
      allowed_company_ids is NOT valid in domain_force in any version (confirmed against
      real account_security.xml).
      _check_company_auto = True available — same as v17/v18.
      attrs= still removed — use invisible= directly.
    </version>
  </version_notes>

  <examples>

    <example id="security_groups" title="Security groups XML (v19)">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo>
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
      </odoo>
      ```
    </example>

    <example id="access_rights" title="ir.model.access.csv (v19)">
      ```csv
      id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
      access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
      access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
      ```
    </example>

    <example id="record_rule_multicompany" title="Multi-company record rule (v19)">
      ```xml
      <!-- v19: company_ids in domain_force — same variable as v17/v18 -->
      <record id="rule_custom_model_company" model="ir.rule">
          <field name="name">Custom Model: Multi-Company</field>
          <field name="model_id" ref="model_custom_model"/>
          <field name="global" eval="True"/>
          <field name="domain_force">[
              '|',
              ('company_id', '=', False),
              ('company_id', 'in', company_ids)
          ]</field>
      </record>
      ```
    </example>

    <example id="model_security" title="Model with Constraint/Index (v19) — type hints optional">
      ```python
      from odoo import api, fields, models, _
      from odoo.exceptions import AccessError
      from odoo.tools import SQL

      class SecureModel(models.Model):
          _name = 'custom.secure'
          _description = 'Secure Model'
          _inherit = ['mail.thread', 'mail.activity.mixin']
          _check_company_auto = True

          # Type hints are optional in v19 — adopt them where they help readability,
          # not because the ORM or test suite require them.
          name = fields.Char(string='Name', required=True, tracking=True)
          active = fields.Boolean(default=True)
          company_id = fields.Many2one(
              comodel_name='res.company',
              string='Company',
              default=lambda self: self.env.company,
              required=True,
          )
          partner_id = fields.Many2one(
              comodel_name='res.partner',
              string='Partner',
              check_company=True,
          )
          state = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('done', 'Done'),
          ], default='draft', tracking=True)

          # v19: models.Constraint() replaces _sql_constraints — a BARE class
          # attribute, never wrapped in a list (confirmed account_journal.py lines 36-39)
          _unique_name_company = models.Constraint(
              'UNIQUE(name, company_id)',
              'Name must be unique per company.',
          )

          # v19: models.Index() replaces index= on fields — also a bare attribute,
          # a single column-list string (confirmed account_move_line.py lines 480-489)
          _company_state_idx = models.Index("(company_id, state)")

          @api.model_create_multi
          def create(self, vals_list):
              return super().create(vals_list)

          def action_sensitive_operation(self) -> None:
              if not self.env.user.has_group('custom_module.group_custom_manager'):
                  raise AccessError(_("Only managers can perform this action."))
              self.check_access_rights('write')
              self.check_access_rule('write')
              self._execute_sensitive_operation()

          def _execute_sensitive_operation(self) -> None:
              pass
      ```
    </example>

    <example id="secure_sql" title="SQL builder for raw SQL (v19 — import from odoo.tools)">
      ```python
      from odoo import models
      from odoo.tools import SQL  # v19: import path changed from odoo.tools.sql

      class SecureModel(models.Model):
          _name = 'custom.secure'
          _description = 'Secure Model'

          def _get_secure_data(self) -> list[dict]:
              query = SQL(
                  """
                  SELECT id, name, amount
                  FROM %(table)s
                  WHERE company_id = %(company_id)s
                    AND active = %(active)s
                    AND create_uid = %(user_id)s
                  """,
                  table=SQL.identifier(self._table),
                  company_id=self.env.company.id,
                  active=True,
                  user_id=self.env.user.id,
              )
              self.env.cr.execute(query)
              return self.env.cr.dictfetchall()
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: allowed_company_ids does not exist in domain_force -->
      <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

      <!-- CORRECT: use company_ids -->
      <field name="domain_force">[('company_id', 'in', company_ids)]</field>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      Claiming type hints are mandatory in v19 and flagging their absence as an error —
      FALSE. Real 19.0 source (account.move.line, 3700+ lines) has only 2 type-hinted
      methods. A previous version of this file made this claim; it has been removed.

      ```python
      # NOT an error in v19 — type hints are optional
      class MyModel(models.Model):
          name = fields.Char(required=True)
          partner_id = fields.Many2one('res.partner')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Wrapping `models.Constraint()` or `models.Index()` in a `_sql_constraints = [...]` /
      `_indexes = [...]` list in v19 — this pattern does not exist in real 19.0 source.
      They are bare class attributes.

      ```python
      # WRONG in v19 — no such list-wrapped pattern exists in real source
      _sql_constraints = [
          models.Constraint('unique(name)', 'Name must be unique!'),
      ]
      _indexes = [
          models.Index('idx_name', ['name']),
      ]

      # CORRECT in v19 (confirmed in account_journal.py, account_move_line.py)
      _name_uniq = models.Constraint('unique(name)', 'Name must be unique!')
      _name_idx = models.Index("(name)")
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: v18 SQL import path in v19
      from odoo.tools.sql import SQL  # v18 path

      # CORRECT for v19
      from odoo.tools import SQL
      ```
    </antipattern>

  </antipatterns>

</pattern>