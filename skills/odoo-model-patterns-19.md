# Odoo 19.0 Model Patterns

<pattern>

<description>
  Model patterns for Odoo 19.0. Key new features: `models.Constraint()` and `models.Index()`
  replace `_sql_constraints` list and manual index definitions; `Domain` class available from
  `odoo.fields`; `bypass_search_access=True` on Many2one fields. Type hints and SQL() are
  ORM-core conventions — recommended but not enforced on addon business code.
  Use this file when the target version is 19.0.

  Verified against real Odoo 19.0 source: account.move.line (addons/account).
</description>

<version_notes>
  <version id="19">
    <change type="breaking">models.Constraint() replaces _sql_constraints list — confirmed in model_19.py lines 463-478</change>
    <change type="breaking">models.Index() replaces manual index definitions — confirmed in model_19.py lines 483-489</change>
    <change type="feature">Domain class available: from odoo.fields import Command, Domain — confirmed in model_19.py line 9</change>
    <change type="feature">bypass_search_access=True on Many2one fields — confirmed in model_19.py lines 38, 99, 172</change>
    <change type="feature">SQL import path changed: from odoo.tools import SQL (not odoo.tools.sql) — confirmed in model_19.py line 10</change>
    <change type="feature">aggregator= on fields — same as v18, confirmed in model_19.py lines 72, 77</change>
    <change type="feature">Chatter syntax same as v18: &lt;chatter reload_on_attachment="True"/&gt; — confirmed in views_19.xml line 1594</change>
    <change type="observed">Type hints: ORM-core convention, NOT enforced on addon code. Only 2 methods in the entire account.move.line source (3700+ lines) use return type annotations — do not treat as mandatory</change>
    <change type="observed">SQL(): recommended for complex queries, but raw parameterized cr.execute() coexists in real 19.0 addon code — not a hard requirement</change>
  </version>
</version_notes>

<examples>

  <example id="new_constraint_index" title="NEW: models.Constraint() and models.Index() — replaces _sql_constraints">

```python
# v18 — _sql_constraints list (still works in v19 but deprecated style)
_sql_constraints = [
    ('name_company_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ('positive_amount', 'CHECK(amount >= 0)', 'Amount must be positive!'),
]

# v19 — models.Constraint() as class attributes (confirmed in model_19.py lines 463-478)
_name_company_uniq = models.Constraint(
    'unique(company_id, name)',
    'Name must be unique per company!',
)
_check_positive_amount = models.Constraint(
    'CHECK(amount >= 0)',
    'Amount must be positive!',
)

# v19 — models.Index() as class attributes (confirmed in model_19.py lines 483-489)
# Simple multi-column index
_partner_ref_idx = models.Index("(partner_id, ref)")

# Index with sort order
_date_name_id_idx = models.Index("(date desc, name desc, id)")

# Partial index (WHERE clause)
_unreconciled_idx = models.Index("(account_id, partner_id) WHERE reconciled IS NOT TRUE")

# Conditional index
_negative_residual_idx = models.Index("(journal_id) WHERE amount_residual < 0")
```

  </example>

  <example id="new_domain_class" title="NEW: Domain class from odoo.fields">

```python
from odoo.fields import Command, Domain  # confirmed in model_19.py line 9

# Domain combination
domain_a = [('state', '=', 'draft')]
domain_b = [('company_id', '=', self.env.company.id)]

# OR combination
combined = Domain.OR([domain_a, domain_b])

# Negative operators
if operator in Domain.NEGATIVE_OPERATORS:
    # handle negation
    pass
```

  </example>

  <example id="new_bypass_search_access" title="NEW: bypass_search_access on Many2one fields">

```python
# v19 — bypass_search_access=True allows finding related records
# even when the user lacks read access to the comodel (confirmed in model_19.py lines 38, 99)
move_id = fields.Many2one(
    comodel_name='account.move',
    required=True,
    readonly=True,
    index=True,
    bypass_search_access=True,  # v19: bypass ir.rules for this field
    ondelete='cascade',
    check_company=True,
)
```

  </example>

  <example id="sql_import_v19" title="SQL import path in v19 — from odoo.tools (not odoo.tools.sql)">

