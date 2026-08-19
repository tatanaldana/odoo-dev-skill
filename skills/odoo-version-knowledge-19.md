# Odoo Version Knowledge — v19

Key changes, patterns, and reference for Odoo 19.0.
Python 3.12+ | OWL 2.x (NOT 3.x)

---

## Breaking changes from v18

| Area | v18 | v19 |
|------|-----|-----|
| Constraints | `_sql_constraints = [...]` | `_my_attr = models.Constraint('sql', 'msg')` (arbitrary attribute name, bare instance not a list) |
| Indexes | manual / `index=True` | `_my_attr = models.Index("(col1, col2)")` (arbitrary attribute name, bare instance not a list) |
| Domain class | not available | `from odoo.fields import Command, Domain` |
| M2O bypass | not available | `bypass_search_access=True` |
| `odoo.osv.expression` | available, no warning | deprecated (`DeprecationWarning` at instantiation, "Since 19.0") → use `odoo.fields.Domain` |
| `record._cr/_context/_uid` | available | deprecated → `self.env.cr/.context/.uid` |
| OWL `readGroup()` | available | removed → `formattedReadGroup()` |
| OWL new | — | `orm.cache()`, `webSaveMulti()`, `webResequence()` |

## NOT changed from v18

- `<list>`, `<chatter/>`, `aggregator=`, `invisible=` — same
- `from odoo import _` — still valid (36 files in account/models use it)
- Type hints — optional (only ~3/3740 lines in account.move.line use them, e.g. `_field_to_sql`, `_reconciled_by_number`)
- `SQL()` — both `from odoo.tools import SQL` and `from odoo.tools.sql import SQL` work in v17/v18/v19 alike; NOT a v18→v19 breaking change (12 files in v19 addons still use the `.sql` form)
- Record rules: `company_ids` in `domain_force`

---

## Model skeleton (v19-specific parts only)

```python
from odoo import api, fields, models, _
from odoo.fields import Command, Domain
from odoo.tools import SQL  # from odoo.tools.sql import SQL also still works

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
| CRITICAL | `_sql_constraints` → `models.Constraint()` in v19 (bare attribute, never list) — logs `_logger.warning(...)` and is silently non-functional, does not raise |
| HIGH | `record._cr/_context/_uid` deprecated → use `self.env.*` |
| HIGH | `from odoo.osv import expression` → prefer `from odoo.fields import Domain` (the `.osv.expression` module still exists but raises `DeprecationWarning` on use) |
| HIGH | `models.Constraint()`/`models.Index()` never wrapped in a list |
| CRITICAL | Type hints NOT mandatory — don't flag absence |