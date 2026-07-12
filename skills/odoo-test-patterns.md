# Test Patterns — v17/v18/v19

TransactionCase, HttpCase, security tests, form simulation.

---

## TransactionCase (unit tests)

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError, AccessError

class TestMyModel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.record = cls.env['my.model'].create({
            'name': 'Test', 'partner_id': cls.partner.id,
        })

    def test_action_confirm(self):
        self.record.action_confirm()
        self.assertEqual(self.record.state, 'confirmed')

    def test_confirm_without_lines_raises(self):
        with self.assertRaises(UserError):
            self.record.action_confirm()

    def test_constraint_positive_amount(self):
        with self.assertRaises(ValidationError):
            self.record.write({'amount': -1})

    def test_unlink_confirmed_raises(self):
        self.record.action_confirm()
        with self.assertRaises(UserError):
            self.record.unlink()

    def test_compute_total(self):
        self.env['my.model.line'].create({'model_id': self.record.id, 'amount': 100})
        self.env['my.model.line'].create({'model_id': self.record.id, 'amount': 200})
        self.assertEqual(self.record.total_amount, 300)
```

## Security tests

```python
class TestMyModelSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_basic = cls.env['res.users'].create({
            'name': 'Basic', 'login': 'basic',
            'groups_id': [(6, 0, [cls.env.ref('my_module.group_user').id])],
        })
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Manager', 'login': 'manager',
            'groups_id': [(6, 0, [cls.env.ref('my_module.group_manager').id])],
        })

    def test_basic_cannot_unlink(self):
        record = self.env['my.model'].with_user(self.user_basic).create({'name': 'Test'})
        with self.assertRaises(AccessError):
            record.unlink()

    def test_manager_can_unlink(self):
        record = self.env['my.model'].with_user(self.user_manager).create({'name': 'Test'})
        record.unlink()

    def test_multi_company_isolation(self):
        company_b = self.env['res.company'].create({'name': 'Company B'})
        record = self.env['my.model'].create({'name': 'A', 'company_id': self.env.company.id})
        records_b = self.env['my.model'].with_company(company_b).search([])
        self.assertNotIn(record, records_b)
```

## HttpCase (OWL / tours)

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestMyWidget(HttpCase):

    def test_widget_loads(self):
        self.start_tour('/web', 'my_module.tour_name', login='admin')
```

## Form simulation (onchange testing)

```python
from odoo.tests import Form

def test_onchange_product(self):
    with Form(self.env['sale.order.line']) as line_form:
        line_form.product_id = self.product
        self.assertEqual(line_form.price_unit, self.product.lst_price)
```

## Query count assertion

```python
def test_batch_performance(self):
    with self.assertQueryCount(admin=5):
        self.env['my.model'].create([{'name': f'R{i}'} for i in range(100)])
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Use `setUpClass` (not `setUp`) for shared fixtures — avoids per-test DB writes |
| HIGH | Always test security: AccessError for unauthorized, success for authorized |
| HIGH | Test multi-company isolation with `with_company()` |
| MEDIUM | Use `Form()` to test onchange — don't call `_onchange_*` directly |
| MEDIUM | Tag HttpCase tests `@tagged('post_install', '-at_install')` |