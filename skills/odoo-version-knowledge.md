# Odoo Version Knowledge - Master Reference

<pattern>

  <description>
    Master reference for Odoo version awareness. Covers breaking changes summary,
    version detection patterns, and compatibility matrix for versions 17, 18 and 19.
    Load the version-specific file after identifying the target version.
  </description>


  <!-- ============================================================
       CRITICAL WARNING
       ============================================================ -->
  <warning>
    Odoo has BREAKING CHANGES between versions. Code written for one version
    often WILL NOT WORK in another version.
    ALWAYS identify the target Odoo version BEFORE writing any code.
  </warning>


  <!-- ============================================================
       VERSION SUPPORT STATUS
       ============================================================ -->
  <version_status>

    | Version | Status    | Python  | End of Support |
    |---------|-----------|---------|----------------|
    | 17.0    | Supported | 3.10+   | October 2026   |
    | 18.0    | Current   | 3.11+   | October 2027   |
    | 19.0    | Development | 3.12+ | TBD            |

  </version_status>


  <!-- ============================================================
       VERSION-SPECIFIC KNOWLEDGE FILES
       ============================================================ -->
  <version_files>

    | Version   | File                              |
    |-----------|-----------------------------------|
    | Odoo 17.0 | skills/odoo-version-knowledge-17.md |
    | Odoo 18.0 | skills/odoo-version-knowledge-18.md |
    | Odoo 19.0 | skills/odoo-version-knowledge-19.md |

  </version_files>


  <!-- ============================================================
       BREAKING CHANGES SUMMARY
       ============================================================ -->
  <breaking_changes>

    <version from="16" to="17">
      <!-- Source: ORM changelog + confirmed in codebase -->
      <change component="attrs"               impact="BREAKING" note="Removed — use invisible=/readonly=/required= directly"/>
      <change component="@api.model_create_multi" impact="BREAKING" note="Mandatory for create() overrides"/>
      <change component="Python"              impact="REQUIREMENT" note="3.10+ required"/>
    </version>

    <version from="17" to="18">
      <!-- Source: ORM changelog + confirmed in codebase -->
      <change component="&lt;tree&gt; tag"    impact="BREAKING" note="Renamed to &lt;list&gt; in XML views"/>
      <change component="_check_company_auto" impact="NEW" note="Auto company validation on models with company_id"/>
      <change component="check_company"       impact="NEW" note="Field-level company validation on relational fields"/>
      <change component="allowed_company_ids" impact="NOT-A-CHANGE" note="Does NOT replace company_ids in ir.rule domain_force — confirmed unchanged against real addons/account/security/account_security.xml in 18.0/19.0. allowed_company_ids is a separate context variable used in view-level field domain= attributes, not in record rules."/>
      <change component="read_group()"        impact="DEPRECATED" note="Use _read_group() / formatted_read_group()"/>
      <change component="@api.private"        impact="NEW" note="Marks methods not exposed to RPC (v18.2)"/>
      <change component="SQL() builder"       impact="RECOMMENDED" note="Safer SQL composition — not mandatory"/>
      <change component="Type hints"          impact="RECOMMENDED" note="Better IDE support — not mandatory"/>
    </version>

    <version from="18" to="19">
      <!-- Source: ORM changelog v19.0 — self-hosted only -->
      <change component="odoo.osv"            impact="DEPRECATED" note="Flag any import or usage"/>
      <change component="record._cr/_context/_uid" impact="DEPRECATED" note="Use self.env.cr, self.env.context, self.env.uid"/>
      <change component="GROUPING SETS"       impact="NEW" note="Now supported in pivot views natively"/>
    </version>

  </breaking_changes>


  <!-- ============================================================
       VERSION DETECTION PATTERNS
       ============================================================ -->
  <version_detection>

    <examples category="python">
      ```python
      # v17 indicators
      @api.model_create_multi        # mandatory in v17+
      # no attrs= in views

      # v18 indicators
      _check_company_auto = True     # v18+
      check_company=True             # v18+

      # v19 indicators
      # record._cr deprecated — use self.env.cr
      # odoo.osv deprecated
      ```
    </examples>

    <examples category="xml">
      ```xml
      <!-- v16 and below -->
      <field name="x" attrs="{'invisible': [...]}"/>
      <tree string="Records">...</tree>

      <!-- v17+ -->
      <field name="x" invisible="condition"/>
      <tree string="Records">...</tree>

      <!-- v18+ -->
      <list string="Records">...</list>
      ```
    </examples>

    <examples category="javascript">
      ```javascript
      // v17 — @odoo-module required
      /** @odoo-module **/
      import { Component } from "@odoo/owl";

      // v18, v19 — direct ES module imports, no @odoo-module needed
      import { Component } from "@odoo/owl";
      ```
    </examples>

  </version_detection>


  <!-- ============================================================
       VERSION COMPATIBILITY MATRIX
       ============================================================ -->
  <compatibility_matrix>

    <!-- Source: ORM changelog + confirmed in codebase -->
    | Feature                | v17 | v18 | v19 |
    |------------------------|-----|-----|-----|
    | attrs= in views        | ❌  | ❌  | ❌  |
    | direct invisible=      | ✅  | ✅  | ✅  |
    | &lt;tree&gt; tag       | ✅  | ⚠️  | ❌  |
    | &lt;list&gt; tag       | ❌  | ✅  | ✅  |
    | @api.model_create_multi| ✅  | ✅  | ✅  |
    | _check_company_auto    | ✅  | ✅  | ✅  |
    | check_company on fields| ✅  | ✅  | ✅  |
    | allowed_company_ids (¹)| ❌  | ✅  | ✅  |
    | read_group()           | ✅  | ⚠️  | ⚠️  |
    | _read_group()          | ❌  | ✅  | ✅  |
    | @api.private           | ❌  | ✅  | ✅  |
    | odoo.osv               | ✅  | ✅  | ⚠️  |
    | record._cr/_uid        | ✅  | ✅  | ⚠️  |
    | OWL 2.x                | ✅  | ✅  | ✅  |
    | @odoo-module required  | ✅  | ❌  | ❌  |
    | SQL() builder          | ⚠️  | ⚠️  | ⚠️  |
    | Type hints             | ⚠️  | ⚠️  | ⚠️  |

    Legend: ✅ Supported | ⚠️ Recommended/Deprecated | ❌ Not available/Removed

    (¹) `allowed_company_ids` exists as a context variable since v18, but it is used in
    view-level field `domain=` attributes (client-side, evaluated against the user's
    selected companies) — NOT in `ir.rule.domain_force`, which has always used
    `company_ids` in v17, v18, and v19 alike (confirmed against real
    addons/account/security/account_security.xml). Do not treat this row as license to
    replace `company_ids` in record rules.

  </compatibility_matrix>

</pattern>