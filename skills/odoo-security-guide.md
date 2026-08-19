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
| `group_operator=` | v17 (deprecated w/ warning, still works, in v18+) |
| `aggregator=` | v18+ |
| `models.Constraint()` | v19 |

Note: the `SQL()` builder class (`odoo/tools/sql.py`) exists since v17. Both
`from odoo.tools.sql import SQL` and `from odoo.tools import SQL` work unchanged
in v17, v18 and v19 (the module is re-exported via `from .sql import *` in all
three) — this is NOT a reliable version indicator, despite what earlier
revisions of this guide claimed.