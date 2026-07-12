---
name: odoo-coding-guidelines-validator
description: Validate Odoo code against the official Coding Guidelines (v17-19).
disable-model-invocation: true
---

Validate code against Odoo Coding Guidelines. Do not generate code. Do not analyze migrations.

Source: https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html

---

## Step 1 — Identify scope

- File type: Python / XML / JS / manifest / security CSV
- New code or modification? (modification → original style takes precedence, flag only functional violations)

## Step 2 — Reasoning block

```
PRE-REVIEW ANALYSIS:
- File type: [X]
- Odoo version: [X]
- New or modification: [X]
- Applicable sections: [list]
- Issues found: [N]
```

## Step 3 — Validate all applicable sections. Every rule passes or is flagged with file + line.

## Step 4 — Output report using format below.

---

## Guidelines checklist

### Module structure
- **MS-01** `CRITICAL` — Mandatory dirs: `models/`, `views/`, `security/` with `__init__.py`
- **MS-02** `HIGH` — Manifest: `name`, `version` (`X.0.Y.Z.W`), `depends`, `data` ordered: security → data → views → wizards
- **MS-03** `MEDIUM` — `README.rst` required (RST not MD)

### Naming (Python)
- **NP-01** `CRITICAL` — Classes: PascalCase
- **NP-02** `CRITICAL` — `_id` suffix for record ID variables, `_ids` for lists
- **NP-03** `HIGH` — M2O: `_id`, O2M/M2M: `_ids`
- **NP-04** `HIGH` — Prefixes: `_compute_`, `_inverse_`, `_search_`, `_onchange_`, `_check_`, `action_` (+ `ensure_one()`)
- **NP-05** `MEDIUM` — Private: `_` prefix, constants: `UPPER_SNAKE_CASE`

### Imports
- **IM-01** `HIGH` — Order: stdlib → odoo core → odoo addons, alphabetical within groups

### Class structure
- **CS-01** `HIGH` — Order: `_name/_inherit` → defaults → fields → constraints → compute → onchange → CRUD → actions → business

### ORM
- **OR-01** `CRITICAL` — No raw SQL when ORM suffices
- **OR-02** `HIGH` — No `browse()`/`search()` in loops
- **OR-03** `HIGH` — `super()` without arguments
- **OR-04** `HIGH` — `@api.model_create_multi` on `create()`
- **OR-05** `MEDIUM` — `if records:` not `if len(records) > 0:`

### XML
- **XV-01** `CRITICAL` — No `attrs=` (removed v17)
- **XV-02** `CRITICAL` — Always xpath inherit, never replace
- **XV-03** `HIGH` — Verify XML IDs before referencing

### Security
- **SEC-01** `CRITICAL` — `ir.model.access.csv` for every model
- **SEC-02** `CRITICAL` — No unjustified `sudo()`
- **SEC-03** `CRITICAL` — No SQL string concatenation
- **SEC-04** `HIGH` — HTML fields: `Markup()` or `sanitize=True`

### JS/OWL
- **JS-01** `HIGH` — One component per file
- **JS-02** `HIGH` — OWL 2.x all versions, `@odoo-module` only v17

### Translations
- **TR-01** `HIGH` — `_()` only with literal strings, never f-strings/concatenation
- **TR-02** `HIGH` — Variables as args: `_('Record %s', record)` not `_('Record %s') % record`

### Performance
- **SR-01** `HIGH` — `search_read()` over search + per-record access
- **SR-02** `HIGH` — `@api.depends('line_ids.price_subtotal')` not `@api.depends('line_ids')`
- **SR-03** `MEDIUM` — Frequently searched fields: `index=True`

### Logging
- **LG-01** `HIGH` — `_logger` at module level
- **LG-02** `HIGH` — Correct log levels (debug/info/warning/error/exception)
- **LG-03** `CRITICAL` — No empty `except` blocks
- **LG-04** `HIGH` — UserError messages in business language, no technical details

### Docstrings
- **DC-01** `HIGH` — Non-trivial methods need docstring with `:param:` and `:return:`
- **DC-02** `MEDIUM` — Methods >50 lines: flag for review (not auto-fail)

### Git
- **GC-01** `MEDIUM` — Format: `[TAG] module: description`
- **GC-02** `MEDIUM` — Don't mix style + logic in same commit

---

## Output format

```
## Validation Report — Odoo Coding Guidelines
File: [filename] | Version: [X]

### Summary
| Severity | Count |
|----------|-------|
| CRITICAL | N |
| HIGH | N |
| MEDIUM | N |
| OK | N rules passed |

### Issues found
#### [CRITICAL] NP-01 — Class must use PascalCase
Line: 12 | Current: `class sale_order` | Fix: `class SaleOrder`

### Rules passed
- IM-01, SEC-01, ...

### Additional recommendations
```