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
            vals['name'] = self.env['ir.sequence'].with_company(
                vals.get('company_id')).next_by_code('my.model') or _("New")
    return super().create(vals_list)
```

Both the inline form (`self.env['ir.sequence'].with_company(...).next_by_code(...)`) and the
separate-line form (`self = self.with_company(...)`) are valid on v17, v18, and v19 — this is
a style choice, not a version-gated API change. Confirmed identically present in core across
all three branches (e.g. `odoo/addons/purchase_requisition/models/purchase_requisition.py`,
`odoo/addons/product/models/product_template.py`). `with_company()` itself has not changed.

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
| HIGH | `noupdate="1"` required — otherwise module update resets counter |