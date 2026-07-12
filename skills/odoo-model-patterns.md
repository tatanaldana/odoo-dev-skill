# Odoo Model Patterns — Version Dispatcher

Route to correct version file. Do NOT generate code from this file.

## Routing

| Target | File |
|--------|------|
| 17.0 | `odoo-model-patterns-17.md` |
| 18.0 | `odoo-model-patterns-18.md` |
| 19.0 | `odoo-model-patterns-19.md` |
| 17→18 | `odoo-model-patterns-17-18.md` |
| 18→19 | `odoo-model-patterns-18-19.md` |

## Version detection

| Indicator | Version |
|-----------|---------|
| `@api.multi` | v14 (removed v15) |
| `tracking=True` | v15+ |
| `Command` class | v16+ |
| `@api.model_create_multi` mandatory | v17+ |
| `attrs=` in views | ≤v16 |
| `group_operator=` | v17 |
| `aggregator=` | v18+ |
| `<tree>` | v17 |
| `<list>` | v18+ |
| `oe_chatter` div | v17 |
| `<chatter/>` | v18+ |
| `models.Constraint()` | v19 |
| `models.Index()` | v19 |
| `from odoo.fields import Domain` | v19 |