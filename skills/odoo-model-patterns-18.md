# Odoo 18.0 Model Patterns

<pattern>

<description>
  Model patterns for Odoo 18.0. Key breaking change from v17: `group_operator=` renamed to
  `aggregator=` on field definitions. Key new syntax: `<tree>` tag renamed to `<list>` in XML
  views, and chatter replaced by `<chatter reload_on_attachment="True"/>`. Type hints recommended.
  Use this file when the target version is 18.0.

  Verified against real Odoo 18.0 source: account.move.line (addons/account) and
  account.move views (addons/account).
</description>

<version_notes>
  <version id="18">
    <change type="breaking">group_operator= renamed to aggregator= on field definitions — confirmed in model_18.py (lines 73, 78, 253, 409 use aggregator=; model_17.py uses group_operator=)</change>
    <change type="breaking">XML list view tag renamed from &lt;tree&gt; to &lt;list&gt; — confirmed in views_18.xml</change>
    <change type="breaking">Chatter syntax changed: &lt;div class="oe_chatter"&gt; with three child fields replaced by &lt;chatter reload_on_attachment="True"/&gt; — confirmed in views_18.xml line 1507</change>
    <change type="feature">@api.model_create_multi mandatory for all create() overrides — same as v17</change>
    <change type="feature">_check_company_auto = True and check_company=True — present since v17, canonical pattern in v18</change>
    <change type="recommended">Type hints on method signatures — recommended in v18, not mandatory</change>
    <change type="recommended">SQL() builder for raw SQL — available since v17, recommended convention in v18</change>
  </version>
</version_notes>

<examples>

  <example id="breaking_aggregator" title="BREAKING: group_operator renamed to aggregator">

```python
# v17 — group_operator=
date = fields.Date(
    related='move_id.date',
    store=True,
    group_operator='min',
)
amount_currency = fields.Monetary(
    group_operator=None,
)

# v18 — aggregator= (confirmed in model_18.py lines 73, 253)
date = fields.Date(
    related='move_id.date',
    store=True,
    aggregator='min',
)
amount_currency = fields.Monetary(
    aggregator=None,
)
```

  </example>

  <example id="breaking_list_tag" title="BREAKING: &lt;tree&gt; renamed to &lt;list&gt; in views">

```xml
<!-- v17 -->
<tree decoration-danger="state == 'cancelled'">
    <field name="name"/>
    <field name="state" widget="badge"/>
</tree>

<!-- v18 — confirmed in views_18.xml -->
<list decoration-danger="state == 'cancelled'">
    <field name="name"/>
    <field name="state" widget="badge"/>
</list>
```

  </example>

  <example id="breaking_chatter" title="BREAKING: chatter syntax changed">

```xml
<!-- v17 — three explicit fields inside div -->
<div class="oe_chatter">
    <field name="message_follower_ids" groups="base.group_user"/>
    <field name="activity_ids"/>
    <field name="message_ids" options="{'post_refresh': 'always'}"/>
</div>

<!-- v18 — single self-closing tag (confirmed in views_18.xml line 1507) -->
<chatter reload_on_attachment="True"/>
```

  </example>

  <example id="model_definition" title="Full model definition — v18 patterns">

