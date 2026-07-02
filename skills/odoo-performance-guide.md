<pattern>

  <description>
    Performance optimization patterns for Odoo modules across versions 17, 18 and 19.
    Covers database query reduction, batch operations, field indexing, computed field
    efficiency, raw SQL usage, prefetching, cron job design, and the built-in profiler.
    Apply these patterns proactively in any module that processes recordsets, runs cron jobs,
    or computes aggregated values.
  </description>

  <version_notes>
    <version id="17">
      SQL class available as: from odoo.tools.sql import SQL
      group_operator= used on numeric and date fields.
      index=True, index='trigram', index='btree_not_null' all available.
      _check_company_auto and check_company= available (not a v18 feature).
      Profiler available via odoo.tools.profiler.Profiler.
    </version>
    <version id="18">
      SQL class available as: from odoo.tools.sql import SQL (same as v17).
      group_operator= replaced by aggregator= — breaking change on all numeric/date fields.
      SQL() builder preferred for raw SQL but not mandatory.
      export_string_translation=False available on fields.
    </version>
    <version id="19">
      SQL class available as: from odoo.tools import SQL (path changed from v17/v18).
      SQL() builder recommended for raw SQL but NOT mandatory — raw string SQL does not
      raise errors. aggregator= inherited from v18.
      models.Constraint() and models.Index() replace _sql_constraints and manual index
      definitions at class level.
      bypass_search_access=True available on Many2one fields.
      _read_group() is the canonical ORM aggregation method (also available in v17/v18).
    </version>
  </version_notes>

  <examples>

    <example id="n_plus_one" title="N+1 query — prefetch and search_read">
      ```python
      # BAD: N+1 queries — one per record for the related field
      for order in orders:
          print(order.partner_id.name)

      # GOOD: prefetch all partners in one query before iterating
      orders.mapped('partner_id')
      for order in orders:
          print(order.partner_id.name)

      # BETTER: use search_read when only specific fields are needed
      data = self.env['sale.order'].search_read(
          [('state', '=', 'sale')],
          ['name', 'partner_id', 'amount_total'],
          limit=100,
      )
      ```
    </example>

    <example id="batch_ops" title="Batch create / write / unlink">
      ```python
      # BAD: individual creates inside a loop
      for data in data_list:
          self.env['my.model'].create(data)

      # GOOD: single ORM call with a list of dicts
      self.env['my.model'].create(data_list)

      # BAD: individual write per record
      for record in records:
          record.write({'state': 'done'})

      # GOOD: write on the entire recordset
      records.write({'state': 'done'})

      # BAD: individual unlinks
      for record in records:
          record.unlink()

      # GOOD: batch unlink
      records.unlink()
      ```
    </example>

    <example id="search_count" title="Count without loading records">
      ```python
      # BAD: loads all records just to count them
      count = len(self.env['my.model'].search([('state', '=', 'draft')]))

      # GOOD: single COUNT(*) query
      count = self.env['my.model'].search_count([('state', '=', 'draft')])

      # BAD: search all then filter in Python
      records = self.env['my.model'].search([])
      draft_records = [r for r in records if r.state == 'draft']

      # GOOD: push the filter to the database domain
      draft_records = self.env['my.model'].search([('state', '=', 'draft')])
      ```
    </example>

    <example id="compute_batch" title="Batch aggregation in computed fields">
      ```python
      # BAD: one search_count per record — O(n) queries
      @api.depends('partner_id')
      def _compute_partner_orders(self):
          for record in self:
              record.order_count = self.env['sale.order'].search_count([
                  ('partner_id', '=', record.partner_id.id)
              ])

      # GOOD: single _read_group call for the entire recordset
      # _read_group is the canonical API in v17/v18/v19
      @api.depends('partner_id')
      def _compute_partner_orders(self):
          if not self:
              return
          domain = [('partner_id', 'in', self.mapped('partner_id').ids)]
          counts_data = self.env['sale.order']._read_group(
              domain, ['partner_id'], ['__count']
          )
          mapped_data = {partner.id: count for partner, count in counts_data}
          for record in self:
              record.order_count = mapped_data.get(record.partner_id.id, 0)
      ```
    </example>

    <example id="raw_sql_v17_v18" title="Raw SQL — v17 and v18">
      ```python
      # v17 and v18: SQL imported from odoo.tools.sql
      from odoo.tools.sql import SQL

      self.env.cr.execute(SQL(
          """
          UPDATE sale_order
          SET state = %s
          WHERE id IN %s
          """,
          'done', tuple(order_ids),
      ))
      # Always invalidate the ORM cache after raw SQL writes
      self.env['sale.order'].invalidate_model(['state'])
      ```
    </example>

    <example id="raw_sql_v19" title="Raw SQL — v19">
      ```python
      # v19: SQL imported from odoo.tools (path changed from v17/v18)
      from odoo.tools import SQL

      self.env.cr.execute(SQL(
          """
          UPDATE sale_order
          SET state = %s
          WHERE id IN %s
          """,
          'done', tuple(order_ids),
      ))
      self.env['sale.order'].invalidate_model(['state'])
      ```
    </example>

    <example id="field_indexing" title="Field index types (v17/v18/v19)">
      ```python
      # Standard B-tree index — equality and range filters
      state = fields.Selection([...], index=True)
      company_id = fields.Many2one(comodel_name='res.company', index=True)
      date = fields.Date(index=True)

      # Trigram index — ILIKE / pattern searches on Char fields (v16+)
      name = fields.Char(index='trigram')

      # B-tree excluding NULLs — when most values are NULL (v16+)
      code = fields.Char(index='btree_not_null')
      ```

      ```python
      # v19 only: models.Index() for multi-column and partial indexes at class level
      # (replaces manual index definitions; _sql_constraints for CHECK stays in v17/v18)
      _partner_ref_idx = models.Index("(partner_id, ref)")
      _unreconciled_idx = models.Index(
          "(account_id, partner_id) WHERE reconciled IS NOT TRUE"
      )
      ```
    </example>

    <example id="stored_vs_nonstored" title="Stored vs non-stored computed fields">
      ```python
      # STORED: computed once, updated when dependency changes
      # Use when frequently read and infrequently changed
      total = fields.Float(
          compute='_compute_total',
          store=True,
      )

      @api.depends('line_ids.amount')
      def _compute_total(self):
          for record in self:
              record.total = sum(record.line_ids.mapped('amount'))

      # NON-STORED: recomputed on every read
      # Use when the value changes very often or is rarely displayed
      days_until_deadline = fields.Integer(
          compute='_compute_days_until_deadline',
      )

      def _compute_days_until_deadline(self):
          today = fields.Date.today()
          for record in self:
              if record.deadline:
                  record.days_until_deadline = (record.deadline - today).days
              else:
                  record.days_until_deadline = 0
      ```
    </example>

    <example id="browse_loop" title="Browse outside loops">
      ```python
      # BAD: browse() inside a loop — one query per iteration
      for record_id in record_ids:
          record = self.env['my.model'].browse(record_id)
          print(record.name)

      # GOOD: browse the entire recordset once; ORM prefetches in batch
      records = self.env['my.model'].browse(record_ids)
      for record in records:
          print(record.name)
      ```
    </example>

    <example id="algorithmic_complexity" title="Reduce algorithmic complexity">
      ```python
      # BAD: O(n^2) — list membership test inside a loop
      invalid_ids = self.search(domain).ids   # a list
      for record in self:
          if record.id in invalid_ids:         # O(n) list scan
              ...

      # GOOD: O(n) — set lookup
      invalid_ids = set(self.search(domain).ids)
      for record in self:
          if record.id in invalid_ids:         # O(1)
              ...

      # ALSO GOOD: recordset arithmetic
      invalid_records = self.search(domain)
      for record in self - invalid_records:
          ...

      # BAD: O(n^2) — nested loop matching by id
      for record in self:
          for result in results:
              if result['id'] == record.id:
                  record.foo = result['foo']
                  break

      # GOOD: O(n) — pre-build lookup dict
      mapped_result = {result['id']: result['foo'] for result in results}
      for record in self:
          record.foo = mapped_result.get(record.id)
      ```
    </example>

    <example id="prefetch_groups" title="Manual prefetch before iteration">
      ```python
      def process_orders(self, orders):
          # Prefetch all related data before the loop — one query per relation
          orders.mapped('partner_id')
          orders.mapped('order_line_ids')
          orders.mapped('order_line_ids.product_id')

          # No additional queries inside the loop
          for order in orders:
              for line in order.order_line_ids:
                  print(line.product_id.name)
      ```
    </example>

    <example id="cron_batch" title="Cron job with batch processing">
      ```python
      @api.model
      def _cron_process_large_dataset(self):
          """Process records in batches to avoid memory pressure."""
          batch_size = 1000
          offset = 0

          while True:
              records = self.search(
                  [('state', '=', 'pending')],
                  limit=batch_size,
                  offset=offset,
              )
              if not records:
                  break

              for record in records:
                  try:
                      record._process_single()
                  except Exception as e:
                      _logger.error("Failed to process %s: %s", record.id, e)

              # Commit this batch and clear the ORM cache
              self.env.cr.commit()
              self.env.invalidate_all()
              offset += batch_size
      ```
    </example>

    <example id="profiler" title="Using the built-in profiler">
      ```python
      # Profile a specific block of code
      from odoo.tools.profiler import Profiler

      with Profiler():
          do_stuff()

      # Profile with specific collectors
      from odoo.tools.profiler import Profiler, PeriodicCollector

      with Profiler(collectors=['sql', PeriodicCollector(interval=0.1)]):
          do_stuff()

      # In tests — shortcut via self.profile()
      with self.profile():
          with self.assertQueryCount(__system__=50):
              do_stuff()

      # Label iterations for speedscope using ExecutionContext
      from odoo.tools.profiler import ExecutionContext

      for index in range(max_index):
          with ExecutionContext(current_index=index):
              do_stuff()
      ```
      Profiling results are saved as ir.profile records, visualized via speedscope
      (Settings > Performance or developer mode tools panel).
      Odoo Online databases cannot be profiled.
      Collectors: sql (SqlCollector), traces_async (PeriodicCollector),
      qweb (QwebCollector), traces_sync (SyncCollector — high overhead, not for perf).
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # N+1 pattern: accessing a relational field inside a loop without prefetch
      for order in orders:
          print(order.partner_id.name)  # one query per order

      # Fix: prefetch with mapped() before the loop
      orders.mapped('partner_id')
      for order in orders:
          print(order.partner_id.name)
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # browse() inside a loop — defeats ORM prefetching
      for record_id in record_ids:
          record = self.env['my.model'].browse(record_id)
          print(record.name)

      # Fix: browse the full recordset once
      records = self.env['my.model'].browse(record_ids)
      for record in records:
          print(record.name)
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # len(search(...)) to count — loads all records unnecessarily
      count = len(self.env['my.model'].search([('state', '=', 'draft')]))

      # Fix
      count = self.env['my.model'].search_count([('state', '=', 'draft')])
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Per-record search_count inside a compute method
      @api.depends('partner_id')
      def _compute_partner_orders(self):
          for record in self:
              record.order_count = self.env['sale.order'].search_count([
                  ('partner_id', '=', record.partner_id.id)
              ])

      # Fix: use _read_group for a single aggregation query
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # v18/v19: group_operator= was removed in v18
      date = fields.Date(group_operator='min')

      # Fix for v18/v19
      date = fields.Date(aggregator='min')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Creating records one by one
      for data in data_list:
          self.env['my.model'].create(data)

      # Fix
      self.env['my.model'].create(data_list)
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # sudo() inside a loop
      for record in records:
          record.sudo().write({'field': value})

      # Fix: cache sudo environment outside the loop
      records.sudo().write({'field': value})
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Skipping ORM cache invalidation after raw SQL writes
      self.env.cr.execute("UPDATE my_model SET state = 'done' WHERE id IN %s",
                          (tuple(ids),))
      # ORM cache now stale — subsequent reads return wrong values

      # Fix: always invalidate after raw SQL writes
      self.env['my.model'].invalidate_model(['state'])
      ```
    </antipattern>

  </antipatterns>

</pattern>