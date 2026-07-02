# Odoo Version Knowledge: 18 to 19 Migration

<pattern>

  <description>
    Migration guide from Odoo 18.0 to 19.0. Covers breaking changes confirmed
    in the official ORM changelog and in 19.0 source code.
    OWL 2.x still in use — no OWL migration required for this hop.
  </description>


  <!-- ============================================================
       BREAKING CHANGES SUMMARY
       ============================================================ -->
  <version_notes>
    <!-- Source: ORM changelog v19.0 + confirmed in model_19.py -->
    <change version="19" type="breaking">models.Constraint() replaces _sql_constraints list — confirmed in model_19.py</change>
    <change version="19" type="breaking">models.Index() now available for index definitions as model attributes — confirmed in model_19.py</change>
    <change version="19" type="deprecated">odoo.osv — flag any import; use from odoo import expression instead</change>
    <change version="19" type="deprecated">record._cr, record._context, record._uid — use self.env.cr, self.env.context, self.env.uid</change>
    <change version="19" type="new">GROUPING SETS now supported natively in pivot views — remove manual workarounds</change>
    <change version="19" type="note">OWL 2.x still in use — confirmed in 19.0 source code. No OWL migration required for this hop.</change>
    <change version="19" type="note">SQL() builder recommended, not mandatory — same as v18</change>
    <change version="19" type="note">Type hints optional — present only in specific internal methods, not enforced globally</change>
  </version_notes>


  <!-- ============================================================
       SQL CONSTRAINTS MIGRATION
       ============================================================ -->
  <examples category="sql_constraints">

    <example id="constraint_migration" title="models.Constraint() replaces _sql_constraints">
      ```python
      # v18: _sql_constraints list
      class MyModel(models.Model):
          _name = 'my.model'

          percentage = fields.Float()

          _sql_constraints = [
              ('check_percentage',
               'CHECK(percentage >= 0 AND percentage <= 100)',
               'The percentage must be between 0 and 100.'),
              ('code_unique',
               'UNIQUE(code)',
               'Code must be unique.'),
          ]

      # v19: models.Constraint() class attributes — confirmed in model_19.py
      class MyModel(models.Model):
          _name = 'my.model'

          percentage = fields.Float()

          _check_percentage = models.Constraint(
              'CHECK(percentage >= 0 AND percentage <= 100)',
              'The percentage must be between 0 and 100.',
          )
          _code_unique = models.Constraint(
              'UNIQUE(code)',
              'Code must be unique.',
          )
      ```
    </example>

  </examples>


  <!-- ============================================================
       INDEX DEFINITION MIGRATION
       ============================================================ -->
  <examples category="indexes">

    <example id="index_migration" title="models.Index() for custom indexes">
      ```python
      # v18: index defined on field
      name = fields.Char(index='trigram')
      code = fields.Char(index=True)

      # v19: models.Index() for multi-column or custom indexes — confirmed in model_19.py
      _name_company_idx = models.Index('(name, company_id)')
      _date_name_id_idx = models.Index('(date desc, move_name desc, id)')

      # Both styles still work in v19 — models.Index() adds multi-column support
      ```
    </example>

  </examples>


  <!-- ============================================================
       DEPRECATED PATTERNS
       ============================================================ -->
  <examples category="deprecated">

    <example id="osv_import" title="odoo.osv deprecated">
      ```python
      # v18: still worked
      from odoo.osv import expression

      # v19: deprecated — use from odoo instead
      from odoo import expression
      ```
    </example>

    <example id="record_attributes" title="record._cr/_context/_uid deprecated">
      ```python
      # v18: worked but discouraged
      cr = record._cr
      ctx = record._context
      uid = record._uid

      # v19: use env attributes
      cr = self.env.cr
      ctx = self.env.context
      uid = self.env.uid
      ```
    </example>

  </examples>


  <!-- ============================================================
       WHAT DOES NOT CHANGE IN THIS HOP
       ============================================================ -->
  <version_notes>
    <change version="19" type="unchanged">OWL 2.x API — no migration needed, same patterns as v18</change>
    <change version="19" type="unchanged">@odoo-module not required — same as v18, direct ES module imports</change>
    <change version="19" type="unchanged">list tag in XML views — same as v18</change>
    <change version="19" type="unchanged">chatter widget — same as v18</change>
    <change version="19" type="unchanged">aggregator on fields — same as v18</change>
    <change version="19" type="unchanged">_check_company_auto and check_company — same as v18</change>
    <change version="19" type="unchanged">allowed_company_ids in record rules — same as v18</change>
  </version_notes>


  <!-- ============================================================
       ANTIPATTERNS
       ============================================================ -->
  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: _sql_constraints list in v19
      _sql_constraints = [
          ('check_name', 'CHECK(name IS NOT NULL)', 'Name required.'),
      ]

      # CORRECT: models.Constraint()
      _check_name = models.Constraint(
          'CHECK(name IS NOT NULL)',
          'Name required.',
      )
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: deprecated record attributes in v19
      cr = record._cr
      ctx = record._context
      uid = record._uid

      # CORRECT
      cr = self.env.cr
      ctx = self.env.context
      uid = self.env.uid
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: odoo.osv deprecated in v19
      from odoo.osv import expression

      # CORRECT
      from odoo import expression
      ```
    </antipattern>

  </antipatterns>


  <!-- ============================================================
       MIGRATION CHECKLIST
       ============================================================ -->
  <migration_checklist>
    <item priority="CRITICAL">Replace all _sql_constraints lists with models.Constraint() class attributes</item>
    <item priority="HIGH">Replace from odoo.osv import expression with from odoo import expression</item>
    <item priority="HIGH">Replace record._cr, record._context, record._uid with self.env.cr, self.env.context, self.env.uid</item>
    <item priority="MEDIUM">Review pivot views — GROUPING SETS now supported natively, remove workarounds</item>
    <item priority="INFO">No OWL migration required — v19 still uses OWL 2.x</item>
    <item priority="INFO">No tree/list migration required — already done in 17→18 hop</item>
    <item priority="INFO">No chatter migration required — already done in 17→18 hop</item>
  </migration_checklist>

</pattern>