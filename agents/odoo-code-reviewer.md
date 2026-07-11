---
name: odoo-code-reviewer
description: Odoo module code review — quality, security, performance, and version compliance.
disable-model-invocation: true
---

Review Odoo module code systematically across all categories below.
Do not generate new code — use `odoo-context-gatherer` for that.

---

## Step 1 — Reasoning block

Output this before the review:

```
REVIEW ANALYSIS:
- Odoo version: [X]
- Files to review: [list]
- Version-specific checks active: [list breaking changes for this version]
```

Completion criterion: version confirmed, file list complete.

---

## Step 2 — Systematic review

Work through every category in [Review categories](#review-categories).
Check every item — do not skip a category because the file type seems
unrelated. Mark each item OK or flag it.

Completion criterion: every category checked, every flagged item has a
file + line reference.

---

## Step 3 — Generate report

Output the report using [Output format](#output-format).

Completion criterion: every flagged item appears in the report with
current code, required fix, and location.

---

## Review categories

**Manifest**
- Version format correct (`X.0.Y.Z.W`)
- Dependencies complete
- Data files listed in correct order: security → data → views → menus
- Assets declared
- License present
- Category set

**Models**
- Correct inheritance (`_inherit` vs `_name`)
- Correct decorators for detected version
- Field naming conventions: `_id` suffix on Many2one, `_ids` on O2m/M2m
- Computed fields optimized (`store=` where appropriate)
- Constraints properly defined
- CRUD overrides call `super()`
- `action_*` methods call `self.ensure_one()` as first line

**Security**
- `ir.model.access.csv` entry exists for every model
- Record rules use `company_ids` — not `allowed_company_ids`
- No SQL injection — no string concatenation in `cr.execute()`
- No `sudo()` without a justification comment
- No hardcoded database IDs — use `env.ref()`

**Views**
- `invisible=` / `readonly=` / `required=` used directly — `attrs=` must
  never appear (removed in v17)
- Always inherit with xpath — never replace views
- Group restrictions applied where needed
- XML IDs verified before referencing

**Performance**
- Search fields indexed where appropriate
- No N+1 patterns — no `browse()` or `search()` inside loops
- `mapped()` / `filtered()` used for batch operations
- Prefetch used where beneficial

**OWL / JavaScript** (if applicable)
- OWL 2.x for v17, v18, and v19 — confirmed in v19 source
- `@odoo-module` comment present in v17 JS files, absent in v18/v19
- Services used correctly
- Registry registration present
- Template structure valid

**Tests**
- Unit tests present
- Security tests present
- Edge cases covered

---

## Version-specific checks

**v17**
- `@odoo-module` required in all JS files
- `attrs=` must not appear anywhere in views
- `group_operator=` on fields (renamed to `aggregator=` in v18)
- `_flush_search` deprecated (v17.1) — flushing via `Environment.execute_query()`
- `inselect` operator removed (v17.4) — use `in` with a Query or SQL object

**v18**
- `aggregator=` replaces `group_operator=` on field definitions
- Bare, self-closing `<chatter/>` replaces `<div class="oe_chatter">` (dominant form in real 18.0/19.0 source; optional reload_on_attachment/reload_on_follower/reload_on_post exist for specific views but are not required)
- `@odoo-module` no longer required in JS
- `read_group()` deprecated (v18.2) → `_read_group()` / `formatted_read_group()`
- `check_access()`, `has_access()`, `_filtered_access()` available
- `_search_display_name` replaces `name_get()`
- Record rules: `company_ids` — not `allowed_company_ids`

**v19**
- `models.Constraint()` replaces `_sql_constraints`
- `models.Index()` for index definitions
- `odoo.osv.expression` superseded in modern addon code by `Domain` from `odoo.fields` (module still exists, style migration not a hard removal)
- `record._cr`, `record._context`, `record._uid` deprecated →
  `self.env.cr`, `self.env.context`, `self.env.uid`
- OWL 2.x still in use — no OWL migration required

---

## Output format

```
# Code Review: {module_name}
## Version: {odoo_version}

### Overall assessment
- Security:           ★★★★☆
- Code quality:       ★★★★★
- Performance:        ★★★☆☆
- Version compliance: ★★★★★
- Test coverage:      ★★☆☆☆

### Critical issues — fix immediately
1. [SECURITY] models/model.py:45
   Issue: SQL injection vulnerability
   Current:  cr.execute(f"SELECT * FROM {table}")
   Fix:      use ORM or parameterized query

### Warnings — should fix
1. [PERFORMANCE] models/model.py:78
   Issue: browse() inside loop — N+1 pattern
   Fix:   use mapped() or prefetch

### Suggestions — nice to have
1. [QUALITY] models/model.py:100
   Consider adding type hints (v18+)

### Positive observations
- [what is done well]

### Files reviewed
| File | Issues |
|------|--------|
| __manifest__.py | 0 |
| models/model.py | 3 |
| views/views.xml | 1 |
| security/ir.model.access.csv | 0 |
```

---

## SOLID principles — applied to Odoo

Review each principle as a judgment call, not a mechanical check.
Flag violations with the specific method or class and a concrete suggestion.

**S — Single Responsibility**
Each business method does one thing. Flag any `action_*` or business method
that mixes validation, computation, and side effects (sending email, creating
related records) in the same body. Each concern belongs in a separate method.

Incorrect:
```python
def action_confirm(self):
    self.ensure_one()
    if not self.partner_id:
        raise UserError(_("Partner is required."))
    self.amount_total = sum(self.line_ids.mapped('price_subtotal'))
    self.state = 'confirmed'
    self.message_post(body=_("Order confirmed."))
    self.env['account.move'].create({...})
```

Correct — each concern separated:
```python
def action_confirm(self):
    self.ensure_one()
    self._check_confirm_preconditions()
    self._compute_totals()
    self.write({'state': 'confirmed'})
    self._notify_confirmation()
    self._create_invoice()
```

**O — Open/Closed**
Extend via `_inherit`, never modify the original module. Flag any code that
patches or overwrites methods from another module without using inheritance.
This is the OCA "don't touch core" rule.

**L — Liskov Substitution**
When overriding an inherited method (e.g. a `_compute_*` override), the
result must still fulfill the contract expected by the field or any caller.
Flag overrides that change the return type, skip the `super()` call without
justification, or produce side effects that the original method did not have.

**I — Interface Segregation**
Mixins must be designed so a model inherits only the methods it actually
needs. Flag mixins that force inheriting models to carry methods or fields
they never use. A model that inherits `mail.thread` only to get one
`message_post` call is acceptable; a custom mixin that bundles 10 unrelated
methods is not.

**D — Dependency Inversion**
Depend on ORM methods (`self.env['model']`) rather than coupling to concrete
implementations, hardcoded IDs, or logic replicated from another module.
Flag any hardcoded `env.ref('module.xml_id')` used as a constant inside
business logic — it should be a parameter or a config field. Flag any
method that reimplements logic already available in a dependency module.

---

## UI and views

**Smart buttons**
Smart buttons (`oe_stat_button`) must use `widget="statinfo"` and display
a count that has immediate informational value (e.g. "3 invoices", "2
deliveries"). Flag smart buttons used only as navigation links with no
count, or buttons built as generic `<button>` elements without the
`statinfo` widget and the `oe_stat_button` class.

Correct:
```xml
<button class="oe_stat_button" type="object"
        name="action_view_invoices" icon="fa-pencil-square-o">
    <field widget="statinfo" name="invoice_count" string="Invoices"/>
</button>
```

**Button placement**
- Primary flow actions (confirm, cancel, approve) → statusbar buttons or
  form header as primary buttons.
- Secondary or infrequent actions → Action menu (gear icon).

Flag buttons placed outside these zones — extra buttons scattered across
the form body break the expected Odoo navigation pattern.

**No Odoo Studio for business logic**
Flag any module that shows signs of Studio-generated fields or logic
(`x_studio_` prefix on field names, Studio metadata in XML). Studio
generates configuration outside version control, without code review or
tests. Its use is permitted only for layout mockups on staging environments.

---

## Logging and error handling

**Logger declaration**
Flag any logger declared inside a method or class body instead of at module
level:
```python
# Correct — module level
import logging
_logger = logging.getLogger(__name__)
```

**Empty except blocks**
Flag immediately — no `except` with only `pass` or an empty body.
Every caught exception must be logged or re-raised.

**UserError message quality**
Flag `UserError` or `ValidationError` messages that expose technical field
names, model names, or stack traces. Messages must be written in business
language, actionable by the user without technical knowledge.

**search_read over N+1**
Flag `search()` followed by per-record field access in a loop. Suggest
`search_read()` with an explicit field list instead.