# Odoo Version Knowledge - Version 18.0

<pattern>

  <description>
    Version-specific patterns, breaking changes, and code examples for Odoo 18.0.
    Key changes: &lt;tree&gt; renamed to &lt;list&gt;, chatter widget, _check_company_auto,
    @odoo-module no longer required in JS.
    Released: October 2024 | Python: 3.11+ | PostgreSQL: 14+ | Frontend: OWL 2.x
  </description>


  <!-- ============================================================
       VERSION NOTES — changes from v17
       ============================================================ -->
  <version_notes>
    <!-- Source: ORM changelog + confirmed in codebase -->
    <change version="18" type="breaking">&lt;tree&gt; tag renamed to &lt;list&gt; in XML views — use odoo-bin upgrade_code --from 17.0 --to 18.0 for automatic conversion</change>
    <change version="18" type="breaking">&lt;div class="oe_chatter"&gt; block replaced by &lt;chatter reload_on_follower="True"/&gt; widget</change>
    <change version="18" type="breaking">company_ids replaced by allowed_company_ids in record rules</change>
    <change version="18" type="breaking">group_operator renamed to aggregator on field definitions — confirmed in model_18.py</change>
    <change version="18" type="new">_check_company_auto = True — automatic company validation on write()</change>
    <change version="18" type="new">check_company=True on relational fields — automatic cross-company validation</change>
    <change version="18" type="new">read_group() deprecated (v18.2) — use _read_group() / formatted_read_group()</change>
    <change version="18" type="new">@api.private introduced (v18.2) — marks methods not exposed to RPC</change>
    <change version="18" type="new">check_access(), has_access(), _filtered_access() — new access methods (v18.0)</change>
    <change version="18" type="new">_search_display_name replaces name_get() (deprecated since v16.4)</change>
    <change version="18" type="new">odoo.Domain API for domain manipulation (v18.1)</change>
    <change version="18" type="new">@odoo-module comment no longer required in JS — use direct ES module imports</change>
    <change version="18" type="recommended">SQL() builder for safer SQL composition</change>
    <change version="18" type="recommended">Type hints on method signatures</change>
  </version_notes>


  <!-- ============================================================
       MODEL PATTERNS
       ============================================================ -->
  <examples category="model">

    <example id="model_definition" title="Model Definition — v18 multi-company pattern">
      ```python
      from odoo import models, fields, api, _
      from odoo.fields import Command
      from odoo.exceptions import UserError, ValidationError
      import logging

      _logger = logging.getLogger(__name__)


      class MyModel(models.Model):
          _name = 'my.model'
          _description = 'My Model'
          _inherit = ['mail.thread', 'mail.activity.mixin']
          _order = 'sequence, id desc'
          _check_company_auto = True

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
          # v18: aggregator replaces group_operator
            date = fields.Date(
                related='move_id.date',
                store=True,
                aggregator='min',  # was group_operator in v17
            )

            # precompute=True confirmed in v18 as well
            sequence = fields.Integer(
                compute='_compute_sequence',
                store=True,
                readonly=False,
                precompute=True,
            )

            # _rec_names_search confirmed in v18
            _rec_names_search = ['name', 'ref', 'partner_id']

          company_id = fields.Many2one(
              'res.company',
              required=True,
              default=lambda self: self.env.company,
              index=True,
          )
          user_id = fields.Many2one('res.users', default=lambda self: self.env.user, tracking=True)
          partner_id = fields.Many2one('res.partner', check_company=True, tracking=True)
          line_ids = fields.One2many('my.model.line', 'model_id', copy=True)

          total_amount = fields.Monetary(compute='_compute_total', store=True, currency_field='currency_id')
          currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
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

      def action_view_records(self):
          return {
              'type': 'ir.actions.act_window',
              'res_model': 'my.model',
              'view_mode': 'list,form',
              'domain': [('partner_id', '=', self.partner_id.id)],
          }
      ```
    </example>

  </examples>


  <!-- ============================================================
       XML VIEW PATTERNS
       ============================================================ -->
  <examples category="xml_views">

    <example id="form_view" title="Form View — v18 with chatter widget and list tag">
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
                      <!-- v18+: chatter widget replaces oe_chatter div block -->
                      <chatter reload_on_follower="True"/>
                  </form>
              </field>
          </record>

          <!-- v18+: use list tag instead of tree -->
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

    <example id="record_rule" title="Record Rule — allowed_company_ids">
      ```xml
      <record id="rule_my_model_company" model="ir.rule">
          <field name="name">My Model: Multi-Company</field>
          <field name="model_id" ref="model_my_model"/>
          <field name="global" eval="True"/>
          <field name="domain_force">[
              '|',
              ('company_id', '=', False),
              ('company_id', 'in', allowed_company_ids)
          ]</field>
      </record>
      ```
    </example>

  </examples>


  <!-- ============================================================
       OWL / JAVASCRIPT PATTERNS
       ============================================================ -->
  <examples category="owl">

    <example id="owl_component" title="OWL 2.x Component — v18 no @odoo-module needed">
      ```javascript
      import { Component, useState, onWillStart } from "@odoo/owl";
      import { useService } from "@web/core/utils/hooks";
      import { registry } from "@web/core/registry";

      export class MyComponent extends Component {
          static template = "my_module.MyComponent";
          static props = { recordId: { type: Number, optional: true } };

          setup() {
              this.orm = useService("orm");
              this.notification = useService("notification");
              this.state = useState({ data: [], loading: true });

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
       SECURITY PATTERNS
       ============================================================ -->
  <examples category="security">

    <example id="access_rights" title="Access Rights (ir.model.access.csv)">
      ```csv
      id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
      access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
      access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
      ```
    </example>

  </examples>


  <!-- ============================================================
       ANTIPATTERNS
       ============================================================ -->
  <antipatterns>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: tree tag removed in v18 -->
      <tree string="Records">...</tree>

      <!-- CORRECT -->
      <list string="Records">...</list>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: oe_chatter div block removed in v18 -->
      <div class="oe_chatter">
          <field name="message_follower_ids"/>
          <field name="activity_ids"/>
          <field name="message_ids"/>
      </div>

      <!-- CORRECT -->
      <chatter reload_on_follower="True"/>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: company_ids in record rules -->
      <field name="domain_force">[('company_id', 'in', company_ids)]</field>

      <!-- CORRECT -->
      <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>
      ```
    </antipattern>

    <antipattern severity="HIGH">
        ```python
        # WRONG: group_operator removed in v18
        date = fields.Date(group_operator='min')

        # CORRECT
        date = fields.Date(aggregator='min')
        ```
    </antipattern>

  </antipatterns>


  <!-- ============================================================
       MANIFEST STRUCTURE
       ============================================================ -->
  <examples category="manifest">

    <example id="manifest" title="v18 Manifest Structure">
      ```python
      {
          'name': 'My Module',
          'version': '18.0.1.0.0',
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