# config-settings-patterns.md

<pattern>

  <description>
    Patterns for extending res.config.settings to add module-level configuration
    options. Covers config_parameter fields, implied_group fields, related fields,
    set_values() overrides, and the settings form XML structure. Verified against
    res_config_settings_17/18/19.py and res_config_settings_17/18/19.xml.
    All three versions share the same Python and XML patterns — no breaking changes
    detected in the reference files.
  </description>

  <version_notes>
    <version id="17">
      `_inherit = 'res.config.settings'` on a TransientModel.
      `config_parameter=` stores a value in ir.config_parameter.
      `implied_group=` adds or removes users from a security group.
      `set_values()` override calls `super().set_values()` first.
      XML: `<app>` block groups settings by module; `<block>` groups within an app;
      `<setting>` is an individual option. `groups=` attribute restricts visibility.
      `check_company=True` confirmed present in v17 (decision #4).
    </version>
    <version id="18">
      Identical Python patterns. XML structure unchanged.
      `deprecated=False` domain condition dropped from some account fields in v18
      reference (minor field-level difference, not a structural pattern change).
    </version>
    <version id="19">
      Same Python and XML patterns. `deprecated=False` domain condition dropped
      from more fields in v19 reference (same as v18 trend).
    </version>
  </version_notes>

  <examples>

    <example id="python_field_types" title="Settings field types: config_parameter and implied_group">
      ```python
      from odoo import _, api, fields, models


      class ResConfigSettings(models.TransientModel):
          _inherit = 'res.config.settings'

          # Stores value in ir.config_parameter (key-value store)
          # Automatically read/written by the settings framework
          my_feature_enabled = fields.Boolean(
              string="Enable My Feature",
              config_parameter='my_module.my_feature_enabled')

          my_api_key = fields.Char(
              string="API Key",
              config_parameter='my_module.api_key')

          my_limit = fields.Integer(
              string="Processing Limit",
              config_parameter='my_module.processing_limit',
              default=100)

          # Adds/removes user from security group (boolean toggle)
          group_my_feature = fields.Boolean(
              string="My Feature",
              implied_group='my_module.group_my_feature')

          # Related to company (readonly=False to allow editing)
          company_setting = fields.Char(
              related='company_id.my_setting',
              readonly=False)

          # Module install/uninstall toggle
          module_my_optional_module = fields.Boolean(
              string="Enable Optional Module")
      ```
    </example>

    <example id="set_values_override" title="set_values() override pattern (all versions)">
      ```python
      from odoo import _, api, fields, models


      class ResConfigSettings(models.TransientModel):
          _inherit = 'res.config.settings'

          my_feature_enabled = fields.Boolean(
              config_parameter='my_module.my_feature_enabled')

          def set_values(self):
              # Always call super() first
              super().set_values()
              # Custom logic after saving
              if self.my_feature_enabled:
                  self.env['my.model']._initialize_feature()
      ```
      `config_parameter=` and `implied_group=` fields are handled automatically
      by the base `set_values()` / `get_values()` — no override needed for them.
      Override only when additional side effects are required after saving.
    </example>

    <example id="get_values_override" title="get_values() override pattern (all versions)">
      ```python
      from odoo import _, api, fields, models


      class ResConfigSettings(models.TransientModel):
          _inherit = 'res.config.settings'

          # Computed field not backed by config_parameter
          my_computed_setting = fields.Integer(
              string="Computed Setting",
              compute='_compute_my_setting',
              inverse='_inverse_my_setting')

          @api.depends('company_id')
          def _compute_my_setting(self):
              for config in self:
                  config.my_computed_setting = int(
                      self.env['ir.config_parameter'].sudo().get_param(
                          'my_module.computed_setting', default=0))

          def _inverse_my_setting(self):
              for config in self:
                  self.env['ir.config_parameter'].sudo().set_param(
                      'my_module.computed_setting',
                      config.my_computed_setting)
      ```
    </example>

    <example id="xml_settings_view" title="Settings form XML — app/block/setting structure">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo>
          <record id="res_config_settings_view_my_module" model="ir.ui.view">
              <field name="name">res.config.settings.view.form.inherit.my_module</field>
              <field name="model">res.config.settings</field>
              <field name="priority" eval="40"/>
              <field name="inherit_id" ref="base.res_config_settings_view_form"/>
              <field name="arch" type="xml">
                  <xpath expr="//form" position="inside">

                      <app data-string="My App" string="My App" name="my_module"
                           groups="my_module.group_my_module_manager">

                          <block title="General Settings">
                              <setting string="Enable My Feature"
                                       help="Activate the main feature of this module">
                                  <field name="my_feature_enabled"/>
                              </setting>

                              <setting string="API Key"
                                       help="Enter your API key"
                                       groups="base.group_system">
                                  <field name="my_api_key"/>
                              </setting>
                          </block>

                          <block title="Advanced">
                              <setting string="Processing Limit"
                                       help="Maximum records to process per run">
                                  <div class="content-group">
                                      <div class="row mt16">
                                          <label for="my_limit" class="col-lg-3 o_light_label"/>
                                          <field name="my_limit"/>
                                      </div>
                                  </div>
                              </setting>
                          </block>

                      </app>

                  </xpath>
              </field>
          </record>
      </odoo>
      ```
    </example>

    <example id="reading_config_parameter" title="Reading config_parameter values in business logic">
      ```python
      from odoo import models

      class MyModel(models.Model):
          _name = 'my.model'

          def _is_feature_enabled(self):
              return self.env['ir.config_parameter'].sudo().get_param(
                  'my_module.my_feature_enabled', default=False)

          def _get_api_key(self):
              return self.env['ir.config_parameter'].sudo().get_param(
                  'my_module.api_key', default='')

          def action_process(self):
              if not self._is_feature_enabled():
                  return
              # proceed with feature
      ```
      `sudo()` is required because `ir.config_parameter` is typically restricted
      to admin users. Values are always stored as strings — cast as needed
      (`bool(...)`, `int(...)`, etc.).
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Defining `get_values()` to read `config_parameter=` fields — these are read
      automatically by the framework. Overriding `get_values()` for such fields
      is redundant and can cause double-read bugs.
      ```python
      # WRONG — config_parameter= handles this automatically
      def get_values(self):
          res = super().get_values()
          res['my_feature_enabled'] = self.env['ir.config_parameter'].sudo().get_param(
              'my_module.my_feature_enabled')
          return res

      # CORRECT — just declare the field
      my_feature_enabled = fields.Boolean(
          config_parameter='my_module.my_feature_enabled')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Calling `super().set_values()` at the end instead of the beginning of the
      override — base set_values() must run first to persist field values before
      any post-save logic reads them back.
      ```python
      # WRONG — super() at end
      def set_values(self):
          self.env['my.model']._initialize_feature()
          super().set_values()  # values not yet saved when initialize runs

      # CORRECT — super() first
      def set_values(self):
          super().set_values()
          self.env['my.model']._initialize_feature()
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Reading `ir.config_parameter` without `sudo()` in non-admin context — this
      raises an access error for portal users and regular employees.
      ```python
      # WRONG
      value = self.env['ir.config_parameter'].get_param('my_module.key')

      # CORRECT
      value = self.env['ir.config_parameter'].sudo().get_param('my_module.key')
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      Naming `config_parameter` keys without a module prefix — unnamespaced keys
      can collide with other modules or Odoo core.
      ```python
      # WRONG — no module prefix
      config_parameter='api_key'

      # CORRECT — module-prefixed
      config_parameter='my_module.api_key'
      ```
    </antipattern>

  </antipatterns>

</pattern>