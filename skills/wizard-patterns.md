<pattern>

  <description>
    Patterns for TransientModel (wizard) implementation in Odoo addons.
    Covers model structure, action return types, view layout, context-based
    defaults, and binding to models. Use when implementing user dialogs,
    confirmation flows, batch operations, or parameter collection before
    report generation.
  </description>

  <version_notes>
    <version id="17">
      TransientModel API is stable: _name, _description, _check_company_auto.
      _check_company_auto = True confirmed in wizard_17.py line 12 — this is
      NOT a v18 feature, it is available in v17.
      check_company=True on Many2one fields also available in v17.
      View: invisible= with Python expressions (attrs= removed in v17).
      footer tag for dialog buttons. target="new" for modal display.
      action_create_payments returns view_mode='tree,form' for multi-record.
      Type hints on action methods are optional in all versions (not present
      in the account.payment.register reference source).
    </version>
    <version id="18">
      TransientModel, _check_company_auto, check_company= API unchanged.
      utf-8 coding header removed (was already absent in v17 account module).
      No new wizard-specific APIs introduced in v18.
    </version>
    <version id="19">
      TransientModel API identical to v18.
      No wizard-specific breaking changes in v19.
      models.Constraint() available for SQL constraints if needed.
    </version>
  </version_notes>

  <examples>

    <example id="basic_wizard" title="Basic TransientModel wizard">
      ```python
      from odoo import api, fields, models, _
      from odoo.exceptions import UserError


      class MyModuleAction(models.TransientModel):
          _name = 'my.module.action'
          _description = 'My Module Action'
          _check_company_auto = True

          # Populated from context via default
          record_id = fields.Many2one(
              comodel_name='my.model',
              string='Record',
              required=True,
              check_company=True,
              default=lambda self: self.env.context.get('active_id'),
          )
          company_id = fields.Many2one(
              comodel_name='res.company',
              default=lambda self: self.env.company,
          )
          date = fields.Date(
              string='Date',
              required=True,
              default=fields.Date.context_today,
          )
          note = fields.Text(string='Notes')

          def action_confirm(self):
              self.ensure_one()
              if not self.record_id:
                  raise UserError(_("No record selected."))
              self.record_id.write({
                  'date': self.date,
                  'notes': self.note,
              })
              return {'type': 'ir.actions.act_window_close'}
      ```
    </example>

    <example id="basic_wizard_view" title="Wizard form view with footer">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo>
          <record id="view_my_module_action_form" model="ir.ui.view">
              <field name="name">my.module.action.form</field>
              <field name="model">my.module.action</field>
              <field name="arch" type="xml">
                  <form string="My Action">
                      <field name="company_id" invisible="1"/>
                      <group>
                          <field name="record_id" readonly="1"
                                 invisible="not record_id"/>
                          <field name="date"/>
                          <field name="note"/>
                      </group>
                      <footer>
                          <button name="action_confirm"
                                  string="Confirm"
                                  type="object"
                                  class="oe_highlight"
                                  data-hotkey="q"/>
                          <button string="Discard"
                                  class="btn btn-secondary"
                                  special="cancel"
                                  data-hotkey="x"/>
                      </footer>
                  </form>
              </field>
          </record>

          <record id="action_my_module_action" model="ir.actions.act_window">
              <field name="name">My Action</field>
              <field name="res_model">my.module.action</field>
              <field name="view_mode">form</field>
              <field name="target">new</field>
              <field name="binding_model_id" ref="my_module.model_my_model"/>
              <field name="binding_view_types">form,list</field>
          </record>
      </odoo>
      ```
    </example>

    <example id="wizard_security" title="Security entry for wizard">
      ```csv
      id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
      access_my_module_action_user,my.module.action,model_my_module_action,base.group_user,1,1,1,1
      ```
    </example>

    <example id="open_wizard_from_button" title="Opening wizard from a model button">
      ```python
      def action_open_wizard(self):
          self.ensure_one()
          return {
              'type': 'ir.actions.act_window',
              'name': _('My Action'),
              'res_model': 'my.module.action',
              'view_mode': 'form',
              'target': 'new',
              'context': {
                  'default_record_id': self.id,
                  'active_id': self.id,
                  'active_ids': self.ids,
                  'active_model': self._name,
              },
          }
      ```
    </example>

    <example id="batch_wizard" title="Batch operation wizard (multi-record)">
      ```python
      class MyModuleBatchAction(models.TransientModel):
          _name = 'my.module.batch.action'
          _description = 'Batch Action'

          record_ids = fields.Many2many(
              comodel_name='my.model',
              string='Records',
              default=lambda self: self.env.context.get('active_ids'),
          )
          new_state = fields.Selection(
              selection=[
                  ('draft', 'Draft'),
                  ('confirmed', 'Confirmed'),
              ],
              string='New Status',
              required=True,
          )

          def action_apply(self):
              self.record_ids.write({'state': self.new_state})
              if len(self.record_ids) == 1:
                  return {
                      'type': 'ir.actions.act_window',
                      'res_model': 'my.model',
                      'res_id': self.record_ids.id,
                      'view_mode': 'form',
                      'target': 'current',
                  }
              return {
                  'type': 'ir.actions.act_window',
                  'name': _('Records'),
                  'res_model': 'my.model',
                  'view_mode': 'list,form',
                  'domain': [('id', 'in', self.record_ids.ids)],
                  'context': {'create': False},
              }
      ```
    </example>

    <example id="action_return_types" title="Common action return types">
      ```python
      # Close the wizard dialog
      return {'type': 'ir.actions.act_window_close'}

      # Show a notification then close
      return {
          'type': 'ir.actions.client',
          'tag': 'display_notification',
          'params': {
              'title': _('Success'),
              'message': _('Operation completed for %s records.', len(self.record_ids)),
              'type': 'success',   # success, warning, danger, info
              'sticky': False,
          },
          'next': {'type': 'ir.actions.act_window_close'},
      }

      # Open a specific record
      return {
          'type': 'ir.actions.act_window',
          'res_model': 'my.model',
          'res_id': record.id,
          'view_mode': 'form',
          'target': 'current',
      }

      # Reload the current page
      return {'type': 'ir.actions.client', 'tag': 'reload'}
      ```
    </example>

    <example id="reopen_wizard" title="Reopening wizard (multi-step flow)">
      ```python
      def _reopen(self):
          return {
              'type': 'ir.actions.act_window',
              'res_model': self._name,
              'res_id': self.id,
              'view_mode': 'form',
              'target': 'new',
          }

      def action_next(self):
          self.ensure_one()
          if self.step == 'select':
              if not self.template_id:
                  raise UserError(_("Please select a template."))
              self.step = 'configure'
          return self._reopen()
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG — forgetting ensure_one() on action methods
      def action_confirm(self):
          self.record_id.write({'state': 'confirmed'})  # crashes on multi-record

      # CORRECT
      def action_confirm(self):
          self.ensure_one()
          self.record_id.write({'state': 'confirmed'})
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG — attrs= syntax (removed in v17) -->
      <field name="date" attrs="{'invisible': [('update_date', '=', False)]}"/>

      <!-- CORRECT — inline Python expression -->
      <field name="date" invisible="not update_date"/>
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG — wizard model name contains "wizard"
      class MyModelWizard(models.TransientModel):
          _name = 'my.model.wizard'

      # CORRECT — use base_model.action or base_model.operation pattern
      class MyModelAction(models.TransientModel):
          _name = 'my.model.action'
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG — no security entry; wizard will raise AccessError
      # (ir.model.access.csv missing entry for the TransientModel)

      # CORRECT — always add to ir.model.access.csv
      # access_my_model_action,my.model.action,model_my_model_action,base.group_user,1,1,1,1
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```xml
      <!-- WRONG — tree tag in v18+ (renamed to list) -->
      <field name="view_mode">tree,form</field>

      <!-- CORRECT for v18/v19 -->
      <field name="view_mode">list,form</field>
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # WRONG — browsing active_ids inside __init__ or at field definition time
      record_ids = fields.Many2many(
          comodel_name='my.model',
          default=self.env.context.get('active_ids'),  # self not available here
      )

      # CORRECT — use lambda
      record_ids = fields.Many2many(
          comodel_name='my.model',
          default=lambda self: self.env.context.get('active_ids'),
      )
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # WRONG — f-string in translatable message
      raise UserError(f"Cannot process {self.record_id.name}")

      # CORRECT — use _() with % formatting for translation support
      raise UserError(_("Cannot process %s", self.record_id.name))
      ```
    </antipattern>

  </antipatterns>

</pattern>