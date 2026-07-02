# odoo-security-guide-17.md

<pattern>

  <description>
    Odoo 17.0 security patterns. Covers access rights (ir.model.access.csv),
    record rules, model-level security, field-level security, view security,
    and secure SQL. Use this file for v17 only — never mix with other versions.
  </description>

  <version_notes>
    <version id="17">
      attrs= removed from views — use invisible=, readonly=, required= directly as Python expressions.
      @api.model_create_multi mandatory on all create() methods.
      _check_company_auto = True available — set on model class to enable automatic company validation.
      check_company=True available on Many2one fields.
      Record rules use company_ids in domain_force for multi-company filtering.
      SQL queries use parameterized syntax: self.env.cr.execute(query, params).
    </version>
  </version_notes>

  <examples>

    <example id="security_groups" title="Security groups XML">
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

    <example id="access_rights" title="ir.model.access.csv (v17)">
      ```csv
      id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
      access_custom_model_user,custom.model.user,model_custom_model,custom_module.group_custom_user,1,1,1,0
      access_custom_model_manager,custom.model.manager,model_custom_model,custom_module.group_custom_manager,1,1,1,1
      ```
    </example>

    <example id="record_rule_multicompany" title="Multi-company record rule (v17)">
      ```xml
      <!-- v17: use company_ids in domain_force -->
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

    <example id="model_security" title="Model with company validation (v17)">
      ```python
      from odoo import api, fields, models, _
      from odoo.exceptions import AccessError

      class SecureModel(models.Model):
          _name = 'custom.secure'
          _description = 'Secure Model'
          _inherit = ['mail.thread', 'mail.activity.mixin']
          _check_company_auto = True

          name = fields.Char(string='Name', required=True, tracking=True)
          company_id = fields.Many2one(
              'res.company',
              string='Company',
              default=lambda self: self.env.company,
              required=True,
              index=True,
          )
          partner_id = fields.Many2one(
              'res.partner',
              string='Partner',
              check_company=True,
          )
          state = fields.Selection([
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
              self._do_sensitive_work()
      ```
    </example>

    <example id="secure_sql" title="Parameterized SQL query (v17)">
      ```python
      def _get_secure_data(self):
          self.env.cr.execute(
              """
              SELECT id, name, amount
              FROM %s
              WHERE company_id = %%s
                AND active = %%s
                AND create_uid = %%s
              """ % self._table,
              [self.env.company.id, True, self.env.user.id]
          )
          return self.env.cr.dictfetchall()
      ```
    </example>

    <example id="view_security" title="View field and button visibility (v17 — no attrs)">
      ```xml
      <form string="Custom Model">
          <header>
              <!-- v17: invisible takes a Python expression -->
              <button name="action_confirm" string="Confirm" type="object"
                      class="btn-primary" invisible="state != 'draft'"/>
              <button name="action_approve" string="Approve" type="object"
                      groups="custom_module.group_custom_manager"
                      invisible="state != 'pending'"/>
              <field name="state" widget="statusbar"/>
          </header>
          <sheet>
              <group>
                  <field name="name"/>
                  <!-- groups= hides the field at model level -->
                  <field name="internal_notes" groups="custom_module.group_custom_manager"/>
                  <!-- invisible= with user_has_groups() for dynamic check -->
                  <field name="cost_price"
                         invisible="not user_has_groups('account.group_account_user')"/>
              </group>
          </sheet>
          <div class="oe_chatter">
              <field name="message_follower_ids"/>
              <field name="activity_ids"/>
              <field name="message_ids"/>
          </div>
      </form>
      ```
    </example>

    <example id="field_level_security" title="Field-level groups= (v17)">
      ```python
      class SecureModel(models.Model):
          _name = 'custom.secure'
          _description = 'Secure Model'

          name = fields.Char(required=True)

          internal_notes = fields.Text(
              string='Internal Notes',
              groups='custom_module.group_custom_manager',
          )

          cost_price = fields.Float(
              string='Cost Price',
              groups='account.group_account_user',
          )
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: attrs= was removed in v17 -->
      <field name="state_field" attrs="{'invisible': [('state', '=', 'draft')]}"/>

      <!-- CORRECT -->
      <field name="state_field" invisible="state == 'draft'"/>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: string formatting in SQL — SQL injection risk
      self.env.cr.execute(
          "SELECT id FROM %s WHERE name = '%s'" % (self._table, user_input)
      )

      # CORRECT: parameterized query
      self.env.cr.execute(
          "SELECT id FROM %s WHERE name = %%s" % self._table,
          [user_input]
      )
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: missing @api.model_create_multi in v17
      def create(self, vals):
          return super().create(vals)

      # CORRECT
      @api.model_create_multi
      def create(self, vals_list):
          return super().create(vals_list)
      ```
    </antipattern>

  </antipatterns>

</pattern>