# odoo-security-guide-18-19.md

<pattern>

  <description>
    Migration guide for Odoo security code upgrading from 18.0 to 19.0.
    Documents what changes are required, recommended, or unchanged.
    Use this file when upgrading an existing v18 module to v19.

    IMPORTANT: this file previously claimed type hints and the SQL() builder are "mandatory"
    in v19, and showed `models.Constraint()`/`models.Index()` wrapped in `_sql_constraints =
    [...]` / `_indexes = [...]` lists. Both claims are FALSE — verified against real 19.0
    source (account.move.line, 3700+ lines, has only 2 type-hinted methods; account_journal.py,
    account_move_line.py, account_bank_statement.py use bare `_name = models.Constraint(...)`
    and `_name = models.Index(...)` class attributes, never a wrapping list). Cross-reference
    odoo-model-patterns-18-19.md, which documents this correctly with the same source citations.
    Corrected below.
  </description>

  <version_notes>
    <version id="18">
      Type hints recommended, not enforced.
      SQL() builder recommended for new code — from odoo.tools.sql import SQL. Raw
      parameterized cr.execute() remains valid.
      Record rules use company_ids in domain_force.
      _check_company_auto = True available.
      group_operator= already replaced by aggregator= (from v17-18 migration).
    </version>
    <version id="19">
      Type hints: still a recommended convention, NOT mandatory. Real 19.0 addon code
      (account.move.line, 3700+ lines) has only 2 methods with return type annotations.
      SQL() builder: recommended, NOT mandatory. Raw parameterized cr.execute() coexists
      with SQL() throughout real 19.0 addon code. Import path changed: from odoo.tools import SQL.
      models.Constraint() replaces _sql_constraints — as a bare class attribute
      (`_my_constraint = models.Constraint(sql, message)`), NOT a list.
      models.Index() replaces manual index creation (_auto_init/create_index) — also a bare
      class attribute (`_my_idx = models.Index("(col1, col2)")`), NOT a list.
      Record rules use company_ids in domain_force — no change from v18.
      Python 3.12+: not a confirmed requirement for addon code — do not flag as a migration blocker.
    </version>
  </version_notes>

  <examples>

    <example id="migration_overview" title="Migration overview table">
      ```
      Component               v18                       v19                        Action
      ----------------------  ------------------------  -------------------------  ----------
      Type hints              recommended               still recommended         optional
      SQL() builder           recommended (tools.sql)   still recommended (tools)  optional (path change if adopted)
      SQL import path         odoo.tools.sql            odoo.tools                 REQUIRED (only if using SQL())
      models.Constraint()     _sql_constraints list      bare class attribute       recommended
      models.Index()          index= on fields           bare class attribute       recommended
      Python                  3.11+                      not confirmed 3.12+ req.   check your target env
      Record rules            company_ids                company_ids               no change
      _check_company_auto     available                  available                 no change
      View syntax             invisible= expression      invisible= expression     no change
      ```
    </example>

    <example id="type_hints_optional" title="Type hints — optional convention in v19, not enforced">
      ```python
      # v18 and v19: type hints are an OPTIONAL stylistic convention, never enforced by the
      # ORM or the test suite. Both forms below are equally valid in v19.

      # Without type hints — valid in v19
      class MyModel(models.Model):
          _name = 'my.model'

          name = fields.Char(required=True)
          partner_id = fields.Many2one('res.partner')
          line_ids = fields.One2many('my.line', 'parent_id')
          tag_ids = fields.Many2many('my.tag')

      # With type hints — also valid in v19, adopt where it improves readability
      from __future__ import annotations

      class MyModel(models.Model):
          _name = 'my.model'

          name: str = fields.Char(required=True)
          partner_id: int = fields.Many2one('res.partner')
          line_ids: list[int] = fields.One2many('my.line', 'parent_id')
          tag_ids: list[int] = fields.Many2many('my.tag')
      ```
    </example>

    <example id="sql_import_migration" title="SQL import path change v18 → v19 (only applies if you use SQL())">
      ```python
      # v18: import from odoo.tools.sql
      from odoo.tools.sql import SQL

      # v19: import from odoo.tools
      from odoo.tools import SQL

      # Raw parameterized cr.execute() remains valid in both versions and does not
      # require migrating to SQL() — adopt SQL() for new/complex queries by choice,
      # not because raw execute() stops working.
      ```
    </example>

    <example id="sql_migration" title="SQL builder examples (v19) — recommended, not mandatory">
      ```python
      from odoo.tools import SQL  # v19 import path

      # Simple query
      def _get_records(self):
          query = SQL(
              "SELECT id, name FROM %(table)s WHERE active = %(active)s",
              table=SQL.identifier('my_table'),
              active=True,
          )
          self.env.cr.execute(query)
          return self.env.cr.fetchall()

      # Complex join query
      def _get_report_data(self):
          query = SQL(
              """
              SELECT m.id, m.name, COALESCE(SUM(l.amount), 0) AS total_amount
              FROM %(main_table)s m
              LEFT JOIN %(line_table)s l ON l.parent_id = m.id
              WHERE m.company_id IN %(company_ids)s
                AND m.state = %(state)s
              GROUP BY m.id, m.name
              """,
              main_table=SQL.identifier(self._table),
              line_table=SQL.identifier('my_model_line'),
              company_ids=tuple(self.env.companies.ids) or (0,),
              state='confirmed',
          )
          self.env.cr.execute(query)
          return self.env.cr.dictfetchall()
      ```
    </example>

    <example id="constraint_index_migration" title="Constraint and index migration (v19) — bare class attributes, not lists">
      ```python
      # v18: _sql_constraints list and index= on fields
      class MyModel(models.Model):
          _name = 'my.model'

          name = fields.Char(required=True, index=True)
          company_id = fields.Many2one('res.company', index=True)

          _sql_constraints = [
              ('unique_name_company', 'UNIQUE(name, company_id)',
               'Name must be unique per company.'),
          ]

      # v19: models.Constraint() and models.Index() as BARE class attributes —
      # confirmed against real 19.0 source (account_journal.py lines 36-39,
      # account_move_line.py lines 463-489). NOT wrapped in _sql_constraints=[...]
      # or _indexes=[...] lists — that pattern does not exist anywhere in real
      # 19.0 addon code.
      class MyModel(models.Model):
          _name = 'my.model'

          name = fields.Char(required=True)
          company_id = fields.Many2one('res.company')

          _unique_name_company = models.Constraint(
              'UNIQUE(name, company_id)',
              'Name must be unique per company.',
          )
          _company_idx = models.Index("(company_id)")
          _name_company_idx = models.Index("(name, company_id)")
      ```
    </example>

    <example id="record_rule_no_change" title="Record rules — no change needed v18 to v19">
      ```xml
      <!-- v18 record rule — no migration needed for v19 -->
      <record id="rule_model_company" model="ir.rule">
          <field name="name">Model: Multi-Company</field>
          <field name="model_id" ref="model_custom_model"/>
          <field name="global" eval="True"/>
          <field name="domain_force">[
              '|',
              ('company_id', '=', False),
              ('company_id', 'in', company_ids)
          ]</field>
      </record>
      <!-- company_ids is the correct variable in v18 and v19 -->
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Claiming type hints are mandatory in v19 and flagging their absence as an error —
      FALSE. Real 19.0 source (account.move.line, 3700+ lines) has only 2 type-hinted
      methods. A previous version of this file made this claim; it has been removed.

```python
      # NOT an error in v19 — type hints are optional in both v18 and v19
      class MyModel(models.Model):
          name = fields.Char(required=True)
          partner_id = fields.Many2one('res.partner')
