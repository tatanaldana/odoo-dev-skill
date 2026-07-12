# Security Guide — Version Dispatcher

Route to version-specific file. Do NOT generate security code from this file.

| Target | File |
|--------|------|
| v17 | `odoo-security-guide-17.md` |
| v18 | `odoo-security-guide-18.md` |
| v19 | `odoo-security-guide-19.md` |
| v17→v18 | `odoo-security-guide-17-18.md` |
| v18→v19 | `odoo-security-guide-18-19.md` |

## Version detection

| Indicator | Version |
|-----------|---------|
| `attrs=` in views | pre-v17 |
| `group_operator=` | v17 |
| `aggregator=` | v18+ |
| `SQL` from `odoo.tools.sql` | v18 |
| `SQL` from `odoo.tools` | v19 |
| `models.Constraint()` | v19 |