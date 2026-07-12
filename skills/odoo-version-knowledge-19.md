# Odoo Version Knowledge — v19

Key changes, patterns, and reference for Odoo 19.0.
Python 3.12+ | OWL 2.x (NOT 3.x)

---

## Breaking changes from v18

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_name = models.Constraint('sql', 'msg')` (bare attribute) |
| Indexes | manual / `index=True` | `_name = models.Index("(col1, col2)")` (bare attribute) |
| SQL import | `from odoo.tools.sql import SQL` | `from odoo.tools import SQL` |
| Domain class | not available | `from odoo.fields import Command, Domain` |
| M2O bypass | not available | `bypass_search_access=True` |
| `odoo.osv` | available | deprecated → `from odoo import expression` |
| `record._cr/_context/_uid` | available | deprecated → `self.env.cr/.context/.uid` |
| OWL `readGroup()` | available | removed → `formattedReadGroup()` |
| OWL new | — | `orm.cache()`, `webSaveMulti()`, `webResequence()` |

## NOT changed from v18

- `<list>`, `<chatter/>`, `aggregator=`, `invisible=` — same
- `from odoo import _` — still valid (36 files in account/models use it)
- Type hints — optional (only 2/3700 lines in account.move.line)
- `SQL()` — recommended not mandatory
- Record rules: `company_ids` in `domain_force`

---

## Model skeleton (v19-specific parts only)

```python
from odoo import api, fields, models, _
from odoo.fields import Command, Domain
from odoo.tools import SQL  # NOT odoo.tools.sql

class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    parent_id = fields.Many2one('my.parent', bypass_search_access=True, ondelete='cascade')

    _name_uniq = models.Constraint('unique(company_id, name)', 'Must be unique!')
    _check_positive = models.Constraint('CHECK(amount >= 0)', 'Must be positive!')
    _partner_date_idx = models.Index("(partner_id, date)")
    _active_idx = models.Index("(state) WHERE active IS TRUE")
```

## OWL component (v19)

```javascript
// No @odoo-module needed
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyComponent extends Component {
    static template = "my_module.MyComponent";
    setup() {
        this.orm = useService("orm");
        this.state = useState({ data: [], loading: true });
        onWillStart(async () => { await this.loadData(); });
    }
    async loadData() {
        this.state.data = await this.orm.searchRead("my.model", [], ["name", "state"]);
        this.state.loading = false;
    }
}
registry.category("actions").add("my_module.my_action", MyComponent);
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `_sql_constraints` → `models.Constraint()` in v19 (bare attribute, never list) |
| CRITICAL | SQL import: `from odoo.tools import SQL` (not `.sql`) |
| HIGH | `record._cr/_context/_uid` deprecated → use `self.env.*` |
| HIGH | `from odoo.osv import expression` → `from odoo import expression` |
| HIGH | `models.Constraint()`/`models.Index()` never wrapped in a list |
| CRITICAL | Type hints NOT mandatory — don't flag absence |