```
    </antipattern>

    <antipattern severity="CRITICAL">
      Using `from odoo.tools.sql import SQL` in v19 when you DO use the SQL() builder —
      import path changed.

```python
      # WRONG: v18 SQL import path in v19
      from odoo.tools.sql import SQL  # v18 path — fails in v19

      # CORRECT
      from odoo.tools import SQL  # v19 path
```
    </antipattern>

    <antipattern severity="CRITICAL">
      Claiming raw SQL is removed/forbidden in v19 and that SQL() is mandatory — FALSE.
      Raw parameterized `cr.execute("...", [val])` remains valid and coexists with SQL()
      throughout real 19.0 addon code. What is always wrong (in any version) is string
      interpolation of untrusted input or table/column names without `SQL.identifier()`.

```python
      # ALWAYS WRONG (any version) — table name via string interpolation
      query = f"SELECT id FROM {self._table} WHERE company_id = %s"

      # VALID in v19 — parameterized raw execute, no SQL() needed
      self.env.cr.execute(
          "SELECT id FROM my_table WHERE active = %s",
          [True]
      )

      # ALSO VALID in v19 — SQL() builder with SQL.identifier() for identifiers
      from odoo.tools import SQL
      self.env.cr.execute(SQL(
          "SELECT id FROM %(t)s WHERE company_id = %(cid)s",
          t=SQL.identifier(self._table),
          cid=self.env.company.id,
      ))
```
    </antipattern>

    <antipattern severity="HIGH">
      Wrapping `models.Constraint()` or `models.Index()` in a `_sql_constraints = [...]` /
      `_indexes = [...]` list in v19 — this pattern does not exist in real 19.0 source.
      They are bare class attributes.

```python
      # WRONG in v19 — no such list-wrapped pattern exists in real source
      _sql_constraints = [
          models.Constraint('unique(name)', 'Name must be unique!'),
      ]
      _indexes = [
          models.Index('idx_name', ['name']),
      ]

      # CORRECT in v19 (confirmed in account_journal.py, account_move_line.py)
      _name_uniq = models.Constraint('unique(name)', 'Name must be unique!')
      _name_idx = models.Index("(name)")
```
    </antipattern>

  </antipatterns>

</pattern>
