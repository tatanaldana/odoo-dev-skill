# odoo-security-guide-18.md

<pattern>

  <description>
    Odoo 18.0 security patterns. Covers access rights, record rules, model-level
    security, field-level security, view security, SQL builder, type hints, and
    audit logging. Use this file for v18 only — never mix with other versions.
  </description>

  <version_notes>
    <version id="18">
      SQL() builder required for raw SQL — from odoo.tools.sql import SQL.
      Type hints recommended on relational fields.
      _check_company_auto = True available (also present in v17 — not a new v18 feature).
      check_company=True available on Many2one fields (also present in v17).
      Record rules use company_ids in domain_force — same variable as v17.
      attrs= still removed (removed in v17) — use invisible= directly.
      aggregator= replaces group_operator= on fields.
    </version>
  </version_notes>

  <examples>

    <example id="security_groups" title="Security groups XML (v18)">
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

    <example id="access_rights" title="ir.model.access.csv (v18)">
      ```csv
      id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
      access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
      access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
      ```
    </example>

    <example id="record_rule_multicompany" title="Multi-company record rule (v18)">
      ```xml
      <!-- v18: company_ids in domain_force — same variable as v17 -->
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

    <example id="model_security" title="Model with company validation and type hints (v18)">
      ```python
      from odoo import api, fields, models, _
      from odoo.exceptions import AccessError

      class SecureModel(models.Model):
          _name = 'custom.secure'
          _description = 'Secure Model'
          _inherit = ['mail.thread', 'mail.activity.mixin']
          _check_company_auto = True

          # v18: type hints recommended on relational fields
          name: str = fields.Char(string='Name', required=True, tracking=True)
          company_id: int = fields.Many2one(
              'res.company',
              string='Company',
              default=lambda self: self.env.company,
              required=True,
              index=True,
          )
          partner_id: int = fields.Many2one(
              'res.partner',
              string='Partner',
              check_company=True,
          )
          warehouse_id: int = fields.Many2one(
              'stock.warehouse',
              string='Warehouse',
              check_company=True,
          )
          state: str = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('done', 'Done'),
          ], default='draft', tracking=True)

          @api.model_create_multi
          def create(self, vals_list):
              return super().create(vals_list)

          def action_sensitive_operation(self):
              if not self.env.user.has_group('custom_module.group_custom_manager'):
                  raise AccessError(_("Only managers can perform this action."))
              self.check_access_rights('write')
              self.check_access_rule('write')
              self._execute_sensitive_operation()

          def _execute_sensitive_operation(self):
              pass
      ```
    </example>

    <example id="secure_sql" title="SQL builder for raw SQL (v18)">
      ```python
      from odoo import models
      from odoo.tools.sql import SQL

      class SecureModel(models.Model):
          _name = 'custom.secure'
          _description = 'Secure Model'

          def _get_secure_data(self):
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

    <example id="complete_template" title="Complete security XML (v18)">
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

          <record id="rule_custom_model_user" model="ir.rule">
              <field name="name">Custom Model: User Own Records</field>
              <field name="model_id" ref="model_custom_model"/>
              <field name="domain_force">[('user_id', '=', user.id)]</field>
              <field name="groups" eval="[(4, ref('group_custom_user'))]"/>
          </record>

          <record id="rule_custom_model_manager" model="ir.rule">
              <field name="name">Custom Model: Manager All Records</field>
              <field name="model_id" ref="model_custom_model"/>
              <field name="domain_force">[(1, '=', 1)]</field>
              <field name="groups" eval="[(4, ref('group_custom_manager'))]"/>
          </record>
      </odoo>
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: string formatting in SQL
      self.env.cr.execute(
          "SELECT id FROM %s WHERE name = '%s'" % (self._table, name)
      )

      # CORRECT: SQL() builder
      from odoo.tools.sql import SQL
      self.env.cr.execute(SQL(
          "SELECT id FROM %(t)s WHERE name = %(name)s",
          t=SQL.identifier(self._table),
          name=name,
      ))
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: allowed_company_ids does not exist in domain_force -->
      <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

      <!-- CORRECT: use company_ids -->
      <field name="domain_force">[('company_id', 'in', company_ids)]</field>
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: _check_company_auto alone without check_company=True on fields
      # The model opt-in does nothing if related fields do not declare check_company=True.
      class MyModel(models.Model):
          _check_company_auto = True

          partner_id = fields.Many2one('res.partner')  # missing check_company=True

      # CORRECT
      class MyModel(models.Model):
          _check_company_auto = True

          partner_id = fields.Many2one('res.partner', check_company=True)
      ```
    </antipattern>

  </antipatterns>

</pattern>