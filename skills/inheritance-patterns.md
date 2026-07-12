# Inheritance Patterns — v17/v18/v19

Model extension, method overrides, view inheritance, selection_add.

---

## Version-specific syntax

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| List tag | `<tree>` | `<list>` | `<list>` |
| Chatter | `oe_chatter` div | `<chatter/>` | `<chatter/>` |
| Constraints | `_sql_constraints` | `_sql_constraints` | `models.Constraint()` |
| Visibility | `invisible=` (no `attrs=`) | same | same |

---

## _inherit — add fields

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_loyalty_points = fields.Integer(default=0)
    x_customer_tier = fields.Selection([
        ('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold'),
    ], compute='_compute_customer_tier', store=True)

    @api.depends('x_loyalty_points')
    def _compute_customer_tier(self):
        for partner in self:
            pts = partner.x_loyalty_points
            partner.x_customer_tier = 'gold' if pts >= 1000 else 'silver' if pts >= 500 else 'bronze'
```

Custom fields on inherited models must use `x_` prefix.

## _inherit — override method

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            order._check_credit_limit()
        result = super().action_confirm()  # ALWAYS call super()
        for order in self:
            order._send_confirmation_notification()
        return result
```

## mail.thread + mail.activity.mixin

```python
class MyDocument(models.Model):
    _name = 'my.document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(required=True)
    state = fields.Selection([...], tracking=True)  # tracking=True logs changes in chatter
    partner_id = fields.Many2one('res.partner', tracking=True)
```

## check_company / _check_company_auto (v17/v18/v19)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', check_company=True)
```

## selection_add

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    state = fields.Selection(
        selection_add=[('pending_approval', 'Pending Approval')],
        ondelete={'pending_approval': 'set default'},  # REQUIRED — omitting causes upgrade errors
    )
```

## create() override

```python
@api.model_create_multi  # MANDATORY in v17+
def create(self, vals_list):
    for vals in vals_list:
        if not vals.get('reference'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('my.model.sequence')
    return super().create(vals_list)
```

## View inheritance (xpath)

```xml
<record id="view_inherit" model="ir.ui.view">
    <field name="name">model.form.inherit.my_module</field>
    <field name="model">target.model</field>
    <field name="inherit_id" ref="base_module.view_id"/>
    <field name="arch" type="xml">
        <field name="partner_id" position="after">
            <field name="x_account_manager_id"/>
        </field>
        <xpath expr="//div[@name='button_box']" position="inside">
            <button class="oe_stat_button" type="object" name="action_view_loyalty" icon="fa-star">
                <field name="x_loyalty_points" widget="statinfo"/>
            </button>
        </xpath>
    </field>
</record>
```

## Constraints by version

```python
# v17/v18
_sql_constraints = [('code_unique', 'UNIQUE(code, company_id)', 'Code must be unique.')]

# v19
_code_unique = models.Constraint('UNIQUE(code, company_id)', 'Code must be unique.')
_code_idx = models.Index("(code, company_id)")
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Always call `super()` in overridden methods |
| CRITICAL | No `attrs=` in v17+ |
| CRITICAL | `selection_add` must include `ondelete=` for every added value |
| HIGH | Never use `string=` as xpath selector |
| HIGH | Custom fields on inherited models must use `x_` prefix |
| HIGH | List every inherited module in `depends=` |
| MEDIUM | Never use positional xpath (`//field[3]`) |
| MEDIUM | v19: don't mix `_sql_constraints` and `models.Constraint()` |