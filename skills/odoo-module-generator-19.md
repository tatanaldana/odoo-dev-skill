# Odoo Module Generator - Version 19.0

<pattern>

<description>
Module generation patterns for Odoo 19.0 (development).
Use only for modules targeting Odoo 19.0.
Do not mix these patterns with other versions.
Note: v19 is in active development — verify patterns against official source when available.
</description>

<version_notes>
  <version id="19">
    Breaking from v18: `models.Constraint()` replaces `_sql_constraints` list.
    Breaking from v18: `models.Index()` replaces manual index definitions.
    Breaking from v18: SQL import path changes — `from odoo.tools import SQL` (was `odoo.tools.sql`).
    New: `Domain` class from `odoo.fields` — `from odoo.fields import Command, Domain`.
    New: `bypass_search_access=True` on Many2one fields.
    New: `kpi_providers` and `author` keys in manifest.
    Chatter: same as v18 — bare, self-closing `&lt;chatter/&gt;` (dominant form in real
    source, 65+ occurrences with no attributes; optional reload_on_attachment/
    reload_on_follower/reload_on_post exist for specific views but are not required).
    List views: same as v18 — `&lt;list&gt;` tag.
    OWL: 2.x — same as v17/v18 (OWL 3.x expected in v20, not confirmed in v19).
    Type hints: recommended convention in ORM core, NOT mandatory in addon code —
    confirmed account.move.line (3700+ lines) has only 2 type-hinted methods.
    SQL() builder: recommended, raw parameterized cr.execute() remains valid.
    Translation: both `from odoo import _` and `self.env._()` remain valid in v19 —
    confirmed `from odoo import _` still used in 36 files of addons/account/models alone
    (e.g. account_move.py). `self.env._()` is available but NOT a required replacement.
    Record rules: `company_ids` in `domain_force` — unchanged from v17/v18. Do NOT use
    `allowed_company_ids` here (confirmed against real account_security.xml).
    models.Constraint() and models.Index() are BARE class attributes, never wrapped in a
    `_sql_constraints=[...]` or `_indexes=[...]` list (confirmed against real
    account_journal.py, account_move_line.py, account_bank_statement.py).
  </version>
</version_notes>

