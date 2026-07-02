<pattern>

<description>
Patterns for company-aware models, cross-company operations, record rules, currency handling,
and multi-company views. Use in any module deployed across multiple business units or branches
in an Odoo multi-company environment.
</description>

<version_notes>
  <version id="17">
    `_check_company_domain` available on models (confirmed: res.partner v17). `check_company=True`
    on Many2one fields works v17+. `_check_company_auto = True` supported v17+. Use `with_company()`
    to switch context — `with_context(force_company=id)` was removed before v17.
  </version>
  <version id="18">
    No breaking changes to multi-company API. `_check_company_domain` still available.
    `_activate_and_install_lang()` introduced (parallel API, not multi-company specific).
  </version>
  <version id="19">
    `_check_company_auto = True` confirmed in res.partner v19 reference. `_check_company_domain`
    confirmed identical to v17/v18. No other breaking changes to multi-company API.
  </version>
</version_notes>

<examples>

  <example id="basic_model" title="Company-aware model">
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True  # validates check_company=True fields on write/create

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    # Relational fields with automatic company validation
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        check_company=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        check_company=True,
    )
```
  </example>

  <example id="check_company_domain" title="Custom company domain on a model">
```python
from odoo import fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _check_company_auto = True
    # Override default check_company domain to allow parent-of hierarchy
    _check_company_domain = models.check_company_domain_parent_of

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        check_company=True,
    )
```
  </example>

  <example id="company_dependent_fields" title="Company-dependent field values">
```python
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Each company stores its own value independently
    x_internal_code = fields.Char(
        string='Internal Code',
        company_dependent=True,
    )
    x_local_price = fields.Float(
        string='Local Price',
        company_dependent=True,
        digits='Product Price',
    )
    x_local_supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Local Supplier',
        company_dependent=True,
    )

    def get_local_data(self):
        # Automatically returns value for the current company in context
        code = self.x_internal_code

        # Read value as seen by a specific company
        other_company = self.env['res.company'].browse(2)
        code_other = self.with_company(other_company).x_internal_code
        return code, code_other
```
  </example>

  <example id="record_rules" title="Multi-company record rules (XML)">
```xml
<odoo>
    <!-- Users see only records belonging to their active companies -->
    <record id="my_model_company_rule" model="ir.rule">
        <field name="name">My Model: Company Rule</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[
            '|',
            ('company_id', '=', False),
            ('company_id', 'in', company_ids)
        ]</field>
        <field name="global" eval="True"/>
    </record>

    <!-- Strict: own company only -->
    <!-- domain_force: [('company_id', '=', company_id)] -->

    <!-- Child companies included -->
    <!-- domain_force: [('company_id', 'child_of', company_id)] -->
</odoo>
```
  </example>

  <example id="with_company" title="Switching company context">
```python
from odoo import api, models


class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def action_process_all_companies(self):
        """Process pending records for every company the user belongs to."""
        for company in self.env.user.company_ids:
            records = self.with_company(company).search([
                ('state', '=', 'pending'),
                ('company_id', '=', company.id),
            ])
            for record in records:
                record._process()

    def action_create_in_company(self, company_id: int):
        """Create a record in a specific company's context."""
        company = self.env['res.company'].browse(company_id)
        return self.with_company(company).create({
            'name': 'New Record',
            'company_id': company.id,
        })
```
  </example>

  <example id="cron_multi_company" title="Cron that iterates all companies">
```python
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def _cron_process_all_companies(self) -> None:
        companies = self.env['res.company'].search([])
        for company in companies:
            self.with_company(company)._process_company_records()

    def _process_company_records(self) -> None:
        records = self.search([
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'pending'),
        ])
        for record in records:
            try:
                record._do_process()
            except Exception as e:
                _logger.error("Error processing record %s: %s", record.id, e)
```
  </example>

  <example id="currency_fields" title="Monetary fields with currency conversion">
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    company_currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        store=True,
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )
    amount_company_currency = fields.Monetary(
        string='Amount (Company Currency)',
        currency_field='company_currency_id',
        compute='_compute_amount_company_currency',
        store=True,
    )

    @api.depends('amount', 'currency_id', 'company_id')
    def _compute_amount_company_currency(self):
        for record in self:
            if record.currency_id != record.company_currency_id:
                record.amount_company_currency = record.currency_id._convert(
                    record.amount,
                    record.company_currency_id,
                    record.company_id,
                    record.date or fields.Date.today(),  # date required for correct rate
                )
            else:
                record.amount_company_currency = record.amount
```
  </example>

  <example id="form_view" title="Form view with company and currency visibility">
```xml
<form string="My Model">
    <sheet>
        <group>
            <group>
                <field name="name"/>
                <field name="partner_id"
                       context="{'default_company_id': company_id}"
                       domain="[('company_id', 'in', [company_id, False])]"/>
            </group>
            <group>
                <field name="company_id"
                       groups="base.group_multi_company"
                       options="{'no_create': True}"/>
                <field name="currency_id"
                       groups="base.group_multi_currency"/>
            </group>
        </group>
        <group string="Amounts">
            <field name="amount"/>
            <field name="amount_company_currency"
                   groups="base.group_multi_currency"
                   invisible="currency_id == company_currency_id"/>
        </group>
    </sheet>
</form>
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
```python
# WRONG: with_context(force_company=) was removed before v17
record.with_context(force_company=company.id)._process()

# CORRECT: always use with_company()
record.with_company(company)._process()
```
  </antipattern>

  <antipattern severity="CRITICAL">
```python
# WRONG: omitting company_id on a business model in multi-company deployment
class MyModel(models.Model):
    _name = 'my.model'
    name = fields.Char()
    # no company_id — records will be shared/unfiltered across all companies

# CORRECT: always declare company_id
class MyModel(models.Model):
    _name = 'my.model'
    name = fields.Char()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
```
  </antipattern>

  <antipattern severity="HIGH">
```python
# WRONG: currency conversion without a date — uses today's rate silently
amount_converted = self.currency_id._convert(
    amount,
    target_currency,
    company,
    # date missing — will use fields.Date.today() internally but hides intent
)

# CORRECT: always pass an explicit date
amount_converted = self.currency_id._convert(
    amount,
    target_currency,
    company,
    self.date or fields.Date.today(),
)
```
  </antipattern>

  <antipattern severity="HIGH">
```xml
<!-- WRONG: using allowed_company_ids in domain_force — not a valid context variable -->
<field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

<!-- CORRECT: use company_ids (the confirmed variable in ir.rule domain_force context) -->
<field name="domain_force">[
    '|',
    ('company_id', '=', False),
    ('company_id', 'in', company_ids)
]</field>
```
  </antipattern>

</antipatterns>

</pattern>