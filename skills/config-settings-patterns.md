# Config Settings Patterns — v17/v18/v19

No breaking changes across versions.

---

## Field types in res.config.settings

```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Stored in ir.config_parameter (key-value)
    my_feature = fields.Boolean(config_parameter='my_module.my_feature')
    my_api_key = fields.Char(config_parameter='my_module.api_key')
    my_limit = fields.Integer(config_parameter='my_module.limit', default=100)

    # Adds/removes user from group (boolean toggle)
    group_my_feature = fields.Boolean(implied_group='my_module.group_my_feature')

    # Related to company field
    company_setting = fields.Char(related='company_id.my_setting', readonly=False)

    # Module install toggle
    module_my_optional = fields.Boolean(string="Enable Optional Module")
```

## set_values() override

```python
def set_values(self):
    super().set_values()  # MUST be first — persists config_parameter values
    if self.my_feature:
        self.env['my.model']._initialize_feature()
```

## XML view

```xml
<xpath expr="//form" position="inside">
    <app data-string="My App" string="My App" name="my_module">
        <block title="General">
            <setting string="Enable Feature" help="Activates the feature">
                <field name="my_feature"/>
            </setting>
            <setting string="API Key" groups="base.group_system">
                <field name="my_api_key"/>
            </setting>
        </block>
    </app>
</xpath>
```

## Reading in business logic

```python
value = self.env['ir.config_parameter'].sudo().get_param('my_module.api_key', default='')
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Don't override `get_values()` for `config_parameter=` fields — auto-handled |
| HIGH | `super().set_values()` must be FIRST in override |
| HIGH | Always `.sudo()` when reading `ir.config_parameter` |
| MEDIUM | Prefix keys with module name (`my_module.key` not just `key`) |