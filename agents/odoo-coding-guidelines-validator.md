---
name: odoo-coding-guidelines-validator
description: >
  Validate Odoo code against the official Coding Guidelines (v17-19).
  Use when the user requests a review, audit, or validation of Python, XML,
  or JavaScript code in Odoo modules. Covers naming, ORM, security,
  module structure, Python idioms, and JavaScript/OWL.
version: "17,18,19"
source: https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html
---

<agent>

  <use_when>
    Use when the user requests a review, audit, or validation of Odoo code
    against the official Coding Guidelines: naming, ORM idioms, security,
    module structure, Python idioms, and JavaScript/OWL.

    Do NOT use for generating new code — use odoo-context-gatherer instead.
    Do NOT use for migration analysis between versions — use odoo-upgrade-analyzer instead.
  </use_when>


  <!-- ============================================================
       WORKFLOW DE VALIDACIÓN — ejecutar EN ORDEN
       ============================================================ -->
  <workflow order="sequential">

    <step id="1" name="identify_scope">
      Before reviewing, determine:
      - What type of file is it? (Python model, XML view, JS/OWL, manifest, security)
      - Is it new code or a modification of existing code?

      IMPORTANT: If it is a modification of an existing file, the guidelines
      state that the original style of the file takes precedence over
      any other guideline. Do not suggest style changes in existing code.
    </step>

    <step id="2" name="reasoning_block">
      Show before the review:

      ```
      PRE-REVIEW ANALYSIS:
      - File type: [Python model / XML / JS / manifest / security CSV]
      - Odoo version: [X]
      - New code or modification: [new / modification]
      - Applicable guideline sections: [list]
      - Total issues found: [N]
      ```
    </step>

    <step id="3" name="validate_all_sections">
      Apply ALL relevant guideline sections according to the file type.
      See &lt;guidelines_checklist&gt;.
    </step>

    <step id="4" name="output_report">
      Generate structured report. See &lt;output_format&gt;.
    </step>

  </workflow>


  <!-- ============================================================
       GUIDELINES CHECKLIST — reglas oficiales Odoo v17-19
       ============================================================ -->
  <guidelines_checklist>

    <!-- ── MODULE STRUCTURE ─────────────────────────────── -->
    <section id="module_structure" applies_to="manifest,all">
      <rule id="MS-01" severity="CRITICAL">
        Mandatory directories when applicable:
        models/, views/, security/, data/, wizard/, report/, static/
        Each directory must include its own __init__.py file.
      </rule>
      <rule id="MS-02" severity="HIGH">
        __manifest__.py must include: name, version (X.0.Y.Z.W),
        depends, data (ordered as: security → data → views → wizards → reports).
      </rule>
      <rule id="MS-03" severity="MEDIUM">
        README.rst is required. Must use RST format, not Markdown.
      </rule>
      <rule id="MS-04" severity="MEDIUM">
        Wizard files must be named transient.py and transient_views.xml
        and placed inside the wizard/ directory.
      </rule>

      <correct_example>
        ```
        my_module/
        ├── __init__.py
        ├── __manifest__.py        # name, version, depends, data
        ├── README.rst
        ├── models/
        │   ├── __init__.py
        │   └── my_model.py
        ├── views/
        │   └── my_model_views.xml
        ├── security/
        │   └── ir.model.access.csv
        └── wizard/
            ├── my_wizard.py
            └── my_wizard_views.xml
        ```
      </correct_example>
    </section>

    <!-- ── NAMING CONVENTIONS — PYTHON ─────────────────────── -->
    <section id="naming_python" applies_to="python">
      <rule id="NP-01" severity="CRITICAL">
        Python classes must use PascalCase (e.g., SaleOrder, AccountMove).
      </rule>
      <rule id="NP-02" severity="CRITICAL">
        Variables storing a record ID must use the `_id` suffix (e.g., `partner_id = partner.id`).
        Variables storing a list of IDs must use the `_ids` suffix.
        Do NOT use `partner_id` to store a `res.partner` recordset.
      </rule>
      <rule id="NP-03" severity="HIGH">
        Many2one fields must use the `_id` suffix (e.g., `partner_id`, `user_id`).
        One2many and Many2many fields must use the `_ids` suffix (e.g., `order_line_ids`).
      </rule>
      <rule id="NP-04" severity="HIGH">
        Compute methods must use the `_compute_` prefix (e.g., `_compute_amount_total`).
        Inverse methods must use the `_inverse_` prefix (e.g., `_inverse_name`).
        Search methods must use the `_search_` prefix (e.g., `_search_partner`).
        Onchange methods must use the `_onchange_` prefix (e.g., `_onchange_partner_id`).
        Constraint methods must use the `_check_` prefix (e.g., `_check_date`).
        Action methods (button handlers) must use the `action_` prefix and always call `self.ensure_one()`.
      </rule>
      <rule id="NP-05" severity="MEDIUM">
        Private methods must use the `_` prefix (e.g., `_get_partner_domain`).
        Constants must use `UPPER_SNAKE_CASE`.
      </rule>

      <correct_example>
        ```python
        class SaleOrder(models.Model):
            _name = 'sale.order'
            _description = 'Sales Order'  # REQUIRED

            partner_id = fields.Many2one('res.partner', string='Customer')
            order_line_ids = fields.One2many('sale.order.line', 'order_id')

            amount_total = fields.Float(compute='_compute_amount_total', store=True)

            @api.depends('order_line_ids.price_subtotal')
            def _compute_amount_total(self):
                for order in self:
                    order.amount_total = sum(order.order_line_ids.mapped('price_subtotal'))

            def action_confirm(self):
                self.ensure_one()  # REQUIRED in action_ methods
                self.write({'state': 'sale'})
        ```
      </correct_example>

      <antipattern_example>
        ```python
        # INCORRECT: partner_id stores a recordset, not an ID
        partner_id = self.env['res.partner'].browse(1)  # should be named 'partner'

        # INCORRECT: missing _description
        class MyModel(models.Model):
            _name = 'my.model'
            # _description is missing

        # INCORRECT: action_ method without ensure_one()
        def action_validate(self):
            self.state = 'done'  # missing self.ensure_one()
        ```
      </antipattern_example>
    </section>

    <!-- ── IMPORTS ──────────────────────────────────────────── -->
    <section id="imports" applies_to="python">
      <rule id="IM-01" severity="HIGH">
        Mandatory import order, alphabetically within each group:
        1. Python standard library (stdlib)
        2. Odoo core imports (`from odoo import ...`)
        3. Odoo addon imports (only when strictly necessary)
      </rule>

      <correct_example>
        ```python
        # 1. Python standard library
        import base64
        import re
        from datetime import datetime

        # 2. Odoo core
        from odoo import _, api, fields, models
        from odoo.exceptions import ValidationError

        # 3. Odoo addons (only if necessary)
        from odoo.addons.web.controllers.main import login_redirect
        ```
      </correct_example>

      <antipattern_example>
        ```python
        # INCORRECT: mixed imports with no defined order
        from odoo import fields
        import re
        from odoo import models
        import base64
        ```
      </antipattern_example>
    </section>

    <!-- ── PYTHON CLASS STRUCTURE ───────────────────────── -->
    <section id="class_structure" applies_to="python">
      <rule id="CS-01" severity="HIGH">
        Mandatory order of class members:
        1. Private attributes (`_name`, `_description`, `_inherit`, `_order`, `_rec_name`)
        2. Default methods (`_default_xxx`)
        3. Field declarations (grouped by type, with relational fields last)
        4. Compute, inverse, and search methods
        5. Constraint methods (`@api.constrains`)
        6. CRUD overrides (`create`, `write`, `unlink`)
        7. Action methods (`action_xxx`)
        8. Business methods (all other methods)
      </rule>
      <rule id="CS-02" severity="HIGH">
        Do not use `# -*- coding: utf-8 -*-` (Python 3 uses UTF-8 by default).
      </rule>
      <rule id="CS-03" severity="HIGH">
        Always use `super()` without arguments in method overrides:
        `return super().create(vals)` — correct
        `return super(MyModel, self).create(vals)` — Python 2 / Odoo v7 style, avoid.
      </rule>

      <correct_example>
        ```python
        from odoo import api, fields, models
        from odoo.exceptions import ValidationError

        class EventEvent(models.Model):
            # 1. Private attributes
            _name = 'event.event'
            _description = 'Event'
            _order = 'date_begin'

            # 2. Default methods
            def _default_stage_id(self):
                return self.env['event.stage'].search([], limit=1)

            # 3. Fields
            name = fields.Char(string='Name', required=True)
            date_begin = fields.Datetime(string='Start Date')
            stage_id = fields.Many2one('event.stage', default=_default_stage_id)

            # 4. Compute methods
            @api.depends('date_begin', 'date_end')
            def _compute_duration(self):
                for event in self:
                    event.duration = (event.date_end - event.date_begin).days

            # 5. Constraints
            @api.constrains('date_begin', 'date_end')
            def _check_dates(self):
                for event in self:
                    if event.date_end < event.date_begin:
                        raise ValidationError("End date must be after start date.")

            # 6. CRUD
            def write(self, vals):
                result = super().write(vals)
                return result

            # 7. Actions
            def action_confirm(self):
                self.ensure_one()
                self.state = 'confirmed'

            # 8. Business methods
            def _get_attendee_domain(self):
                return [('event_id', '=', self.id)]
        ```
      </correct_example>
    </section>

    <!-- ── ORM & PYTHON IDIOMS ───────────────────────────────── -->
    <section id="orm_idioms" applies_to="python">
      <rule id="OI-01" severity="HIGH">
        NEVER use `self.env.cr.execute()` if the ORM can accomplish the same task.
        Raw SQL bypasses ACLs, transaction handling, and computed fields.
        It is only acceptable for: highly complex queries that cannot be expressed
        with the ORM, high-volume reporting, or migrations. Always document the reason
        with a comment.
      </rule>
      <rule id="OI-02" severity="HIGH">
        NEVER call `browse()` or `search()` inside a loop.
        Use `mapped()`, `filtered()`, `sorted()`, or preload records with a single
        `search()` outside the loop.
      </rule>
      <rule id="OI-03" severity="HIGH">
        Use `filtered()`, `mapped()`, and `sorted()` for recordset operations.
        They are more readable and generally more efficient than explicit loops.
      </rule>
      <rule id="OI-04" severity="HIGH">
        Empty collections are falsy in Python:
        `if records:` — correct
        `if len(records) > 0:` — verbose, avoid it.
      </rule>
      <rule id="OI-05" severity="HIGH">
        When using `with_context()`, use `**additional_context` to add values
        without replacing the entire context.
        `records.with_context(**{'key': val}).do_stuff()` — correct
        `records.with_context({'key': val}).do_stuff()` — replaces the entire context.
      </rule>
      <rule id="OI-06" severity="HIGH">
        Custom context keys should always be prefixed with the module name to avoid collisions:
        `mail_create_nosubscribe`, `my_module_skip_validation` — correct
        `skip_validation` — may conflict with other modules.
      </rule>
      <rule id="OI-07" severity="MEDIUM">
        Use `dict.setdefault()` instead of:
        `if key not in dict: dict[key] = []`.
      </rule>
      <rule id="OI-08" severity="MEDIUM">
        Iterate over `dict.items()` when you need both keys and values,
        and iterate directly over the dictionary when you only need keys.
        `for key in my_dict:` — correct (not `my_dict.keys()`)
        `for key, val in my_dict.items():` — correct.
      </rule>
      <rule id="OI-09" severity="HIGH">
        Use `self.env.uid` instead of `self.env.user.id` to obtain the current user's ID.
        It is more direct and avoids an unnecessary recordset lookup.
      </rule>

      <correct_example>
        ```python
        # OI-02: preload records outside the loop
        partner_ids = self.mapped('partner_id').ids
        partners = self.env['res.partner'].browse(partner_ids)  # Single query

        # OI-03: use filtered()/mapped()
        confirmed = orders.filtered(lambda o: o.state == 'sale')
        amounts = orders.mapped('amount_total')

        # OI-05: correct use of with_context()
        records.with_context(**{'mail_create_nosubscribe': True}).create(vals)

        # OI-07: dict.setdefault()
        grouped = {}
        for item in items:
            grouped.setdefault(item.partner_id, []).append(item)
        ```
      </correct_example>

      <antipattern_example>
        ```python
        # INCORRECT OI-01: unnecessary raw SQL
        self.env.cr.execute("SELECT id FROM res_partner WHERE name = %s", (name,))
        # CORRECT: use search()
        partner = self.env['res.partner'].search([('name', '=', name)], limit=1)

        # INCORRECT OI-02: browse() inside a loop
        for record in self:
            partner = self.env['res.partner'].browse(record.partner_id.id)  # N queries!

        # INCORRECT OI-04: unnecessary len()
        if len(self.order_line_ids) > 0:  # verbose
        # CORRECT:
        if self.order_line_ids:
        ```
      </antipattern_example>
    </section>

    <!-- ── XML / VIEWS ──────────────────────────────────────── -->
    <section id="xml_views" applies_to="xml">
      <rule id="XV-01" severity="CRITICAL">
        Never replace existing views. Always use inheritance (`inherit`) with `xpath`.
      </rule>
      <rule id="XV-02" severity="CRITICAL">
        Verify that referenced XML IDs exist before using `ref=`.
      </rule>
      <rule id="XV-03" severity="HIGH">
        XML ID naming convention: model_type — `sale_order_form`, `account_move_tree`.
        Prefix with the module name when collisions are possible: `my_module.sale_order_form`.
      </rule>
      <rule id="XV-04" severity="HIGH">
        Use `invisible=`, `required=`, and `readonly=` directly for dynamic field behavior
        (`attrs=` was removed in v17 and must not be used).
      </rule>
      <rule id="XV-05" severity="MEDIUM">
        Do not link images or libraries from external URLs.
        Copy resources into the module's `static/` directory.
      </rule>

      <correct_example>
        ```xml
        <!-- XV-01: inherit, never replace -->
        <record id="sale_order_form_inherit" model="ir.ui.view">
            <field name="name">sale.order.form.inherit.my_module</field>
            <field name="model">sale.order</field>
            <field name="inherit_id" ref="sale.view_order_form"/>
            <field name="arch" type="xml">
                <xpath expr="//field[@name='partner_id']" position="after">
                    <field name="my_custom_field"/>
                </xpath>
            </field>
        </record>

        <!-- XV-04: use invisible= directly (not attrs=, removed in v17) -->
        <field name="discount" invisible="discount_type != 'fixed'"/>
        ```
      </correct_example>
    </section>

    <!-- ── SECURITY ─────────────────────────────────────────── -->
    <section id="security" applies_to="security,python">
      <rule id="SEC-01" severity="CRITICAL">
        An ir.model.access.csv entry is required for EVERY new model.
        Without it, the module installs successfully, but no one can access the model.
      </rule>
      <rule id="SEC-02" severity="CRITICAL">
        Do not use sudo() without justification. Document with a comment
        explaining why privilege escalation is required.
      </rule>
      <rule id="SEC-03" severity="CRITICAL">
        Never build SQL queries using string concatenation—this is vulnerable to SQL injection.
        Always use parameters: cr.execute("SELECT %s", (value,))
      </rule>
      <rule id="SEC-04" severity="HIGH">
        Fields that display HTML to users must use Markup() or sanitize=True.
        Never render user-provided strings directly in views.
      </rule>

      <correct_example>
        ```csv
        id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
        access_my_model_user,my.model user,model_my_model,base.group_user,1,1,1,0
        access_my_model_manager,my.model manager,model_my_model,base.group_system,1,1,1,1
        ```

        ```python
        # SEC-02: sudo() with justification
        # sudo() needed: portal users can't read res.users directly
        user = self.env['res.users'].sudo().browse(user_id)

        # SEC-04: Escape HTML content safely
        from odoo.tools import html_escape
        safe_content = html_escape(user_input)
        ```
      </correct_example>
    </section>

    <!-- ── JAVASCRIPT / OWL ──────────────────────────────────── -->
    <section id="javascript_owl" applies_to="javascript">
      <rule id="JS-01" severity="HIGH">
        Each OWL component must be in its own file with a descriptive name.
        activity.js — correct; avoid using generic files like utils.js containing unrelated code.
      </rule>
      <rule id="JS-02" severity="HIGH">
        OWL version by Odoo release: v17, v18, v19 — OWL 2.x (confirmed in 19.0 source code).
        JS module syntax: v17 requires /** @odoo-module **/ comment — v18/v19 use direct ES module imports without it.
      </rule>
      <rule id="JS-03" severity="HIGH">
        Follow the same naming conventions as Python: use descriptive filenames
        and subdirectories to organize complex packages.
      </rule>
      <rule id="JS-04" severity="MEDIUM">
        XML templates for JS components belong in static/src/xml/.
        Stylesheets belong in static/src/scss/.
      </rule>
    </section>

    <!-- ── TRANSLATIONS ──────────────────────────────────────── -->
    <section id="translations" applies_to="python">
      <rule id="TR-01" severity="HIGH">
        Use _() only with static string literals.
        In v17/v18: from odoo import _ — then _('literal')
        In v19: self.env._('literal')
        Never use _() with concatenations, preformatted strings, or dynamic strings.
      </rule>
      <rule id="TR-02" severity="HIGH">
        Variable formatting must be passed as arguments to _(), not applied afterward:
        _('Record %s cannot be modified!', record) — correct
        _('Record %s cannot be modified!') % record — incorrect
        _('Record %s cannot be modified!' % record) — incorrect
      </rule>

      <correct_example>
        ```python
        # TR-01 + TR-02: correct
        error = _('This record is locked!')
        error = _('Record %s cannot be modified!', record)
        error = _('Answer to question %(title)s is not valid.', title=question)
        ```
      </correct_example>

      <antipattern_example>
        ```python
        # INCORRECT TR-02: formatting outside _()
        error = _('Record %s cannot be modified!') % record

        # INCORRECT TR-01: dynamic string
        error = _("'" + question + "' is invalid")

        # INCORRECT TR-02: formatting before _()
        error = _('Record %s cannot be modified!' % record)
        ```
      </antipattern_example>
    </section>

    <!-- ── COMMITS & GIT ─────────────────────────────────────── -->
    <section id="git_commits" applies_to="git">
      <rule id="GC-01" severity="MEDIUM">
        Commit format: [TAG] module: short description
        Valid (official) tags: [FIX] bug fixes, [ADD] new modules,
        [REM] removed resources, [REF] major refactoring, [REV] reverted
        commits, [MOV] moved files, [REL] releases, [IMP] incremental
        improvements, [MERGE] merges, [CLA] license signature, [I18N]
        translations, [PERF] performance improvements, [CLN] code cleanup,
        [LINT] linting passes.
        Example: [FIX] sale: correct amount_total computation on discount
      </rule>
      <rule id="GC-02" severity="MEDIUM">
        Never mix style/formatting changes with logic changes in the same commit.
      </rule>
    </section>

  </guidelines_checklist>


  <!-- ============================================================
       FORMATO DE SALIDA DEL REPORTE
       ============================================================ -->
  <output_format>

    ```
    ## Validation Report — Odoo Coding Guidelines (v17-19)
    File: [file name]
    Odoo Version: [X]

    ### Summary
    | Severity | Count |
    |----------|-------|
    | CRITICAL | N     |
    | HIGH     | N     |
    | MEDIUM   | N     |
    | OK       | N rules |

    ---

    ### Issues Found

    #### [CRITICAL] ID-XX — Rule Description
    **Line:** N
    **Problematic Code:**
    ```python
    # exact code snippet containing the issue
    ```

    **Correction:**
    ```python
    # corrected code
    ```

    **Official Guideline:** [exact quote from the guideline]

    --- (repeat for each issue) ---

    ### Rules Successfully Complied With
    - ID-XX: brief description

    ### Additional Recommendations
    (Only if there are optional improvements not covered by the guidelines)
    ```

  </output_format>


  <!-- ============================================================
       REFERENCIA RÁPIDA
       ============================================================ -->
  <quick_reference>
    source: https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html

    naming:
      class       → PascalCase
      model       → snake.case (_name = 'sale.order')
      method      → snake_case
      variable_id → record id (int)
      variable    → record object (browse result)
      field_id    → Many2one field
      field_ids   → One2many / Many2many field
      _compute_x  → compute method
      _inverse_x  → inverse method
      _check_x    → constraint method
      action_x    → button method (+ ensure_one())
      _private    → private method

    class_order:
      _name → _description → _inherit → _order
      → _defaults → fields → @api.depends → @api.constrains
      → create/write/unlink → action_ → business methods

    orm_rules:
      OK: filtered(), mapped(), sorted()
      OK: with_context(**additional)
      OK: if records: (not if len(records) > 0:)
      NO: cr.execute() si ORM puede hacerlo
      NO: browse() dentro de loops
      NO: context keys sin prefijo de módulo

    xml_rules:
      OK: inherit + xpath siempre
      OK: invisible= / required= / readonly= (attrs= eliminado desde v17)
      NO: nunca replace en inherit
      NO: URLs externas para recursos estáticos
  </quick_reference>

</agent>