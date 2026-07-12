# Odoo 19.0 Model Patterns

Verified against account.move.line (addons/account).

---

## Key v19 changes from v18

| Change | v18 | v19 |
|--------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name_uniq = models.Constraint('unique(name)', 'msg')` |
| Indexes | manual | `_my_idx = models.Index("(col1, col2)")` |
| Domain class | not available | `from odoo.fields import Command, Domain` |
| M2O bypass | not available | `bypass_search_access=True` |
| SQL import | `from odoo.tools.sql import SQL` | `from odoo.tools import SQL` |
| `aggregator=` | same as v18 | same |
| Chatter | `<chatter/>` | same |
| Type hints | recommended | ORM-core convention, NOT mandatory in addon code |

---

## v19-specific patterns

```python
# Constraints — class attributes (replaces _sql_constraints)
_name_company_uniq = models.Constraint('unique(company_id, name)', 'Name must be unique!')
_check_positive = models.Constraint('CHECK(amount >= 0)', 'Amount must be positive!')

# Indexes — class attributes
_partner_date_idx = models.Index("(partner_id, date)")
_date_desc_idx = models.Index("(date desc, name desc, id)")
_unreconciled_idx = models.Index("(account_id, partner_id) WHERE reconciled IS NOT TRUE")

# Domain class
from odoo.fields import Command, Domain
combined = Domain.OR([domain_a, domain_b])

# bypass_search_access on M2O
move_id = fields.Many2one(comodel_name='account.move', bypass_search_access=True,
    ondelete='cascade', index=True, check_company=True)

# SQL import path changed
from odoo.tools import SQL  # NOT odoo.tools.sql
```

---

## Full model skeleton

```python
from odoo import api, fields, models, _
from odoo.fields import Command, Domain
from odoo.exceptions import UserError, ValidationError
from odoo.tools import SQL
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
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('done', 'Done'), ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    date = fields.Date(default=fields.Date.context_today, aggregator='min')

    company_id = fields.Many2one(comodel_name='res.company', required=True,
        default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one(comodel_name='res.partner', tracking=True, check_company=True)
    parent_id = fields.Many2one(comodel_name='my.model.parent',
        bypass_search_access=True, ondelete='cascade', index=True, check_company=True)
    line_ids = fields.One2many(comodel_name='my.model.line', inverse_name='model_id', copy=True)
    currency_id = fields.Many2one(comodel_name='res.currency', related='company_id.currency_id')

    total_amount = fields.Monetary(compute='_compute_total', store=True, currency_field='currency_id')
    line_count = fields.Integer(compute='_compute_line_count')

    # v19 constraints
    _name_company_uniq = models.Constraint('unique(company_id, name)', 'Name must be unique!')
    _check_positive_amount = models.Constraint('CHECK(total_amount >= 0)', 'Cannot be negative!')

    # v19 indexes
    _partner_date_idx = models.Index("(partner_id, date)")
    _active_state_idx = models.Index("(state) WHERE active IS TRUE")

    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

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

    def action_confirm(self):
        for record in self.filtered(lambda r: r.state == 'draft'):
            if not record.line_ids:
                raise UserError(_("Add at least one line to confirm '%s'.") % record.name)
        self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

    def action_done(self):
        self.filtered(lambda r: r.state == 'confirmed').write({'state': 'done'})

    def action_cancel(self):
        self.filtered(lambda r: r.state not in ('done', 'cancelled')).write({'state': 'cancelled'})

    def action_view_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window', 'name': _('Lines'),
            'res_model': 'my.model.line', 'view_mode': 'list,form',
            'domain': [('model_id', '=', self.id)],
        }

    def _get_summary_data(self):
        query = SQL("""
            SELECT state, COUNT(*) AS count, SUM(total_amount) AS total
            FROM %s WHERE company_id = %s GROUP BY state
        """, SQL.identifier(self._table), self.env.company.id)
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
```

---

## XML views (v19 — same as v18: `<list>`, `<chatter/>`)

```xml
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
        <group>
            <group><field name="partner_id"/><field name="user_id"/></group>
            <group><field name="date"/><field name="company_id" groups="base.group_multi_company"/></group>
        </group>
        <notebook>
            <page string="Lines">
                <field name="line_ids" readonly="state == 'done'">
                    <list editable="bottom">
                        <field name="sequence" widget="handle"/><field name="name"/>
                        <field name="amount" sum="Total"/>
                    </list>
                </field>
            </page>
        </notebook>
    </sheet>
    <chatter/>
</form>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `_sql_constraints` → `models.Constraint()` in v19 |
| CRITICAL | SQL import: `from odoo.tools import SQL` (not `odoo.tools.sql`) |
| CRITICAL | No SQL injection — never string format with user input |
| CRITICAL | `@api.model_create_multi` mandatory |
| CRITICAL | Type hints NOT mandatory in addon code (only 2/3700 lines in account.move.line use them) |
| HIGH | `unlink()` must guard states |
| HIGH | `<div class="oe_chatter">` → `<chatter/>` |