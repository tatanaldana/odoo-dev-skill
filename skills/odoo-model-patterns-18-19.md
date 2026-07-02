# Odoo Model Patterns Migration Guide: 18.0 → 19.0

<pattern>

<description>
  Migration guide for model patterns from Odoo 18.0 to 19.0. The confirmed breaking changes
  are: `models.Constraint()` replaces `_sql_constraints` list; `models.Index()` replaces manual
  index definitions; `Domain` class is now available from `odoo.fields`; `bypass_search_access=True`
  is a new Many2one field attribute; and the SQL import path changed from `odoo.tools.sql` to
  `odoo.tools`.

  IMPORTANT: Type hints and SQL() builder are NOT mandatory in v19 addon code. Verified against
  real 19.0 source: account.move.line (3700+ lines) has only 2 methods with return type
  annotations, and raw parameterized cr.execute() coexists with SQL() throughout. Do not treat
  their absence as a migration error.

  Verified against real Odoo 18.0 and 19.0 source: account.move.line (addons/account).
</description>

<version_notes>
  <version id="18">
    <change type="feature">_sql_constraints list — standard pattern for SQL constraints</change>
    <change type="feature">SQL() via from odoo.tools.sql import SQL — confirmed in model_18.py line 11</change>
    <change type="feature">aggregator= on fields — replaces group_operator= (from v17)</change>
    <change type="feature">No Domain class in odoo.fields — use odoo.osv.expression instead</change>
  </version>
  <version id="19">
    <change type="breaking">models.Constraint() replaces _sql_constraints list — confirmed in model_19.py lines 463-478</change>
    <change type="breaking">models.Index() replaces manual index definitions — confirmed in model_19.py lines 483-489</change>
    <change type="breaking">SQL import path changed: from odoo.tools import SQL (not odoo.tools.sql) — confirmed in model_19.py line 10</change>
    <change type="feature">Domain class: from odoo.fields import Command, Domain — confirmed in model_19.py line 9</change>
    <change type="feature">bypass_search_access=True on Many2one fields — confirmed in model_19.py lines 38, 99, 172</change>
    <change type="observed">Type hints: recommended convention, NOT mandatory — verified: account.move.line has only 2 typed methods in 3700+ lines</change>
    <change type="observed">SQL() builder: recommended for complex queries, raw parameterized cr.execute() remains valid — both coexist in real 19.0 addon code</change>
  </version>
</version_notes>

<examples>

  <example id="breaking_constraint" title="BREAKING: models.Constraint() replaces _sql_constraints">

```python
# v18 — _sql_constraints list
_sql_constraints = [
    ('name_company_uniq', 'unique(company_id, name)', 'Name must be unique per company!'),
    ('positive_amount', 'CHECK(amount >= 0)', 'Amount must be positive!'),
]

# v19 — models.Constraint() as class attributes (confirmed in model_19.py lines 463-478)
_name_company_uniq = models.Constraint(
    'unique(company_id, name)',
    'Name must be unique per company!',
)
_check_positive_amount = models.Constraint(
    'CHECK(amount >= 0)',
    'Amount must be positive!',
)
```

  </example>

  <example id="breaking_index" title="BREAKING: models.Index() replaces manual index definitions">

```python
# v18 — indexes defined in _auto_init() or via init() overrides
def _auto_init(self):
    res = super()._auto_init()
    tools.create_index(
        self._cr, 'my_model_partner_date_idx',
        self._table, ['partner_id', 'date']
    )
    return res

# v19 — models.Index() as class attributes (confirmed in model_19.py lines 483-489)
_partner_date_idx = models.Index("(partner_id, date)")

# With sort direction
_date_name_id_idx = models.Index("(date desc, move_name desc, id)")

# Partial index (WHERE clause)
_unreconciled_idx = models.Index("(account_id, partner_id) WHERE reconciled IS NOT TRUE")

# Conditional index
_negative_residual_idx = models.Index("(journal_id) WHERE amount_residual < 0")
```

  </example>

  <example id="breaking_sql_import" title="BREAKING: SQL import path changed">

```python
# v18 — import from submodule (confirmed in model_18.py line 11)
from odoo.tools.sql import create_index, SQL

# v19 — import directly from odoo.tools (confirmed in model_19.py line 10)
from odoo.tools import frozendict, float_compare, groupby, Query, SQL, OrderedSet

# Usage is identical in both versions — only the import path changes
query = SQL(
    "SELECT id, name FROM %s WHERE state = %s",
    SQL.identifier(self._table),
    'confirmed',
)
self.env.cr.execute(query)
```

  </example>

  <example id="new_domain_class" title="NEW: Domain class from odoo.fields">

