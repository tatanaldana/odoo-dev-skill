<pattern>

<description>
Patterns for translating Python strings, field content, XML views, QWeb reports, and module
`.po` files. Use in any module that must support multiple languages or locales.
</description>

<version_notes>
  <version id="17">
    Import `_` from `odoo`: `from odoo import _`. Lazy translation via `_lt` class defined
    directly in `odoo.tools.translate` (no `LazyTranslate` name exported). `export_string_translation`
    field attribute present and used by the translation export machinery (confirmed translate_17.py).
    `res.lang._activate_lang(code)` available.
  </version>
  <version id="18">
    `from odoo import _` still valid. `LazyTranslate` class introduced in `odoo.tools.translate`
    and exported (confirmed translate_18.py). `_lt` is now an alias for `LazyGettext` internally.
    `self.env._()` API available for dynamic translation (confirmed translate_18.py).
    `res.lang._activate_and_install_lang(code)` new method (activates and loads translations).
    `export_string_translation` attribute present (confirmed translate_18.py).
  </version>
  <version id="19">
    IMPORTANT — corrected: a previous version of this file claimed `from odoo import _`
    was "removed" in v19. This is FALSE. Verified against real 19.0 source:
    `from odoo import _` is still used in 36 files of addons/account/models alone
    (including account_move.py, a core actively-maintained file). Both `from odoo
    import _` and `self.env._()` remain valid in v19 — `self.env._()` is available as
    an alternative (useful when you don't want a module-level import, or want the
    translation bound to the current env's language explicitly) but is NOT a required
    replacement.
    `LazyTranslate` still imported from `odoo.tools.translate` for module-level constants
    (confirmed translate_19.py). `_lt` still works as alias. `_activate_lang()` and
    `_activate_and_install_lang()` identical to v18 (confirmed res_lang_19.py).
    `export_string_translation` attribute present (confirmed translate_19.py).
  </version>
</version_notes>

<examples>

  <example id="import_and_basic_usage_v17_v18" title="Import and basic _() usage (v17/v18)">
```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string='Name', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    def action_confirm(self):
        for record in self:
            if not record.name:
                raise UserError(_("Name is required to confirm."))
            record.state = 'confirmed'
            record.message_post(body=_("Document confirmed."))
```
  </example>

  <example id="env_translation_v19" title="Translation via self.env._() — an alternative, not a requirement (v18/v19)">
```python
from odoo import api, fields, models
from odoo.exceptions import UserError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string='Name', required=True)

    def action_confirm(self):
        for record in self:
            if not record.name:
                # self.env._() is available since v18 as an alternative to the
                # imported _() — both remain valid in v19, this is a style choice
                raise UserError(self.env._("Name is required to confirm."))
            record.state = 'confirmed'
            record.message_post(body=self.env._("Document confirmed."))
```
  </example>

  <example id="lazy_translate_v18_v19" title="Module-level constants with LazyTranslate (v18/v19)">
```python
# v18/v19: LazyTranslate for module-level string constants
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

# Evaluated lazily at render time, not at import time
LABEL_PENDING = _lt("Pending approval")
LABEL_DONE = _lt("Completed")

# v17: _lt is a class importable from odoo.tools.translate directly
# from odoo.tools.translate import _lt
# LABEL_PENDING = _lt("Pending approval")
```
  </example>

  <example id="string_formatting" title="Correct string formatting in _()">
```python
from odoo import _

# Use % formatting — f-strings break extraction
name = record.name
count = len(records)

# Single value
message = _("Record %s has been created") % name

# Multiple positional values
message = _("Created %s records in %s seconds") % (count, elapsed)

# Named placeholders (recommended for clarity)
message = _("Record %(name)s created by %(user)s") % {
    'name': record.name,
    'user': self.env.user.name,
}

# Do NOT use f-strings — the extractor cannot parse them
# Bad:  _(f"Record {name} created")
# Bad:  _("Hello ") + name + _("!")  -- split strings confuse translators
```
  </example>

  <example id="translate_true_fields" title="Translatable field content (translate=True)">
```python
from odoo import fields, models


class MyProduct(models.Model):
    _name = 'my.product'

    # translate=True: each language stores its own value in the database
    name = fields.Char(string='Name', translate=True, required=True)
    description = fields.Text(string='Description', translate=True)
    website_description = fields.Html(string='Website Description', translate=True)

    def get_name_in_languages(self):
        return {
            'current': self.name,
            'fr_FR': self.with_context(lang='fr_FR').name,
            'de_DE': self.with_context(lang='de_DE').name,
        }

    def set_translation(self, lang, value):
        self.with_context(lang=lang).write({'name': value})
```
  </example>

  <example id="export_string_translation" title="Suppressing field string export">
```python
from odoo import fields, models


class MyModel(models.Model):
    _name = 'my.model'

    # export_string_translation=False prevents the field label from being
    # included in .pot export — useful for internal/technical labels
    internal_ref = fields.Char(
        string='Internal Reference',
        export_string_translation=False,
    )
```
  </example>

  <example id="activate_lang" title="Language activation (v17/v18/v19)">
```python
from odoo import api, models


class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def install_language(self, lang_code: str):
        """Activate a language and load module translations for it."""
        # _activate_lang: activates the language record (identical v17/v18/v19)
        lang = self.env['res.lang']._activate_lang(lang_code)
        if not lang:
            # Create language record if it does not exist yet
            lang = self.env['res.lang']._create_lang(lang_code)
        if lang:
            self.env['ir.module.module']._load_module_terms(
                ['my_module'], [lang_code]
            )
        return lang

    @api.model
    def install_language_v18_plus(self, lang_code: str):
        """v18/v19: _activate_and_install_lang activates and loads translations."""
        # Equivalent to _activate_lang + toggle_active + load translations
        return self.env['res.lang']._activate_and_install_lang(lang_code)

    def get_available_languages(self):
        return self.env['res.lang'].search([('active', '=', True)])

    def get_user_language(self) -> str:
        return self.env.user.lang or self.env.context.get('lang', 'en_US')
```
  </example>

  <example id="language_context" title="Language context switching">
```python
from odoo import models


class MyModel(models.Model):
    _name = 'my.model'

    def send_email_in_partner_language(self):
        """Render and send a mail template in the partner's language."""
        for record in self:
            lang = record.partner_id.lang or 'en_US'
            template = self.env.ref('my_module.email_template')
            template.with_context(lang=lang).send_mail(record.id)
```
  </example>

  <example id="po_file_structure" title=".po / .pot file layout (unverified — no reference file)">
```
my_module/
├── i18n/
│   ├── my_module.pot      # Translation template (source strings)
│   ├── fr.po              # French
│   ├── de.po              # German
│   └── pt_BR.po           # Portuguese (Brazil)
```

```po
# Translation for Odoo module my_module — French
msgid ""
msgstr ""
"Language: fr\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#. module: my_module
#: model:ir.model,name:my_module.model_my_model
msgid "My Model"
msgstr "Mon Modèle"

#. module: my_module
#: code:addons/my_module/models/my_model.py:0
#, python-format
msgid "Record %s has been created"
msgstr "L'enregistrement %s a été créé"

#. module: my_module
#: model_terms:ir.ui.view,arch_db:my_module.my_model_view_form
msgid "Confirm"
msgstr "Confirmer"
```
  </example>

  <example id="report_language" title="QWeb report in partner language">
```xml
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h1>Order Confirmation</h1>
                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.line_ids" t-as="line">
                                <tr>
                                    <!-- render product name in the document's language -->
                                    <td t-esc="line.product_id.with_context(lang=doc.partner_id.lang).name"/>
                                    <td t-esc="line.quantity"/>
                                    <td t-field="line.price_unit"/>
                                </tr>
                            </t>
                        </tbody>
                    </table>
                </div>
            </t>
        </t>
    </t>
</template>
```
  </example>

  <example id="selection_translation" title="Selection field translations">
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'

    # Static selection: labels extracted automatically
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')

    # Dynamic selection: wrap labels with _() or self.env._() — both work in v17/v18/v19
    @api.model
    def _get_type_selection(self):
        return [
            ('type_a', self.env._('Type A')),
            ('type_b', self.env._('Type B')),
        ]

    type = fields.Selection(selection='_get_type_selection', string='Type')
```
  </example>

  <example id="test_translation" title="Testing field translations">
```python
class TestTranslation(common.TransactionCase):

    def test_field_translate(self):
        record = self.env['my.model'].create({'name': 'English Name'})
        record.with_context(lang='fr_FR').write({'name': 'Nom Français'})

        self.assertEqual(record.name, 'English Name')
        self.assertEqual(
            record.with_context(lang='fr_FR').name,
            'Nom Français',
        )
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Claiming `from odoo import _` is removed/broken in v19 — FALSE. A previous version
    of this file made this claim; it does not match real 19.0 source, where `from odoo
    import _` is still used in 36 files of addons/account/models alone (e.g.
    account_move.py). Both remain valid; do not "fix" working code that imports `_`
    this way, and do not flag it as an error in review.

```python
# VALID in v19 — this is NOT an error
from odoo import _
raise UserError(_("Cannot delete confirmed record."))

# ALSO VALID in v19 — an alternative, not a required replacement
raise UserError(self.env._("Cannot delete confirmed record."))
```
  </antipattern>

  <antipattern severity="CRITICAL">
```python
# WRONG: f-strings break translation extraction — the extractor cannot parse them
raise UserError(_(f"Record {record.name} cannot be deleted"))

# CORRECT: use % formatting
raise UserError(_("Record %s cannot be deleted") % record.name)
```
  </antipattern>

  <antipattern severity="HIGH">
```python
# WRONG: string concatenation splits the translation unit
raise UserError(_("Hello ") + name + _("!"))

# CORRECT: single translatable string with placeholder
raise UserError(_("Hello %s!") % name)
```
  </antipattern>

  <antipattern severity="HIGH">
```python
# WRONG: translating log messages wastes extraction effort and bloats .po files
_logger.info(_("Record %s processed"), record.id)

# CORRECT: keep log messages in English (not translated)
_logger.info("Record %s processed", record.id)
# Translated messages belong only in user-visible strings
record.message_post(body=_("Record processed."))
```
  </antipattern>

  <antipattern severity="MEDIUM">
```python
# WRONG: ambiguous single word that translators cannot contextualise
_("Order")  # noun or verb?

# CORRECT: provide enough context for unambiguous translation
_("Sales Order")   # clearly a noun
_("Order by date") # clearly a verb
```
  </antipattern>

</antipatterns>

</pattern>