```python
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.sql import SQL  # confirmed import path in model_18.py line 11


class MyModel(models.Model):
    _name = 'my_module.my_model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    # === BASIC FIELDS === #
    name = fields.Char(
        string='Name',
        required=True,
        index='trigram',
        tracking=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    # === RELATIONAL FIELDS === #
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        tracking=True,
        check_company=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        default=lambda self: self.env.user,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name='my_module.my_model.line',
        inverse_name='parent_id',
        copy=True,
    )
    tag_ids = fields.Many2many(comodel_name='my_module.tag')

    # === MONETARY FIELDS === #
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    amount = fields.Monetary(currency_field='currency_id')

    # === COMPUTED FIELDS === #
    total_amount = fields.Float(
        compute='_compute_total_amount',
        store=True,
    )

    # v18: aggregator= replaces group_operator=
    date_min = fields.Date(
        related='line_ids.date',
        aggregator='min',
        store=True,
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self) -> None:
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CONSTRAINTS === #
    @api.constrains('amount')
    def _check_amount(self) -> None:
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("Amount must be positive."))

    _sql_constraints = [
        ('name_company_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ]

    # === CRUD METHODS === #
    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> 'MyModel':
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'my_module.my_model'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals: dict) -> bool:
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self) -> bool:
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("Cannot delete confirmed records."))
        return super().unlink()

    def copy(self, default: dict | None = None) -> 'MyModel':
        default = dict(default or {})
        default.setdefault('name', _("%s (Copy)", self.name))
        return super().copy(default)

    # === ACTION METHODS === #
    def action_confirm(self) -> None:
        self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

    def action_done(self) -> None:
        self.filtered(lambda r: r.state == 'confirmed').write({'state': 'done'})

    def action_cancel(self) -> None:
        self.filtered(lambda r: r.state not in ('done', 'cancelled')).write({'state': 'cancelled'})

    def action_draft(self) -> None:
        self.filtered(lambda r: r.state == 'cancelled').write({'state': 'draft'})

    def action_view_lines(self) -> dict:
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lines'),
            'res_model': 'my_module.my_model.line',
            'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id},
        }

    # === SQL PATTERN === #
    def _get_report_data(self) -> list[dict]:
        query = SQL(
            """
            SELECT m.id, m.name, SUM(l.amount) AS total
            FROM %s m
            LEFT JOIN %s l ON l.parent_id = m.id
            WHERE m.company_id IN %s
              AND m.state = %s
            GROUP BY m.id, m.name
            ORDER BY m.create_date DESC
            """,
            SQL.identifier(self._table),
            SQL.identifier('my_module_my_model_line'),
            tuple(self.env.companies.ids),
            'confirmed',
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
```

  </example>

  <example id="line_model" title="Line model — v18">

```python
class MyModelLine(models.Model):
    _name = 'my_module.my_model.line'
    _description = 'My Model Line'
    _order = 'sequence, id'
    _check_company_auto = True

    parent_id = fields.Many2one(
        comodel_name='my_module.my_model',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='parent_id.company_id',
        store=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Description', required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        check_company=True,
    )
    quantity = fields.Float(default=1.0)
    price_unit = fields.Float(string='Unit Price')
    amount = fields.Float(
        compute='_compute_amount',
        store=True,
    )

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self) -> None:
        for line in self:
            line.amount = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self) -> None:
        if self.product_id:
            self.name = self.product_id.display_name
            self.price_unit = self.product_id.lst_price
```

  </example>

  <example id="xml_views" title="XML views — form with &lt;list&gt; and &lt;chatter&gt; (v18 verified syntax)">

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View — note <chatter reload_on_attachment="True"/> replacing oe_chatter div -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my_module.my_model.form</field>
        <field name="model">my_module.my_model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" type="object"
                            string="Confirm" class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" type="object"
                            string="Mark Done"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" type="object"
                            string="Cancel"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" type="object"
                            string="Reset to Draft"
                            invisible="state != 'cancelled'"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box">
                        <button name="action_view_lines" type="object"
                                class="oe_stat_button" icon="fa-list">
                            <field name="total_amount" widget="statinfo" string="Total"/>
                        </button>
                    </div>
                    <widget name="web_ribbon" title="Archived" invisible="active"/>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name" placeholder="Enter name..."
                                   readonly="state != 'draft'"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id" readonly="state != 'draft'"/>
                            <field name="user_id"/>
                            <field name="currency_id" groups="base.group_multi_currency"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="amount"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids" readonly="state == 'done'">
                                <!-- v18: <list> replaces <tree> inside One2many -->
                                <list editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="product_id"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount" sum="Total"/>
                                </list>
                            </field>
                        </page>
                        <page string="Tags" name="tags">
                            <field name="tag_ids" widget="many2many_tags"/>
                        </page>
                    </notebook>
                </sheet>
                <!-- v18: replaces <div class="oe_chatter"> block -->
                <chatter reload_on_attachment="True"/>
            </form>
        </field>
    </record>

    <!-- List View — v18: <list> tag -->
    <record id="view_my_model_list" model="ir.ui.view">
        <field name="name">my_module.my_model.list</field>
        <field name="model">my_module.my_model</field>
        <field name="arch" type="xml">
            <list decoration-danger="state == 'cancelled'"
                  decoration-success="state == 'done'">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="total_amount" sum="Total"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-info="state == 'confirmed'"
                       decoration-danger="state == 'cancelled'"/>
                <field name="company_id" groups="base.group_multi_company" optional="hide"/>
            </list>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_my_model_search" model="ir.ui.view">
        <field name="name">my_module.my_model.search</field>
        <field name="model">my_module.my_model</field>
        <field name="arch" type="xml">
            <search>
                <field name="name"/>
                <field name="partner_id"/>
                <separator/>
                <filter name="filter_my" string="My Records"
                        domain="[('user_id', '=', uid)]"/>
                <filter name="filter_draft" string="Draft"
                        domain="[('state', '=', 'draft')]"/>
                <filter name="filter_done" string="Done"
                        domain="[('state', '=', 'done')]"/>
                <group expand="0" string="Group By">
                    <filter name="groupby_state" string="State"
                            context="{'group_by': 'state'}"/>
                    <filter name="groupby_partner" string="Partner"
                            context="{'group_by': 'partner_id'}"/>
                </group>
            </search>
        </field>
    </record>
