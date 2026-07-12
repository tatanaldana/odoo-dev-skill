# Odoo Module Generator — Version Dispatcher

Route to the correct version-specific file. Do NOT generate code from this file.

## Version routing

| Target | File |
|--------|------|
| 17.0 | `odoo-module-generator-17.md` |
| 18.0 | `odoo-module-generator-18.md` |
| 19.0 | `odoo-module-generator-19.md` |

Migration: `odoo-module-generator-17-18.md`, `odoo-module-generator-18-19.md`

## Workflow

1. Identify target version (ask if unspecified)
2. Load version-specific file
3. Generate with ONLY that version's patterns

## Version detection from code

| Indicator | Version |
|-----------|---------|
| `attrs=` in views | ≤v16 |
| `invisible=` directly | v17+ |
| `group_operator=` | v17 |
| `aggregator=` | v18+ |
| `<tree>` | v17 |
| `<list>` | v18+ |
| `oe_chatter` div | v17 |
| `<chatter/>` | v18+ |
| `models.Constraint()` | v19 |
| `models.Index()` | v19 |