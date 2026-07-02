<pattern>

  <description>
    Constraints prevent invalid data from being saved.
    Odoo provides two mechanisms: SQL constraints (enforced by the database)
    and Python constraints (@api.constrains, enforced by the ORM).
    In v19, models.Constraint() and models.Index() replace the
    _sql_constraints list and manual index definitions respectively.
    Use SQL constraints for uniqueness and simple checks; use Python
    constraints for complex cross-field validation.
  </description>

  <version_notes>
    <version id="17">
      SQL constraints: _sql_constraints class attribute (list of 3-tuples).
      Python constraints: @api.constrains decorator.
      Indexes: defined in init() using create_index() from odoo.tools.sql.
      check_company=True on Many2one fields enforces company isolation.
      _check_company_auto = True on the model triggers automatic check.
      Both are present in v17 — NOT a v18 feature.
    </version>
    <version id="18">
      _sql_constraints and @api.constrains unchanged.
      Indexes still via init() with create_index().
      check_company=True and _check_company_auto unchanged from v17.
    </version>
    <version id="19">
      models.Constraint() replaces _sql_constraints — new in v19.
      models.Index() replaces manual index definitions in init() — new in v19.
      @api.constrains unchanged.
      check_company=True and _check_company_auto unchanged.
      Both styles (_sql_constraints and models.Constraint) coexist during migration.
    </version>
  </version_notes>

  <examples>

    <example id="sql_constraints_v17_v18" title="SQL constraints (v17/v18)">
      ```python
      # Verified against model_17.py — _sql_constraints pattern is standard ORM
      # Format: [('constraint_name', 'SQL CHECK(...)', 'Error message')]
      class SaleOrder(models.Model):
          _name = 'sale.order'
          _description = 'Sales Order'

          _sql_constraints = [
              (
                  'check_discount',
                  'CHECK(discount >= 0 AND discount <= 100)',
                  'Discount must be between 0 and 100.',
              ),
              (
                  'unique_reference',
                  'UNIQUE(company_id, name)',
                  'Order reference must be unique per company.',
              ),
          ]
      ```
    </example>

    <example id="models_constraint_v19" title="models.Constraint() (v19)">
      ```python
      # Verified against model_19.py structure — models.Constraint is new in v19
      # (decision #7: models.Constraint() and models.Index() new in v19)
      from odoo import fields, models

      class SaleOrder(models.Model):
          _name = 'sale.order'
          _description = 'Sales Order'

          check_discount = models.Constraint(
              'CHECK(discount >= 0 AND discount <= 100)',
              'Discount must be between 0 and 100.',
          )
          unique_reference = models.Constraint(
              'UNIQUE(company_id, name)',
              'Order reference must be unique per company.',
          )
      ```
    </example>

    <example id="python_constraint" title="Python constraint with @api.constrains">
      ```python
      # @api.constrains works identically across v17/v18/v19
      # Verified against project_task_17.py / project_task_19.py patterns
      from odoo.exceptions import ValidationError

      class ProjectTask(models.Model):
          _name = 'project.task'

          date_deadline = fields.Datetime(string='Deadline')
          date_start = fields.Datetime(string='Start Date')

          @api.constrains('date_start', 'date_deadline')
          def _check_dates(self):
              for task in self:
                  if task.date_start and task.date_deadline:
                      if task.date_start > task.date_deadline:
                          raise ValidationError(
                              _('Start date must be before the deadline.')
                          )
      ```
    </example>

    <example id="check_company" title="Company constraint on Many2one (v17/v18/v19)">
      ```python
      # Verified against model_17.py lines 25, 42, 95
      # _check_company_auto triggers automatic company checks on all
      # Many2one fields that have check_company=True.
      # Present in v17 — NOT a v18 feature (decision #3, #4).
      class AccountMoveLine(models.Model):
          _name = 'account.move.line'
          _check_company_auto = True  # triggers auto-check

          move_id = fields.Many2one(
              comodel_name='account.move',
              check_company=True,   # enforced automatically by _check_company_auto
              required=True,
          )
          account_id = fields.Many2one(
              comodel_name='account.account',
              check_company=True,
          )
      ```
    </example>

    <example id="index_v17_v18" title="Custom index in init() (v17/v18)">
      ```python
      # Verified against model_17.py imports — create_index from odoo.tools.sql
      from odoo.tools.sql import create_index

      class AccountMoveLine(models.Model):
          _name = 'account.move.line'

          def init(self):
              # Composite index not expressible as a field-level index=
              create_index(
                  self._cr,
                  'account_move_line_account_id_date_idx',
                  self._table,
                  ['account_id', 'date'],
              )
      ```
    </example>

    <example id="index_v19" title="models.Index() (v19)">
      ```python
      # decision #7: models.Index() new in v19
      # Replaces the manual init() + create_index() pattern
      from odoo import fields, models

      class AccountMoveLine(models.Model):
          _name = 'account.move.line'

          account_id_date_idx = models.Index('account_id, date')
          # With custom method:
          account_id_date_unique = models.Index(
              'account_id, date',
              unique=True,
          )
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # Using @api.constrains on a non-stored compute field
      # The constraint will never fire because the field is never written
      amount_total = fields.Float(compute='_compute_total')  # non-stored

      @api.constrains('amount_total')  # WRONG — will never fire
      def _check_positive(self):
          for rec in self:
              if rec.amount_total < 0:
                  raise ValidationError(_('Total must be positive.'))

      # Fix: constrain the source fields instead
      @api.constrains('price_unit', 'qty')
      def _check_positive(self):
          for rec in self:
              if rec.price_unit * rec.qty < 0:
                  raise ValidationError(_('Total must be positive.'))
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Catching ValidationError inside a constrains method to suppress it
      # Swallows errors silently — invalid data is saved
      @api.constrains('date_deadline')
      def _check_deadline(self):
          try:
              for rec in self:
                  if rec.date_deadline < fields.Date.today():
                      raise ValidationError(_('Deadline must be in the future.'))
          except ValidationError:
              pass  # WRONG — swallows the validation

      # Correct: let ValidationError propagate
      @api.constrains('date_deadline')
      def _check_deadline(self):
          for rec in self:
              if rec.date_deadline and rec.date_deadline < fields.Date.today():
                  raise ValidationError(_('Deadline must be in the future.'))
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Using _sql_constraints format in v19 models.Constraint() call
      # models.Constraint() takes 2 args, not 3 — the name is the attribute name
      class MyModel(models.Model):
          _sql_constraints = [  # Old style — still valid in v19 but not idiomatic
              ('check_qty', 'CHECK(qty >= 0)', 'Quantity must be non-negative.'),
          ]

          # WRONG: passing name as first arg to models.Constraint
          check_qty = models.Constraint(
              'check_qty',             # WRONG — this is the SQL expression slot
              'CHECK(qty >= 0)',
              'Quantity must be non-negative.',
          )

          # Correct v19 style:
          check_qty = models.Constraint(
              'CHECK(qty >= 0)',
              'Quantity must be non-negative.',
          )
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Forgetting to list all changed fields in @api.constrains
      # If the user changes partner_id alone, the constraint won't fire
      @api.constrains('amount')  # WRONG: missing partner_id
      def _check_credit_limit(self):
          for rec in self:
              if rec.partner_id.credit_limit < rec.amount:
                  raise ValidationError(_('Exceeds credit limit.'))

      # Correct: list every field the constraint reads
      @api.constrains('amount', 'partner_id')
      def _check_credit_limit(self):
          for rec in self:
              if rec.partner_id.credit_limit < rec.amount:
                  raise ValidationError(_('Exceeds credit limit.'))
      ```
    </antipattern>

  </antipatterns>

</pattern>