</odoo>
```

  </example>

  <example id="wizard" title="Transient model (wizard)">

```python
class MyWizard(models.TransientModel):
    _name = 'my_module.wizard'
    _description = 'My Wizard'

    def _default_record_ids(self):
        return self.env['my_module.my_model'].browse(
            self._context.get('active_ids', [])
        )

    record_ids = fields.Many2many(
        comodel_name='my_module.my_model',
        default=_default_record_ids,
    )
    date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )
    note = fields.Text()

    def action_confirm(self) -> dict:
        self.ensure_one()
        self.record_ids.write({'state': 'confirmed'})
        return {'type': 'ir.actions.act_window_close'}
```

  </example>

  <example id="command_class" title="Command class — x2many operations reference">

```python
# All x2many write operations use Command class (never raw tuples)
record.write({
    'line_ids': [
        Command.create({'name': 'New Line', 'quantity': 1}),  # insert new
        Command.update(line_id, {'quantity': 2}),             # update existing
        Command.delete(line_id),                              # delete from DB
        Command.unlink(line_id),                              # remove relation only
        Command.link(existing_id),                            # add existing record
        Command.clear(),                                      # remove all
        Command.set([id1, id2, id3]),                         # replace all
    ]
})
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using `group_operator=` on fields in v18 — renamed to `aggregator=`, causes field definition error.

```python
# WRONG in v18
date = fields.Date(group_operator='min')

# CORRECT in v18
date = fields.Date(aggregator='min')
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using `<tree>` tag for list views in v18 — renamed to `<list>`, old tag not recognized.

```xml
<!-- WRONG in v18 -->
<tree><field name="name"/></tree>

<!-- CORRECT in v18 -->
<list><field name="name"/></list>
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using the old `<div class="oe_chatter">` block in v18 — replaced by `<chatter/>` tag.

```xml
<!-- WRONG in v18 -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>

<!-- CORRECT in v18 -->
<chatter reload_on_attachment="True"/>
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Overriding `create()` without `@api.model_create_multi`.
  </antipattern>

  <antipattern severity="HIGH">
    Using `from odoo.tools import SQL` — correct import path is `from odoo.tools.sql import SQL` (confirmed in model_18.py line 11).
  </antipattern>

  <antipattern severity="HIGH">
    Using raw `(0, 0, {...})` tuples for x2many writes instead of `Command` class.
  </antipattern>

  <antipattern severity="HIGH">
    Allowing `unlink()` without a state guard on multi-state models.
  </antipattern>

</antipatterns>

</pattern>