# Odoo Model Patterns Migration Guide: 17.0 → 18.0

<pattern>

<description>
  Migration guide for model patterns from Odoo 17.0 to 18.0. The three breaking changes are:
  `group_operator=` renamed to `aggregator=` on field definitions; `&lt;tree&gt;` tag renamed
  to `&lt;list&gt;` in XML views; and chatter replaced from `&lt;div class="oe_chatter"&gt;`
  to the self-closing `&lt;chatter/&gt;` tag (optional attributes like
  `reload_on_attachment`/`reload_on_follower`/`reload_on_post` exist for specific views but
  are not required — most 18.0/19.0 views just use bare `&lt;chatter/&gt;`).

  Note: `_check_company_auto` and `check_company=True` are NOT new in v18 — they are confirmed
  present in v17 source (account.move.line line 25). Record rules keep using `company_ids` in
  `domain_force` in v18 — this is unchanged from v17 (see corrected note below).

  Verified against real Odoo 17.0 and 18.0 source: account.move.line, account.move views, and
  addons/account/security/account_security.xml (real ir.rule domain_force examples), addons/sale/views/sale_order_views.xml (real chatter tag usage).
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
    <change type="breaking">Chatter: &lt;div class="oe_chatter"&gt; replaced by self-closing &lt;chatter/&gt; — confirmed as the dominant form (65 occurrences with no attributes) in addons/sale/views/sale_order_views.xml line 921 of real 18.0/19.0 source; optional attributes (reload_on_attachment, reload_on_follower, reload_on_post, open_attachments, groups, position) exist in specific views (account_move_views.xml, hr_employee_views.xml, etc.) but are not required</change>
    <change type="not-a-change">Record rules: domain_force still uses company_ids in v18 — NOT replaced by allowed_company_ids. Confirmed unchanged against addons/account/security/account_security.xml in both 18.0 and 19.0 branches. `allowed_company_ids` is a real Odoo context variable, but it is used in view-level field domain= attributes (client-side eval context), never in ir.rule domain_force. A prior version of this file incorrectly claimed this was a breaking change — corrected here.</change>
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

Note: only the XML arch root/nested tag is renamed. Existing `ir.ui.view` record `id`s
(e.g. `id="sale_order_tree"`) are NOT renamed in real Odoo source — renaming an established
external ID would break every module that inherits it via `inherit_id`. Only the human-readable
`name` field (e.g. `"sale.order.tree"` → `"sale.order.list"`) and `view_mode` field values
(`tree,form` → `list,form`) are updated.

  </example>

  <example id="breaking_chatter" title="BREAKING: chatter syntax changed">

```xml
<!-- v17 — confirmed in views_17.xml lines 1387-1391 -->
<div class="oe_chatter">
    <field name="message_follower_ids" groups="base.group_user"/>
    <field name="activity_ids"/>
    <field name="message_ids" options="{'post_refresh': 'always'}"/>
</div>

<!-- v18 — bare self-closing tag, confirmed as the dominant form in real source
     (addons/sale/views/sale_order_views.xml line 921, and 65 other occurrences
     across 18.0/19.0 addons with no attributes at all) -->
<chatter/>

<!-- v18 — optional attributes exist for specific behaviors, used only where needed
     (confirmed in addons/account/views/account_move_views.xml line 1507,
     addons/hr/views/hr_employee_views.xml, addons/crm/views/crm_lead_views.xml) -->
<chatter reload_on_attachment="True"/>
<chatter reload_on_follower="True"/>
<chatter reload_on_post="True"/>
```

Default to the bare `<chatter/>` tag unless a specific reload behavior is actually needed —
do not add `reload_on_attachment="True"` by default, it is not part of the baseline migration.

  </example>

  <example id="record_rules_no_change" title="Record rules — company_ids unchanged in v18 (corrected)">

```xml
<!-- v17 record rule -->
<field name="domain_force">[
    ('company_id', 'in', company_ids)
]</field>

<!-- v18 — NO CHANGE. company_ids remains correct.
     Confirmed against addons/account/security/account_security.xml in the real 18.0 branch:
     <field name="domain_force">[('company_id', 'in', company_ids)]</field> appears unchanged. -->
<field name="domain_force">[
    ('company_id', 'in', company_ids)
]</field>
```

`allowed_company_ids` is a real v18+ context variable, but it belongs to view-level field
`domain=` attributes (e.g. `domain="[('company_id', 'in', allowed_company_ids)]"` on a
Many2one field in a form view), which is evaluated client-side against the user's currently
allowed companies — a different context from `ir.rule.domain_force`, which is evaluated
server-side per-request and has always used `company_ids`.

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
[ ] Rename <tree> to <list> in all XML view files (top-level views and inside One2many),
    including view_mode field values (tree,form -> list,form). Do NOT rename existing
    ir.ui.view record ids.
[ ] Replace <div class="oe_chatter"> block with <chatter/> (bare, unless a specific
    reload_on_attachment/reload_on_follower/reload_on_post behavior is actually needed)

NO CHANGE NEEDED (contrary to a previous version of this guide):
[ ] Record rules: company_ids in domain_force is still correct in v18 — do NOT replace
    with allowed_company_ids

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
<chatter/>
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Claiming `allowed_company_ids` replaces `company_ids` in record rule `domain_force` in
    v18 — this is FALSE. A previous version of this file made this claim; it does not match
    real Odoo source (addons/account/security/account_security.xml, 18.0 and 19.0 branches).

```xml
<!-- WRONG — allowed_company_ids is not valid in ir.rule domain_force, in any version -->
<field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

<!-- CORRECT in both v17 and v18 -->
<field name="domain_force">[('company_id', 'in', company_ids)]</field>
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
