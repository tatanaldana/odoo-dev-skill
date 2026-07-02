# sequence-numbering-patterns.md

<pattern>

  <description>
    Patterns for defining ir.sequence records and consuming them in model create()
    methods to generate document reference numbers (e.g. SO0001). Covers XML
    sequence definition and the Python create() guard pattern. Verified against
    ir_sequence_17/18/19.xml, ir_sequence_17/18/19.py, sale_order_sequence_17/18/19.py.
  </description>

  <version_notes>
    <version id="17">
      ir_sequence Python imports raw psycopg2: `from psycopg2 import sql`.
      In create(): multi-company variant uses `self.with_company(vals['company_id'])`
      on a separate line before the sequence call.
      `next_by_code()` decorated with `@api.model`.
      XML sequence definition: `name`, `code`, `prefix`, `padding`, `company_id`.
      `implementation` field: `standard` (default, gaps allowed, fast) or `no_gap`.
    </version>
    <version id="18">
      ir_sequence Python imports `from odoo.tools import SQL` (replaces psycopg2 sql).
      In create(): multi-company handled inline with
      `.with_company(vals.get('company_id'))` on the sequence call itself.
      XML definition unchanged.
    </version>
    <version id="19">
      Same as v18: `from odoo.tools import SQL`, inline `.with_company()`.
      XML definition unchanged.
    </version>
  </version_notes>

  <examples>

    <example id="ir_sequence_xml" title="ir.sequence XML definition (v17/18/19 identical)">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo noupdate="1">

          <record id="seq_sale_order" model="ir.sequence">
              <field name="name">Sales Order</field>
              <field name="code">sale.order</field>
              <field name="prefix">S</field>
              <field name="padding">5</field>
              <field name="company_id" eval="False"/>
          </record>

      </odoo>
      ```
      `noupdate="1"` prevents data file from overwriting customized sequences on
      module update. `company_id` set to False makes the sequence shared across
      all companies. Set to a company ref for company-specific sequences.
      `padding=5` produces `S00001`, `S00002`, etc.
    </example>

    <example id="ir_sequence_xml_with_implementation" title="ir.sequence with no_gap implementation">
      ```xml
      <record id="seq_invoice" model="ir.sequence">
          <field name="name">Customer Invoice</field>
          <field name="code">account.move</field>
          <field name="prefix">INV/%(year)s/</field>
          <field name="padding">4</field>
          <field name="number_increment">1</field>
          <field name="implementation">no_gap</field>
          <field name="company_id" eval="False"/>
      </record>
      ```
      `no_gap` ensures no sequence number is skipped (required for legal compliance
      in some countries). It is slower than `standard` because it uses row-level
      locking. Deleted records still leave gaps — `no_gap` only prevents gaps
      from concurrent transactions.
    </example>

    <example id="create_sequence_v17" title="create() sequence guard — v17">
      ```python
      from odoo import _, api, fields, models

      class SaleOrder(models.Model):
          _name = 'sale.order'

          name = fields.Char(
              string="Order Reference",
              required=True, copy=False, readonly=False,
              index='trigram',
              default=lambda self: _('New'))

          @api.model_create_multi
          def create(self, vals_list):
              for vals in vals_list:
                  if 'company_id' in vals:
                      self = self.with_company(vals['company_id'])
                  if vals.get('name', _("New")) == _("New"):
                      seq_date = fields.Datetime.context_timestamp(
                          self, fields.Datetime.to_datetime(vals['date_order'])
                      ) if 'date_order' in vals else None
                      vals['name'] = self.env['ir.sequence'].next_by_code(
                          'sale.order', sequence_date=seq_date) or _("New")
              return super().create(vals_list)
      ```
    </example>

    <example id="create_sequence_v18_v19" title="create() sequence guard — v18/v19">
      ```python
      from odoo import _, api, fields, models

      class SaleOrder(models.Model):
          _name = 'sale.order'

          name = fields.Char(
              string="Order Reference",
              required=True, copy=False, readonly=False,
              index='trigram',
              default=lambda self: _('New'))

          @api.model_create_multi
          def create(self, vals_list):
              for vals in vals_list:
                  if vals.get('name', _("New")) == _("New"):
                      seq_date = fields.Datetime.context_timestamp(
                          self, fields.Datetime.to_datetime(vals['date_order'])
                      ) if 'date_order' in vals else None
                      # v18/v19: with_company() applied inline on the env call
                      vals['name'] = self.env['ir.sequence'].with_company(
                          vals.get('company_id')).next_by_code(
                          'sale.order', sequence_date=seq_date) or _("New")
              return super().create(vals_list)
      ```
      The key change from v17: multi-company context is set via
      `.with_company(vals.get('company_id'))` chained directly on `self.env['ir.sequence']`
      rather than reassigning `self`.
    </example>

    <example id="next_by_code" title="next_by_code() and next_by_id() API (all versions)">
      ```python
      # next_by_code() — recommended, uses sequence code string
      # Decorated @api.model — call on the model, not a record
      name = self.env['ir.sequence'].next_by_code('sale.order')
      # Returns False if no sequence found for the given code

      # next_by_id() — use when you have the sequence record directly
      # Requires read access check; call on a single record
      seq = self.env['ir.sequence'].browse(sequence_id)
      name = seq.next_by_id()

      # Deprecated — do not use
      # self.env['ir.sequence'].get('sale.order')  # calls get_id internally
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Calling `next_by_code()` unconditionally in create() without the `_("New")`
      guard — this wastes sequence numbers when records are created with an explicit
      name (e.g. from imports or copy()).
      ```python
      # WRONG — always consumes a sequence number
      def create(self, vals_list):
          for vals in vals_list:
              vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
          return super().create(vals_list)

      # CORRECT — guard on _("New") sentinel
      def create(self, vals_list):
          for vals in vals_list:
              if vals.get('name', _("New")) == _("New"):
                  vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _("New")
          return super().create(vals_list)
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Using v17's `self = self.with_company(vals['company_id'])` pattern in v18/v19.
      In v18/v19 the with_company() call moves to the sequence env lookup and uses
      `.get()` to safely handle a missing company_id key.
      ```python
      # WRONG in v18/v19
      if 'company_id' in vals:
          self = self.with_company(vals['company_id'])
      vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')

      # CORRECT in v18/v19
      vals['name'] = self.env['ir.sequence'].with_company(
          vals.get('company_id')).next_by_code('sale.order') or _("New")
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Forgetting `noupdate="1"` on ir.sequence data records — without it, each
      module upgrade overwrites the sequence counter, resetting numbering.
      ```xml
      <!-- WRONG -->
      <odoo>
          <record id="seq_sale_order" model="ir.sequence">...</record>
      </odoo>

      <!-- CORRECT -->
      <odoo noupdate="1">
          <record id="seq_sale_order" model="ir.sequence">...</record>
      </odoo>
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      Relying on `_get_last_sequence()` as a standard ir.sequence API method — this
      method is not present in the ir_sequence reference files for any version.
      Mark any use of it as unverified against your codebase.
    </antipattern>

  </antipatterns>

</pattern>