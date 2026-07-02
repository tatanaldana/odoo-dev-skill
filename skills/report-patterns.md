<pattern>

<description>
PDF report patterns for Odoo: ir.actions.report action definition, QWeb template structure,
Python model with _table_query (for SQL-based reports like sale.report), and triggering
reports from Python methods. Cross-reference qweb-template-patterns.md for full QWeb syntax.
Verified against sale_report_17/18/19.py, sale_report_templates_17/18/19.xml,
and sale_report_templates_19.xml (full template).
</description>

<version_notes>
  <version id="17">
    `ir.actions.report` action definition syntax unchanged across v17/v18/v19.
    `_render_qweb_pdf()`, `_render_qweb_html()` available on `ir.actions.report`.
    SQL report pattern: `_table_query` property returning full SELECT statement (confirmed sale_report_17.py).
    `group_operator=` on Float/Integer fields in SQL report models.
  </version>
  <version id="18">
    Report action syntax unchanged.
    `aggregator=` replaces `group_operator=` on field definitions (breaking change from v18).
    SQL report structure unchanged.
  </version>
  <version id="19">
    Report action and template syntax unchanged from v18.
    Full sale order template moved to `report_saleorder_document` (not just inherit) — uses
    `t-call="web.external_layout"`, `t-foreach="lines_to_report"`, `_get_order_lines_to_report()`.
    `models.Constraint()` and `models.Index()` available for model-level constraints.
  </version>
</version_notes>

<examples>

  <example id="report_action_xml" title="ir.actions.report definition (v17/v18/v19)">
```xml
<!-- Report action — syntax identical across versions -->
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model_document</field>
    <field name="report_file">my_module.report_my_model_document</field>
    <field name="print_report_name">'My Report - %s' % object.name</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>

<!-- With paper format -->
<record id="paperformat_my_report" model="report.paperformat">
    <field name="name">My Report Paper Format</field>
    <field name="default" eval="False"/>
    <field name="format">A4</field>
    <field name="page_height">0</field>
    <field name="page_width">0</field>
    <field name="orientation">Portrait</field>
    <field name="margin_top">40</field>
    <field name="margin_bottom">23</field>
    <field name="margin_left">7</field>
    <field name="margin_right">7</field>
    <field name="header_line" eval="False"/>
    <field name="header_spacing">35</field>
    <field name="dpi">90</field>
</record>
```
  </example>

  <example id="report_template_structure" title="QWeb PDF template structure (v17/v18)">
```xml
<!-- Verified pattern from sale_ir_actions_report_templates_17/18.xml -->
<!-- Inheriting an existing report template -->
<template id="report_my_document_inherit"
          inherit_id="base_module.report_my_document">
    <xpath expr="//div[@name='target_section']" position="after">
        <div t-if="doc.my_field_ids">
            <t t-set="has_discount"
               t-value="any(line.discount != 0.0 for line in doc.my_field_ids)"/>
            <table class="table table-sm">
                <thead class="fw-bold">
                    <tr>
                        <td class="text-start">Description</td>
                        <td t-if="has_discount" class="text-start">Disc.%</td>
                        <td class="text-end">Unit Price</td>
                    </tr>
                </thead>
                <tbody>
                    <tr t-foreach="doc.my_field_ids" t-as="line">
                        <td><span t-field="line.name"/></td>
                        <td t-if="has_discount">
                            <t t-out="line.discount">0</t>%
                        </td>
                        <td class="text-end">
                            <span t-field="line.price_unit"
                                  t-options='{"widget": "monetary",
                                              "display_currency": doc.currency_id}'/>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </xpath>
</template>
```
  </example>

  <example id="report_template_full" title="QWeb PDF template — full document (v19 pattern)">
```xml
<!-- Verified against sale_report_templates_19.xml -->
<template id="report_my_document">
    <t t-call="web.external_layout">
        <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
        <div class="page">
            <!-- Computed variables -->
            <t t-set="lines_to_report" t-value="doc._get_lines_to_report()"/>
            <t t-set="display_discount"
               t-value="any(l.discount > 0 for l in lines_to_report)"/>

            <!-- Header info -->
            <div class="row mb-4">
                <div t-if="doc.date_order" class="col">
                    <strong>Order Date</strong>
                    <div t-field="doc.date_order" t-options='{"widget": "date"}'/>
                </div>
                <div t-if="doc.user_id.name" class="col">
                    <strong>Salesperson</strong>
                    <div t-field="doc.user_id"/>
                </div>
            </div>

            <!-- Lines table -->
            <table class="table table-borderless">
                <thead>
                    <tr>
                        <th class="text-start">Description</th>
                        <th class="text-end">Qty</th>
                        <th class="text-end">Unit Price</th>
                        <th t-if="display_discount" class="text-end">Disc.%</th>
                        <th class="text-end">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <t t-foreach="lines_to_report" t-as="line">
                        <tr>
                            <td><span t-field="line.name"/></td>
                            <td class="text-end">
                                <span t-field="line.product_uom_qty"/>
                            </td>
                            <td class="text-end">
                                <span t-field="line.price_unit"
                                      t-options='{"widget": "monetary",
                                                  "display_currency": doc.currency_id}'/>
                            </td>
                            <td t-if="display_discount" class="text-end">
                                <span t-out="line.discount">0</span>%
                            </td>
                            <td class="text-end">
                                <span t-field="line.price_subtotal"
                                      t-options='{"widget": "monetary",
                                                  "display_currency": doc.currency_id}'/>
                            </td>
                        </tr>
                    </t>
                </tbody>
            </table>
        </div>
    </t>
</template>

<!-- Container iterates docs -->
<template id="report_my_raw">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="my_module.report_my_document"
               t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>
```
  </example>

  <example id="sql_report_model" title="SQL report model with _table_query (v17)">