```python
# v18 — import from submodule
from odoo.tools.sql import SQL

# v19 — import directly from odoo.tools (confirmed in model_19.py line 10)
from odoo.tools import frozendict, float_compare, groupby, Query, SQL, OrderedSet

# Usage is identical in both versions
query = SQL(
    "SELECT id, name FROM %s WHERE state = %s",
    SQL.identifier(self._table),
    'confirmed',
)
self.env.cr.execute(query)
rows = self.env.cr.dictfetchall()
```

  </example>

  <example id="model_definition" title="Full model definition — v19 patterns">

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

    # === FIELDS === #
    name = fields.Char(
        string='Name',
        required=True,
        index='trigram',
        tracking=True,
    )
    code = fields.Char(index=True, copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    date = fields.Date(
        default=fields.Date.context_today,
        aggregator='min',
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
    parent_id = fields.Many2one(
        comodel_name='my.model.parent',
        bypass_search_access=True,  # v19
        ondelete='cascade',
        index=True,
        check_company=True,
    )
    line_ids = fields.One2many(
        comodel_name='my.model.line',
        inverse_name='model_id',
        copy=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
    )

    # === COMPUTED FIELDS === #
    total_amount = fields.Monetary(
        compute='_compute_total',
        store=True,
        currency_field='currency_id',
    )
    line_count = fields.Integer(compute='_compute_line_count')

    # === CONSTRAINTS — v19 style === #
    _name_company_uniq = models.Constraint(
        'unique(company_id, name)',
        'Name must be unique per company!',
    )
    _check_positive_amount = models.Constraint(
        'CHECK(total_amount >= 0)',
        'Total amount cannot be negative!',
    )

    # === INDEXES — v19 style === #
    _partner_date_idx = models.Index("(partner_id, date)")
    _active_state_idx = models.Index("(state) WHERE active IS TRUE")

    # === COMPUTE METHODS === #
    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    @api.depends('line_ids')
    def _compute_line_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    # === CRUD METHODS === #
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('my.model')
            if 'company_id' not in vals:
                vals['company_id'] = self.env.company.id
        records = super().create(vals_list)
        for record in records:
            record.message_post(body=_("Record created."))
        return records

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'confirmed':
            for record in self:
                if not record.line_ids:
                    raise UserError(
                        _("Record '%s' must have at least one line.") % record.name
                    )
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancelled'):
                raise UserError(
                    _("Cannot delete '%s' in state '%s'.") % (record.name, record.state)
                )
        return super().unlink()

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (copy)", self.name)
        default['state'] = 'draft'
        return super().copy(default)

    # === ACTION METHODS === #
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
            'type': 'ir.actions.act_window',
            'name': _('Lines'),
            'res_model': 'my.model.line',
            'view_mode': 'list,form',
            'domain': [('model_id', '=', self.id)],
            'context': {'default_model_id': self.id},
        }

    # === SQL === #
    def _get_summary_data(self):
        query = SQL(
            """
            SELECT state, COUNT(*) AS count, SUM(total_amount) AS total
            FROM %s
            WHERE company_id = %s
            GROUP BY state
            ORDER BY count DESC
            """,
            SQL.identifier(self._table),
            self.env.company.id,
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
```

  </example>

  <example id="xml_views" title="XML views — v19 (list tag and chatter same as v18, verified)">

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Form View — chatter: <chatter reload_on_attachment="True"/> confirmed in views_19.xml -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
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
                                class="oe_stat_button" icon="fa-list"
                                invisible="line_count == 0">
                            <field name="line_count" widget="statinfo" string="Lines"/>
                        </button>
                    </div>
                    <widget name="web_ribbon" title="Archived" invisible="active"/>
                    <div class="oe_title">
                        <label for="name"/>
                        <h1>
                            <field name="name" readonly="state != 'draft'"/>
                        </h1>
                    </div>
                    <group>
                        <group>
                            <field name="code" readonly="state != 'draft'"/>
                            <field name="partner_id" readonly="state == 'done'"/>
                            <field name="user_id"/>
                        </group>
                        <group>
                            <field name="date"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids" readonly="state == 'done'">
                                <list editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount" sum="Total"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </sheet>
                <!-- v19: same chatter syntax as v18 — confirmed in views_19.xml line 1594 -->
                <chatter reload_on_attachment="True"/>
            </form>
        </field>
    </record>

    <!-- List View — v19 uses <list> same as v18 -->
    <record id="view_my_model_list" model="ir.ui.view">
        <field name="name">my.model.list</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <list decoration-danger="state == 'cancelled'"
                  decoration-success="state == 'done'">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="date"/>
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
        <field name="name">my.model.search</field>
        <field name="model">my.model</field>
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

  <example id="type_hints_optional" title="Type hints — ORM-core convention, not mandatory in addon code">

```python
# Both styles are valid in v19 addon code.
# Verified: account.move.line (3700+ lines) has only 2 methods with return type annotations.

# Without hints — common in real 19.0 addon code, equally correct:
def action_confirm(self):
    self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

# With hints — matches ORM-core style (odoo/orm/models.py), good for new code:
def action_confirm(self) -> None:
    self.filtered(lambda r: r.state == 'draft').write({'state': 'confirmed'})

# Full typed method with from __future__ import annotations:
from __future__ import annotations
from typing import Any

def get_summary(self, include_cancelled: bool = False) -> list[dict[str, Any]]:
    domain = [('state', '!=', 'cancelled')] if not include_cancelled else []
    return self.search_read(domain, ['name', 'state', 'total_amount'])
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="HIGH">
    Using `_sql_constraints` list style in v19 — `models.Constraint()` is the new pattern.
    Both technically work, but `_sql_constraints` is the deprecated style in v19.

```python
# DEPRECATED in v19
_sql_constraints = [
    ('name_uniq', 'unique(name)', 'Name must be unique!'),
]

# CORRECT in v19 (confirmed in model_19.py)
_name_uniq = models.Constraint(
    'unique(name)',
    'Name must be unique!',
)
```
  </antipattern>

  <antipattern severity="HIGH">
    Using `from odoo.tools.sql import SQL` in v19 — import path changed.

```python
# WRONG in v19 (was correct in v18)
from odoo.tools.sql import SQL

# CORRECT in v19 (confirmed in model_19.py line 10)
from odoo.tools import SQL
```
  </antipattern>

  <antipattern severity="HIGH">
    Using the old `<div class="oe_chatter">` block in v19 — same as v18, replaced by `<chatter/>`.

```xml
<!-- WRONG in v19 -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>

<!-- CORRECT in v19 (confirmed in views_19.xml line 1594) -->
<chatter reload_on_attachment="True"/>
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Treating type hints as mandatory in v19 addon code — they are an ORM-core convention,
    not enforced. Real addon source (account.move.line, 3700+ lines) uses them in only 2 methods.
    Do not flag their absence as an error in code review.
  </antipattern>

  <antipattern severity="CRITICAL">
    Raw SQL built via string formatting with untrusted input — SQL injection risk regardless of version.

```python
# ALWAYS WRONG — injection risk
self.env.cr.execute("SELECT * FROM %s WHERE name = '%s'" % (table, user_input))

# CORRECT — parameterized (both styles valid in v19)
self.env.cr.execute("SELECT * FROM my_table WHERE name = %s", [user_input])
# or
self.env.cr.execute(SQL("SELECT * FROM my_table WHERE name = %s", user_input))
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Overriding `create()` without `@api.model_create_multi`.
  </antipattern>

  <antipattern severity="HIGH">
    Missing `unlink()` state guard on multi-state models.
  </antipattern>

</antipatterns>

</pattern>