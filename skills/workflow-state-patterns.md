# Workflow & State Machine Patterns — v17/v18/v19

---

## Basic state machine

```python
class MyDocument(models.Model):
    _name = 'my.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(required=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('done', 'Done'), ('cancel', 'Cancelled'),
    ], default='draft', required=True, tracking=True)

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Only draft documents can be confirmed.")
            record.state = 'confirmed'

    def action_done(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError("Only confirmed documents can be done.")
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            if record.state == 'done':
                raise UserError("Cannot cancel completed documents.")
            record.state = 'cancel'

    def action_draft(self):
        for record in self:
            if record.state != 'cancel':
                raise UserError("Only cancelled can be reset.")
            record.state = 'draft'
```

## Statusbar view

```xml
<header>
    <button name="action_confirm" string="Confirm" type="object"
            class="oe_highlight" invisible="state != 'draft'"/>
    <button name="action_done" string="Done" type="object"
            class="oe_highlight" invisible="state != 'confirmed'"/>
    <button name="action_cancel" string="Cancel" type="object"
            invisible="state in ('done', 'cancel')"/>
    <button name="action_draft" string="Reset" type="object"
            invisible="state != 'cancel'"/>
    <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
</header>
```

## Multi-level approval

```python
class ApprovalDocument(models.Model):
    _name = 'approval.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'), ('submitted', 'Submitted'),
        ('first_approval', 'First Approval'), ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)
    submitted_by = fields.Many2one('res.users', readonly=True)
    first_approver_id = fields.Many2one('res.users', readonly=True)

    def action_submit(self):
        self.ensure_one()
        self.write({'state': 'submitted', 'submitted_by': self.env.uid})
        self._notify_approvers()

    def action_first_approve(self):
        self.ensure_one()
        if not self.env.user.has_group('my_module.group_first_approver'):
            raise AccessError("No approval rights.")
        self.write({'state': 'first_approval', 'first_approver_id': self.env.uid})
```

## Stage-based kanban

```python
class Task(models.Model):
    _name = 'my.task'
    stage_id = fields.Many2one('my.task.stage', group_expand='_read_group_stage_ids',
        tracking=True, default=lambda self: self.env['my.task.stage'].search([], limit=1))
    state = fields.Selection(related='stage_id.state', store=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['my.task.stage'].search([])

class TaskStage(models.Model):
    _name = 'my.task.stage'
    _order = 'sequence, id'
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('done', 'Done')])
```

## Cron state transition

```python
@api.model
def _cron_check_expiry(self):
    self.search([('state', '=', 'active'), ('expiry_date', '<', fields.Date.today())]).write({'state': 'expired'})
```

```xml
<record id="ir_cron_expiry" model="ir.cron">
    <field name="name">Check Expiry</field>
    <field name="model_id" ref="model_auto_close_document"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_expiry()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `attrs=` in v17+ |
| CRITICAL | v18+: `<tree>` → `<list>`, `oe_chatter` → `<chatter/>` |
| HIGH | Always guard state transitions (check current state before writing) |
| HIGH | `tracking=True` without `mail.thread` inheritance has no effect |
| MEDIUM | Don't use `ensure_one()` on multi-record action methods — iterate instead |