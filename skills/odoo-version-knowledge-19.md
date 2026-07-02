# Odoo Version Knowledge - Version 19.0

<pattern>

  <description>
    Version-specific patterns, breaking changes, and code examples for Odoo 19.0.
    Key changes: models.Constraint() replaces _sql_constraints, models.Index() for indexes,
    odoo.osv deprecated, record._cr/_context/_uid deprecated.
    OWL 2.x still in use — confirmed in 19.0 source code.
    Released: October 2025 (Expected) | Python: 3.12+ | Frontend: OWL 2.x
  </description>


  <!-- ============================================================
       VERSION NOTES — changes from v18
       ============================================================ -->
  <version_notes>
    <!-- Source: ORM changelog v19.0 + confirmed in model_19.py and views_19.xml -->
    <change version="19" type="breaking">models.Constraint() replaces _sql_constraints list — confirmed in model_19.py</change>
    <change version="19" type="new">models.Index() for defining indexes as model attributes — confirmed in model_19.py</change>
    <change version="19" type="deprecated">odoo.osv — flag any import or usage</change>
    <change version="19" type="deprecated">record._cr, record._context, record._uid — use self.env.cr, self.env.context, self.env.uid</change>
    <change version="19" type="new">GROUPING SETS now supported in pivot views natively</change>
    <change version="19" type="note">OWL 2.x still in use — confirmed in 19.0 source code. Migration to OWL 3.x expected in v20.</change>
    <change version="19" type="note">Type hints optional — present only in specific internal methods, not enforced globally</change>
    <change version="19" type="note">SQL() builder recommended, not mandatory — same as v18</change>
  </version_notes>


  <!-- ============================================================
       MODEL PATTERNS
       ============================================================ -->
  <examples category="model">

    <example id="model_definition" title="Model Definition — v19 with models.Constraint and models.Index">
      ```python
      from odoo import models, fields, api, _
      from odoo.fields import Command
      from odoo.exceptions import UserError, ValidationError
      from odoo.tools.sql import SQL
      import logging

      _logger = logging.getLogger(__name__)


      class MyModel(models.Model):
          _name = 'my.model'
          _description = 'My Model'
          _inherit = ['mail.thread', 'mail.activity.mixin']
          _order = 'sequence, id desc'
          _check_company_auto = True
          _rec_names_search = ['name', 'code']

          name = fields.Char(required=True, index='trigram', tracking=True)
          code = fields.Char(index=True, copy=False)

          state = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('done', 'Done'),
              ('cancelled', 'Cancelled'),
          ], default='draft', tracking=True, index=True)

          sequence = fields.Integer(default=10)
          active = fields.Boolean(default=True)
          date = fields.Date(
              default=fields.Date.context_today,
              aggregator='min',
          )

          company_id = fields.Many2one(
              'res.company',
              required=True,
              default=lambda self: self.env.company,
              index=True,
          )
          user_id = fields.Many2one('res.users', default=lambda self: self.env.user, tracking=True)
          partner_id = fields.Many2one('res.partner', check_company=True, tracking=True)
          line_ids = fields.One2many('my.model.line', 'model_id', copy=True)

          total_amount = fields.Monetary(
              compute='_compute_total',
              store=True,
              currency_field='currency_id',
          )
          currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

          # v19: models.Constraint() replaces _sql_constraints list
          _check_name_required = models.Constraint(
              'CHECK(name IS NOT NULL AND name != \'\')',
              'Name is required and cannot be empty.',
          )

          # v19: models.Index() for custom indexes
          _name_company_idx = models.Index('(name, company_id)')
      ```
    </example>

    <example id="crud_methods" title="CRUD Methods">
      ```python
      @api.model_create_multi
      def create(self, vals_list):
          for vals in vals_list:
              if not vals.get('code'):
                  vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
          return super().create(vals_list)

      def write(self, vals):
          if 'state' in vals and vals['state'] == 'confirmed':
              for record in self:
                  if not record.line_ids:
                      raise UserError(_("Add at least one line."))
          return super().write(vals)

      def unlink(self):
          for record in self:
              if record.state not in ('draft', 'cancelled'):
                  raise UserError(_("Only draft or cancelled records can be deleted."))
          return super().unlink()
      ```
    </example>

    <example id="computed_fields" title="Computed Fields">
      ```python
      @api.depends('line_ids.amount')
      def _compute_total(self):
          for record in self:
              record.total_amount = sum(record.line_ids.mapped('amount'))

      def action_confirm(self):
          self.ensure_one()
          self.write({'state': 'confirmed'})
      ```
    </example>

  </examples>


  <!-- ============================================================
       XML VIEW PATTERNS
       ============================================================ -->
  <examples category="xml_views">

    <example id="form_view" title="Form View — v19 with chatter widget and list tag">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo>
          <record id="view_my_model_form" model="ir.ui.view">
              <field name="name">my.model.form</field>
              <field name="model">my.model</field>
              <field name="arch" type="xml">
                  <form>
                      <header>
                          <button name="action_confirm" type="object"
                                  string="Confirm" class="btn-primary"
                                  invisible="state != 'draft'"/>
                          <button name="action_cancel" type="object"
                                  string="Cancel"
                                  invisible="state in ('done', 'cancelled')"/>
                          <field name="state" widget="statusbar"
                                 statusbar_visible="draft,confirmed,done"/>
                      </header>
                      <sheet>
                          <group>
                              <group>
                                  <field name="code" readonly="state != 'draft'"/>
                                  <field name="partner_id"
                                         readonly="state == 'done'"
                                         required="state == 'confirmed'"/>
                                  <field name="company_id"
                                         groups="base.group_multi_company"
                                         readonly="state != 'draft'"/>
                              </group>
                              <group>
                                  <field name="date"/>
                              </group>
                          </group>
                          <notebook>
                              <page string="Lines" name="lines">
                                  <field name="line_ids" readonly="state == 'done'">
                                      <list editable="bottom">
                                          <field name="sequence" widget="handle"/>
                                          <field name="name"/>
                                          <field name="quantity"/>
                                          <field name="price"/>
                                          <field name="amount" sum="Total"/>
                                      </list>
                                  </field>
                              </page>
                          </notebook>
                      </sheet>
                      <!-- v18/v19: chatter widget -->
                      <chatter reload_on_attachment="True"/>
                  </form>
              </field>
          </record>

          <record id="view_my_model_list" model="ir.ui.view">
              <field name="name">my.model.list</field>
              <field name="model">my.model</field>
              <field name="arch" type="xml">
                  <list decoration-danger="state == 'cancelled'"
                        decoration-success="state == 'done'">
                      <field name="sequence" widget="handle"/>
                      <field name="name"/>
                      <field name="partner_id"/>
                      <field name="date"/>
                      <field name="total_amount" sum="Total"/>
                      <field name="state" widget="badge"
                             decoration-success="state == 'done'"
                             decoration-info="state == 'confirmed'"/>
                  </list>
              </field>
          </record>
      </odoo>
      ```
    </example>

  </examples>


  <!-- ============================================================
       OWL / JAVASCRIPT PATTERNS
       ============================================================ -->
  <examples category="owl">

    <example id="owl_component" title="OWL 2.x Component — v19 no @odoo-module needed">
      ```javascript
      import { Component, useState, onWillStart } from "@odoo/owl";
      import { useService } from "@web/core/utils/hooks";
      import { registry } from "@web/core/registry";

      export class MyComponent extends Component {
          static template = "my_module.MyComponent";
          static props = {
              recordId: { type: Number, optional: true },
              onConfirm: { type: Function, optional: true },
          };

          setup() {
              this.orm = useService("orm");
              this.notification = useService("notification");
              this.state = useState({
                  data: [],
                  loading: true,
              });

              onWillStart(async () => {
                  await this.loadData();
              });
          }

          async loadData() {
              try {
                  this.state.data = await this.orm.searchRead(
                      "my.model", [], ["name", "state"],
                      { order: "create_date DESC" }
                  );
              } catch (error) {
                  this.notification.add("Error loading data", { type: "danger" });
              } finally {
                  this.state.loading = false;
              }
          }
      }

      registry.category("actions").add("my_module.my_action", MyComponent);
      ```
    </example>

  </examples>


  <!-- ============================================================
       ANTIPATTERNS
       ============================================================ -->
  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: _sql_constraints list deprecated in v19
      _sql_constraints = [
          ('check_name', 'CHECK(name IS NOT NULL)', 'Name is required.'),
      ]

      # CORRECT: models.Constraint()
      _check_name = models.Constraint(
          'CHECK(name IS NOT NULL)',
          'Name is required.',
      )
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: deprecated attributes in v19
      self.env.cr.execute(query)  # use self.env.cr — OK
      record._cr                  # DEPRECATED — use self.env.cr
      record._context             # DEPRECATED — use self.env.context
      record._uid                 # DEPRECATED — use self.env.uid
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: odoo.osv deprecated in v19
      from odoo.osv import expression

      # CORRECT
      from odoo import expression
      ```
    </antipattern>

  </antipatterns>


  <!-- ============================================================
       MANIFEST STRUCTURE
       ============================================================ -->
  <examples category="manifest">

    <example id="manifest" title="v19 Manifest Structure">
      ```python
      {
          'name': 'My Module',
          'version': '19.0.1.0.0',
          'category': 'Tools',
          'summary': 'Module summary',
          'author': 'Your Company',
          'website': 'https://yourwebsite.com',
          'license': 'LGPL-3',
          'depends': ['base', 'mail', 'web'],
          'data': [
              'security/security.xml',
              'security/ir.model.access.csv',
              'views/my_model_views.xml',
              'views/menu.xml',
          ],
          'assets': {
              'web.assets_backend': [
                  'my_module/static/src/**/*.js',
                  'my_module/static/src/**/*.xml',
                  'my_module/static/src/**/*.scss',
              ],
          },
          'installable': True,
          'application': False,
      }
      ```
    </example>

  </examples>

</pattern>