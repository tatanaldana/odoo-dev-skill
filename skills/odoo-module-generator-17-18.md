# Odoo Module Migration Guide: 17.0 → 18.0

<pattern>

<description>
Migration patterns for upgrading Odoo modules from 17.0 to 18.0.
Use when working on modules that must support one or both versions,
or when migrating an existing v17 module to v18.
</description>

<version_notes>
  <version id="17">
    Baseline: `group_operator=` on fields, `&lt;tree&gt;` tag, `oe_chatter` div,
    `from odoo.tools.sql import SQL`, `/** @odoo-module **/` required in JS.
  </version>
  <version id="18">
    Breaking: `group_operator=` → `aggregator=` on fields.
    Breaking: `&lt;tree&gt;` → `&lt;list&gt;` tag in XML views.
    Breaking: `oe_chatter` div → `&lt;chatter/&gt;` (bare, self-closing — dominant form in real 18.0/19.0 source).
    New: `export_string_translation=False` on fields.
    New: `web.assets_unit_tests` key in manifest.
    New: `@odoo-module` comment no longer required in JS.
    Recommended: type hints on method signatures.
    Recommended: `SQL()` builder for raw SQL (import from `odoo.tools.sql`).
    Multi-company record rules: `company_ids` in `domain_force` — unchanged from v17.
  </version>
</version_notes>

<examples>

  <example id="breaking_group_operator" title="BREAKING: group_operator= renamed to aggregator=">

Before (v17):
```python
amount = fields.Float(group_operator='sum')
quantity = fields.Float(group_operator='avg')
```

After (v18):
```python
amount = fields.Float(aggregator='sum')
quantity = fields.Float(aggregator='avg')
```

  </example>

  <example id="breaking_tree_to_list" title="BREAKING: tree tag renamed to list">

Before (v17):
```xml
<tree editable="bottom">
    <field name="name"/>
    <field name="amount"/>
</tree>
```

After (v18):
```xml
<list editable="bottom">
    <field name="name"/>
    <field name="amount"/>
</list>
```

Also applies to standalone list views:
```xml
<!-- v17 -->
<tree string="Records" multi_edit="1">...</tree>

<!-- v18 -->
<list string="Records" multi_edit="1">...</list>
```

  </example>

  <example id="breaking_chatter" title="BREAKING: oe_chatter div replaced by chatter tag">

Before (v17):
```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

After (v18):
```xml
<chatter/>
```

Note: the attribute varies by model — `reload_on_attachment` for documents,
`reload_on_follower` for task-like models. Use `reload_on_attachment` as the default.

  </example>

  <example id="breaking_owl_module_comment" title="BREAKING: @odoo-module comment no longer required in v18">

Before (v17 — REQUIRED):
```javascript
/** @odoo-module **/

import { Component } from "@odoo/owl";
```

After (v18 — comment not needed):
```javascript
import { Component } from "@odoo/owl";
```

  </example>

  <example id="sql_builder" title="Recommended: SQL() builder for raw SQL queries">

v17 — raw SQL (still allowed but injection-prone):
```python
query = """
    SELECT partner_id, SUM(amount) as total
    FROM %s
    WHERE company_id = %s AND state = '%s'
    GROUP BY partner_id
""" % (self._table, self.env.company.id, 'confirmed')
self.env.cr.execute(query)
```

v18 — SQL builder (recommended, import from odoo.tools.sql):
```python
from odoo.tools.sql import SQL

query = SQL(
    """
    SELECT partner_id, SUM(amount) as total
    FROM %s
    WHERE company_id = %s AND state = %s
    GROUP BY partner_id
    """,
    SQL.identifier(self._table),
    self.env.company.id,
    'confirmed',
)
self.env.cr.execute(query)
return self.env.cr.dictfetchall()
```

  </example>

  <example id="type_hints" title="Recommended: type hints on method signatures">

v17 (no type hints):
```python
def process_partner(self, partner_id, options=None):
    partner = self.env['res.partner'].browse(partner_id)
    return partner.name
```

v18 (type hints recommended):
```python
from typing import Optional, Any

def process_partner(
    self,
    partner_id: int,
    options: Optional[dict[str, Any]] = None,
) -> str:
    partner = self.env['res.partner'].browse(partner_id)
    return partner.name
```

  </example>

  <example id="export_string_translation" title="New in v18: export_string_translation=False">

```python
# v18: Suppress translation export for internal/computed fields
internal_ref = fields.Char(
    string='Internal Reference',
    export_string_translation=False,
)
```

  </example>

  <example id="record_rules" title="Multi-company record rules — company_ids unchanged">

Both v17 and v18 use `company_ids` in `domain_force` (confirmed in official source):
```xml
<record id="rule_my_model_company" model="ir.rule">
    <field name="name">My Model: Multi-Company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="global" eval="True"/>
    <field name="domain_force">[
        '|',
        ('company_id', '=', False),
        ('company_id', 'in', company_ids)
    ]</field>
</record>
```

  </example>

  <example id="manifest_version" title="Manifest version string update">

```python
# v17
'version': '17.0.1.0.0',

# v18
'version': '18.0.1.0.0',
```

  </example>

  <example id="migration_checklist" title="Migration checklist 17 → 18">

Models (Python):
- Replace `group_operator=` with `aggregator=` on all fields
- Add type hints to method signatures (recommended)
- Replace raw SQL with `SQL()` builder (recommended)
- Update `from odoo.tools.sql import SQL` (same path in v18, changes in v19)
- Add `export_string_translation=False` on internal fields where needed
- Update manifest version from `17.0.x.x.x` to `18.0.x.x.x`

Views (XML):
- Replace ALL `&lt;tree&gt;` tags with `&lt;list&gt;`
- Replace `oe_chatter` div with `&lt;chatter/&gt;` (bare, self-closing — dominant form in real 18.0/19.0 source)
- Verify no `attrs=` remain (removed since v17)

JavaScript (OWL):
- Remove `/** @odoo-module **/` comment if desired (no longer required)
- Verify service usage patterns work in v18

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Keeping `group_operator=` in v18 — the field will not aggregate correctly.

    ```python
    # WRONG in v18
    amount = fields.Float(group_operator='sum')

    # CORRECT in v18
    amount = fields.Float(aggregator='sum')
    ```
  </antipattern>

  <antipattern severity="CRITICAL">
    Keeping `&lt;tree&gt;` tags in v18 views — the view will not render.

    Replace all occurrences of `&lt;tree&gt;` with `&lt;list&gt;`.
  </antipattern>

  <antipattern severity="CRITICAL">
    Keeping the `oe_chatter` div in v18 — the chatter will not load.

    ```xml
    <!-- WRONG in v18 -->
    <div class="oe_chatter">...</div>

    <!-- CORRECT in v18 -->
    <chatter/>
    ```
  </antipattern>

  <antipattern severity="MEDIUM">
    Using raw SQL string interpolation — injection risk and discouraged in v18.

    ```python
    # RISKY — use SQL() builder instead
    query = "SELECT * FROM %s WHERE id = %s" % (self._table, record_id)
    ```
  </antipattern>

</antipatterns>

</pattern>