```python
# v18 — no Domain class, use odoo.osv.expression
from odoo.osv import expression
domain = expression.OR([domain_a, domain_b])

# v19 — Domain class available (confirmed in model_19.py line 9)
from odoo.fields import Command, Domain

domain_a = [('state', '=', 'draft')]
domain_b = [('company_id', '=', self.env.company.id)]

combined = Domain.OR([domain_a, domain_b])

if operator in Domain.NEGATIVE_OPERATORS:
    # handle negation
    pass
```

  </example>

  <example id="new_bypass_search_access" title="NEW: bypass_search_access on Many2one fields">

```python
# v18 — no bypass_search_access attribute on fields

# v19 — bypass_search_access=True (confirmed in model_19.py lines 38, 99, 172)
# Allows finding related records even when user lacks read access to the comodel.
# Used on fields where ir.rules should be bypassed for the relation lookup.
move_id = fields.Many2one(
    comodel_name='account.move',
    required=True,
    readonly=True,
    index=True,
    bypass_search_access=True,  # v19: bypass ir.rules for this field
    ondelete='cascade',
    check_company=True,
)
```

  </example>

  <example id="migration_checklist" title="Full migration checklist v18 → v19">

```
BREAKING CHANGES — must fix:
[ ] Convert _sql_constraints list entries to models.Constraint() class attributes
[ ] Convert manual index creation (_auto_init, create_index calls) to models.Index()
[ ] Update SQL import: from odoo.tools.sql import SQL → from odoo.tools import SQL

NEW FEATURES — adopt where applicable:
[ ] Use Domain class for domain manipulation: from odoo.fields import Command, Domain
[ ] Add bypass_search_access=True to Many2one fields that need to bypass ir.rules
[ ] Use models.Index() partial indexes (WHERE clause) for filtered index optimization

NOT REQUIRED (contrary to common claims):
[ ] Type hints on all methods — recommended convention, not enforced
[ ] SQL() builder on all raw SQL — raw parameterized cr.execute() remains valid
[ ] Python 3.12 — not a confirmed requirement for v19 addon code
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="HIGH">
    Using `_sql_constraints` list style in v19 — `models.Constraint()` is the new pattern.

```python
# DEPRECATED in v19
_sql_constraints = [
    ('name_uniq', 'unique(name)', 'Name must be unique!'),
]

# CORRECT in v19 (confirmed in model_19.py lines 463-478)
_name_uniq = models.Constraint(
    'unique(name)',
    'Name must be unique!',
)
```
  </antipattern>

  <antipattern severity="HIGH">
    Using `from odoo.tools.sql import SQL` in v19 — import path changed.

```python
# WRONG in v19 (was correct in v18)
from odoo.tools.sql import SQL

# CORRECT in v19 (confirmed in model_19.py line 10)
from odoo.tools import SQL
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Claiming type hints are mandatory in v19 — they are NOT enforced on addon code.
    Real 19.0 source (account.move.line, 3700+ lines) has only 2 methods with return
    type annotations. Do not flag missing type hints as a migration error.
  </antipattern>

  <antipattern severity="CRITICAL">
    Claiming raw SQL is removed in v19 and raises SecurityError — this is false.
    Raw parameterized `cr.execute("SELECT ... WHERE x = %s", [val])` remains valid
    and coexists with SQL() in real 19.0 addon code. What is never valid (in any version)
    is string formatting with untrusted input:

```python
# ALWAYS WRONG — injection risk (any version)
self.env.cr.execute("SELECT * FROM %s" % user_input)

# VALID in v19 — parameterized
self.env.cr.execute("SELECT * FROM my_table WHERE id = %s", [record_id])

# ALSO VALID in v19 — SQL() builder
self.env.cr.execute(SQL("SELECT * FROM my_table WHERE id = %s", record_id))
```
  </antipattern>

  <antipattern severity="HIGH">
    Using `SQL.identifier()` incorrectly — it wraps table/column names as SQL identifiers,
    not for value parameters.

```python
# WRONG — SQL.identifier() on a value
SQL("SELECT * FROM my_table WHERE state = %s", SQL.identifier('confirmed'))

# CORRECT — SQL.identifier() only for table/column names
SQL("SELECT * FROM %s WHERE state = %s", SQL.identifier(self._table), 'confirmed')
```
  </antipattern>

</antipatterns>

</pattern>