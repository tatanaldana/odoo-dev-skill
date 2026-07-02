# Odoo Model Patterns - Version Dispatcher

<pattern>

<description>
  Dispatcher file for version-specific model patterns. Always load the correct version file
  before writing any model code. This file provides quick version reference and routing only.

  Scope: Odoo 17.0, 18.0, 19.0 (self-hosted). Versions 14-16 are legacy and not covered.
</description>

<version_notes>
  <version id="17">
    <change type="breaking">@api.model_create_multi mandatory for all create() overrides</change>
    <change type="breaking">attrs= removed from XML views — use invisible= / readonly= / required= directly</change>
    <change type="feature">_check_company_auto = True and check_company=True available — confirmed in model_17.py line 25</change>
    <change type="feature">index='trigram', index='btree', index='btree_not_null' supported on fields</change>
    <change type="feature">Command class for x2many canonical (introduced v15)</change>
    <change type="feature">SQL() available via from odoo.tools.sql import SQL</change>
    <change type="feature">group_operator= on fields for aggregate behavior</change>
    <change type="feature">OWL 2.x — confirmed in component_17.js</change>
  </version>
  <version id="18">
    <change type="breaking">group_operator= renamed to aggregator= on fields — confirmed model_17.py vs model_18.py</change>
    <change type="breaking">&lt;tree&gt; tag renamed to &lt;list&gt; in XML views — confirmed views_18.xml</change>
    <change type="breaking">&lt;div class="oe_chatter"&gt; replaced by &lt;chatter reload_on_attachment="True"/&gt; — confirmed views_18.xml line 1507</change>
    <change type="breaking">allowed_company_ids replaces company_ids in record rule domain_force</change>
    <change type="feature">export_string_translation=False on fields — confirmed project_task_18.py</change>
    <change type="feature">SQL() import: from odoo.tools.sql import SQL — confirmed model_18.py line 11</change>
    <change type="feature">OWL 2.x — same as v17, confirmed component_18.js</change>
    <change type="recommended">Type hints on method signatures — recommended, not mandatory</change>
  </version>
  <version id="19">
    <change type="breaking">models.Constraint() replaces _sql_constraints list — confirmed model_19.py lines 463-478</change>
    <change type="breaking">models.Index() replaces manual index definitions — confirmed model_19.py lines 483-489</change>
    <change type="breaking">SQL import path: from odoo.tools import SQL — confirmed model_19.py line 10</change>
    <change type="feature">Domain class: from odoo.fields import Command, Domain — confirmed model_19.py line 9</change>
    <change type="feature">bypass_search_access=True on Many2one fields — confirmed model_19.py lines 38, 99</change>
    <change type="feature">OWL 2.x — same as v17/v18, confirmed component_19.js</change>
    <change type="observed">Type hints: ORM-core convention, NOT mandatory in addon code — account.move.line has only 2 typed methods in 3700+ lines</change>
    <change type="observed">SQL() builder: recommended, raw parameterized cr.execute() remains valid in addon code</change>
  </version>
</version_notes>

<examples>

  <example id="version_routing" title="Which file to load per version">

```
Target version → File to load
─────────────────────────────────────────────────
17.0            → skills/odoo-model-patterns-17.md
18.0            → skills/odoo-model-patterns-18.md
19.0            → skills/odoo-model-patterns-19.md
17.0 → 18.0     → skills/odoo-model-patterns-17-18.md
18.0 → 19.0     → skills/odoo-model-patterns-18-19.md
```

  </example>

  <example id="version_detection" title="Detecting version from existing code">

```python
# Indicator                        → Version
# ──────────────────────────────────────────
# @api.multi decorator             → 14.0 (removed in v15)
# track_visibility='onchange'      → 14.0 (replaced by tracking= in v15)
# tracking=True                    → 15.0+
# Command class                    → 16.0+
# @api.model_create_multi          → 17.0+ (mandatory)
# attrs= in XML views              → pre-17 (removed in v17)
# group_operator= on fields        → 17.0 (renamed to aggregator= in v18)
# aggregator= on fields            → 18.0+
# <tree> tag in list views         → 17.0 (renamed to <list> in v18)
# <list> tag in list views         → 18.0+
# <div class="oe_chatter">         → 17.0 (replaced by <chatter/> in v18)
# <chatter reload_on_.../>         → 18.0+
# export_string_translation=False  → 18.0+
# models.Constraint()              → 19.0+
# models.Index()                   → 19.0+
# from odoo.fields import Domain   → 19.0+
# bypass_search_access=True        → 19.0+
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using model patterns from the wrong version — causes crashes or deprecated code warnings.
    Always identify the target version first and load the corresponding file.
  </antipattern>

  <antipattern severity="CRITICAL">
    Omitting @api.model_create_multi on create() overrides in v17+ — causes silent data loss
    on batch creates.
  </antipattern>

  <antipattern severity="HIGH">
    Claiming type hints are mandatory in v19 — they are NOT enforced in addon business code.
    Verified: account.move.line (3700+ lines) has only 2 methods with return type annotations.
  </antipattern>

  <antipattern severity="HIGH">
    Claiming SQL() builder is mandatory in v19 — raw parameterized cr.execute() remains valid
    and coexists with SQL() in real 19.0 addon code.
  </antipattern>

  <antipattern severity="HIGH">
    Claiming _check_company_auto is a v18 feature — confirmed present in v17 source
    (model_17.py line 25). No migration needed for this attribute.
  </antipattern>

  <antipattern severity="HIGH">
    Claiming OWL 3.x in v19 — v17, v18 and v19 all use OWL 2.x, confirmed in
    component_17/18/19.js. OWL 3.x migration is expected in v20.
  </antipattern>

</antipatterns>

</pattern>