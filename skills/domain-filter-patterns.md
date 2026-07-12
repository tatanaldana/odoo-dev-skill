# Domain & Filter Patterns — v17/v18/v19

---

## Basic syntax

```python
# Implicit AND between tuples
domain = [('state', '=', 'draft'), ('partner_id', '!=', False), ('amount', '>', 1000)]

# Operators: =, !=, <, >, <=, >=, like, ilike, in, not in, child_of, parent_of
```

## Logical operators (prefix — apply to NEXT two terms)

```python
# OR
['|', ('state', '=', 'draft'), ('state', '=', 'cancel')]

# Complex: (draft OR cancel) AND partner set
['&', '|', ('state', '=', 'draft'), ('state', '=', 'cancel'), ('partner_id', '!=', False)]

# Triple OR: need N-1 '|' operators
['|', '|', ('state', '=', 'a'), ('state', '=', 'b'), ('state', '=', 'c')]
```

## expression module (v17/v18)

```python
from odoo.osv import expression
combined = expression.AND([domain_a, domain_b])
either = expression.OR([domain_a, domain_b])
```

## Domain object (v19)

```python
from odoo.fields import Domain
domain = Domain('state', '=', 'draft') & Domain('partner_id', '!=', False)
combined = Domain.OR([domain_a, domain_b])
```

## domain= on fields

```python
partner_id = fields.Many2one('res.partner',
    domain="['|', ('company_id', '=', False), ('company_id', '=?', company_id)]")
stage_id = fields.Many2one('project.task.type',
    domain="[('project_ids', '=', project_id)]")
```

## filtered() for in-memory filtering

```python
active_users = self.user_ids.filtered('active')
draft_records = self.line_ids.filtered(lambda l: l.state == 'draft')
```

## Action domain

```python
def action_view_tasks(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window', 'res_model': 'project.task',
        'domain': [('project_id', '=', self.id)], 'view_mode': 'list,form',
    }
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `search()` inside loops — use `('field', 'in', ids)` |
| CRITICAL | Prefix `\|` applies to exactly 2 terms — miscounting breaks logic |
| HIGH | `allowed_company_ids` NOT valid in `domain_force` — use `company_ids` |
| MEDIUM | No hardcoded IDs — use `env.ref()` |
| MEDIUM | No `browse()` in loop to filter — use `filtered()` |