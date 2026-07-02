# Odoo Model Patterns Migration Guide: 17.0 → 18.0

<pattern>

<description>
  Migration guide for model patterns from Odoo 17.0 to 18.0. The three breaking changes are:
  `group_operator=` renamed to `aggregator=` on field definitions; `&lt;tree&gt;` tag renamed
  to `&lt;list&gt;` in XML views; and chatter replaced from `&lt;div class="oe_chatter"&gt;`
  to `&lt;chatter reload_on_attachment="True"/&gt;`.

  Note: `_check_company_auto` and `check_company=True` are NOT new in v18 — they are confirmed
  present in v17 source (account.move.line line 25). The canonical change in v18 is
  `allowed_company_ids` replacing `company_ids` in record rule domain_force expressions.

  Verified against real Odoo 17.0 and 18.0 source: account.move.line and account.move views.
</description>

<version_notes>
  <version id="17">
    <change type="feature">group_operator= on fields for aggregate behavior</change>
    <change type="feature">XML list views use &lt;tree&gt; tag</change>
    <change type="feature">Chatter: &lt;div class="oe_chatter"&gt; with message_follower_ids, activity_ids, message_ids — confirmed in views_17.xml line 1387</change>
    <change type="feature">_check_company_auto = True and check_company=True already available — confirmed in model_17.py line 25</change>
    <change type="feature">SQL() available via from odoo.tools.sql import SQL — confirmed in model_17.py line 11</change>
  </version>
  <version id="18">
    <change type="breaking">group_operator= renamed to aggregator= on field definitions — confirmed in model_18.py lines 73, 78, 253, 409</change>
    <change type="breaking">&lt;tree&gt; tag renamed to &lt;list&gt; in XML views — confirmed in views_18.xml</change>
    <change type="breaking">Chatter: &lt;div class="oe_chatter"&gt; replaced by &lt;chatter reload_on_attachment="True"/&gt; — confirmed in views_18.xml line 1507</change>
    <change type="breaking">allowed_company_ids replaces company_ids in record rule domain_force expressions</change>
    <change type="feature">SQL() import path: from odoo.tools.sql import SQL — confirmed in model_18.py line 11</change>
    <change type="recommended">Type hints on method signatures — recommended convention, not mandatory</change>
  </version>
</version_notes>

<examples>

  <example id="breaking_aggregator" title="BREAKING: group_operator renamed to aggregator">

```python
# v17 — confirmed in model_17.py lines 65, 70, 131
date = fields.Date(
    related='move_id.date',
    store=True,
    group_operator='min',
)
amount_currency = fields.Monetary(
    group_operator=None,
)

# v18 — confirmed in model_18.py lines 73, 78, 253
date = fields.Date(
    related='move_id.date',
    store=True,
    aggregator='min',
)
amount_currency = fields.Monetary(
    aggregator=None,
)
```

  </example>

  <example id="breaking_list_tag" title="BREAKING: &lt;tree&gt; renamed to &lt;list&gt; in views">

```xml
<!-- v17 — confirmed in views_17.xml -->
<tree decoration-danger="state == 'cancelled'"
      decoration-success="state == 'done'">
    <field name="name"/>
    <field name="state" widget="badge"/>
</tree>

<!-- Inside One2many fields also uses tree in v17 -->
<field name="line_ids">
    <tree editable="bottom">
        <field name="name"/>
        <field name="quantity"/>
    </tree>
</field>

<!-- v18 — confirmed in views_18.xml -->
<list decoration-danger="state == 'cancelled'"
      decoration-success="state == 'done'">
    <field name="name"/>
    <field name="state" widget="badge"/>
</list>

<!-- Inside One2many in v18 -->
<field name="line_ids">
    <list editable="bottom">
        <field name="name"/>
        <field name="quantity"/>
    </list>
</field>
```

  </example>

  <example id="breaking_chatter" title="BREAKING: chatter syntax changed">

```xml
<!-- v17 — confirmed in views_17.xml lines 1387-1391 -->
<div class="oe_chatter">
    <field name="message_follower_ids" groups="base.group_user"/>
    <field name="activity_ids"/>
    <field name="message_ids" options="{'post_refresh': 'always'}"/>
</div>

<!-- v18 — confirmed in views_18.xml line 1507 -->
<chatter reload_on_attachment="True"/>
```

  </example>

  <example id="breaking_record_rules" title="BREAKING: allowed_company_ids in record rules">

