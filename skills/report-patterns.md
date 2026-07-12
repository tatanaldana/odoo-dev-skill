# Report Patterns — v17/v18/v19

PDF reports, SQL report models, QWeb templates.

---

## ir.actions.report (all versions)

```xml
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_document</field>
    <field name="print_report_name">'Report - %s' % object.name</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

## Template structure (separate container + document)

```xml
<template id="report_my_raw">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="my_module.report_my_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>

<template id="report_my_document">
    <t t-call="web.external_layout">
        <div class="page">
            <table class="table table-sm">
                <thead><tr><th>Name</th><th class="text-end">Amount</th></tr></thead>
                <tbody>
                    <t t-foreach="doc.line_ids" t-as="line">
                        <tr>
                            <td><span t-field="line.name"/></td>
                            <td class="text-end">
                                <span t-field="line.amount"
                                      t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
                            </td>
                        </tr>
                    </t>
                </tbody>
            </table>
        </div>
    </t>
</template>
```

## SQL report model

```python
class MyReport(models.Model):
    _name = 'my.report'
    _auto = False  # REQUIRED for SQL view models
    _order = 'date desc'

    date = fields.Datetime(readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    amount = fields.Monetary(readonly=True)
    nbr = fields.Integer(readonly=True,
        aggregator='count')  # v17: group_operator='count'

    @property
    def _table_query(self):
        return """
            SELECT MIN(l.id) AS id, s.date_order AS date,
                   s.partner_id, SUM(l.price_subtotal) AS amount, COUNT(*) AS nbr
            FROM sale_order_line l LEFT JOIN sale_order s ON s.id = l.order_id
            WHERE l.display_type IS NULL
            GROUP BY s.date_order, s.partner_id
        """
```

## Trigger from Python

```python
def action_print(self):
    return self.env.ref('my_module.action_report_my_model').report_action(self)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | v18+: `group_operator=` → `aggregator=` |
| HIGH | Separate container (iterates docs) from document (renders one) |
| HIGH | `t-field` only for ORM fields — use `t-out` for computed values |
| MEDIUM | SQL report models need `_auto = False` |