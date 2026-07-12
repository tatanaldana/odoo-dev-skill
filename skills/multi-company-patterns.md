# Multi-Company Patterns — v17/v18/v19

---

## Version notes

- `_check_company_auto`, `check_company=True`, `with_company()` — all available v17+
- `_check_company_domain` — available v17+
- Record rules: `company_ids` in `domain_force` — all versions
- `with_context(force_company=)` removed before v17 — use `with_company()`

---

## Company-aware model

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True,
        default=lambda self: self.env.company, index=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    warehouse_id = fields.Many2one('stock.warehouse', check_company=True)
```

## Company-dependent fields

```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    x_internal_code = fields.Char(company_dependent=True)
    x_local_price = fields.Float(company_dependent=True)

    def get_other_company_value(self):
        return self.with_company(other_company).x_internal_code
```

## Record rule

```xml
<record id="my_model_company_rule" model="ir.rule">
    <field name="name">My Model: Company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
    <field name="global" eval="True"/>
</record>
```

## with_company() — cross-company operations

```python
def action_process_all_companies(self):
    for company in self.env.user.company_ids:
        records = self.with_company(company).search([
            ('state', '=', 'pending'), ('company_id', '=', company.id),
        ])
        records._process()
```

## Cron iterating all companies

```python
@api.model
def _cron_process_all(self):
    for company in self.env['res.company'].search([]):
        self.with_company(company)._process_company_records()
```

## Monetary fields + currency conversion

```python
currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)
amount = fields.Monetary(currency_field='currency_id')
amount_company = fields.Monetary(currency_field='company_currency_id',
    compute='_compute_amount_company', store=True)

@api.depends('amount', 'currency_id', 'company_id')
def _compute_amount_company(self):
    for rec in self:
        if rec.currency_id != rec.company_currency_id:
            rec.amount_company = rec.currency_id._convert(
                rec.amount, rec.company_currency_id, rec.company_id,
                rec.date or fields.Date.today())
        else:
            rec.amount_company = rec.amount
```

## View patterns

```xml
<field name="company_id" groups="base.group_multi_company" options="{'no_create': True}"/>
<field name="currency_id" groups="base.group_multi_currency"/>
<field name="partner_id" context="{'default_company_id': company_id}"
       domain="[('company_id', 'in', [company_id, False])]"/>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `with_context(force_company=)` removed — use `with_company()` |
| CRITICAL | Business models must have `company_id` field |
| HIGH | `allowed_company_ids` NOT valid in `domain_force` — use `company_ids` |
| HIGH | Currency conversion without explicit date |