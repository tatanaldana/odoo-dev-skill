# Odoo 18.0 Model Patterns

Verified against account.move.line and account.move views (addons/account).

---

## Key v18 breaking changes from v17

| Change | v17 | v18 |
|--------|-----|-----|
| Field aggregation | `group_operator='min'` | `aggregator='min'` |
| List view tag | `<tree>` | `<list>` |
| Chatter | `<div class="oe_chatter">` + 3 fields | `<chatter/>` (bare tag dominant; `reload_on_attachment="True"` where needed) |
| SQL import | `from odoo.tools.sql import SQL` | same (changes in v19) |

## Carried from v17

- `@api.model_create_multi` mandatory
- `_check_company_auto = True` + `check_company=True`
- `invisible=`/`readonly=`/`required=` — no `attrs=`
- Type hints recommended but not mandatory

---

## Full model skeleton

```python
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.sql import SQL
import logging

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my_module.my_model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    name = fields.Char(required=True, index='trigram', tracking=True)
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('done', 'Done'), ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True, copy=False)

    company_id = fields.Many2one(comodel_name='res.company', required=True,
        default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one(comodel_name='res.partner', tracking=True, check_company=True)
    user_id = fields.Many2one(comodel_name='res.users',
        default=lambda self: self.env.user, tracking=True)
    line_ids = fields.One2many(comodel_name='my_module.my_model.line',
        inverse_name='parent_id', copy=True)
    currency_id = fields.Many2one(comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id, required=True)
    amount = fields.Monetary(currency_field='currency_id')

    # v18: aggregator= replaces group_operator=
    date_min = fields.Date(related='line_ids.date', aggregator='min', store=True)

    total_amount = fields.Float(compute='_compute_total_amount', store=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ]

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('my_module.my_model') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("Cannot delete confirmed records."))
        return super().unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault('name', _("%s (Copy)", self.name))
        return super().copy(default)

    def action_confirm(self):
        self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

    def action_done(self):
        self.filtered(lambda r: r.state == 'confirmed').write({'state': 'done'})

    def action_cancel(self):
        self.filtered(lambda r: r.state not in ('done', 'cancelled')).write({'state': 'cancelled'})

    def action_view_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': _('Lines'),
            'res_model': 'my_module.my_model.line', 'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id)],
        }
```

## Line model

```python
class MyModelLine(models.Model):
    _name = 'my_module.my_model.line'
    _description = 'My Model Line'
    _order = 'sequence, id'
    _check_company_auto = True

    parent_id = fields.Many2one(comodel_name='my_module.my_model',
        required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='parent_id.company_id', store=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float()
    amount = fields.Float(compute='_compute_amount', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit
```

## Wizard

```python
class MyWizard(models.TransientModel):
    _name = 'my_module.wizard'
    _description = 'My Wizard'

    def _default_record_ids(self):
        return self.env['my_module.my_model'].browse(self._context.get('active_ids', []))

    record_ids = fields.Many2many(comodel_name='my_module.my_model', default=_default_record_ids)
    date = fields.Date(default=fields.Date.context_today, required=True)

    def action_confirm(self):
        self.ensure_one()
        self.record_ids.write({'state': 'confirmed'})
        return {'type': 'ir.actions.act_window_close'}
```

---

## XML views (v18 syntax)

```xml
<!-- Form: <list> inside O2M, <chatter/> at bottom -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                class="btn-primary" invisible="state != 'draft'"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <group>
            <group><field name="partner_id"/><field name="user_id"/></group>
            <group><field name="company_id" groups="base.group_multi_company"/></group>
        </group>
        <notebook>
            <page string="Lines">
                <field name="line_ids" readonly="state == 'done'">
                    <list editable="bottom">
                        <field name="sequence" widget="handle"/><field name="name"/>
                        <field name="quantity"/><field name="price_unit"/>
                        <field name="amount" sum="Total"/>
                    </list>
                </field>
            </page>
        </notebook>
    </sheet>
    <chatter/>
</form>

<!-- List (v18: <list> not <tree>) -->
<list decoration-danger="state == 'cancelled'">
    <field name="name"/><field name="partner_id"/><field name="total_amount" sum="Total"/>
    <field name="state" widget="badge"/>
</list>
```

## Command class reference

```python
record.write({'line_ids': [
    Command.create({'name': 'New'}),    Command.update(id, {'qty': 2}),
    Command.delete(id),                 Command.unlink(id),
    Command.link(id),                   Command.clear(),
    Command.set([id1, id2]),
]})
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `group_operator=` → `aggregator=` in v18 |
| CRITICAL | `<tree>` → `<list>` in v18 |
| CRITICAL | `<div class="oe_chatter">` → `<chatter/>` in v18 |
| CRITICAL | `@api.model_create_multi` mandatory |
| HIGH | SQL import: `from odoo.tools.sql import SQL` (changes to `odoo.tools` in v19) |
| HIGH | No raw `(0,0,{})` tuples — use `Command` class |
| HIGH | `unlink()` must guard states |