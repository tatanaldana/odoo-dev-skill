# Onchange & Dynamic Domain Patterns — v17/v18/v19

---

## Basic onchange

```python
@api.onchange('product_id')
def _onchange_product_id(self):
    if self.product_id:
        self.price_unit = self.product_id.lst_price
        self.name = self.product_id.description_sale or self.product_id.name
    else:
        self.price_unit = 0.0
        self.name = ''
```

## Onchange with warning

```python
@api.onchange('date_deadline')
def _onchange_date_deadline(self):
    if self.date_deadline and self.date_deadline < fields.Date.today():
        return {'warning': {'title': 'Warning', 'message': 'Deadline is in the past.'}}
```

## Computed domain field (replaces deprecated domain return from onchange)

```python
pricelist_domain = fields.Char(compute='_compute_pricelist_domain')

@api.depends('company_id')
def _compute_pricelist_domain(self):
    for rec in self:
        rec.pricelist_domain = str([('company_id', 'in', [rec.company_id.id, False])])
```

```xml
<field name="pricelist_id" domain="pricelist_domain"/>
```

## Cascading onchange (clear dependents)

```python
@api.onchange('project_id')
def _onchange_project_id(self):
    if self.stage_id.project_ids and self.project_id not in self.stage_id.project_ids:
        self.stage_id = False
    if self.milestone_id.project_id != self.project_id:
        self.milestone_id = False
```

## Domain object (v19)

```python
from odoo.fields import Domain
domain = Domain('id', 'in', followers.partner_id.ids) & base_domain
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| HIGH | Don't return domain dicts from onchange — deprecated in v17+ |
| HIGH | Don't write to DB inside onchange — runs on virtual record |
| MEDIUM | No `attrs=` in v17+ — use `invisible=` directly |
| MEDIUM | Don't rely on onchange for data integrity — use `@api.constrains` |