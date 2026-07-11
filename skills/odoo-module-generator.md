# Odoo Module Generator - Version Dispatcher

<pattern>

<description>
Version dispatcher for the Odoo Module Generator skill family.
Routes to the correct version-specific file before any module code is generated.
Use this file to understand the skill structure and to identify which sub-file to load.
Do NOT use this file to generate actual module code.
</description>

<version_notes>
  <version id="17">
    Supported — load odoo-module-generator-17.md
  </version>
  <version id="18">
    Current — load odoo-module-generator-18.md
  </version>
  <version id="19">
    Development — load odoo-module-generator-19.md
  </version>
</version_notes>

<examples>

  <example id="version_routing" title="Version-specific files">

Version-specific generation files:

| Target Version | File to Load |
|----------------|-------------|
| Odoo 17.0 | `odoo-module-generator-17.md` |
| Odoo 18.0 | `odoo-module-generator-18.md` |
| Odoo 19.0 | `odoo-module-generator-19.md` |

Migration guides:

| Migration Path | File to Load |
|----------------|-------------|
| 17.0 → 18.0 | `odoo-module-generator-17-18.md` |
| 18.0 → 19.0 | `odoo-module-generator-18-19.md` |

  </example>

  <example id="usage_workflow" title="How to use this skill">

Step 1 — Identify target version.
If the user does not specify, ask before proceeding:
"What Odoo version should I target? (17.0, 18.0, 19.0)"

Step 2 — Load the correct version-specific file.

Step 3 — Gather input parameters:

| Parameter | Required | Example |
|-----------|----------|---------|
| `module_name` | Yes | `custom_inventory` |
| `module_description` | Yes | `Custom inventory tracking` |
| `odoo_version` | Yes | `18.0` |
| `target_apps` | No | `['stock', 'sale']` |
| `multi_company` | No | `true` |
| `security_level` | No | `basic`, `advanced`, `audit` |
| `custom_models` | No | list of model definitions |

Step 4 — Apply only patterns from the loaded version-specific file.
Never mix patterns from different versions.

  </example>

  <example id="version_detection_hints" title="Version detection from existing code">

If version is not stated, look for these indicators:

| Indicator | Version |
|-----------|---------|
| `@api.multi` decorator | v14 (removed in v15) |
| `track_visibility` parameter | v14 |
| `tracking` parameter | v15+ |
| Tuple syntax for x2many | v14–v15 |
| `Command` class usage | v16+ |
| `attrs` in views | v14–v16 |
| Direct `invisible`/`readonly` | v17+ |
| `@api.model_create_multi` mandatory | v17+ |
| `group_operator=` on fields | v17 |
| `aggregator=` on fields | v18+ |
| `<tree>` tag in list views | v17 |
| `<list>` tag in list views | v18+ |
| `oe_chatter` div block | v17 |
| `<chatter .../>` tag | v18+ |
| `models.Constraint()` | v19 |
| `models.Index()` | v19 |
| `from odoo.fields import Domain` | v19 |

  </example>

  <example id="structured_input_schema" title="Structured JSON input for programmatic generation">

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["module_name", "module_description", "odoo_version"],
  "properties": {
    "module_name": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*$",
      "description": "Technical module name (snake_case)"
    },
    "module_description": {
      "type": "string",
      "description": "Human-readable description"
    },
    "odoo_version": {
      "type": "string",
      "enum": ["17.0", "18.0", "19.0"]
    },
    "target_apps": {
      "type": "array",
      "items": {"type": "string"}
    },
    "multi_company": {"type": "boolean", "default": false},
    "multi_currency": {"type": "boolean", "default": false},
    "security_level": {
      "type": "string",
      "enum": ["basic", "advanced", "audit"],
      "default": "basic"
    },
    "custom_models": {"type": "array"},
    "custom_fields": {"type": "array"},
    "include_tests": {"type": "boolean", "default": true},
    "include_demo": {"type": "boolean", "default": false}
  }
}
```

  </example>

  <example id="workflow_examples" title="Example agent workflows">

Example 1 — Basic module (v18):
1. Identify version: 18.0
2. Load: odoo-module-generator-18.md
3. Generate with v18 patterns: `aggregator=`, `<list>`, `<chatter/>` (bare, self-closing), `company_ids` in record rules

Example 2 — Sales extension (v17):
1. Identify version: 17.0
2. Load: odoo-module-generator-17.md
3. Generate with v17 patterns: `@api.model_create_multi`, `group_operator=`, `<tree>`, `oe_chatter` div, `company_ids` in record rules

Example 3 — Migration project (v17 → v18):
1. Load: odoo-module-generator-17-18.md
2. Apply breaking changes: `group_operator=` → `aggregator=`, `<tree>` → `<list>`, oe_chatter div → `<chatter/>` tag

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Generating module code without first loading the version-specific file.
    The dispatcher file (this file) does not contain generation patterns.
  </antipattern>

  <antipattern severity="CRITICAL">
    Mixing patterns from different Odoo versions in the same generated module.
    Each generated file must use only patterns from its target version.
  </antipattern>

  <antipattern severity="HIGH">
    Proceeding with module generation when the target Odoo version is unspecified.
    Always ask before generating any code.
  </antipattern>

</antipatterns>

</pattern>