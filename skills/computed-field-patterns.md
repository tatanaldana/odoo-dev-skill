<pattern>

  <description>
    Computed fields derive their value from other fields or business logic.
    They can be stored (persisted in DB) or non-stored (calculated on read).
    Use this pattern when a field value depends on other fields and must stay
    in sync automatically. Covers compute, inverse, search, precompute, and
    the readonly=False editable-computed pattern.
  </description>

  <version_notes>
    <version id="17">
      group_operator= controls aggregation in pivot/group views.
      SQL import: from odoo.tools.sql import SQL
      precompute=True computes during record creation before first save.
    </version>
    <version id="18">
      group_operator= renamed to aggregator= — this is a breaking change.
      SQL import path unchanged: from odoo.tools.sql import SQL
      precompute=True behavior identical to v17.
    </version>
    <version id="19">
      aggregator= (same as v18).
      SQL import moved: from odoo.tools import SQL
      Domain object available: from odoo.fields import Domain
      bypass_search_access=True new option on Many2one fields.
      Type hints and SQL() are recommended, not mandatory.
    </version>
  </version_notes>

  <examples>

    <example id="basic_stored" title="Stored computed field with @api.depends">
      ```python
      # Verified against model_17.py lines 82, 89-90, 100-102
      # store=True → written to DB; readonly=False → user can override
      sequence = fields.Integer(
          compute='_compute_sequence',
          store=True,
          readonly=False,
          precompute=True,
      )
      name = fields.Char(
          compute='_compute_name',
          store=True,
          readonly=False,
          precompute=True,
          tracking=True,
      )

      @api.depends('move_id.sequence')
      def _compute_sequence(self):
          for line in self:
              line.sequence = line.move_id.sequence

      @api.depends('move_id.name', 'product_id')
      def _compute_name(self):
          for line in self:
              line.name = line.product_id.name or line.move_id.name or ''
      ```
    </example>

    <example id="inverse" title="Computed field with inverse (bidirectional)">
      ```python
      # Verified against model_17.py lines 103-112
      # debit/credit are computed but also user-editable via inverse methods
      debit = fields.Monetary(
          compute='_compute_debit_credit',
          inverse='_inverse_debit',
          store=True,
          precompute=True,
          currency_field='company_currency_id',
      )
      credit = fields.Monetary(
          compute='_compute_debit_credit',
          inverse='_inverse_credit',
          store=True,
          precompute=True,
          currency_field='company_currency_id',
      )

      @api.depends('balance', 'debit', 'credit')
      def _compute_debit_credit(self):
          for line in self:
              if not line.is_storno:
                  line.debit = line.balance if line.balance > 0 else 0.0
                  line.credit = -line.balance if line.balance < 0 else 0.0
              else:
                  line.debit = line.balance if line.balance < 0 else 0.0
                  line.credit = -line.balance if line.balance > 0 else 0.0

      def _inverse_debit(self):
          for line in self:
              if not line.is_storno:
                  line.balance = line.debit - line.credit
              else:
                  line.balance = line.credit - line.debit

      def _inverse_credit(self):
          for line in self:
              if not line.is_storno:
                  line.balance = line.debit - line.credit
              else:
                  line.balance = line.credit - line.debit
      ```
    </example>

    <example id="non_stored_search" title="Non-stored field with custom search method">
      ```python
      # Non-stored fields are computed on every read and never written to DB.
      # A search= method enables filtering on them in domains.
      # Verified against project_task_17.py lines 172-173
      portal_user_names = fields.Char(
          compute='_compute_portal_user_names',
          compute_sudo=True,
          search='_search_portal_user_names',
      )

      @api.depends('user_ids.partner_id')
      def _compute_portal_user_names(self):
          for task in self:
              task.portal_user_names = ', '.join(
                  task.user_ids.filtered('share').mapped('name')
              )

      def _search_portal_user_names(self, operator, value):
          # Must return a domain list
          return [('user_ids.name', operator, value)]
      ```
    </example>

    <example id="aggregator_v17" title="group_operator on aggregatable field (v17)">
      ```python
      # Verified against model_17.py lines 63-71
      # group_operator= controls how pivot/group views aggregate the field
      date = fields.Date(
          related='move_id.date',
          store=True,
          copy=False,
          group_operator='min',
      )
      invoice_date = fields.Date(
          related='move_id.invoice_date',
          store=True,
          copy=False,
          group_operator='min',
      )
      # Disable aggregation entirely:
      amount_currency = fields.Monetary(
          group_operator=None,
          ...
      )
      ```
    </example>

    <example id="aggregator_v18_v19" title="aggregator= on aggregatable field (v18/v19)">
      ```python
      # Verified against model_19.py lines 69-78
      # group_operator= renamed to aggregator= — breaking change in v18
      date = fields.Date(
          related='move_id.date',
          store=True,
          copy=False,
          aggregator='min',
      )
      invoice_date = fields.Date(
          related='move_id.invoice_date',
          store=True,
          copy=False,
          aggregator='min',
      )
      ```
    </example>

    <example id="related_precompute" title="Related stored field with precompute">
      ```python
      # Verified against model_17.py lines 43-51
      # related= + store=True + precompute=True: value written at record creation
      journal_id = fields.Many2one(
          related='move_id.journal_id',
          store=True,
          precompute=True,
          index=True,
          copy=False,
      )
      company_id = fields.Many2one(
          related='move_id.company_id',
          store=True,
          readonly=True,
          precompute=True,
          index=True,
      )
      ```
    </example>

    <example id="manual_recompute" title="Manually triggering recomputation">
      ```python
      # Verified against model_17.py lines 1545-1552
      # Use env.add_to_compute() to force recompute when needed
      def _conditional_add_to_compute(self, fname, condition):
          field = self._fields[fname]
          to_reset = self.filtered(lambda line:
              condition(line)
              and not self.env.is_protected(field, line)
          )
          to_reset.invalidate_recordset([fname])
          self.env.add_to_compute(field, to_reset)
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # Missing dependency in @api.depends — silent staleness bug
      # The field will not recompute when move_id.date changes
      @api.depends('move_id')       # WRONG: incomplete dependency
      def _compute_date(self):
          for line in self:
              line.date = line.move_id.date

      # Correct:
      @api.depends('move_id.date')
      def _compute_date(self):
          for line in self:
              line.date = line.move_id.date
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # ORM call inside compute without full dependency chain
      # Causes N+1 queries and may loop on recomputation
      @api.depends('project_id')
      def _compute_task_count(self):
          for rec in self:
              # WRONG: search inside compute without depending on task fields
              rec.task_count = self.env['project.task'].search_count(
                  [('project_id', '=', rec.id)]
              )

      # Correct — use read_group for batch efficiency:
      @api.depends('task_ids')
      def _compute_task_count(self):
          for rec in self:
              rec.task_count = len(rec.task_ids)
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Using group_operator= in v18/v19 — silently ignored, no aggregation
      # v18+ renamed it to aggregator=
      date = fields.Date(group_operator='min')  # WRONG in v18/v19

      # Correct for v18/v19:
      date = fields.Date(aggregator='min')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Non-stored compute without search method used in domain
      # Will raise: Field X is not searchable
      is_active_customer = fields.Boolean(compute='_compute_is_active_customer')
      # Then in a view: domain="[('is_active_customer', '=', True)]" → CRASH

      # Fix: add store=True or add a search= method
      is_active_customer = fields.Boolean(
          compute='_compute_is_active_customer',
          search='_search_is_active_customer',
      )
      ```
    </antipattern>

  </antipatterns>

</pattern>