<pattern>

  <description>
    Domains are list-based filter expressions used throughout Odoo: in
    search(), filtered(), XML view attributes (domain=, invisible=,
    readonly=), record rules, and action domains. This pattern covers:
    domain syntax, combining operators, expression module helpers,
    the Domain object (v19), and common patterns verified in reference files.
    Use this pattern whenever you need to filter records or restrict visibility.
  </description>

  <version_notes>
    <version id="17">
      Domains are Python lists of tuples: [('field', 'operator', 'value')].
      Logical operators: '&', '|', '!' as prefix elements.
      from odoo.osv import expression for programmatic domain composition.
      Verified: project_task_17.py line 13 imports expression.
    </version>
    <version id="18">
      Domain syntax unchanged.
      from odoo.osv import expression unchanged.
    </version>
    <version id="19">
      from odoo.fields import Domain — new object-oriented domain API.
      (decision #10: Domain from odoo.fields in v19)
      Domain() supports &amp; and | operators for safe composition.
      list-based domains still fully supported.
      Verified: project_task_19.py lines 10, 2228-2232 use Domain.
    </version>
  </version_notes>

  <examples>

    <example id="basic_domain" title="Basic domain syntax">
      ```python
      # Standard domain — list of (field, operator, value) tuples
      # Implicit AND between tuples at the top level
      domain = [
          ('state', '=', 'draft'),
          ('partner_id', '!=', False),
          ('amount_total', '>', 1000.0),
      ]
      records = self.env['sale.order'].search(domain)

      # Common operators: =, !=, <, >, <=, >=
      # like (case-sensitive), ilike (case-insensitive, wildcards with %)
      # in, not in (value must be a list)
      # =like, =ilike (exact match with SQL wildcards)
      # child_of, parent_of (hierarchical)
      ```
    </example>

    <example id="logical_operators" title="Combining with | and &amp;">
      ```python
      # | and & are PREFIX operators — they apply to the NEXT TWO terms
      # Verified against model_17.py lines 3386-3398 (_get_tax_exigible_domain)

      # OR: records where state=draft OR state=cancel
      domain = ['|', ('state', '=', 'draft'), ('state', '=', 'cancel')]

      # AND explicitly (same as default):
      domain = ['&', ('state', '=', 'draft'), ('partner_id', '!=', False)]

      # Complex: (state=draft OR state=cancel) AND partner_id is set
      domain = [
          '&',
              '|', ('state', '=', 'draft'), ('state', '=', 'cancel'),
              ('partner_id', '!=', False),
      ]

      # NOT: records where state is NOT 'done'
      domain = ['!', ('state', '=', 'done')]
      # Equivalent:
      domain = [('state', '!=', 'done')]
      ```
    </example>

    <example id="real_domain" title="Real domain from reference — tax exigibility">
      ```python
      # Verified against model_17.py lines 3381-3399
      # Demonstrates multi-level OR chaining with prefix operators
      @api.model
      def _get_tax_exigible_domain(self):
          return [
              '|', ('move_id.always_tax_exigible', '=', True),
              '|', '&', ('tax_line_id', '=', False), ('tax_ids', '=', False),
              '|', ('move_id.tax_cash_basis_rec_id', '!=', False),
              '|', ('tax_line_id.tax_exigibility', '!=', 'on_payment'),
                   ('tax_ids.tax_exigibility', '!=', 'on_payment'),
          ]
      ```
    </example>

    <example id="expression_module" title="expression module for programmatic composition">
      ```python
      # Verified: project_task_17.py line 13 imports expression
      # Use for safely combining domains in code
      from odoo.osv import expression

      base_domain = [('state', '=', 'active')]
      extra_domain = [('company_id', '=', self.env.company.id)]

      # AND two domains together:
      combined = expression.AND([base_domain, extra_domain])

      # OR two domains:
      either = expression.OR([base_domain, extra_domain])

      # Normalize: converts leaf tuples to canonical 3-tuple form
      clean = expression.normalize_domain(combined)
      ```
    </example>

    <example id="domain_on_field" title="Domain= on field and in views">
      ```python
      # Verified against project_task_17.py lines 162, 134-137
      # domain= on a field definition uses a Python expression string
      # Field names in the expression refer to fields on the current record

      project_id = fields.Many2one(
          'project.project',
          domain="['|', ('company_id', '=', False), ('company_id', '=?', company_id)]",
      )
      stage_id = fields.Many2one(
          'project.task.type',
          domain="[('project_ids', '=', project_id)]",
      )
      ```

      ```xml
      <!-- Domain in a view attribute — restricts the dropdown options -->
      <!-- Verified against views_17.xml lines 19-21, 27 -->
      <field name="partner_id"
          domain="['|', ('parent_id', '=', False), ('is_company', '=', True)]"/>
      <field name="account_id"
          domain="[('company_id', 'parent_of', company_id), ('deprecated', '=', False)]"/>
      ```
    </example>

    <example id="filtered" title="filtered() for in-memory domain filtering">
      ```python
      # Use filtered() on a recordset instead of searching in a loop
      # Verified against project_task_19.py lines 2085-2086
      def action_archive(self):
          # Filter child tasks before archiving — no extra query
          child_tasks = self.child_ids.filtered(
              lambda child_task: not child_task.display_in_project
          )
          if child_tasks:
              child_tasks.action_archive()
          return super().action_archive()

      # filtered() with a string — uses field truthiness
      active_users = self.user_ids.filtered('active')
      portal_users = self.user_ids.filtered('share')
      ```
    </example>

    <example id="domain_object_v19" title="Domain object composition (v19)">
      ```python
      # Verified against project_task_19.py lines 2228-2232
      # Domain() uses & and | as infix operators — cleaner for complex logic
      from odoo.fields import Domain

      def _build_partner_domain(self, search_term):
          base = Domain(self.env['res.partner']._get_mention_suggestions_domain(search_term))
          followers = self.sudo().message_follower_ids
          restrict = Domain('id', 'in', followers.partner_id.ids)
          return base & restrict

      # Equivalent using list syntax:
      # expression.AND([base_domain, restrict_domain])
      ```
    </example>

    <example id="action_domain" title="Dynamic domain on a window action">
      ```python
      # Verified against project_task_17.py lines 1654-1666
      # Modify an action's domain to filter records shown
      def action_dependent_tasks(self):
          self.ensure_one()
          action = {
              'res_model': 'project.task',
              'type': 'ir.actions.act_window',
              'context': {
                  **self._context,
                  'default_depend_on_ids': [Command.link(self.id)],
              },
          }
          if self.dependent_tasks_count == 1:
              action['view_mode'] = 'form'
              action['res_id'] = self.dependent_ids.id
              action['views'] = [(False, 'form')]
          else:
              action['domain'] = [('depend_on_ids', '=', self.id)]
              action['name'] = _('Dependent Tasks')
              action['view_mode'] = 'list,form,kanban,calendar,pivot,graph,activity'
          return action
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # Using search() inside a loop — N+1 query problem
      for project in projects:
          tasks = self.env['project.task'].search([('project_id', '=', project.id)])
          # WRONG — one query per project

      # Correct: single query with 'in' operator
      tasks = self.env['project.task'].search(
          [('project_id', 'in', projects.ids)]
      )
      # Then group by project_id in Python if needed
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # Malformed domain — prefix operator applied to wrong number of terms
      # '|' applies to exactly the NEXT two terms
      domain = [
          '|',
          ('state', '=', 'draft'),
          ('state', '=', 'cancel'),
          ('partner_id', '!=', False),  # WRONG — this floats outside the OR
      ]
      # The above reads as: (state=draft OR state=cancel), AND partner_id!=False
      # would need explicit & to be correct if that's the intent

      # If you want all three in one OR:
      domain = [
          '|', '|',
          ('state', '=', 'draft'),
          ('state', '=', 'cancel'),
          ('partner_id', '!=', False),
      ]
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # Using allowed_company_ids in domain_force of record rules
      # NOT confirmed in any reference file — use company_ids instead
      # (decision #19: company_ids in domain_force v17/18/19)

      # WRONG — allowed_company_ids is not the field used in ir.rule domain_force
      <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

      # Correct — verified in ir_rules reference files:
      <field name="domain_force">[('company_id', 'in', company_ids)]</field>
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Hardcoding IDs in a domain — breaks across installations
      domain = [('stage_id', '=', 5)]  # WRONG — ID 5 may differ per instance

      # Correct: use xml_id via env.ref()
      stage = self.env.ref('project.project_stage_in_progress')
      domain = [('stage_id', '=', stage.id)]
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Using browse() inside a loop to filter — very inefficient
      result = []
      for task_id in task_ids:
          task = self.env['project.task'].browse(task_id)
          if task.state == 'done':
              result.append(task)
      # WRONG — N ORM reads

      # Correct: search or filtered
      tasks = self.env['project.task'].browse(task_ids)
      result = tasks.filtered(lambda t: t.state == 'done')
      ```
    </antipattern>

  </antipatterns>

</pattern>