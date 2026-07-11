# Odoo 17.0 Version Knowledge

<pattern>

  <description>
    Version-specific patterns, breaking changes, and code examples for Odoo 17.0.
    Key changes: attrs= removed, @api.model_create_multi mandatory, /** @odoo-module **/ required in JS.
    Released: October 2023 | Python: 3.10+ | PostgreSQL: 13+ | Frontend: OWL 2.x
  </description>


  <!-- ============================================================
       BREAKING CHANGES FROM v16
       ============================================================ -->
  <version_notes>
    <change version="17" type="breaking">attrs= attribute removed from XML views — use invisible=, readonly=, required= with Python expressions directly</change>
    <change version="17" type="breaking">@api.model create(self, vals) signature no longer accepted — @api.model_create_multi create(self, vals_list) is mandatory</change>
    <change version="17" type="new">index='trigram' field option introduced for GIN trigram indexing on Char fields</change>
    <change version="17" type="new">SQL() wrapper introduced for safer SQL composition — flag raw string concatenation in cr.execute()</change>
    <change version="17" type="new">Field.group_operator renamed to Field.aggregator (v17.2)</change>
    <change version="17" type="new">_flush_search deprecated (v17.1) — flushing now handled by Environment.execute_query()</change>
    <change version="17" type="new">inselect operator removed (v17.4) — use in with a Query or SQL object</change>
    <change version="17" type="new">precompute=True on computed fields — pre-computes value at record creation</change>
    <change version="17" type="new">_rec_names_search — list of fields used in name_search()</change>
    <change version="17" type="note">group_operator still valid in v17 — renamed to aggregator in v18</change>
  </version_notes>


  <!-- ============================================================
       MODEL PATTERNS
       ============================================================ -->
  <examples category="model">

    <example id="model_definition" title="Model Definition">
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

          # ADD these field attributes confirmed in model_17.py:
        name = fields.Char(
            required=True,
            index='trigram',
            tracking=True,
        )

        # group_operator still valid in v17 (renamed to aggregator in v18)
        date = fields.Date(
            related='move_id.date',
            store=True,
            group_operator='min',
        )

        # precompute=True available in v17
        sequence = fields.Integer(
            compute='_compute_sequence',
            store=True,
            readonly=False,
            precompute=True,
        )

        # _rec_names_search available in v17
        _rec_names_search = ['name', 'ref', 'partner_id']

          code = fields.Char(index=True, copy=False)

          state = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('in_progress', 'In Progress'),
              ('done', 'Done'),
              ('cancelled', 'Cancelled'),
          ], default='draft', tracking=True, index=True)

          sequence = fields.Integer(default=10)
          active = fields.Boolean(default=True)

          date = fields.Date(default=fields.Date.context_today)
          date_deadline = fields.Date(index=True)

          company_id = fields.Many2one(
              'res.company',
              required=True,
              default=lambda self: self.env.company,
              index=True,
          )

          user_id = fields.Many2one(
              'res.users',
              default=lambda self: self.env.user,
              tracking=True,
          )

          partner_id = fields.Many2one(
              'res.partner',
              tracking=True,
          )

          line_ids = fields.One2many(
              'my.model.line',
              'model_id',
              copy=True,
          )

          total_amount = fields.Monetary(
              compute='_compute_total',
              store=True,
              currency_field='currency_id',
          )

          currency_id = fields.Many2one(
              'res.currency',
              related='company_id.currency_id',
          )
      ```
    </example>

    <example id="crud_methods" title="CRUD Methods — v17 mandatory pattern">
      ```python
      @api.model_create_multi
      def create(self, vals_list):
          for vals in vals_list:
              if not vals.get('code'):
                  vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
          records = super().create(vals_list)
          for record in records:
              record.message_post(body=_("Record created."))
          return records

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

  </examples>


  <!-- ============================================================
       XML VIEW PATTERNS
       ============================================================ -->
  <examples category="xml_views">

    <example id="form_view" title="Form View — v17 required syntax">
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
                                 statusbar_visible="draft,confirmed,in_progress,done"/>
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
                                  <field name="date_deadline"
                                         invisible="state == 'draft'"/>
                              </group>
                          </group>
                          <notebook>
                              <page string="Lines" name="lines">
                                  <field name="line_ids" readonly="state == 'done'">
                                      <tree editable="bottom">
                                          <field name="sequence" widget="handle"/>
                                          <field name="name"/>
                                          <field name="quantity"/>
                                          <field name="price"/>
                                          <field name="amount" sum="Total"/>
                                      </tree>
                                  </field>
                              </page>
                          </notebook>
                      </sheet>
                      <div class="oe_chatter">
                          <field name="message_follower_ids"/>
                          <field name="activity_ids"/>
                          <field name="message_ids"/>
                      </div>
                  </form>
              </field>
          </record>

          <record id="view_my_model_tree" model="ir.ui.view">
              <field name="name">my.model.tree</field>
              <field name="model">my.model</field>
              <field name="arch" type="xml">
                  <tree decoration-danger="state == 'cancelled'"
                        decoration-success="state == 'done'">
                      <field name="sequence" widget="handle"/>
                      <field name="name"/>
                      <field name="partner_id"/>
                      <field name="date"/>
                      <field name="total_amount" sum="Total"/>
                      <field name="state" widget="badge"
                             decoration-success="state == 'done'"
                             decoration-info="state == 'confirmed'"/>
                  </tree>
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

    <example id="owl_component" title="OWL 2.x Component — v17 requires @odoo-module">
      ```javascript
      /** @odoo-module **/

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
                  selectedIds: new Set(),
              });

              onWillStart(async () => {
                  await this.loadData();
              });
          }

          async loadData() {
              try {
                  this.state.data = await this.orm.searchRead(
                      "my.model",
                      [],
                      ["name", "state"],
                      { order: "create_date DESC", limit: 100 }
                  );
              } finally {
                  this.state.loading = false;
              }
          }

          toggleSelect(id) {
              if (this.state.selectedIds.has(id)) {
                  this.state.selectedIds.delete(id);
              } else {
                  this.state.selectedIds.add(id);
              }
              // Force reactivity for Set in OWL 2.x
              this.state.selectedIds = new Set(this.state.selectedIds);
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
      ```xml
      <!-- WRONG: attrs= removed in v17 -->
      <field name="partner_id"
             attrs="{'invisible': [('state', '=', 'draft')],
                     'required': [('state', '=', 'confirmed')]}"/>

      <!-- CORRECT -->
      <field name="partner_id"
             invisible="state == 'draft'"
             required="state == 'confirmed'"/>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: old create signature breaks in v17
      @api.model
      def create(self, vals):
          return super().create(vals)

      # CORRECT
      @api.model_create_multi
      def create(self, vals_list):
          return super().create(vals_list)
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```xml
      <!-- WRONG: domain-style list syntax in visibility attributes -->
      <field name="x" invisible="[('state', '=', 'draft')]"/>

      <!-- CORRECT: Python expression -->
      <field name="x" invisible="state == 'draft'"/>
      ```
    </antipattern>

  </antipatterns>


  <!-- ============================================================
       MANIFEST STRUCTURE
       ============================================================ -->
  <examples category="manifest">

    <example id="manifest" title="v17 Manifest Structure">
      ```python
      {
          'name': 'My Module',
          'version': '17.0.1.0.0',
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


  <!-- ============================================================
       PREPARING FOR v18
       ============================================================ -->
  <version_notes>
    <change version="18" type="upcoming">oe_chatter div block replaced by the bare, self-closing &lt;chatter/&gt; tag (optional reload_on_attachment/reload_on_follower/reload_on_post attributes exist for specific views but are not required — confirmed the bare form is dominant in real 18.0/19.0 source)</change>
    <change version="18" type="upcoming">tree tag renamed to list in XML views — use odoo-bin upgrade_code --from 17.0 --to 18.0</change>
    <change version="17" type="already-available">_check_company_auto = True on models with company_id — confirmed present in v17 source (account.move.line line 25), NOT a new v18 feature</change>
    <change version="17" type="already-available">check_company=True on relational fields with company dependency — same as above, already available in v17</change>
    <change version="18" type="not-a-change">Record rules keep using company_ids in domain_force — allowed_company_ids does NOT replace it (confirmed against addons/account/security/account_security.xml in real 18.0/19.0 source; a previous version of this file incorrectly claimed this change)</change>
    <change version="18" type="upcoming">@odoo-module no longer required in JS — direct ES module imports</change>
  </version_notes>

</pattern>