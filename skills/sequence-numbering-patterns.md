# Sequence Numbering Patterns — v17/v18/v19

---

## ir.sequence XML

```xml
<odoo noupdate="1">
    <record id="seq_my_model" model="ir.sequence">
        <field name="name">My Model</field>
        <field name="code">my.model</field>
        <field name="prefix">MYM/%(year)s/</field>
        <field name="padding">5</field>
        <field name="company_id" eval="False"/>  <!-- shared; set ref for per-company -->
    </record>
</odoo>
```

`implementation`: `standard` (default, fast, gaps ok) or `no_gap` (row-level lock, legal compliance)

## create() guard

```python
name = fields.Char(required=True, copy=False, default=lambda self: _('New'))

@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', _("New")) == _("New"):
            # v18/v19: with_company inline
            vals['name'] = self.env['ir.sequence'].with_company(
                vals.get('company_id')).next_by_code('my.model') or _("New")
    return super().create(vals_list)
```

v17 difference: `self = self.with_company(vals['company_id'])` on separate line before sequence call.

## API reference

```python
self.env['ir.sequence'].next_by_code('my.model')  # by code string (recommended)
seq_record.next_by_id()                             # by record (requires access)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Guard with `_("New")` sentinel — don't consume sequence on imports/copy |
| HIGH | v18/v19: `with_company()` inline on env call, not `self = self.with_company()` |
| HIGH | `noupdate="1"` required — otherwise module update resets counter |