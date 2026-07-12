# Odoo 17.0 Model Patterns

Verified against account.move.line (addons/account).

---

## Key v17 breaking changes from v16

- `attrs=` removed from views — use `invisible=`/`readonly=`/`required=` as Python expressions
- `@api.model_create_multi` mandatory for all `create()` overrides

## v17 features

- `index='trigram'`, `index='btree'`, `index='btree_not_null'` on fields
- `Command` class for x2many (mandatory convention)
- `_check_company_auto = True` + `check_company=True` on relational fields
- `SQL()` via `from odoo.tools.sql import SQL`
- `group_operator=` on fields (renamed to `aggregator=` in v18)
- Chatter: `<div class="oe_chatter">` with child fields
- List views: `<tree>` tag (renamed to `<list>` in v18)

---

## Full model skeleton

```python
from odoo import api, fields, models, Command, _
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

    # === FIELDS === #
    name = fields.Char(required=True, index='trigram', tracking=True)
    code = fields.Char(index=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('done', 'Done'), ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    date = fields.Date(default=fields.Date.context_today)

    # === RELATIONAL === #
    company_id = fields.Many2one(comodel_name='res.company', required=True,
        default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one(comodel_name='res.partner', tracking=True,
        check_company=True)
    user_id = fields.Many2one(comodel_name='res.users',
        default=lambda self: self.env.user, tracking=True)
    parent_id = fields.Many2one(comodel_name='my.model.parent',
        required=True, ondelete='cascade', index=True, check_company=True)
    line_ids = fields.One2many(comodel_name='my.model.line',
        inverse_name='model_id', copy=True)
    tag_ids = fields.Many2many(comodel_name='my.model.tag')
    currency_id = fields.Many2one(comodel_name='res.currency',
        related='company_id.currency_id')

    # === COMPUTED === #
    total_amount = fields.Monetary(compute='_compute_total', store=True,
        currency_field='currency_id')
    line_count = fields.Integer(compute='_compute_line_count')

    # === CONSTRAINTS (v17 style) === #
    _sql_constraints = [
        ('name_company_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ]

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    # === CRUD === #
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
                    raise UserError(_("Record '%s' must have at least one line.") % record.name)
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancelled'):
                raise UserError(_("Cannot delete '%s' in state '%s'.") % (record.name, record.state))
        return super().unlink()

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        default['state'] = 'draft'
        return super().copy(default)

    # === ACTIONS === #
    def action_confirm(self):
        for record in self.filtered(lambda r: r.state == 'draft'):
            if not record.line_ids:
                raise UserError(_("Add at least one line to confirm '%s'.") % record.name)
        self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

    def action_done(self):
        self.filtered(lambda r: r.state == 'confirmed').write({'state': 'done'})

    def action_cancel(self):
        self.filtered(lambda r: r.state not in ('done', 'cancelled')).write({'state': 'cancelled'})

    def action_draft(self):
        self.filtered(lambda r: r.state == 'cancelled').write({'state': 'draft'})

    def action_view_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': _('Lines'),
            'res_model': 'my.model.line', 'view_mode': 'tree,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'default_model_id': self.id},
        }
```

---

## XML views (v17 syntax)

```xml
<!-- Form: invisible= as Python expr, no attrs=. Chatter: oe_chatter div -->
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                class="btn-primary" invisible="state != 'draft'"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button name="action_view_lines" type="object"
                    class="oe_stat_button" icon="fa-list" invisible="line_count == 0">
                <field name="line_count" widget="statinfo" string="Lines"/>
            </button>
        </div>
        <div class="oe_title"><h1><field name="name" readonly="state == 'done'"/></h1></div>
        <group>
            <group><field name="partner_id"/><field name="user_id"/></group>
            <group><field name="date"/><field name="company_id" groups="base.group_multi_company"/></group>
        </group>
        <notebook>
            <page string="Lines">
                <field name="line_ids" readonly="state == 'done'">
                    <tree editable="bottom">
                        <field name="sequence" widget="handle"/><field name="name"/>
                        <field name="quantity"/><field name="price_unit"/>
                        <field name="amount" sum="Total"/>
                    </tree>
                </field>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/><field name="activity_ids"/><field name="message_ids"/>
    </div>
</form>

<!-- Tree (v17 uses <tree>, renamed to <list> in v18) -->
<tree decoration-danger="state == 'cancelled'" decoration-success="state == 'done'">
    <field name="name"/><field name="partner_id"/><field name="total_amount" sum="Total"/>
    <field name="state" widget="badge"/>
</tree>

<!-- Search -->
<search>
    <field name="name"/><field name="partner_id"/>
    <filter name="filter_my" string="My Records" domain="[('user_id', '=', uid)]"/>
    <filter name="filter_draft" string="Draft" domain="[('state', '=', 'draft')]"/>
    <group expand="0" string="Group By">
        <filter name="groupby_state" string="State" context="{'group_by': 'state'}"/>
    </group>
</search>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `attrs=` in views — crashes in v17 |
| CRITICAL | `@api.model_create_multi` mandatory on `create()` |
| HIGH | `unlink()` must guard against non-draft states |
| HIGH | `self.ensure_one()` before single-record ops (`copy`, `action_view_*`) |
| MEDIUM | Use `Command.create()`/`.update()` — not raw `(0,0,{})` tuples |
| MEDIUM | Use `comodel_name=` kwarg — not positional string |