<examples>

  <example id="manifest" title="__manifest__.py template (v19)">

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '19.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'description': """
{Detailed description}
    """,
    'author': '{Author}',   # v19: author key new
    'website': '{Website}',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        # ORDER IS CRITICAL — define before reference
        'security/{module_name}_security.xml',
        'security/ir.model.access.csv',
        'views/{model_name}_views.xml',
        'views/menuitems.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '{module_name}/static/src/**/*.js',
            '{module_name}/static/src/**/*.xml',
            '{module_name}/static/src/**/*.scss',
        ],
        'web.assets_unit_tests': [
            '{module_name}/static/tests/**/*.js',
        ],
    },
    # v19: kpi_providers key
    'kpi_providers': [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

  </example>

  <example id="model" title="Model template (v19 — models.Constraint, models.Index, Domain, correct SQL import)">

```python
# -*- coding: utf-8 -*-
from typing import Any, Optional
from collections.abc import Sequence

from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
# v19: SQL import path changed from odoo.tools.sql to odoo.tools
from odoo.tools import SQL
# v19: Domain class available
from odoo.fields import Command, Domain


class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    # === BASIC FIELDS === #
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )
    active: bool = fields.Boolean(default=True)
    sequence: int = fields.Integer(default=10)

    # === RELATIONAL FIELDS === #
    company_id: int = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    partner_id: int = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        tracking=True,
        check_company=True,
        # v19: bypass_search_access available for cross-company lookup fields
        # bypass_search_access=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        check_company=True,
    )
    line_ids: list = fields.One2many(
        comodel_name='{module_name}.{model_name}.line',
        inverse_name='parent_id',
        string='Lines',
        copy=True,
    )

    # === SELECTION FIELDS === #
    state: str = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )

    # === COMPUTED FIELDS === #
    total_amount: float = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        aggregator='sum',
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

    # v19: models.Constraint() replaces _sql_constraints — a BARE class attribute,
    # never wrapped in a list (confirmed account_journal.py lines 36-39)
    _name_company_uniq = models.Constraint(
        'UNIQUE(name, company_id)',
        'Name must be unique per company!',
    )

    # v19: models.Index() replaces manual index creation — also a bare attribute,
    # a single SQL-like column-list string, with an optional trailing WHERE clause
    # for partial indexes (confirmed account_move_line.py lines 480-489)
    _name_company_idx = models.Index("(name, company_id)")
    _state_idx = models.Index("(state) WHERE state != 'cancelled'")

    # === CRUD METHODS === #
    @api.model_create_multi
    def create(self, vals_list: list[dict[str, Any]]) -> '{ModelName}':
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals: dict[str, Any]) -> bool:
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self) -> bool:
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_("Cannot delete non-draft records."))
        return super().unlink()

    def copy(self, default: Optional[dict[str, Any]] = None) -> '{ModelName}':
        default = dict(default or {})
        default.setdefault('name', _("%s (copy)", self.name))
        return super().copy(default)

    # === ACTION METHODS === #
    def action_confirm(self) -> None:
        self.write({'state': 'confirmed'})

    def action_done(self) -> None:
        self.write({'state': 'done'})

    def action_cancel(self) -> None:
        self.write({'state': 'cancelled'})

    def action_draft(self) -> None:
        self.write({'state': 'draft'})

    # === SQL OPERATIONS === #
    def _get_report_data(self) -> list[dict[str, Any]]:
        """v19: SQL import from odoo.tools (not odoo.tools.sql)."""
        query = SQL(
            """
            SELECT
                m.id,
                m.name,
                COALESCE(SUM(l.amount), 0) as total
            FROM %s m
            LEFT JOIN %s l ON l.parent_id = m.id
            WHERE m.company_id IN %s
            GROUP BY m.id, m.name
            ORDER BY m.create_date DESC
            """,
            SQL.identifier(self._table),
            SQL.identifier('{module_name}_{model_name}_line'),
            tuple(self.env.companies.ids),
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()

    # v19: Domain class for business logic
    def _get_active_domain(self) -> Domain:
        return Domain('state', 'in', ('confirmed', 'done'))


class {ModelName}Line(models.Model):
    _name = '{module_name}.{model_name}.line'
    _description = '{Model Name} Line'
    _order = 'sequence, id'

    parent_id: int = fields.Many2one(
        comodel_name='{module_name}.{model_name}',
        string='Parent',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id: int = fields.Many2one(
        related='parent_id.company_id',
        store=True,
    )
    sequence: int = fields.Integer(default=10)
    name: str = fields.Char(string='Description', required=True)
    quantity: float = fields.Float(string='Quantity', default=1.0)
    price_unit: float = fields.Float(string='Unit Price')
    amount: float = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True,
        aggregator='sum',
    )

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self) -> None:
        for line in self:
            line.amount = line.quantity * line.price_unit
```

  </example>

  <example id="views_form" title="Form view (v19 — same list tag and chatter as v18)">

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="{model_name}_view_form" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.form</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <form string="{Model Title}">
                <header>
                    <button name="action_confirm" string="Confirm" type="object"
                            class="btn-primary"
                            invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            invisible="state in ('done', 'cancelled')"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            invisible="active"/>
                    <div class="oe_title">
                        <h1><field name="name" placeholder="Name..."/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="partner_id"/>
                            <field name="user_id"/>
                        </group>
                        <group>
                            <field name="company_id" groups="base.group_multi_company"/>
                            <field name="total_amount"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Lines" name="lines">
                            <field name="line_ids">
                                <!-- v19: same list tag as v18 -->
                                <list editable="bottom">
                                    <field name="sequence" widget="handle"/>
                                    <field name="name"/>
                                    <field name="quantity"/>
                                    <field name="price_unit"/>
                                    <field name="amount"/>
                                </list>
                            </field>
                        </page>
                    </notebook>
                </sheet>
                <!-- v19: same chatter tag as v18 — bare form is dominant in real source -->
                <chatter/>
            </form>
        </field>
    </record>
</odoo>
```

  </example>

  <example id="security" title="Security templates (v19 — company_ids in domain_force, same as v17/v18)">

ir.model.access.csv (format identical across v17/v18/v19):
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
```

Security groups XML:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_{module_name}" model="ir.module.category">
        <field name="name">{Module Title}</field>
        <field name="sequence">100</field>
    </record>

    <record id="group_{module_name}_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_{module_name}"/>
    </record>

    <record id="group_{module_name}_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_{module_name}"/>
        <field name="implied_ids" eval="[(4, ref('group_{module_name}_user'))]"/>
        <field name="users" eval="[(4, ref('base.user_admin'))]"/>
    </record>

    <!-- v19: company_ids in domain_force — confirmed ir_rules_19.xml -->
    <record id="rule_{model_name}_company" model="ir.rule">
        <field name="name">{Model Name}: Multi-Company</field>
        <field name="model_id" ref="model_{module_name}_{model_name}"/>
        <field name="global" eval="True"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
    </record>
</odoo>
```

  </example>

  <example id="owl_component" title="OWL 2.x component (v19 — same as v18, no @odoo-module required)">

```javascript
/* v19: OWL 2.x — same as v18. @odoo-module NOT required. */

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class {ComponentName} extends Component {
    static template = "{module_name}.{ComponentName}";
    static props = {
        recordId: { type: Number, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            data: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.data = await this.orm.searchRead(
                "{module_name}.{model_name}",
                [],
                ["name", "state", "amount"],
                { limit: 100, order: "create_date DESC" }
            );
        } catch (error) {
            this.state.error = error.message;
            this.notification.add("Failed to load data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using `_sql_constraints` list — replaced by `models.Constraint()` in v19. It is a
    BARE class attribute, never wrapped in a `_constraints=[...]` or similar list
    (confirmed against real account_journal.py, account_move_line.py in 19.0 source).

    ```python
    # WRONG in v19 (old style)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name, company_id)', 'Name must be unique!'),
    ]

    # ALSO WRONG in v19 — models.Constraint() does not exist in real source
    _constraints = [
        models.Constraint('UNIQUE(name, company_id)', 'Name must be unique!'),
    ]

    # CORRECT in v19
    _name_uniq = models.Constraint('UNIQUE(name, company_id)', 'Name must be unique!')
    ```
  </antipattern>

  <antipattern severity="HIGH">
    Claiming `self.env._()` replaces `from odoo import _` in v19 — both remain valid.
    `from odoo import _` is still used throughout real 19.0 addon code (e.g. 36 files
    in addons/account/models alone, including account_move.py). Do not flag the classic
    import as an error.
  </antipattern>

  <antipattern severity="CRITICAL">
    Wrong SQL import path in v19.

    ```python
    # WRONG in v19 (this is the v17/v18 path)
    from odoo.tools.sql import SQL

    # CORRECT in v19
    from odoo.tools import SQL
    ```
  </antipattern>

  <antipattern severity="HIGH">
    Using `attrs=` in any view — removed since v17.
  </antipattern>

  <antipattern severity="HIGH">
    Using `group_operator=` on fields — renamed to `aggregator=` since v18.
  </antipattern>

  <antipattern severity="HIGH">
    Using `&lt;tree&gt;` tag — renamed to `&lt;list&gt;` since v18.
  </antipattern>

</antipatterns>

</pattern>