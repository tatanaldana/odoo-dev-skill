# Odoo Module Generator - Version 18.0

<pattern>

<description>
Module generation patterns for Odoo 18.0.
Use only for modules targeting Odoo 18.0.
Do not mix these patterns with other versions.
</description>

<version_notes>
  <version id="18">
    Breaking from v17: `group_operator=` renamed to `aggregator=` on fields.
    Breaking from v17: `&lt;tree&gt;` tag renamed to `&lt;list&gt;` in XML views.
    Breaking from v17: `&lt;div class="oe_chatter"&gt;` replaced by `&lt;chatter/&gt;` (bare, self-closing — dominant form in real 18.0/19.0 source).
    New: `export_string_translation=False` on fields.
    New: `web.assets_unit_tests` key in manifest.
    New: `@odoo-module` comment no longer required in JS files.
    Type hints: recommended on method signatures, NOT mandatory.
    Multi-company record rules: `company_ids` in `domain_force` — same as v17
    (the `allowed_company_ids` variable is available in rule context but `company_ids`
    is confirmed in official ir_rules source for both v17 and v18).
    SQL builder: `from odoo.tools.sql import SQL` in v18 (path changes in v19).
  </version>
</version_notes>

<examples>

  <example id="manifest" title="__manifest__.py template (v18)">

```python
# -*- coding: utf-8 -*-
{
    'name': '{Module Title}',
    'version': '18.0.1.0.0',
    'category': '{Category}',
    'summary': '{Short description}',
    'description': """
{Detailed description}
    """,
    'author': '{Author}',
    'website': '{Website}',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
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
        # v18: new unit test bundle key
        'web.assets_unit_tests': [
            '{module_name}/static/tests/**/*.js',
        ],
    },
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

  </example>

  <example id="model" title="Model template (v18 — aggregator=, type hints recommended)">

```python
# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.sql import SQL

class {ModelName}(models.Model):
    _name = '{module_name}.{model_name}'
    _description = '{Model Description}'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _check_company_auto = True

    # === BASIC FIELDS === #
    # v18: type hints recommended (not mandatory)
    name: str = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index='btree',
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
        check_company=True,
        tracking=True,
    )
    user_id: int = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        check_company=True,
        tracking=True,
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
        readonly=True,
        # v18: aggregator= replaces group_operator=
        aggregator='sum',
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))

    # === CONSTRAINTS === #
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name and len(record.name) < 3:
                raise ValidationError(_("Name must be at least 3 characters."))

    _sql_constraints = [
        ('name_company_uniq', 'UNIQUE(name, company_id)',
         'Name must be unique per company!'),
    ]

    # === CRUD METHODS === #
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    '{module_name}.{model_name}'
                ) or _('New')
        return super().create(vals_list)

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if not record.line_ids:
                    raise UserError(_("Cannot complete without lines."))
        return super().write(vals)

    def unlink(self):
        for record in self:
            if record.state not in ('draft', 'cancelled'):
                raise UserError(_("Cannot delete record in state '%s'.") % record.state)
        return super().unlink()

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': _("%s (copy)", self.name),
            'state': 'draft',
        })
        return super().copy(default)

    # === ACTION METHODS === #
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Only draft records can be confirmed."))
        self.write({'state': 'confirmed'})

    def action_done(self):
        for record in self:
            if record.state != 'confirmed':
                raise UserError(_("Only confirmed records can be marked done."))
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    # === BUSINESS METHODS === #
    def _get_report_data(self):
        """v18: SQL builder recommended for raw SQL queries."""
        from odoo.tools.sql import SQL
        query = SQL(
            """
            SELECT id, name, total_amount
            FROM %s
            WHERE company_id = %s
              AND state = %s
            ORDER BY total_amount DESC
            """,
            SQL.identifier(self._table),
            self.env.company.id,
            'done',
        )
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()


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
    def _compute_amount(self):
        for line in self:
            line.amount = line.quantity * line.price_unit
