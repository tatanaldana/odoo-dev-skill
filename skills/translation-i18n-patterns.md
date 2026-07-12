# Translation & i18n Patterns — v17/v18/v19

---

## Version differences

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| `from odoo import _` | valid | valid | **still valid** (36 files in account/models use it) |
| `self.env._()` | not available | available | available (alternative, NOT replacement) |
| `LazyTranslate` | `from odoo.tools.translate import _lt` | `LazyTranslate(__name__)` | same as v18 |
| `_activate_and_install_lang` | not available | new | same as v18 |
| `export_string_translation` | available | available | available |

**IMPORTANT:** `from odoo import _` is NOT removed in v19. Both `_()` and `self.env._()` are valid.

---

## Basic usage

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError

# String formatting — always use %, never f-strings
raise UserError(_("Record %s cannot be deleted") % record.name)
raise UserError(_("Created %(count)s records by %(user)s") % {'count': count, 'user': user.name})

# WRONG: f-string breaks extraction
# raise UserError(_(f"Record {name} deleted"))
# WRONG: concatenation splits translation unit
# raise UserError(_("Hello ") + name + _("!"))
```

## LazyTranslate (v18/v19) — module-level constants

```python
from odoo.tools.translate import LazyTranslate
_lt = LazyTranslate(__name__)
LABEL_PENDING = _lt("Pending approval")  # evaluated lazily at render time

# v17: from odoo.tools.translate import _lt
```

## self.env._() (v18/v19) — alternative

```python
# Style choice — not a required migration from _()
raise UserError(self.env._("Name is required to confirm."))
```

## Translatable fields

```python
name = fields.Char(translate=True)  # each language stores its own value
internal_ref = fields.Char(export_string_translation=False)  # suppress from .pot

# Read in specific language
fr_name = record.with_context(lang='fr_FR').name
```

## Language activation

```python
# v17/v18/v19
self.env['res.lang']._activate_lang('fr_FR')
# v18/v19 shortcut
self.env['res.lang']._activate_and_install_lang('fr_FR')
```

## .po file structure

```
my_module/i18n/
├── my_module.pot    # template (source strings)
├── fr.po            # French
└── es.po            # Spanish
```

## Email/report in partner language

```python
template = self.env.ref('my_module.email_template')
template.with_context(lang=record.partner_id.lang).send_mail(record.id)
```

## Selection translation

```python
# Static: labels extracted automatically
priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')])

# Dynamic: use _() or self.env._()
@api.model
def _get_type_selection(self):
    return [('type_a', self.env._('Type A')), ('type_b', self.env._('Type B'))]
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `from odoo import _` is NOT removed in v19 — don't flag it |
| CRITICAL | No f-strings inside `_()` — breaks extraction |
| HIGH | No string concatenation splitting translation units |
| HIGH | Don't translate log messages — only user-visible strings |
| MEDIUM | Provide enough context in strings (`"Sales Order"` not just `"Order"`) |