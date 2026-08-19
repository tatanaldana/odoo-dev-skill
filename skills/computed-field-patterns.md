# Computed Field Patterns — v17/v18/v19

---

## Version differences

| Feature | v17 | v18/v19 |
|---------|-----|---------|
| Aggregation | `group_operator='min'` | `aggregator='min'` |
| SQL import | `odoo.tools.sql` | `odoo.tools` |

> Both `from odoo.tools.sql import SQL` and `from odoo.tools import SQL` work unchanged in **all three** versions (17.0, 18.0, 19.0) — `odoo/tools/__init__.py` does `from .sql import *` in every branch (confirmed via `git show {17.0,18.0,19.0}:odoo/tools/__init__.py`). There is no v19-specific import break; prefer `from odoo.tools import SQL` for style, not because the other path stops working.

---

## Stored computed + editable

```python
total = fields.Monetary(compute='_compute_total', store=True, currency_field='currency_id')
name = fields.Char(compute='_compute_name', store=True, readonly=False, precompute=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for rec in self:
        rec.total = sum(rec.line_ids.mapped('amount'))
```

## Inverse (bidirectional)

```python
debit = fields.Monetary(compute='_compute_debit_credit', inverse='_inverse_debit', store=True)

@api.depends('balance')
def _compute_debit_credit(self):
    for line in self:
        line.debit = line.balance if line.balance > 0 else 0.0
        line.credit = -line.balance if line.balance < 0 else 0.0

def _inverse_debit(self):
    for line in self:
        line.balance = line.debit - line.credit
```

## Non-stored with search

```python
portal_names = fields.Char(compute='_compute_portal_names', compute_sudo=True,
    search='_search_portal_names')

def _search_portal_names(self, operator, value):
    return [('user_ids.name', operator, value)]
```

## Aggregation

```python
# v17
date = fields.Date(related='move_id.date', store=True, group_operator='min')
# v18/v19
date = fields.Date(related='move_id.date', store=True, aggregator='min')
```

## Related + precompute

```python
journal_id = fields.Many2one(related='move_id.journal_id', store=True, precompute=True, index=True)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `@api.depends('move_id')` incomplete — use `@api.depends('move_id.date')` |
| CRITICAL | No ORM search inside compute without full dependency chain |
| MEDIUM | `group_operator=` → `aggregator=` in v18+ (soft deprecation: still accepted, auto-remapped to `aggregator` with a `DeprecationWarning`, per `odoo/orm/fields.py` line ~485 in 19.0 and `odoo/fields.py` line ~480 in 18.0 — not a hard break) |
| HIGH | Non-stored compute in domain without `search=` method crashes |