# Constraint Patterns — v17/v18/v19

SQL constraints + Python constraints + company validation.

---

## Version differences

| Feature | v17/v18 | v19 |
|---------|---------|-----|
| SQL constraints | `_sql_constraints = [(...)]` | `_name = models.Constraint('SQL', 'msg')` |
| Indexes | `init()` + `create_index()` | `_name = models.Index("(cols)")` |
| `@api.constrains` | identical | identical |
| `_check_company_auto` | available since v17 | same |

---

## SQL constraints (v17/v18)

```python
_sql_constraints = [
    ('check_discount', 'CHECK(discount >= 0 AND discount <= 100)', 'Discount 0-100.'),
    ('unique_ref', 'UNIQUE(company_id, name)', 'Unique per company.'),
]
```

## models.Constraint (v19)

```python
_check_discount = models.Constraint('CHECK(discount >= 0 AND discount <= 100)', 'Discount 0-100.')
_unique_ref = models.Constraint('UNIQUE(company_id, name)', 'Unique per company.')
```

## Python constraint (@api.constrains — all versions)

```python
@api.constrains('date_start', 'date_deadline')
def _check_dates(self):
    for task in self:
        if task.date_start and task.date_deadline and task.date_start > task.date_deadline:
            raise ValidationError(_('Start must be before deadline.'))
```

## Company constraint (all versions)

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True
    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
```

## Indexes

```python
# v17/v18
def init(self):
    create_index(self._cr, 'my_idx', self._table, ['account_id', 'date'])

# v19
_account_date_idx = models.Index("(account_id, date)")
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Don't `@api.constrains` on non-stored computed fields — never fires |
| HIGH | Don't catch/suppress ValidationError inside constrains |
| HIGH | `models.Constraint()` takes 2 args (sql, msg) — name is the attribute name |
| MEDIUM | List ALL read fields in `@api.constrains` decorator |