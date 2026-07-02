<pattern>

  <description>
    State machine and workflow patterns for Odoo models across versions 17, 18 and 19.
    Covers Selection-based state fields, action_* transition methods, statusbar widgets,
    mail.thread tracking, activity scheduling, stage-based (kanban) workflows, and
    scheduled state transitions via cron jobs.
    Use when modeling any business process with defined states and transitions.
  </description>

  <version_notes>
    <version id="17">
      attrs= removed — use invisible=, readonly=, required= directly on XML elements.
      Chatter: oe_chatter div block (confirmed project_task_views_17.xml line 479).
      &lt;tree&gt; tag for list views.
      state field on project.task is a computed field with inverse (_compute_state,
      _inverse_state) — derived from stage_id and blocking dependencies.
      tracking=True on Selection fields logs changes in the chatter when the model
      inherits mail.thread.
    </version>
    <version id="18">
      &lt;tree&gt; replaced by &lt;list&gt; — breaking change.
      Chatter: &lt;chatter reload_on_follower="True"/&gt; (confirmed project_task_views_18.xml line 587).
      aggregator= replaces group_operator= on fields — breaking change.
      export_string_translation=False available on string fields.
    </version>
    <version id="19">
      Identical chatter and list syntax to v18 (confirmed project_task_views_19.xml line 589).
      models.Constraint() replaces _sql_constraints for CHECK constraints.
      models.Index() replaces manual index definitions.
      SQL import path changed: from odoo.tools import SQL.
    </version>
  </version_notes>

  <examples>

    <example id="basic_state_machine" title="Basic state machine — Python">
      ```python
      from odoo import api, fields, models
      from odoo.exceptions import UserError


      class MyDocument(models.Model):
          _name = 'my.document'
          _description = 'My Document'

          name = fields.Char(required=True)
          state = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('done', 'Done'),
              ('cancel', 'Cancelled'),
          ], string='Status', default='draft', required=True, tracking=True)

          def action_confirm(self):
              for record in self:
                  if record.state != 'draft':
                      raise UserError("Only draft documents can be confirmed.")
                  record.state = 'confirmed'

          def action_done(self):
              for record in self:
                  if record.state != 'confirmed':
                      raise UserError("Only confirmed documents can be marked done.")
                  record.state = 'done'

          def action_cancel(self):
              for record in self:
                  if record.state == 'done':
                      raise UserError("Cannot cancel completed documents.")
                  record.state = 'cancel'

          def action_draft(self):
              for record in self:
                  if record.state != 'cancel':
                      raise UserError("Only cancelled documents can be reset to draft.")
                  record.state = 'draft'
      ```
    </example>

    <example id="statusbar_view_v17" title="Form view with statusbar — v17">
      ```xml
      <form>
          <header>
              <button name="action_confirm" string="Confirm"
                      type="object" invisible="state != 'draft'"
                      class="oe_highlight"/>
              <button name="action_done" string="Mark Done"
                      type="object" invisible="state != 'confirmed'"
                      class="oe_highlight"/>
              <button name="action_cancel" string="Cancel"
                      type="object" invisible="state in ['done', 'cancel']"/>
              <button name="action_draft" string="Reset to Draft"
                      type="object" invisible="state != 'cancel'"/>
              <field name="state" widget="statusbar"
                     statusbar_visible="draft,confirmed,done"/>
          </header>
          <sheet>
              <group>
                  <field name="name" readonly="state != 'draft'"/>
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

    <example id="statusbar_view_v18_v19" title="Form view with statusbar — v18/v19">
      ```xml
      <form>
          <header>
              <button name="action_confirm" string="Confirm"
                      type="object" invisible="state != 'draft'"
                      class="oe_highlight"/>
              <button name="action_done" string="Mark Done"
                      type="object" invisible="state != 'confirmed'"
                      class="oe_highlight"/>
              <button name="action_cancel" string="Cancel"
                      type="object" invisible="state in ['done', 'cancel']"/>
              <button name="action_draft" string="Reset to Draft"
                      type="object" invisible="state != 'cancel'"/>
              <field name="state" widget="statusbar"
                     statusbar_visible="draft,confirmed,done"/>
          </header>
          <sheet>
              <group>
                  <field name="name" readonly="state != 'draft'"/>
              </group>
          </sheet>
          <!-- v18/v19: <chatter/> tag replaces oe_chatter div -->
          <chatter reload_on_follower="True"/>
      </form>
      ```
    </example>

    <example id="mail_thread_tracking" title="State tracking with mail.thread">
      ```python
      class TrackedDocument(models.Model):
          _name = 'tracked.document'
          _inherit = ['mail.thread', 'mail.activity.mixin']

          name = fields.Char()
          state = fields.Selection([
              ('draft', 'Draft'),
              ('confirmed', 'Confirmed'),
              ('done', 'Done'),
          ], default='draft', tracking=True)

          def action_confirm(self):
              for record in self:
                  record.state = 'confirmed'
                  record.message_post(
                      body="Document confirmed.",
                      subtype_xmlid='mail.mt_note',
                  )
      ```
    </example>

    <example id="activity_scheduling" title="Activity scheduling on state transition">
      ```python
      def action_submit_for_approval(self):
          self.ensure_one()
          self.state = 'pending_approval'

          approver = self._get_approver()
          self.activity_schedule(
              'mail.mail_activity_data_todo',
              user_id=approver.id,
              summary='Approval Required',
              note='Please review and approve: %s' % self.name,
          )
      ```
    </example>

    <example id="approval_workflow" title="Multi-level approval workflow">
      ```python
      class ApprovalDocument(models.Model):
          _name = 'approval.document'
          _inherit = ['mail.thread', 'mail.activity.mixin']

          name = fields.Char(required=True)
          amount = fields.Float()
          state = fields.Selection([
              ('draft', 'Draft'),
              ('submitted', 'Submitted'),
              ('first_approval', 'First Approval'),
              ('approved', 'Approved'),
              ('rejected', 'Rejected'),
          ], default='draft', tracking=True)

          submitted_by = fields.Many2one(comodel_name='res.users', readonly=True)
          submitted_date = fields.Datetime(readonly=True)
          first_approver_id = fields.Many2one(comodel_name='res.users', readonly=True)
          rejection_reason = fields.Text()

          def action_submit(self):
              self.ensure_one()
              if self.state != 'draft':
                  raise UserError("Document must be in draft state.")
              self.write({
                  'state': 'submitted',
                  'submitted_by': self.env.uid,
                  'submitted_date': fields.Datetime.now(),
              })
              self._notify_approvers()

          def action_first_approve(self):
              self.ensure_one()
              if not self.env.user.has_group('my_module.group_first_approver'):
                  raise AccessError("You do not have approval rights.")
              self.write({
                  'state': 'first_approval',
                  'first_approver_id': self.env.uid,
              })

          def action_approve(self):
              self.ensure_one()
              self.write({'state': 'approved'})

          def action_reject(self):
              self.ensure_one()
              if not self.rejection_reason:
                  raise UserError("Please provide a rejection reason.")
              self.write({'state': 'rejected'})
      ```
    </example>

    <example id="stage_based_kanban" title="Stage-based kanban workflow">
      ```python
      class Task(models.Model):
          _name = 'my.task'

          name = fields.Char(required=True)
          stage_id = fields.Many2one(
              comodel_name='my.task.stage',
              string='Stage',
              group_expand='_read_group_stage_ids',
              tracking=True,
              default=lambda self: self._get_default_stage(),
          )
          state = fields.Selection(related='stage_id.state', store=True)

          def _get_default_stage(self):
              return self.env['my.task.stage'].search([], limit=1)

          @api.model
          def _read_group_stage_ids(self, stages, domain, order):
              return self.env['my.task.stage'].search([])


      class TaskStage(models.Model):
          _name = 'my.task.stage'
          _order = 'sequence, id'

          name = fields.Char(required=True)
          sequence = fields.Integer(default=10)
          fold = fields.Boolean(string='Folded in Kanban')
          state = fields.Selection([
              ('draft', 'Draft'),
              ('in_progress', 'In Progress'),
              ('done', 'Done'),
          ], default='draft')
          is_closed = fields.Boolean(string='Closing Stage')
      ```
    </example>

    <example id="cron_state_transition" title="Scheduled state transition via cron">
      ```python
      class AutoCloseDocument(models.Model):
          _name = 'auto.close.document'

          state = fields.Selection([
              ('active', 'Active'),
              ('expired', 'Expired'),
          ], default='active')
          expiry_date = fields.Date()

          @api.model
          def _cron_check_expiry(self):
              expired = self.search([
                  ('state', '=', 'active'),
                  ('expiry_date', '<', fields.Date.today()),
              ])
              expired.write({'state': 'expired'})
      ```

      ```xml
      <record id="ir_cron_check_document_expiry" model="ir.cron">
          <field name="name">Check Document Expiry</field>
          <field name="model_id" ref="model_auto_close_document"/>
          <field name="state">code</field>
          <field name="code">model._cron_check_expiry()</field>
          <field name="interval_number">1</field>
          <field name="interval_type">days</field>
          <field name="numbercall">-1</field>
      </record>
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- v17+: attrs= was removed; this breaks at runtime -->
      <field name="name" attrs="{'readonly': [('state', '!=', 'draft')]}"/>

      <!-- Fix for v17/v18/v19 -->
      <field name="name" readonly="state != 'draft'"/>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- v18/v19: <tree> was renamed to <list> -->
      <field name="line_ids">
          <tree editable="bottom">
              <field name="product_id"/>
          </tree>
      </field>

      <!-- Fix for v18/v19 -->
      <field name="line_ids">
          <list editable="bottom">
              <field name="product_id"/>
          </list>
      </field>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- v18/v19: oe_chatter div block no longer valid -->
      <div class="oe_chatter">
          <field name="message_follower_ids"/>
          <field name="activity_ids"/>
          <field name="message_ids"/>
      </div>

      <!-- Fix for v18/v19 -->
      <chatter reload_on_follower="True"/>
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Transition without state guard — allows invalid transitions
      def action_confirm(self):
          self.state = 'confirmed'   # no check on current state

      # Fix: always guard transitions
      def action_confirm(self):
          for record in self:
              if record.state != 'draft':
                  raise UserError("Only draft documents can be confirmed.")
              record.state = 'confirmed'
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Using tracking=True without inheriting mail.thread
      # The field will store tracking=True but no chatter messages are created
      class MyModel(models.Model):
          _name = 'my.model'
          # missing: _inherit = ['mail.thread', 'mail.activity.mixin']

          state = fields.Selection([...], tracking=True)  # silent — no effect
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # action_* method on a multi-record set without iterating
      def action_confirm(self):
          self.ensure_one()          # raises if called on multiple records
          self.state = 'confirmed'

      # Fix: iterate or remove ensure_one() depending on intent
      def action_confirm(self):
          for record in self:
              if record.state != 'draft':
                  raise UserError("Only draft records can be confirmed.")
              record.state = 'confirmed'
      ```
    </antipattern>

  </antipatterns>

</pattern>