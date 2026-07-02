<pattern>

  <description>
    The environment (self.env) is the gateway to the ORM: it carries the
    database cursor, user identity, context dictionary, and company scope.
    This pattern covers: reading and modifying context, sudo/with_user,
    with_company, env.ref(), env.context, active_test, and the translation
    function _() in each version.
    Use this pattern whenever you need to change execution context, bypass
    access rights safely, or resolve XML IDs.
  </description>

  <version_notes>
    <version id="17">
      from odoo import _ for translation.
      self.env.context is a frozendict — use dict(self.env.context) to copy.
      self.with_context() and self.with_user() and self.sudo() all return
      a new recordset; the original is unchanged.
    </version>
    <version id="18">
      Translation identical to v17.
      context handling unchanged.
    </version>
    <version id="19">
      self.env._() replaces the imported _ for translations in methods.
      (decision #24: self.env._() replaces from odoo import _ in v19)
      from odoo import _ still works but self.env._() is the idiomatic form.
      bypass_search_access=True new on Many2one (decision #11).
      Everything else (sudo, with_context, with_user) unchanged.
    </version>
  </version_notes>

  <examples>

    <example id="reading_context" title="Reading context values safely">
      ```python
      # Verified against project_task_17.py lines 93-96, 108-111
      # Always use .get() with a default — never direct key access
      def _get_default_stage_id(self):
          project_id = self.env.context.get('default_project_id')
          if not project_id:
              return False
          return self.stage_find(project_id, order="fold, sequence, id")

      @api.model
      def _default_company_id(self):
          if self._context.get('default_project_id'):
              return self.env['project.project'].browse(
                  self._context['default_project_id']
              ).company_id
          return False
      ```
    </example>

    <example id="with_context" title="Passing context to ORM calls">
      ```python
      # Verified against model_17.py line 181-184 (context= on field)
      # and project_task_17.py line 170 (active_test in field context)

      # Disable active filter for a search:
      all_tasks = self.env['project.task'].with_context(
          active_test=False
      ).search([('project_id', '=', self.id)])

      # Set default values for a new record created from an action:
      def action_create_subtask(self):
          self.ensure_one()
          return {
              'type': 'ir.actions.act_window',
              'res_model': 'project.task',
              'view_mode': 'form',
              'context': {
                  'default_parent_id': self.id,
                  'default_project_id': self.project_id.id,
              },
          }
      ```
    </example>

    <example id="building_action_context" title="Building context for window actions">
      ```python
      # Verified against model_17.py lines 1529-1535
      # Always copy env.context before mutating — it is a frozendict
      def action_automatic_entry(self, default_action=None):
          action = self.env['ir.actions.act_window']._for_xml_id(
              'account.account_automatic_entry_wizard_action'
          )
          ctx = dict(self.env.context)
          ctx.pop('active_id', None)
          ctx.pop('default_journal_id', None)
          ctx['active_ids'] = self.ids
          ctx['active_model'] = 'account.move.line'
          if default_action:
              ctx['default_action'] = default_action
          action['context'] = ctx
          return action
      ```
    </example>

    <example id="sudo" title="sudo() — bypassing access rights">
      ```python
      # sudo() returns a new recordset as the superuser.
      # Use it only for specific operations that require elevated rights.
      # Never use sudo() to suppress a bug in your security setup.

      def _compute_portal_user_names(self):
          # compute_sudo=True on the field is cleaner for compute methods,
          # but sudo() can be used directly when needed in business logic:
          for task in self:
              # sudo() to read followers without requiring special access
              followers = task.sudo().message_follower_ids
              task.portal_user_names = ', '.join(
                  f.partner_id.name for f in followers if f.partner_id
              )
      ```
    </example>

    <example id="with_user" title="with_user() — running as a specific user">
      ```python
      # with_user() switches identity without granting SUPERUSER privileges.
      # Access rights of the target user are enforced.
      # Verified against project_task_19.py lines 2091-2097

      def _get_access_action(self, access_uid=None, force_website=False):
          self.ensure_one()
          user = (
              self.env['res.users'].sudo().browse(access_uid)
              if access_uid
              else self.env.user
          )
          if user and user._is_portal():
              # Check with that user's rights
              if self.with_user(user).has_access('read'):
                  return {
                      'type': 'ir.actions.act_url',
                      'url': f'/my/projects/{self.project_id.id}',
                  }
          return super()._get_access_action(access_uid, force_website)
      ```
    </example>

    <example id="env_ref" title="env.ref() — resolving XML IDs">
      ```python
      # Verified against project_task_17.py lines 1682-1688
      # env.ref() is the only safe way to reference records by XML ID.
      # Never hardcode database IDs.
      def action_open_ratings(self):
          self.ensure_one()
          action = self.env['ir.actions.act_window']._for_xml_id(
              'project.rating_rating_action_task'
          )
          if self.rating_count == 1:
              action['view_mode'] = 'form'
              action['res_id'] = self.rating_ids[0].id
              action['views'] = [[
                  self.env.ref('project.rating_rating_view_form_project').id,
                  'form',
              ]]
          return action
      ```
    </example>

    <example id="translation_v17_v18" title="Translation with _ (v17/v18)">
      ```python
      # Verified against model_17.py line 7: from odoo import api, fields, models, _
      # and project_task_17.py line 9: from odoo import api, ..., _
      from odoo import _, api, fields, models
      from odoo.exceptions import UserError

      class ProjectTask(models.Model):
          _name = 'project.task'

          def action_validate(self):
              self.ensure_one()
              if not self.user_ids:
                  raise UserError(_('Please assign at least one user before validating.'))
      ```
    </example>

    <example id="translation_v19" title="Translation with self.env._() (v19)">
      ```python
      # decision #24: self.env._() is idiomatic in v19
      # Verified against project_task_19.py line 9: from odoo import ..., _
      # Both forms work; self.env._() is preferred for new code in v19.
      from odoo import api, fields, models
      from odoo.exceptions import UserError

      class ProjectTask(models.Model):
          _name = 'project.task'

          def action_validate(self):
              self.ensure_one()
              if not self.user_ids:
                  raise UserError(
                      self.env._('Please assign at least one user before validating.')
                  )
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # Direct mutation of self.env.context — it is a frozendict
      self.env.context['active_ids'] = self.ids  # RAISES TypeError

      # Correct: copy first
      ctx = dict(self.env.context)
      ctx['active_ids'] = self.ids
      new_records = self.with_context(ctx)
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # Using _ on dynamic strings or f-strings
      # Translation only works on literal strings
      name = 'Invoice'
      raise UserError(_(f'Cannot delete {name}'))     # WRONG — f-string
      raise UserError(_('Cannot delete ' + name))     # WRONG — concatenation
      raise UserError(_('Cannot delete %s' % name))  # WRONG — % formatting

      # Correct: use _('pattern %s', variable) or pass variable separately
      raise UserError(_('Cannot delete %s', name))
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Blanket sudo() that persists across an entire method
      # Grants superuser to every ORM call in the method
      def action_process(self):
          self = self.sudo()  # WRONG — elevates everything that follows
          self.partner_id.write({'active': False})  # unintended superuser write
          return self.env['ir.actions.act_window']._for_xml_id('...')

      # Correct: apply sudo() only to the specific call that needs it
      def action_process(self):
          self.ensure_one()
          self.sudo().partner_id.write({'active': False})
          return self.env['ir.actions.act_window']._for_xml_id('...')
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Hardcoding a database ID instead of using env.ref()
      stage = self.env['project.task.type'].browse(5)  # WRONG — hardcoded ID

      # Correct:
      stage = self.env.ref('project.project_stage_progress')
      ```
    </antipattern>

  </antipatterns>

</pattern>