```python
# Verified against sale_report_17.py — group_operator= in v17
from odoo import api, fields, models


class MyReport(models.Model):
    _name = 'my.report'
    _description = 'My Analysis Report'
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char(string='Reference', readonly=True)
    date = fields.Datetime(string='Date', readonly=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', readonly=True)
    company_id = fields.Many2one(
        comodel_name='res.company', readonly=True)
    amount = fields.Monetary(string='Amount', readonly=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
    )
    nbr = fields.Integer(
        string='# of Lines',
        readonly=True,
        group_operator='count',  # v17: group_operator=
    )

    @api.depends_context('allowed_company_ids')
    def _compute_currency_id(self):
        self.currency_id = self.env.company.currency_id

    def _select(self):
        return """
            MIN(l.id) AS id,
            s.name AS name,
            s.date_order AS date,
            s.partner_id AS partner_id,
            s.company_id AS company_id,
            SUM(l.price_subtotal) AS amount,
            COUNT(*) AS nbr
        """

    def _from(self):
        return """
            sale_order_line l
            LEFT JOIN sale_order s ON s.id = l.order_id
        """

    def _where(self):
        return "l.display_type IS NULL"

    def _group_by(self):
        return """
            s.name, s.date_order, s.partner_id, s.company_id, s.id
        """

    def _query(self):
        return f"""
            SELECT {self._select()}
            FROM {self._from()}
            WHERE {self._where()}
            GROUP BY {self._group_by()}
        """

    @property
    def _table_query(self):
        return self._query()
```
  </example>

  <example id="sql_report_model_v18" title="SQL report model field difference — v18 (aggregator=)">
```python
# v18: group_operator= renamed to aggregator= (decision #6)
# Verified against sale_report_18.py

nbr = fields.Integer(
    string='# of Lines',
    readonly=True,
    aggregator='count',  # v18+: aggregator= replaces group_operator=
)
discount = fields.Float(
    string='Discount %',
    readonly=True,
    aggregator='avg',    # v18+
)
```
  </example>

  <example id="trigger_report_python" title="Triggering a report from a Python method">
```python
def action_print_report(self):
    """Print report for this record."""
    return self.env.ref('my_module.action_report_my_model').report_action(self)

def action_print_selected(self):
    """Print report for selected records (multi-record)."""
    return self.env.ref('my_module.action_report_my_model').report_action(self.ids)

def action_print_with_data(self):
    """Print with custom data passed to template."""
    data = {
        'date_from': self.date_from,
        'date_to': self.date_to,
    }
    return self.env.ref('my_module.action_report_my_model').report_action(
        self, data=data
    )

def _show_report_in_portal(self, report_type='pdf'):
    """Render a report in portal context (verified pattern from http_controller_17.py)."""
    ReportAction = self.env['ir.actions.report'].sudo()
    method_name = '_render_qweb_%s' % report_type
    report = getattr(ReportAction, method_name)(
        'my_module.action_report_my_model',
        list(self.ids),
        data={'report_type': report_type},
    )[0]
    return report
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
Using `group_operator=` on fields in v18+ — renamed to `aggregator=`.
```python
# WRONG in v18+
amount = fields.Monetary(string='Amount', readonly=True, group_operator='sum')

# CORRECT in v18+
amount = fields.Monetary(string='Amount', readonly=True, aggregator='sum')
```
  </antipattern>

  <antipattern severity="HIGH">
Iterating `docs` directly in the document template instead of using the container/raw pattern.
The document template should render one record (`doc`); the container iterates `docs`.
```xml
<!-- WRONG: iterating in the document template -->
<template id="report_my_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc"> ... </t>
    </t>
</template>

<!-- CORRECT: separate container and document templates -->
<template id="report_my_document">
    <t t-call="web.external_layout">
        <!-- renders single doc -->
    </t>
</template>
<template id="report_my_raw">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="my_module.report_my_document"
               t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>
```
  </antipattern>

  <antipattern severity="HIGH">
Using `t-field` for computed or non-ORM values in report templates — `t-field` only works
with actual record fields. Use `t-out` or `t-esc` for computed values.
```xml
<!-- WRONG: t-field on a computed Python expression -->
<span t-field="(1 - line.discount / 100.0) * line.price_unit"/>

<!-- CORRECT: t-out for computed values, t-options for formatting -->
<t t-out="(1 - line.discount / 100.0) * line.price_unit"
   t-options='{"widget": "monetary", "display_currency": doc.currency_id}'/>
```
  </antipattern>

  <antipattern severity="MEDIUM">
Setting `_auto = True` (default) on a SQL report model — the ORM will try to create a
real table for it. SQL report models require `_auto = False` and a `_table_query` property.
```python
# WRONG: default _auto creates a real table
class MyReport(models.Model):
    _name = 'my.report'
    _description = 'My Report'
    # _auto not set = True by default

# CORRECT: SQL reports must declare _auto = False
class MyReport(models.Model):
    _name = 'my.report'
    _description = 'My Report'
    _auto = False  # required for SQL view-based models

    @property
    def _table_query(self):
        return self._query()
```
  </antipattern>

</antipatterns>

</pattern>