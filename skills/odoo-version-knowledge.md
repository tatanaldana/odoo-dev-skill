# Odoo Version Knowledge — Master Reference

ALWAYS identify target version BEFORE writing code.

## Version status

| Version | Status | Python | End of Support |
|---------|--------|--------|----------------|
| 17.0 | Supported | 3.10+ | October 2026 |
| 18.0 | Current | 3.11+ | October 2027 |
| 19.0 | Development | 3.12+ | TBD |

## Version files

| Version | File |
|---------|------|
| 17.0 | `odoo-version-knowledge-17.md` |
| 18.0 | `odoo-version-knowledge-18.md` |
| 19.0 | `odoo-version-knowledge-19.md` |
| 17→18 | `odoo-version-knowledge-17-18.md` |
| 18→19 | `odoo-version-knowledge-18-19.md` |

## Compatibility matrix

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| `attrs=` | ❌ | ❌ | ❌ |
| `invisible=` direct | ✅ | ✅ | ✅ |
| `<tree>` / `<list>` | ✅/❌ | ❌/✅ | ❌/✅ |
| `group_operator=` / `aggregator=` | ✅/❌ | ❌/✅ | ❌/✅ |
| `oe_chatter` / `<chatter/>` | ✅/❌ | ❌/✅ | ❌/✅ |
| `@api.model_create_multi` | ✅ | ✅ | ✅ |
| `_check_company_auto` | ✅ | ✅ | ✅ |
| `@odoo-module` required | ✅ | ❌ | ❌ |
| `_sql_constraints` / `models.Constraint()` | ✅/❌ | ✅/❌ | ⚠️/✅ |
| `models.Index()` | ❌ | ❌ | ✅ |
| OWL | 2.x | 2.x | 2.x |
| Record rules: `company_ids` | ✅ | ✅ | ✅ |

`allowed_company_ids` is for view-level `domain=` attributes (client-side), NOT for `ir.rule.domain_force`.