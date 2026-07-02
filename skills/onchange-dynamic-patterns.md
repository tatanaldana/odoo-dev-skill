<pattern>

  <description>
    @api.onchange triggers Python logic when a user changes a field in a form
    view, before saving. Use it to update other fields, show warnings, or
    adjust domains dynamically. onchange runs only in the browser session —
    it is never called during write() or create() via the ORM directly.
    For data integrity on save, use @api.depends (computed fields) or
    @api.constrains instead. Covers onchange, dynamic domains on Many2one
    fields, and the domain= attribute on field definitions.
  </description>

  <version_notes>
    <version id="17">
      @api.onchange behavior: set field values, return a warning dict, or
      set a domain dict. Returning domains from onchange is deprecated in v17
      and may be removed in a future version — use computed domain fields instead.
      domain= on field definitions uses Python expression strings (v17+).
      invisible=/readonly= use Python expression strings (not attrs=).
    </version>
    <version id="18">
      @api.onchange unchanged.
      Returning domain dict from onchange still deprecated.
    </version>
    <version id="19">
      @api.onchange unchanged.
      Domain object available: from odoo.fields import Domain
      Domain() can be used in Python code for composing domains; the
      domain= attribute on fields still uses string expressions in XML views.
    </version>
  </version_notes>

  <examples>

    <example id="basic_onchange" title="Basic onchange — updating related fields">
      ```python
      # Verified against project_task_17.py lines 162-170 for domain= on field
      # onchange pattern is standard across v17/v18/v19
      from odoo import api, fields, models

      class SaleOrderLine(models.Model):
          _name = 'sale.order.line'
          _description = 'Sales Order Line'

          order_id = fields.Many2one('sale.order', required=True, ondelete='cascade')
          product_id = fields.Many2one('product.product', string='Product')
          price_unit = fields.Float(string='Unit Price')
          name = fields.Text(string='Description')

          @api.onchange('product_id')
          def _onchange_product_id(self):
              if self.product_id:
                  self.price_unit = self.product_id.lst_price
                  self.name = self.product_id.description_sale or self.product_id.name
              else:
                  self.price_unit = 0.0
                  self.name = ''
      ```
    </example>

    <example id="onchange_warning" title="onchange returning a user warning">
      ```python
      # Returning a warning notifies the user without blocking the save.
      # This is still supported — unlike domain returns which are deprecated.
      @api.onchange('date_deadline')
      def _onchange_date_deadline(self):
          if self.date_deadline and self.date_deadline < fields.Date.today():
              return {
                  'warning': {
                      'title': 'Warning',
                      'message': 'The deadline is set in the past.',
                  }
              }
      ```
    </example>

    <example id="domain_on_field" title="Static domain= on field definition">
      ```python
      # Verified against project_task_17.py lines 134-137, 162
      # domain= uses a Python expression string; field names refer to
      # fields on the current record.
      class Task(models.Model):
          _name = 'project.task'

          project_id = fields.Many2one(
              'project.project',
              string='Project',
              domain="['|', ('company_id', '=', False), ('company_id', '=?', company_id)]",
              index=True,
              tracking=True,
              change_default=True,
          )
          stage_id = fields.Many2one(
              'project.task.type',
              string='Stage',
              domain="[('project_ids', '=', project_id)]",
          )
          user_ids = fields.Many2many(
              'res.users',
              string='Assignees',
              domain="[('share', '=', False), ('active', '=', True)]",
          )
      ```
    </example>

    <example id="computed_domain" title="Computed domain field for dynamic filtering">
      ```python
      # When the domain depends on business logic, use a computed Char field
      # instead of returning a domain from onchange (which is deprecated).
      class SaleOrder(models.Model):
          _name = 'sale.order'

          company_id = fields.Many2one('res.company', required=True)
          pricelist_id = fields.Many2one('product.pricelist')
          pricelist_domain = fields.Char(compute='_compute_pricelist_domain')

          @api.depends('company_id')
          def _compute_pricelist_domain(self):
              for order in self:
                  order.pricelist_domain = str([
                      ('company_id', 'in', [order.company_id.id, False])
                  ])
      ```

      ```xml
      <!-- Use the computed domain field in the view -->
      <field name="pricelist_id" domain="pricelist_domain"/>
      ```
    </example>

    <example id="domain_object_v19" title="Domain object for Python composition (v19)">
      ```python
      # Verified against project_task_19.py lines 2228-2232
      # Domain() is used in Python code to compose domains safely.
      # The domain= attribute on fields in XML still uses string expressions.
      from odoo.fields import Domain

      def get_mention_suggestions(self, search, limit=8):
          self.ensure_one()
          followers = self.sudo().message_follower_ids
          domain = (
              Domain(self.env['res.partner']._get_mention_suggestions_domain(search))
              & Domain('id', 'in', followers.partner_id.ids)
          )
          return self.env['res.partner'].sudo()._search_mention_suggestions(
              domain, limit
          )
      ```
    </example>

    <example id="onchange_cascade" title="Cascading onchange — clearing dependent fields">
      ```python
      # When a parent field changes, clear dependent child fields.
      # This prevents stale values from persisting in the form.
      class ProjectTask(models.Model):
          _name = 'project.task'

          project_id = fields.Many2one('project.project')
          stage_id = fields.Many2one('project.task.type')
          milestone_id = fields.Many2one('project.milestone')

          @api.onchange('project_id')
          def _onchange_project_id(self):
              if self.stage_id.project_ids and self.project_id not in self.stage_id.project_ids:
                  self.stage_id = False
              if self.milestone_id.project_id != self.project_id:
                  self.milestone_id = False
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="HIGH">
      ```python
      # Returning a domain dict from onchange — deprecated in v17+
      # Will be removed in a future version; produces a warning in the logs
      @api.onchange('company_id')
      def _onchange_company_id(self):
          return {
              'domain': {
                  'warehouse_id': [('company_id', '=', self.company_id.id)],
              }
          }  # WRONG — deprecated; use a computed domain field instead

      # Correct: use a computed Char field for the domain
      warehouse_domain = fields.Char(compute='_compute_warehouse_domain')

      @api.depends('company_id')
      def _compute_warehouse_domain(self):
          for rec in self:
              rec.warehouse_domain = str(
                  [('company_id', '=', rec.company_id.id)]
              )
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # ORM write/create inside an onchange
      # onchange runs on a virtual record in the browser — changes are not
      # persisted. Writing to DB here creates inconsistent side effects.
      @api.onchange('partner_id')
      def _onchange_partner_id(self):
          if self.partner_id:
              # WRONG — writes to DB from an onchange context
              self.partner_id.write({'customer_rank': self.partner_id.customer_rank + 1})
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Using attrs= for dynamic visibility — removed in v17+
      # invisible= is the correct attribute since v17

      <!-- WRONG — attrs= is not supported in v17+ -->
      <field name="discount" attrs="{'invisible': [('product_id', '=', False)]}"/>

      <!-- Correct — use invisible= with a Python expression -->
      <field name="discount" invisible="not product_id"/>
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # Relying on onchange for data integrity — onchange is skipped
      # when creating records via the ORM (e.g. from tests, imports, automation)
      @api.onchange('qty')
      def _onchange_qty(self):
          if self.qty <= 0:
              self.qty = 1.0  # WRONG — not enforced on ORM create/write

      # Correct: use @api.constrains for validation on save
      @api.constrains('qty')
      def _check_qty(self):
          for rec in self:
              if rec.qty <= 0:
                  raise ValidationError(_('Quantity must be positive.'))
      ```
    </antipattern>

  </antipatterns>

</pattern>