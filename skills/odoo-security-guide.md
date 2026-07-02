# odoo-security-guide.md

<pattern>

  <description>
    Dispatcher for the Odoo Security Guide skill family.
    Routes to the correct version-specific file before generating any security code.
    Covers versions 17, 18, and 19 only.
  </description>

  <version_notes>
    <version id="17">
      attrs= removed from views — use invisible=, readonly=, required= directly with Python expressions.
      @api.model_create_multi mandatory on create() methods.
      _check_company_auto and check_company=True available.
      Record rules use company_ids in domain_force.
    </version>
    <version id="18">
      SQL() builder required for raw SQL — from odoo.tools.sql import SQL.
      Type hints recommended on relational fields.
      _check_company_auto and check_company=True available (same as v17).
      Record rules use company_ids in domain_force (same as v17).
    </version>
    <version id="19">
      Type hints mandatory on all fields.
      SQL() builder mandatory — from odoo.tools import SQL.
      models.Constraint() and models.Index() replace _sql_constraints and index=True.
      Record rules use company_ids in domain_force (same as v17/v18).
    </version>
  </version_notes>

  <examples>

    <example id="routing" title="Version routing decision">
      ```
      Generating NEW code for v17  → read odoo-security-guide-17.md
      Generating NEW code for v18  → read odoo-security-guide-18.md
      Generating NEW code for v19  → read odoo-security-guide-19.md
      Upgrading v17 → v18          → read odoo-security-guide-17-18.md
      Upgrading v18 → v19          → read odoo-security-guide-18-19.md
      ```
    </example>

    <example id="version_detection" title="Version detection hints">
      ```
      attrs= in views                    → pre-v17 (do not generate)
      invisible= with Python expression  → v17+
      group_operator= on fields          → v17
      aggregator= on fields              → v18+
      SQL from odoo.tools.sql            → v18
      SQL from odoo.tools                → v19
      models.Constraint() / models.Index() → v19
      Type hints mandatory               → v19
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Generating security code from this dispatcher file directly — always load
      the version-specific file first. This file contains routing logic only.
    </antipattern>

    <antipattern severity="CRITICAL">
      Mixing patterns from multiple version files in one implementation.
      Each generated file must target exactly one Odoo version.
    </antipattern>

  </antipatterns>

</pattern>