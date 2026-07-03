---
name: odoo-coding-guidelines-validator
description: Validate Odoo code against the official Coding Guidelines (v17-19).
disable-model-invocation: true
---

Validate Python, XML, or JavaScript code against the official Odoo Coding
Guidelines. Do not generate new code — use `odoo-context-gatherer` for that.
Do not analyze migrations — use `odoo-upgrade-analyzer` for that.

Source: https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html

---

## Step 1 — Identify scope

Determine before reviewing:
- File type: Python model / XML view / JS-OWL / manifest / security CSV
- New code or modification of existing file?

If it is a **modification** of an existing file, the original file's style
takes precedence over any guideline. Do not suggest style changes in
existing code — only flag functional violations.

Completion criterion: file type known, new vs modification determined.

---

## Step 2 — Reasoning block

Output this before the review:

```
PRE-REVIEW ANALYSIS:
- File type: [Python model / XML / JS / manifest / security CSV]
- Odoo version: [X]
- New code or modification: [new / modification]
- Applicable guideline sections: [list]
- Total issues found: [N]
```

Completion criterion: applicable sections listed, issue count estimated.

---

## Step 3 — Validate all sections

Apply every guideline section that matches the file type.
See [Guidelines checklist](#guidelines-checklist) below.
Every rule either passes or is flagged with file + line reference.

Completion criterion: every applicable rule checked, none skipped.

---

## Step 4 — Output report

Use [Output format](#output-format).

Completion criterion: every flagged rule in the report with current code,
correction, and guideline reference.

---

## Guidelines checklist

### Module structure — applies to: manifest, all files

**MS-01** `CRITICAL` — Mandatory directories when applicable:
`models/`, `views/`, `security/`, `data/`, `wizard/`, `report/`,
`static/`. Each must include its own `__init__.py`.

**MS-02** `HIGH` — `__manifest__.py` must include: `name`, `version`
(`X.0.Y.Z.W`), `depends`, `data` ordered as:
security → data → views → wizards → reports.

**MS-03** `MEDIUM` — `README.rst` required. RST format, not Markdown.

**MS-04** `MEDIUM` — Wizard files named `transient.py` and
`transient_views.xml`, placed inside `wizard/`.

---

### Naming conventions — applies to: Python

**NP-01** `CRITICAL` — Classes use PascalCase (`SaleOrder`, `AccountMove`).

**NP-02** `CRITICAL` — Variables storing a record ID use `_id` suffix
(`partner_id = partner.id`). Variables storing a list of IDs use `_ids`.
Never use `partner_id` to store a `res.partner` recordset.

**NP-03** `HIGH` — Many2one fields use `_id` suffix. One2many and
Many2many fields use `_ids` suffix.

**NP-04** `HIGH` — Method prefixes:
- `_compute_` — compute methods
- `_inverse_` — inverse methods
- `_search_` — search methods
- `_onchange_` — onchange methods
- `_check_` — constraint methods
- `action_` — button handlers, must call `self.ensure_one()` first

**NP-05** `MEDIUM` — Private methods use `_` prefix. Constants use
`UPPER_SNAKE_CASE`.

---

### Imports — applies to: Python

**IM-01** `HIGH` — Mandatory import order, alphabetical within each group:
1. Python standard library
2. Odoo core (`from odoo import ...`)
3. Odoo addons (only when strictly necessary)

---

### Class structure — applies to: Python

**CS-01** `HIGH` — Mandatory order of class members:
1. Private attributes (`_name`, `_description`, `_inherit`, `_order`, `_rec_name`)
2. Default methods (`_default_xxx`)
3. Field declarations
4. SQL constraints / `models.Constraint()` (v19+)
5. Compute / search / inverse methods
6. Selection methods
7. `@api.constrains` / `@api.onchange`
8. CRUD overrides (`create`, `write`, `unlink`)
9. `action_*` methods
10. Business methods

---

### ORM usage — applies to: Python

**OR-01** `CRITICAL` — Never use raw SQL (`cr.execute`) when the ORM can
do the same — use `search()`, `read_group()`, or `filtered()`.

**OR-02** `HIGH` — Never call `browse()` or `search()` inside a loop —
use `mapped()` or `filtered()`.

**OR-03** `HIGH` — Always use `super()` without arguments in overrides.

**OR-04** `HIGH` — `@api.model_create_multi` required on `create()`
overrides — iterate with `for record in self`.

**OR-05** `MEDIUM` — Use `if records:` not `if len(records) > 0:`.

**OR-06** `MEDIUM` — Context keys must include a module prefix to avoid
collisions (e.g. `my_module_key`, not just `key`).

---

### XML views — applies to: XML

**XV-01** `CRITICAL` — `attrs=` must never appear — removed in v17.
Use `invisible=` / `readonly=` / `required=` directly.

**XV-02** `CRITICAL` — Always inherit with xpath — never replace views.

**XV-03** `HIGH` — XML IDs verified before referencing in xpath or
`inherit_id`.

**XV-04** `MEDIUM` — Group restrictions applied with `groups=` where
access control is needed at the view level.

---

### Security — applies to: security CSV, Python

**SEC-01** `CRITICAL` — `ir.model.access.csv` entry required for every
new model.

**SEC-02** `CRITICAL` — Never use `sudo()` without a justification
comment explaining why privilege escalation is required.

**SEC-03** `CRITICAL` — Never build SQL with string concatenation —
always use parameters: `cr.execute("SELECT %s", (value,))`.

**SEC-04** `HIGH` — Fields rendering HTML to users must use `Markup()`
or `sanitize=True`.

---

### JavaScript / OWL — applies to: JS

**JS-01** `HIGH` — One OWL component per file, descriptive filename.

**JS-02** `HIGH` — OWL 2.x for v17, v18, and v19 — confirmed in v19
source. `@odoo-module` required in v17, not needed in v18/v19.

**JS-03** `HIGH` — Same naming conventions as Python: descriptive
filenames, subdirectories for complex packages.

**JS-04** `MEDIUM` — XML templates in `static/src/xml/`.
Stylesheets in `static/src/scss/`.

---

### Translations — applies to: Python

**TR-01** `HIGH` — `_()` only with static string literals.
v17/v18: `from odoo import _` then `_('literal')`.
v19: `self.env._('literal')`.
Never use `_()` on concatenations, f-strings, or dynamic strings.

**TR-02** `HIGH` — Pass variables as arguments to `_()`, not after:
- Correct: `_('Record %s cannot be modified!', record)`
- Incorrect: `_('Record %s cannot be modified!') % record`
- Incorrect: `_('Record %s cannot be modified!' % record)`

---

### Git commits — applies to: git

**GC-01** `MEDIUM` — Commit format: `[TAG] module: short description`.
Valid tags: `[FIX]`, `[ADD]`, `[REM]`, `[REF]`, `[REV]`, `[MOV]`,
`[REL]`, `[IMP]`, `[MERGE]`, `[CLA]`, `[I18N]`, `[PERF]`, `[CLN]`,
`[LINT]`.

**GC-02** `MEDIUM` — Never mix style changes with logic changes in the
same commit.

---

## Output format

```
## Validation Report — Odoo Coding Guidelines (v17-19)
File: [filename]
Odoo version: [X]

### Summary
| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| OK       | N rules passed |

---

### Issues found

#### [CRITICAL] NP-01 — Class must use PascalCase
Line: 12
Current:
  class sale_order(models.Model):
Correction:
  class SaleOrder(models.Model):
Guideline: "Python classes must use PascalCase"

--- (repeat for each issue) ---

### Rules passed
- IM-01: import order correct
- SEC-01: ir.model.access.csv present

### Additional recommendations
(Optional improvements not covered by the guidelines)
```

---

### Docstrings and method size — applies to: Python

**DC-01** `HIGH` — Every non-trivial method requires a docstring explaining
its purpose, `:param:` for each input parameter, and `:return:` for the
return value. Trivial methods (one-liners, property-like accessors) are
exempt. The docstring describes *what* and *why*, not a line-by-line *how*.

Correct:
```python
def _compute_total_amount(self):
    """Compute the total amount summing all order line subtotals.

    :return: None — updates total_amount field in place.
    """
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('price_subtotal'))
```

Incorrect — inline comments are not a docstring substitute:
```python
def _compute_total_amount(self):
    # loop through records and sum subtotals
    for record in self:
        record.total_amount = sum(record.line_ids.mapped('price_subtotal'))
```

**DC-02** `MEDIUM` — Methods or classes exceeding 50-60 lines are a review
signal, not a hard block. Flag them with the line count and suggest
reviewing whether the method mixes responsibilities. Do not auto-fail.

---

### Performance — applies to: Python

**SR-01** `HIGH` — Prefer `search_read()` with an explicit field list over
`search()` followed by per-record field access. The latter triggers one
query per record (N+1 pattern).

Correct:
```python
records = self.env['sale.order'].search_read(
    [('state', '=', 'sale')],
    fields=['name', 'partner_id', 'amount_total'],
)
```

Incorrect:
```python
records = self.env['sale.order'].search([('state', '=', 'sale')])
for rec in records:
    name = rec.name          # triggers query per record
    total = rec.amount_total
```

**SR-02** `HIGH` — `@api.depends` must not trigger mass recomputation
unnecessarily. Flag dependencies on a `One2many` or `Many2many` field
without a specific subfield path.

Incorrect:
```python
@api.depends('line_ids')               # recomputes on ANY change to lines
def _compute_total(self):
    ...
```

Correct:
```python
@api.depends('line_ids.price_subtotal')  # only when subtotal changes
def _compute_total(self):
    ...
```

**SR-03** `MEDIUM` — Fields used frequently in `search()` domains or
`order=` clauses must have `index=True`.

---

### Logging — applies to: Python

**LG-01** `HIGH` — Logger declared at module level, not inside methods or
classes:
```python
import logging
_logger = logging.getLogger(__name__)
```
Never use `print()` as a substitute — flag every `print()` in code
intended for production.

**LG-02** `HIGH` — Correct logger level by situation:
- `_logger.debug` — diagnostic detail, development only; acceptable in
  production only if it does not affect performance when debug is off
- `_logger.info` — relevant operational events (batch start, integration
  completed, record count processed)
- `_logger.warning` — anomaly the system handled but that needs attention
  (missing config with default applied, unexpected state auto-corrected);
  a recurring warning in production is a low-severity bug, not acceptable
  behaviour
- `_logger.error` — failure that prevented an operation but system
  recovered partially; always add `exc_info=True` inside `except`
- `_logger.exception` — equivalent to `error` with automatic stack trace;
  preferred inside `except` blocks over `error + exc_info=True`

Flag any logger call without sufficient context to be actionable in
production (e.g. bare `_logger.error("failed")` with no record ID or
operation name).

**LG-03** `CRITICAL` — No empty `except` blocks and no `except` with only
`pass`. Every caught exception must be logged or re-raised.

Incorrect:
```python
try:
    record.action_confirm()
except Exception:
    pass
```

Correct:
```python
try:
    record.action_confirm()
except Exception:
    _logger.exception("Failed to confirm record %s", record.id)
    raise UserError(_("Could not confirm the record. Check the logs."))
```

**LG-04** `HIGH` — `UserError` and `ValidationError` messages must not
expose technical field names, model names, or stack traces. The message
must be actionable by the user without technical knowledge.

Incorrect:
```python
raise UserError(f"sale.order field amount_total: {traceback.format_exc()}")
```

Correct:
```python
raise UserError(_("The order total could not be computed. Please check the order lines."))
```