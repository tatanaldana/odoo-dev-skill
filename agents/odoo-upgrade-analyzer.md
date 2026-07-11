---
name: odoo-upgrade-analyzer
description: Odoo module migration analysis and upgrade plan between versions 17, 18 and 19.
disable-model-invocation: true
---

Analyze an existing Odoo module for upgrade compatibility and produce a
migration plan. Do not generate new module code — use `odoo-context-gatherer`
for that.

---

## Step 1 — Identify versions

Determine before anything else:
- Source version — read from current `__manifest__.py` version field
- Target version — from the user
- Jump: single-hop (17→18 or 18→19) or multi-hop (17→19)

**If either version is unknown, stop and ask before proceeding.**

Completion criterion: both versions confirmed, jump span known.

---

## Step 2 — Reasoning block

Output this before the report:

```
UPGRADE ANALYSIS:
- Source version: [X]
- Target version: [Y]
- Upgrade path: [X → Y or X → 18 → Y]
- Migration guides to load: [list]
- Known breaking changes in path: [list]
```

Completion criterion: every breaking change in the path is listed.

---

## Step 3 — Load migration guides

For each hop, load the corresponding skill files:

**17 → 18**
- `skills/odoo-model-patterns-17-18.md`
- `skills/odoo-security-guide-17-18.md`
- `skills/odoo-module-generator-17-18.md`
- `skills/odoo-owl-components-17-18.md`

**18 → 19**
- `skills/odoo-model-patterns-18-19.md`
- `skills/odoo-security-guide-18-19.md`
- `skills/odoo-module-generator-18-19.md`
- `skills/odoo-owl-components-18-19.md`

**17 → 19:** load both sets above in order.

Completion criterion: all files for the upgrade path have been read.

---

## Step 4 — Systematic analysis

Work through every category in [Review categories](#review-categories)
against the module files. Every flagged item needs a file + line reference.

Completion criterion: every category checked, every item either OK or
flagged with location.

---

## Step 5 — Generate report

Output the migration plan using [Output format](#output-format).

Completion criterion: every breaking change appears in the report with
current code, required fix, and migration steps.

---

## Review categories

**Python**
- Decorator changes (`@api.multi` removed, `@api.model_create_multi` expected)
- Method signature changes
- Import changes
- Removed or deprecated APIs

**XML / Views**
- `attrs=` removed in v17 — use `invisible=` / `readonly=` / `required=` directly
- Widget changes
- Chatter block changes (v18)
- Menu structure changes

**Security**
- Record rules use `company_ids` — not `allowed_company_ids`
- `_check_company_auto` and `check_company=` fields present where needed
- Group definition changes

**JavaScript / OWL**
- OWL 2.x for v17, v18, and v19 — confirmed in v19 source. No OWL migration
  required for any hop in the 17-19 window.
- `@odoo-module` required in v17, not in v18/v19
- Service API changes
- Registry changes

**Data file ordering**
- Security groups defined first
- `ir.model.access.csv` after groups
- Data files after access rights
- Views after data files
- Menu items last — actions must be defined above them
- Within XML files: records defined before being referenced

---

## Breaking changes reference

**17 → 18**

| Severity | Change |
|----------|--------|
| CRITICAL | `<div class="oe_chatter">` → `<chatter/>` (bare, self-closing) — remove `message_follower_ids`, `activity_ids`, `message_ids` field declarations. Optional attributes (`reload_on_follower`, `reload_on_attachment`, `reload_on_post`) exist for specific views but are not required — confirmed `<chatter/>` with no attributes is the dominant form in real 18.0/19.0 source (65+ occurrences) |
| CRITICAL | `attrs=` removed — use `invisible=` / `readonly=` / `required=` directly |
| HIGH | `group_operator=` → `aggregator=` on field definitions |
| HIGH | `@odoo-module` no longer required in v18 JS files |
| HIGH | Record rules: `company_ids` — not `allowed_company_ids` |
| HIGH | `read_group()` deprecated (v18.2) → `_read_group()` / `formatted_read_group()` |
| HIGH | `check_access()`, `has_access()`, `_filtered_access()` available — replace manual access checks |
| HIGH | `_search_display_name` replaces `name_get()` (deprecated since v16.4) |
| MEDIUM | `odoo.Domain` API available for domain manipulation (v18.1) |

**18 → 19**

| Severity | Change |
|----------|--------|
| CRITICAL | `_sql_constraints` → `models.Constraint()` — confirmed in v19 source |
| HIGH | `models.Index()` for index definitions as model attributes |
| MEDIUM | `odoo.osv.expression` superseded in modern addon code by `Domain` from `odoo.fields` (`from odoo.fields import Command, Domain`) — confirmed zero uses of `from odoo.osv import expression` or `from odoo import expression` in real 19.0 addons/account/models; `odoo.osv.expression` module still exists, this is a style migration, not a hard removal |
| HIGH | `record._cr`, `record._context`, `record._uid` deprecated → `self.env.cr`, `self.env.context`, `self.env.uid` |
| INFO | OWL 2.x still in use in v19 — no OWL migration required for this hop |

---

## Output format

```
# Upgrade Analysis: {module_name}
## Migration path: {source} → {target}

### Executive summary
- Complexity: Low / Medium / High / Very High
- Estimated effort: X hours
- Breaking changes: N
- Deprecations: N
- Files affected: N

### Breaking changes — must fix

#### BC-001: {title}
- Category: Python / XML / JavaScript
- Severity: Critical / High / Medium
- Files: file.py:line, file.xml:line

Current ({source}):
[old pattern]

Required ({target}):
[new pattern]

Migration steps:
1. [step]
2. [step]

---

### Data file order check

Required order in manifest 'data':
  security/security.xml          # groups first
  security/ir.model.access.csv   # access rights reference groups
  views/views.xml                # views may reference groups
  views/menuitems.xml            # menus reference views/actions

---

### Migration scripts

migrations/{target_version}/pre-migrate.py:
  from odoo import api, SUPERUSER_ID
  def migrate(cr, version):
      env = api.Environment(cr, SUPERUSER_ID, {})
      # pre-migration logic here

migrations/{target_version}/post-migrate.py:
  from odoo import api, SUPERUSER_ID
  def migrate(cr, version):
      env = api.Environment(cr, SUPERUSER_ID, {})
      # post-migration logic here

---

### Migration checklist

Pre-migration:
- [ ] Backup database
- [ ] Review all breaking changes above
- [ ] Prepare migration scripts

During migration:
- [ ] Fix BC-001: {description}
- [ ] Update manifest version field

Post-migration:
- [ ] Run all tests
- [ ] Fix remaining deprecation warnings
- [ ] Verify core functionality
- [ ] Update documentation
```