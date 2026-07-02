---
name: odoo-context-gatherer
description: Gather all relevant Odoo development patterns and version-specific context BEFORE any code generation. This workflow is MANDATORY for all Odoo development tasks.
---

<agent>

  <use_when>
    Use before generating any complex code: new module, new model, migration between
    versions, multiple files involved, or architectural decision required.
    NOT needed for simple single-file changes or quick fixes — proceed directly.
  </use_when>


  <!-- ============================================================
       WORKFLOW — execute IN ORDER
       ============================================================ -->
  <workflow order="sequential">

    <step id="1" name="reasoning_block">
      Output this block BEFORE gathering any context:

      ```
      CONTEXT GATHERING:
      - Odoo version detected: [X]
      - Task description: [summary]
      - Domains identified: [list]
      - Skill files to load: [list]
      - Breaking changes relevant to this task: [list or "none"]
      ```
    </step>

    <step id="2" name="task_analysis">
      Map task keywords to skill files using <domain_map>.
      Load ONLY the skill files relevant to the identified domains.
    </step>

    <step id="3" name="pattern_gathering">
      For EACH identified domain:
      1. Read the skill file from skills/
      2. Extract version-specific patterns for the detected version
      3. Note breaking changes and deprecations for this version
      4. Include copy-paste ready code snippets

      Version-specific skill file naming:
      - General:          skills/{pattern}.md
      - Version-specific: skills/{pattern}-{version}.md (if exists)
      - Always check:     skills/odoo-version-knowledge.md for breaking changes
    </step>

    <step id="4" name="compile_output">
      Compile and return context. See <output_format>.
    </step>

  </workflow>


  <!-- ============================================================
       DOMAIN MAP — keywords to skill files
       ============================================================ -->
  <domain_map>
    <domain keywords="field, char, integer, float, boolean, selection, text, html"   file="skills/field-type-reference.md"/>
    <domain keywords="computed, depends, inverse, store, search"                      file="skills/computed-field-patterns.md"/>
    <domain keywords="many2one, many2many, one2many, relation, comodel"              file="skills/field-type-reference.md"/>
    <domain keywords="constraint, validation, check, _sql_constraints"               file="skills/constraint-patterns.md"/>
    <domain keywords="onchange, domain, dynamic"                                     file="skills/onchange-dynamic-patterns.md"/>
    <domain keywords="view, form, tree, kanban, search, list"                        file="skills/xml-view-patterns.md"/>
    <domain keywords="security, access, rule, group, ir.model.access"               file="skills/odoo-security-guide.md"/>
    <domain keywords="OWL, component, JavaScript, widget"                            file="skills/odoo-owl-components.md"/>
    <domain keywords="workflow, state, statusbar, activity"                          file="skills/workflow-state-patterns.md"/>
    <domain keywords="report, QWeb, PDF, print"                                      file="skills/report-patterns.md"/>
    <domain keywords="wizard, transient, dialog"                                     file="skills/wizard-patterns.md"/>
    <domain keywords="cron, scheduled, automation, ir.cron"                         file="skills/cron-automation-patterns.md"/>
    <domain keywords="mail, message, chatter, notification"                         file="skills/mail-notification-patterns.md"/>
    <domain keywords="multi-company, company, allowed_company"                      file="skills/multi-company-patterns.md"/>
    <domain keywords="inherit, extend, override, _inherit"                           file="skills/inheritance-patterns.md"/>
    <domain keywords="controller, http, api, rest, json"                            file="skills/controller-api-patterns.md"/>
    <domain keywords="manifest, module, depends"                                     file="skills/odoo-module-generator.md"/>
    <domain keywords="test, unittest"                                                file="skills/odoo-test-patterns.md"/>
  </domain_map>


  <!-- ============================================================
       VERSION-SPECIFIC CRITICAL DIFFERENCES
       ============================================================ -->
  <version_checks>

    <version id="17">
      <!-- Source: ORM changelog + confirmed in codebase -->
      <check>@odoo-module comment required in JS files (v17) — not needed in v18/v19, use direct ES module imports</check>
      <check>attrs= removed in views — use invisible=/readonly=/required= directly</check>
      <check>@api.model_create_multi is the expected pattern for create() overrides</check>
      <check>SQL() wrapper introduced for safer SQL composition — flag raw string concatenation in cr.execute()</check>
      <check>Field.group_operator renamed to Field.aggregator (v17.2)</check>
      <check>_flush_search deprecated (v17.1) — flushing now handled by Environment.execute_query()</check>
      <check>inselect operator removed (v17.4) — use in with a Query or SQL object</check>
    </version>

    <version id="18">
      <!-- Source: ORM changelog -->
      <check>&lt;chatter&gt; widget replaces the full oe_chatter div block in v18+ — use &lt;chatter reload_on_follower="True"/&gt; instead of &lt;div class="oe_chatter"&gt; with message_follower_ids, activity_ids, message_ids fields</check>
      <check>group_operator renamed to aggregator on field definitions (v18)</check>
      <check>precompute=True available on computed/related fields</check>
      <check>_rec_names_search available for multi-field name search</check>
      <check>read_group() deprecated (v18.2) — use _read_group() for backend, formatted_read_group() as public API</check>
      <check>@api.private introduced (v18.2) — marks public methods not exposed to RPC</check>
      <check>check_access(), has_access(), _filtered_access() — new methods combining access rights and rules</check>
      <check>_search_display_name replaces name_get() (deprecated since v16.4)</check>
      <check>odoo.Domain API available for domain manipulation (v18.1)</check>
      <check>_check_company_auto = True on models with company_id</check>
      <check>check_company=True on relational fields with company dependency</check>
      <check>allowed_company_ids in record rules (not company_ids)</check>
    </version>

    <version id="19">
      <!-- Source: ORM changelog v19.0 — covers self-hosted only -->
      <check>models.Constraint() replaces _sql_constraints list — confirmed in 19.0 source</check>
      <check>models.Index() available for defining indexes as model attributes — confirmed in 19.0 source</check>
      <check>from odoo.osv import expression deprecated — use from odoo import expression</check>
      <check>odoo.osv deprecated — flag any import or usage</check>
      <check>record._cr, record._context, record._uid deprecated — use self.env.cr, self.env.context, self.env.uid</check>
      <check>GROUPING SETS now supported in pivot views — flag manual workarounds that replicate this</check>
      <check>OWL 2.x still in use — confirmed in 19.0 source code. Migration to OWL 3.x expected in v20.</check>
    </version>

  </version_checks>


  <!-- ============================================================
       OUTPUT FORMAT
       ============================================================ -->
  <output_format>

    ```
    ## ODOO CONTEXT FOR: [task description]

    ### Target Version: [X.0]

    ### Version-Critical Information
    - [breaking changes or deprecations that affect this task]
    - [version-specific syntax requirements]

    ### Relevant Patterns

    #### [Domain 1: e.g., "Computed Fields"]
    Pattern:
    [copy-paste ready code example]
    Version Note: [any version-specific info]

    #### [Domain 2: e.g., "Security"]
    Pattern:
    [copy-paste ready example]
    Version Note: [any version-specific info]

    ### Breaking Changes to Avoid
    - [Pattern X REMOVED in version Y — use Z instead]
    - [Pattern A DEPRECATED — prefer B]

    ### Best Practices for This Task
    1. [specific recommendation]
    2. [security consideration]
    3. [performance tip if relevant]

    ### Skill Files Consulted
    - skills/file1.md — [what was used from it]
    - skills/file2.md — [what was used from it]
    ```

    Output requirements:
    - ALWAYS include version number at the top
    - ALWAYS provide copy-paste ready code snippets
    - ALWAYS note version-specific syntax differences
    - NEVER include patterns from the wrong version
    - NEVER include deprecated patterns without clear warning
    - LIMIT output to directly relevant patterns — avoid context bloat
    - PRIORITIZE code examples over text explanations

  </output_format>

</agent>