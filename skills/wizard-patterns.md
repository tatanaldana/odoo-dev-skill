# Wizard (TransientModel) Patterns — v17/v18/v19

No breaking changes across versions for wizard API.

---

## Basic wizard

```python
class MyModuleAction(models.TransientModel):
    _name = 'my.module.action'
    _description = 'My Action'
    _check_company_auto = True

    record_id = fields.Many2one('my.model', required=True, check_company=True,
        default=lambda self: self.env.context.get('active_id'))
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    date = fields.Date(required=True, default=fields.Date.context_today)

    def action_confirm(self):
        self.ensure_one()
        self.record_id.write({'date': self.date})
        return {'type': 'ir.actions.act_window_close'}
```

## Batch wizard

```python
class BatchAction(models.TransientModel):
    _name = 'my.module.batch.action'
    record_ids = fields.Many2many('my.model', default=lambda self: self.env.context.get('active_ids'))
    new_state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], required=True)

    def action_apply(self):
        self.record_ids.write({'state': self.new_state})
        return {'type': 'ir.actions.act_window_close'}
```

## View + action

```xml
<form string="My Action">
    <group><field name="record_id" readonly="1"/><field name="date"/></group>
    <footer>
        <button name="action_confirm" string="Confirm" type="object" class="oe_highlight"/>
        <button string="Cancel" special="cancel"/>
    </footer>
</form>

<record id="action_my_wizard" model="ir.actions.act_window">
    <field name="res_model">my.module.action</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
    <field name="binding_model_id" ref="model_my_model"/>
</record>
```

## Opening from Python

```python
def action_open_wizard(self):
    self.ensure_one()
    return {'type': 'ir.actions.act_window', 'res_model': 'my.module.action',
        'view_mode': 'form', 'target': 'new',
        'context': {'default_record_id': self.id, 'active_id': self.id}}
```

## Return types

```python
{'type': 'ir.actions.act_window_close'}                    # close
{'type': 'ir.actions.client', 'tag': 'display_notification',
 'params': {'title': 'Done', 'type': 'success'}}           # notification
{'type': 'ir.actions.act_window', 'res_model': 'my.model',
 'res_id': id, 'view_mode': 'form'}                        # open record
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `ensure_one()` on action methods |
| CRITICAL | No `attrs=` in v17+ |
| HIGH | Don't name model with "wizard" — use `base_model.action` |
| HIGH | Always add ir.model.access.csv entry for TransientModel |
| HIGH | v18+: `view_mode` uses `list` not `tree` |
| MEDIUM | Use `lambda self:` for defaults, not direct `self.env` |