```xml
<!-- v17 record rule -->
<field name="domain_force">[
    ('company_id', 'in', company_ids)
]</field>

<!-- v18 — company_ids replaced by allowed_company_ids -->
<field name="domain_force">[
    ('company_id', 'in', allowed_company_ids)
]</field>
```

  </example>

  <example id="sql_import" title="SQL() import path — available in both v17 and v18">

```python
# v17 and v18 — same import path (confirmed in model_17.py line 11, model_18.py line 11)
from odoo.tools.sql import create_index, SQL

# v17 — raw string SQL still common (no breaking change, SQL() just recommended in v18)
def _get_statistics(self):
    query = """
        SELECT partner_id, SUM(amount) AS total
        FROM %s
        WHERE company_id = %%s AND state = %%s
        GROUP BY partner_id
    """ % self._table
    self.env.cr.execute(query, (self.env.company.id, 'confirmed'))
    return self.env.cr.dictfetchall()

# v18 recommended — SQL() builder for safer composition
def _get_statistics(self):
    query = SQL(
        """
        SELECT partner_id, SUM(amount) AS total
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

  <example id="company_check" title="_check_company_auto and check_company — present in both v17 and v18">

```python
# Both patterns confirmed in model_17.py (lines 25, 41, 95) and model_18.py (lines 25, 41, 95)
# No migration needed — if already using them in v17, they carry over to v18 unchanged.

class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True  # present since v17

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        check_company=True,  # present since v17
    )
```

  </example>

  <example id="migration_checklist" title="Full migration checklist v17 → v18">

```
BREAKING CHANGES — must fix:
[ ] Rename group_operator= to aggregator= on all field definitions
[ ] Rename <tree> to <list> in all XML view files (top-level views and inside One2many)
[ ] Replace <div class="oe_chatter"> block with <chatter reload_on_attachment="True"/>
[ ] Update record rules: replace company_ids with allowed_company_ids in domain_force

RECOMMENDED — not breaking but good practice:
[ ] Adopt SQL() builder for new raw SQL methods (from odoo.tools.sql import SQL)
[ ] Add type hints to new method signatures
[ ] Use SQL.identifier() for table/column names in SQL() calls
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using `group_operator=` on fields in v18 — renamed to `aggregator=`.

```python
# WRONG in v18
date = fields.Date(group_operator='min')

# CORRECT in v18
date = fields.Date(aggregator='min')
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using `&lt;tree&gt;` tag in v18 XML views — renamed to `&lt;list&gt;`.

```xml
<!-- WRONG in v18 -->
<tree><field name="name"/></tree>

<!-- CORRECT in v18 -->
<list><field name="name"/></list>
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Using `&lt;div class="oe_chatter"&gt;` block in v18 — replaced by `&lt;chatter/&gt;`.

```xml
<!-- WRONG in v18 -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>

<!-- CORRECT in v18 -->
<chatter reload_on_attachment="True"/>
```
  </antipattern>

  <antipattern severity="HIGH">
    Using `company_ids` in record rule `domain_force` in v18 — replaced by `allowed_company_ids`.

```xml
<!-- WRONG in v18 -->
<field name="domain_force">[('company_id', 'in', company_ids)]</field>

<!-- CORRECT in v18 -->
<field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>
```
  </antipattern>

  <antipattern severity="MEDIUM">
    Claiming `_check_company_auto` is a new v18 feature — it is confirmed present in v17
    (model_17.py line 25). No migration needed for this attribute.
  </antipattern>

  <antipattern severity="HIGH">
    Using raw string SQL with table name interpolation without `SQL.identifier()` — SQL injection risk.

```python
# WRONG — table name via % formatting is injection risk
query = "SELECT * FROM %s WHERE id = %%s" % self._table

# CORRECT — use SQL.identifier() for identifiers
query = SQL("SELECT * FROM %s WHERE id = %s", SQL.identifier(self._table), self.id)
```
  </antipattern>

</antipatterns>

</pattern>