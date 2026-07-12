# Performance Guide — v17/v18/v19

---

## N+1 prevention

```python
# BAD: one query per record
for order in orders:
    print(order.partner_id.name)

# GOOD: prefetch first
orders.mapped('partner_id')
for order in orders:
    print(order.partner_id.name)

# BETTER: search_read for specific fields
data = self.env['sale.order'].search_read(domain, ['name', 'partner_id'], limit=100)
```

## Batch operations

```python
# BAD: create in loop → N inserts
for d in data_list: self.env['my.model'].create(d)
# GOOD: single call
self.env['my.model'].create(data_list)

# BAD: write per record
for r in records: r.write({'state': 'done'})
# GOOD: batch write
records.write({'state': 'done'})
```

## Count without loading

```python
# BAD: len(search(...))
# GOOD:
count = self.env['my.model'].search_count(domain)
```

## Batch aggregation in compute

```python
@api.depends('partner_id')
def _compute_order_count(self):
    if not self: return
    data = self.env['sale.order']._read_group(
        [('partner_id', 'in', self.mapped('partner_id').ids)],
        ['partner_id'], ['__count'])
    mapped = {p.id: c for p, c in data}
    for rec in self:
        rec.order_count = mapped.get(rec.partner_id.id, 0)
```

## Field indexing

```python
name = fields.Char(index='trigram')       # ILIKE searches
state = fields.Selection([...], index=True)  # equality
code = fields.Char(index='btree_not_null')   # sparse data

# v19: multi-column
_partner_date_idx = models.Index("(partner_id, date)")
_partial_idx = models.Index("(account_id) WHERE reconciled IS NOT TRUE")
```

## Stored vs non-stored compute

- **Stored**: computed once, updated on dependency change → frequent reads, rare updates
- **Non-stored**: every read → values change constantly or rarely displayed

## Raw SQL + cache invalidation

```python
# v17/v18: from odoo.tools.sql import SQL
# v19: from odoo.tools import SQL
self.env.cr.execute(SQL("UPDATE %s SET state = %s WHERE id IN %s",
    SQL.identifier(self._table), 'done', tuple(ids)))
self.env['my.model'].invalidate_model(['state'])  # REQUIRED after raw SQL
```

## Algorithmic complexity

```python
# BAD: O(n²) list membership
invalid = self.search(domain).ids  # list
for r in self:
    if r.id in invalid: ...  # O(n) scan

# GOOD: O(n) set lookup
invalid = set(self.search(domain).ids)
```

## Cron batch processing

```python
@api.model
def _cron_process(self):
    batch_size = 1000
    while True:
        records = self.search([('state', '=', 'pending')], limit=batch_size)
        if not records: break
        for rec in records:
            try: rec._process()
            except Exception as e: _logger.error("Failed %s: %s", rec.id, e)
        self.env.cr.commit()
        self.env.invalidate_all()
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `browse()`/`search()` inside loops |
| CRITICAL | N+1: prefetch with `mapped()` before iterating relations |
| HIGH | `len(search(...))` → `search_count()` |
| HIGH | Per-record `search_count` in compute → `_read_group()` |
| HIGH | v18+: `group_operator=` → `aggregator=` |
| MEDIUM | Always `invalidate_model()` after raw SQL writes |
| MEDIUM | Don't `sudo()` inside loops — cache outside |