```

  </example>

  <example id="views_form" title="Form view (v18 — list tag, chatter tag)">

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
                            class="btn-primary" invisible="state != 'draft'"/>
                    <button name="action_done" string="Done" type="object"
                            invisible="state != 'confirmed'"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            invisible="state in ('done', 'cancelled')"/>
                    <button name="action_draft" string="Reset to Draft" type="object"
                            invisible="state not in ('cancelled',)"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                            invisible="active"/>
                    <div class="oe_title">
                        <label for="name"/>
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
                                <!-- v18: list tag replaces tree tag -->
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
                <!-- v18: chatter tag replaces oe_chatter div -->
                <chatter/>
            </form>
        </field>
    </record>

    <!-- v18: list tag for standalone list view -->
    <record id="{model_name}_view_list" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.list</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <list string="{Model Title}" multi_edit="1">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="user_id" widget="many2one_avatar_user"/>
                <field name="total_amount" sum="Total"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-info="state == 'confirmed'"
                       decoration-warning="state == 'draft'"/>
                <field name="company_id" groups="base.group_multi_company" optional="hide"/>
            </list>
        </field>
    </record>

    <record id="{model_name}_view_search" model="ir.ui.view">
        <field name="name">{module_name}.{model_name}.search</field>
        <field name="model">{module_name}.{model_name}</field>
        <field name="arch" type="xml">
            <search string="{Model Title}">
                <field name="name"/>
                <field name="partner_id"/>
                <field name="user_id"/>
                <separator/>
                <filter string="My Records" name="my_records"
                        domain="[('user_id', '=', uid)]"/>
                <filter string="Draft" name="draft"
                        domain="[('state', '=', 'draft')]"/>
                <filter string="Archived" name="inactive"
                        domain="[('active', '=', False)]"/>
                <group expand="0" string="Group By">
                    <filter string="Partner" name="group_partner"
                            context="{'group_by': 'partner_id'}"/>
                    <filter string="Status" name="group_state"
                            context="{'group_by': 'state'}"/>
                </group>
            </search>
        </field>
    </record>
</odoo>
```

  </example>

  <example id="security" title="Security templates (v18)">

ir.model.access.csv (format identical to v17):
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_name}_user,{model_name}.user,model_{module_name}_{model_name},{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_manager,{model_name}.manager,model_{module_name}_{model_name},{module_name}.group_{module_name}_manager,1,1,1,1
access_{model_name}_line_user,{model_name}.line.user,model_{module_name}_{model_name}_line,{module_name}.group_{module_name}_user,1,1,1,0
access_{model_name}_line_manager,{model_name}.line.manager,model_{module_name}_{model_name}_line,{module_name}.group_{module_name}_manager,1,1,1,1
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

    <!-- v18: company_ids in domain_force — confirmed ir_rules_18.xml -->
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

  <example id="owl_component" title="OWL 2.x component (v18 — @odoo-module NOT required)">

```javascript
/* v18: @odoo-module comment is NOT required */

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
        this.notification = useService("notification");
        this.action = useService("action");

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
                [["state", "=", "confirmed"]],
                ["name", "total_amount", "partner_id"]
            );
        } catch (error) {
            this.notification.add("Error loading data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onRecordClick(recordId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "{module_name}.{model_name}",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("{module_name}.{component_name}", {ComponentName});
```

  </example>

  <example id="tests" title="Test template (v18)">

```python
# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError, ValidationError

@tagged('post_install', '-at_install')
class Test{ModelName}(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'company_id': cls.company.id,
        })

    def test_create_record(self):
        """Test basic record creation."""
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        self.assertTrue(record.id)
        self.assertEqual(record.state, 'draft')

    def test_confirm_record(self):
        """Test record confirmation workflow."""
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
            'partner_id': self.partner.id,
        })
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')

    def test_cannot_delete_confirmed(self):
        """Test that confirmed records cannot be deleted."""
        record = self.env['{module_name}.{model_name}'].create({
            'name': 'Test Record',
        })
        record.action_confirm()
        with self.assertRaises(UserError):
            record.unlink()
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using `attrs=` in any view — removed since v17.

    ```xml
    <!-- WRONG -->
    <field name="amount" attrs="{'invisible': [('state', '=', 'draft')]}"/>

    <!-- CORRECT -->
    <field name="amount" invisible="state == 'draft'"/>
    ```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using `group_operator=` on fields — renamed to `aggregator=` in v18.

    ```python
    # WRONG in v18
    amount = fields.Float(group_operator='sum')

    # CORRECT in v18
    amount = fields.Float(aggregator='sum')
    ```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using `&lt;tree&gt;` tag for list views — renamed to `&lt;list&gt;` in v18.

    ```xml
    <!-- WRONG in v18 -->
    <tree editable="bottom">...</tree>

    <!-- CORRECT in v18 -->
    <list editable="bottom">...</list>
    ```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using the `oe_chatter` div block — replaced by `&lt;chatter/&gt;` tag in v18.

    ```xml
    <!-- WRONG in v18 -->
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>

    <!-- CORRECT in v18 -->
    <chatter/>
    ```
  </antipattern>

  <antipattern severity="HIGH">
    Defining `create()` without `@api.model_create_multi`.
  </antipattern>

  <antipattern severity="MEDIUM">
    Using raw SQL string interpolation — use the `SQL()` builder instead.

    ```python
    # WRONG — SQL injection risk
    query = "SELECT * FROM %s WHERE id = %s" % (self._table, record_id)

    # CORRECT
    from odoo.tools.sql import SQL
    query = SQL("SELECT * FROM %s WHERE id = %s", SQL.identifier(self._table), record_id)
    ```
  </antipattern>

</antipatterns>

</pattern>