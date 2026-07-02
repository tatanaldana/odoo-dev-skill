<pattern>

  <description>
    Exception handling patterns for Odoo modules across versions 17, 18 and 19.
    Covers choosing the right exception type, pre-action validation, savepoints for
    batch processing, transaction safety, user feedback via notifications, and
    error logging conventions.
    Use whenever a method can fail due to business logic, invalid data, or external
    service errors.
  </description>

  <version_notes>
    <version id="17">
      All exception types available: UserError, ValidationError, AccessError,
      MissingError, AccessDenied, RedirectWarning.
      @api.model_create_multi is the canonical create() override decorator.
      self.env.cr.savepoint() available for transaction isolation.
    </version>
    <version id="18">
      Exception API unchanged from v17.
      export_string_translation=False available on string fields.
    </version>
    <version id="19">
      Exception API unchanged from v17/v18.
      Use self.env._() instead of importing _ from odoo for translations.
      SQL() from odoo.tools for raw SQL (recommended, not mandatory).
    </version>
  </version_notes>

  <examples>

    <example id="exception_types" title="When to use each exception type">
      ```python
      from odoo.exceptions import (
          UserError,        # Business logic errors — shown to user in a dialog
          ValidationError,  # Data constraint violations — from @api.constrains
          AccessError,      # Permission / security violations
          MissingError,     # Record not found (browse on deleted ID)
          RedirectWarning,  # Error with a corrective action button
      )
      ```

      Exception selection guide:
      - UserError: invalid operation, wrong state, missing required data
      - ValidationError: date range check, format check, numerical constraint
      - AccessError: user lacks a group or rule to perform the action
      - MissingError: raised automatically by ORM; rarely raised manually
      - RedirectWarning: missing configuration with a link to fix it
    </example>

    <example id="user_error" title="UserError — business logic validation">
      ```python
      from odoo.exceptions import UserError


      class MyModel(models.Model):
          _name = 'my.model'

          def action_confirm(self):
              self.ensure_one()

              if not self.line_ids:
                  raise UserError("Cannot confirm without lines.")

              if self.state != 'draft':
                  raise UserError(
                      "Only draft records can be confirmed. "
                      "Current state: %s" % self.state
                  )

              self.write({'state': 'confirmed'})
      ```
    </example>

    <example id="validation_error" title="ValidationError — @api.constrains">
      ```python
      from odoo.exceptions import ValidationError
      import re


      class MyModel(models.Model):
          _name = 'my.model'

          @api.constrains('date_start', 'date_end')
          def _check_dates(self):
              for record in self:
                  if record.date_start and record.date_end:
                      if record.date_start > record.date_end:
                          raise ValidationError(
                              "Start date must be before end date."
                          )

          @api.constrains('quantity')
          def _check_quantity(self):
              for record in self:
                  if record.quantity < 0:
                      raise ValidationError("Quantity cannot be negative.")
      ```
    </example>

    <example id="redirect_warning" title="RedirectWarning — error with corrective action">
      ```python
      from odoo.exceptions import RedirectWarning


      class MyModel(models.Model):
          _name = 'my.model'

          def action_process(self):
              self.ensure_one()
              if not self.env.company.x_config_complete:
                  action = self.env.ref('my_module.action_config_wizard')
                  raise RedirectWarning(
                      "Configuration is incomplete. Please complete setup first.",
                      action.id,
                      "Go to Configuration",
                  )
      ```
    </example>

    <example id="savepoint_batch" title="Savepoints for batch processing">
      ```python
      def process_batch(self):
          """Process each record in isolation — failure of one does not abort the rest."""
          for record in self:
              try:
                  with self.env.cr.savepoint():
                      record._process_single()
              except Exception as e:
                  _logger.error("Failed to process %s: %s", record.id, e)
                  record.message_post(
                      body="Processing failed: %s" % e,
                      subtype_xmlid='mail.mt_note',
                  )
      ```
    </example>

    <example id="pre_action_validation" title="Pre-action validation — collect all errors">
      ```python
      class MyModel(models.Model):
          _name = 'my.model'

          def action_confirm(self):
              self._validate_confirm()
              self.write({'state': 'confirmed'})

          def _validate_confirm(self):
              errors = []
              for record in self:
                  if not record.partner_id:
                      errors.append("[%s] Partner is required." % record.name)
                  if not record.line_ids:
                      errors.append("[%s] At least one line required." % record.name)
                  if record.amount_total <= 0:
                      errors.append("[%s] Amount must be positive." % record.name)
              if errors:
                  raise UserError("\n".join(errors))
      ```
    </example>

    <example id="notification_feedback" title="Batch result feedback via notification">
      ```python
      def action_process_batch(self):
          total = len(self)
          processed = 0
          errors = []

          for record in self:
              try:
                  record._process()
                  processed += 1
              except Exception as e:
                  errors.append("%s: %s" % (record.name, e))

          if errors:
              return {
                  'type': 'ir.actions.client',
                  'tag': 'display_notification',
                  'params': {
                      'title': 'Processing Complete',
                      'message': 'Processed %d/%d. %d errors occurred.' % (
                          processed, total, len(errors)
                      ),
                      'type': 'warning',
                      'sticky': True,
                  },
              }
          return {
              'type': 'ir.actions.client',
              'tag': 'display_notification',
              'params': {
                  'title': 'Success',
                  'message': 'Successfully processed %d records.' % total,
                  'type': 'success',
              },
          }
      ```
    </example>

    <example id="external_service" title="External service error handling">
      ```python
      def sync_external(self):
          import requests

          try:
              response = requests.get(self.api_url, timeout=30)
              response.raise_for_status()
              return response.json()
          except requests.Timeout:
              raise UserError(
                  "External service timed out. Please try again later."
              )
          except requests.ConnectionError:
              raise UserError(
                  "Cannot connect to external service. Check your connection."
              )
          except requests.HTTPError as e:
              if e.response.status_code == 401:
                  raise UserError("Authentication failed. Check API credentials.")
              elif e.response.status_code == 404:
                  raise UserError("Resource not found on external service.")
              else:
                  raise UserError(
                      "External service error: %s" % e.response.status_code
                  )
          except Exception as e:
              _logger.exception("Unexpected error in sync")
              raise UserError("Sync failed: %s" % e)
      ```
    </example>

    <example id="sql_constraint_handling" title="SQL constraint with create override">
      ```python
      from psycopg2 import IntegrityError


      class MyModel(models.Model):
          _name = 'my.model'

          # v17/v18: _sql_constraints tuple list
          _sql_constraints = [
              ('code_unique', 'UNIQUE(code, company_id)',
               'Code must be unique per company.'),
          ]

          @api.model_create_multi
          def create(self, vals_list):
              try:
                  return super().create(vals_list)
              except IntegrityError as e:
                  if 'code_unique' in str(e):
                      raise UserError("A record with this code already exists.")
                  raise
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # Bare except that silently swallows all exceptions
      try:
          do_something()
      except:
          pass
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # Silent failure by returning False instead of raising
      try:
          do_something()
      except Exception:
          return False
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # Catching and suppressing UserError — it must reach the user as a dialog
      try:
          self._do_work()
      except UserError:
          pass   # user never sees the error
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Losing original error context — UserError message has no detail
      try:
          do_something()
      except Exception:
          raise UserError("Something went wrong")

      # Fix: include the original exception
      try:
          do_something()
      except Exception as e:
          _logger.exception("Failed in do_something")
          raise UserError("Operation failed: %s" % e)
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Using UserError inside @api.constrains — must use ValidationError
      @api.constrains('quantity')
      def _check_quantity(self):
          for record in self:
              if record.quantity < 0:
                  raise UserError("Quantity cannot be negative.")   # wrong

      # Fix
      @api.constrains('quantity')
      def _check_quantity(self):
          for record in self:
              if record.quantity < 0:
                  raise ValidationError("Quantity cannot be negative.")
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Processing a batch without savepoints — one failure aborts all records
      def process_batch(self):
          for record in self:
              record._process_single()   # if this raises, nothing is saved

      # Fix: wrap each record in a savepoint
      def process_batch(self):
          for record in self:
              try:
                  with self.env.cr.savepoint():
                      record._process_single()
              except Exception as e:
                  _logger.error("Failed %s: %s", record.id, e)
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Using cr.commit() inside a method without a rollback in the except block
      def process_with_commit(self):
          for record in self:
              record._process()
          self.env.cr.commit()   # if _process() raises above, commit is never reached
                                 # and the partial state is inconsistent

      # Fix: only call cr.commit() in cron jobs that intentionally batch-commit;
      # never inside regular RPC-called methods
      ```
    </antipattern>

  </antipatterns>

</pattern>