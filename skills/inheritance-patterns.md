<pattern>

  <description>
    Model and view inheritance patterns for Odoo modules across versions 17, 18 and 19.
    Phase 1 scope: _inherit for model extension, mail.thread and mail.activity.mixin,
    check_company= / _check_company_auto, selection_add, CRUD method overrides,
    XPath-based view inheritance, and the OCA field naming convention.
    Phase 2 (out of scope here): AbstractModel design, _inherits delegation.
  </description>

  <version_notes>
    <version id="17">
      attrs= removed — use invisible=, required=, readonly= directly on XML elements.
      _check_company_auto and check_company= available (present since v15, not a v18 feature).
      &lt;tree&gt; tag for list views.
      Chatter: oe_chatter div block.
      _inherit accepts a string or a list: _inherit = 'model' or _inherit = ['model'].
      _sql_constraints for CHECK constraints at class level.
      group_operator= on numeric / date fields.
    </version>
    <version id="18">
      &lt;tree&gt; replaced by &lt;list&gt; — breaking change.
      Chatter: &lt;chatter reload_on_follower="True"/&gt; or &lt;chatter reload_on_attachment="True"/&gt;.
      aggregator= replaces group_operator= — breaking change.
      export_string_translation=False available on string fields.
      _check_company_auto and check_company= unchanged from v17.
    </version>
    <version id="19">
      models.Constraint() replaces _sql_constraints for CHECK constraints.
      models.Index() replaces manual index definitions at class level.
      SQL import path: from odoo.tools import SQL.
      Type hints recommended on method signatures but NOT mandatory.
      _check_company_auto and check_company= unchanged from v17/v18.
      Chatter and list syntax identical to v18.
    </version>
  </version_notes>

  <examples>

    <example id="model_extension" title="_inherit — add fields to existing model">
      ```python
      from odoo import api, fields, models


      class ResPartner(models.Model):
          _inherit = 'res.partner'

          x_loyalty_points = fields.Integer(
              string='Loyalty Points',
              default=0,
          )
          x_customer_tier = fields.Selection(
              selection=[
                  ('bronze', 'Bronze'),
                  ('silver', 'Silver'),
                  ('gold', 'Gold'),
              ],
              string='Customer Tier',
              compute='_compute_customer_tier',
              store=True,
          )
          x_account_manager_id = fields.Many2one(
              comodel_name='res.users',
              string='Account Manager',
          )

          @api.depends('x_loyalty_points')
          def _compute_customer_tier(self):
              for partner in self:
                  if partner.x_loyalty_points >= 1000:
                      partner.x_customer_tier = 'gold'
                  elif partner.x_loyalty_points >= 500:
                      partner.x_customer_tier = 'silver'
                  else:
                      partner.x_customer_tier = 'bronze'
      ```
      Custom fields must use the x_ prefix to avoid collisions with future Odoo core fields.
    </example>

    <example id="method_override" title="_inherit — override method with super()">
      ```python
      class SaleOrder(models.Model):
          _inherit = 'sale.order'

          def action_confirm(self):
              # Pre-processing before calling the original method
              for order in self:
                  order._check_credit_limit()

              # Call the original method and capture its return value
              result = super().action_confirm()

              # Post-processing after the original method
              for order in self:
                  order._send_confirmation_notification()

              return result

          def _check_credit_limit(self):
              if self.partner_id.credit_limit and \
                 self.amount_total > self.partner_id.credit_limit:
                  raise UserError("Order exceeds credit limit.")
      ```
    </example>

    <example id="mail_thread" title="mail.thread and mail.activity.mixin">
      ```python
      class MyDocument(models.Model):
          _name = 'my.document'
          _description = 'My Document'
          _inherit = ['mail.thread', 'mail.activity.mixin']

          name = fields.Char(required=True)
          state = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('done', 'Done'),
          ], default='draft', tracking=True)

          partner_id = fields.Many2one(
              comodel_name='res.partner',
              tracking=True,
          )
      ```
      Use mail.thread for any model where users need a chatter, message history, or
      field-level change tracking. mail.activity.mixin adds the activity buttons.
      tracking=True on a field logs changes automatically when mail.thread is inherited.
    </example>

    <example id="check_company" title="Multi-company fields — check_company and _check_company_auto">
      ```python
      # _check_company_auto and check_company= have been available since v15
      # They are NOT new in v17 or v18

      class MyModel(models.Model):
          _name = 'my.model'
          _description = 'My Model'
          _check_company_auto = True   # auto-validate all check_company= fields on write

          company_id = fields.Many2one(
              comodel_name='res.company',
              required=True,
              index=True,
              default=lambda self: self.env.company,
          )
          partner_id = fields.Many2one(
              comodel_name='res.partner',
              check_company=True,    # validated against company_id
          )
          warehouse_id = fields.Many2one(
              comodel_name='stock.warehouse',
              check_company=True,
          )
      ```
    </example>

    <example id="selection_add" title="Extend Selection field with selection_add">
      ```python
      class SaleOrder(models.Model):
          _inherit = 'sale.order'

          state = fields.Selection(
              selection_add=[
                  ('pending_approval', 'Pending Approval'),
                  ('approved', 'Approved'),
              ],
              ondelete={
                  'pending_approval': 'set default',
                  'approved': 'set default',
              },
          )

          def action_submit_approval(self):
              self.write({'state': 'pending_approval'})

          def action_approve(self):
              self.action_confirm()
      ```
      Always provide ondelete= for every custom value — omitting it causes upgrade
      errors when the module is uninstalled.
    </example>

    <example id="create_override" title="create() override with @api.model_create_multi">
      ```python
      class MyModel(models.Model):
          _inherit = 'my.model'

          @api.model_create_multi
          def create(self, vals_list):
              for vals in vals_list:
                  if not vals.get('reference'):
                      vals['reference'] = self.env['ir.sequence'].next_by_code(
                          'my.model.sequence'
                      )
              return super().create(vals_list)
      ```
    </example>

    <example id="view_inheritance_v17" title="View inheritance with XPath — v17">
      ```xml
      <record id="view_my_document_form_inherit" model="ir.ui.view">
          <field name="name">my.document.form.inherit.my_module</field>
          <field name="model">my.document</field>
          <field name="inherit_id" ref="base_module.my_document_form_view"/>
          <field name="arch" type="xml">
              <!-- Add after an existing field -->
              <field name="partner_id" position="after">
                  <field name="x_account_manager_id"/>
              </field>

              <!-- Add a smart button -->
              <xpath expr="//div[@name='button_box']" position="inside">
                  <button class="oe_stat_button" type="object"
                          name="action_view_loyalty_history"
                          icon="fa-star">
                      <field string="Points" name="x_loyalty_points"
                             widget="statinfo"/>
                  </button>
              </xpath>

              <!-- Conditional field with v17+ syntax (no attrs=) -->
              <field name="name" position="after">
                  <field name="x_approval_notes"
                         invisible="state not in ['waiting_approval', 'approved']"/>
              </field>
          </field>
      </record>
      ```
    </example>

    <example id="view_inheritance_v18_v19" title="View inheritance with chatter — v18/v19">
      ```xml
      <record id="view_my_document_form_inherit" model="ir.ui.view">
          <field name="name">my.document.form.inherit.my_module</field>
          <field name="model">my.document</field>
          <field name="inherit_id" ref="base_module.my_document_form_view"/>
          <field name="arch" type="xml">
              <!-- Add a field -->
              <field name="partner_id" position="after">
                  <field name="x_account_manager_id"/>
              </field>

              <!-- v18/v19: chatter tag replaces oe_chatter div
                   Use this when adding chatter to a model that did not have it -->
              <xpath expr="//form" position="inside">
                  <chatter reload_on_follower="True"/>
              </xpath>
          </field>
      </record>
      ```
    </example>

    <example id="sql_constraints_v17_v18" title="SQL constraints — v17 and v18">
      ```python
      class MyModel(models.Model):
          _name = 'my.model'

          _sql_constraints = [
              ('code_unique', 'UNIQUE(code, company_id)',
               'Code must be unique per company.'),
              ('amount_positive', 'CHECK(amount >= 0)',
               'Amount must be positive.'),
          ]
      ```
    </example>

    <example id="constraints_v19" title="SQL constraints — v19">
      ```python
      class MyModel(models.Model):
          _name = 'my.model'

          # models.Constraint() replaces _sql_constraints at class level
          _code_unique = models.Constraint(
              'UNIQUE(code, company_id)',
              'Code must be unique per company.',
          )
          _amount_positive = models.Constraint(
              'CHECK(amount >= 0)',
              'Amount must be positive.',
          )

          # models.Index() replaces manual index definitions
          _code_company_idx = models.Index("(code, company_id)")
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # Omitting super() in an overridden method breaks all downstream modules
      class SaleOrder(models.Model):
          _inherit = 'sale.order'

          def action_confirm(self):
              self.write({'x_custom_field': True})
              # Missing: result = super().action_confirm()

      # Fix: always call super() and return its result
      def action_confirm(self):
          self.write({'x_custom_field': True})
          return super().action_confirm()
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- v17+: attrs= was removed; raises a view parse error -->
      <field name="x_notes"
             attrs="{'invisible': [('state', 'not in', ['pending', 'approved'])]}"/>

      <!-- Fix -->
      <field name="x_notes"
             invisible="state not in ['pending', 'approved']"/>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # selection_add without ondelete — causes upgrade error on module uninstall
      state = fields.Selection(
          selection_add=[('waiting_approval', 'Waiting Approval')],
          # missing: ondelete={'waiting_approval': 'set default'}
      )

      # Fix: always provide ondelete for every added value
      state = fields.Selection(
          selection_add=[('waiting_approval', 'Waiting Approval')],
          ondelete={'waiting_approval': 'set default'},
      )
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```xml
      <!-- Using string= as XPath selector — translatable and unstable -->
      <field string="Partner" position="after">
          <field name="x_account_manager_id"/>
      </field>

      <!-- Fix: use name= or a specific XPath expression -->
      <field name="partner_id" position="after">
          <field name="x_account_manager_id"/>
      </field>
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Custom fields without the x_ prefix — collision risk with future Odoo fields
      class ResPartner(models.Model):
          _inherit = 'res.partner'

          loyalty_points = fields.Integer()   # could clash with future core field

      # Fix: always use x_ prefix for custom fields
      class ResPartner(models.Model):
          _inherit = 'res.partner'

          x_loyalty_points = fields.Integer()
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Inheriting a model whose module is not listed in depends=
      # __manifest__.py:
      {
          'depends': ['base'],   # missing 'sale' — but code inherits sale.order
      }

      # Fix: list every module whose models or views you inherit
      {
          'depends': ['base', 'sale'],
      }
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```xml
      <!-- Positional XPath selector — fragile when upstream view changes -->
      <xpath expr="//field[3]" position="after">
          <field name="x_notes"/>
      </xpath>

      <!-- Fix: use a named selector -->
      <xpath expr="//field[@name='partner_id']" position="after">
          <field name="x_notes"/>
      </xpath>
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # v19: _sql_constraints still works but models.Constraint() is the new idiom
      # Do not mix both in the same model class
      _sql_constraints = [
          ('code_unique', 'UNIQUE(code)', 'Code must be unique.'),
      ]
      _code_check = models.Constraint('CHECK(code IS NOT NULL)', 'Code required.')
      # Fix: use one mechanism consistently; prefer models.Constraint() in v19
      ```
    </antipattern>

  </antipatterns>

</pattern>