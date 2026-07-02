<pattern>

<description>
QWeb templating patterns for three distinct contexts in Odoo:
1. OWL client-side templates (t-name, t-if, t-foreach, t-att-, t-key, t-slot, t-call) — used in JS components
2. Server-side PDF report templates — rendered by wkhtmltopdf via ir.actions.report
3. Server-side email templates — rendered via mail.template body_html field

Each context has different available variables and rendering rules.
Verified against kanban_record_17/18/19.xml, sale_ir_actions_report_templates_17/18/19.xml,
sale_report_templates_19.xml, and mail_template_data_17/18/19.xml.
</description>

<version_notes>
  <version id="17">
    OWL client templates: `t-name` on `<t>` element inside `<templates>` wrapper.
    KanbanRecord root: `<div role="article" t-att-class="..." t-att-data-id="..." t-on-click="..." t-ref="root">`
    KanbanRecordMenu: uses `<Dropdown>` component with `t-set-slot="toggler"` slot pattern.
    PDF templates: `t-foreach` on `docs` recordset — variable named `doc` per iteration (v17/18/19 consistent).
    Email templates: `object` is the record, `user` is the sending user; `t-out` preferred over `t-esc` for HTML-safe output.
    `t-esc` still present in v17 email templates (project_message_user_assigned).
  </version>
  <version id="18">
    OWL client templates: KanbanRecord root changes from `<div role="article">` to `<article>` element.
    KanbanRecordMenu: `t-set-slot="toggler"` replaced by `<button>` directly inside `<Dropdown>`,
    slot content moved to `<t t-set-slot="content">`.
    `this.mainTemplate` instead of `templates[this.constructor.KANBAN_BOX_ATTRIBUTE]`.
    PDF and email template syntax unchanged from v17.
    Email: `task_invitation_follower` template added using `t-out` (not `t-esc`).
  </version>
  <version id="19">
    OWL client templates: KanbanRecord root gains `role="link"`, `t-custom-click`, touch event handlers,
    and selection tooltip span. KANBAN_CARD_ATTRIBUTE replaces KANBAN_BOX_ATTRIBUTE.
    KanbanRecordMenu: `'o-dropdown--kanban-record-menu'` class, icon changes from `fa-ellipsis-v` to `oi oi-ellipsis-v`.
    PDF template: full `report_saleorder_document` template present (not just inherit).
    Uses `t-call="web.external_layout"`, `t-foreach="lines_to_report"`, `t-set` for computed variables,
    `t-options` with monetary widget, `t-attf-href` for dynamic URLs.
    Email template syntax unchanged from v18.
  </version>
</version_notes>

<examples>

  <example id="owl_kanban_record_v17" title="OWL KanbanRecord template — v17">
```xml
<templates xml:space="preserve">

    <t t-name="web.KanbanRecord">
        <div
            role="article"
            t-att-class="getRecordClasses()"
            t-att-data-id="props.record.id"
            t-att-tabindex="props.record.model.useSampleModel ? -1 : 0"
            t-on-click="onGlobalClick"
            t-ref="root">
            <t t-call="{{ templates[this.constructor.KANBAN_BOX_ATTRIBUTE] }}"
               t-call-context="this.renderingContext"/>
            <t t-call="{{ this.constructor.menuTemplate }}"/>
        </div>
    </t>

    <t t-name="web.KanbanRecordMenu">
        <t t-if="showMenu">
            <Dropdown class="'o_dropdown_kanban bg-transparent position-absolute end-0'"
                      menuClass="'dropdown-menu'"
                      togglerClass="'btn o-no-caret rounded-0'"
                      position="'bottom-end'"
                      title="'Dropdown menu'">
                <t t-set-slot="toggler">
                    <span class="fa fa-ellipsis-v"/>
                </t>
                <KanbanDropdownMenuWrapper>
                    <t t-call="{{ templates[this.constructor.KANBAN_MENU_ATTRIBUTE] }}"
                       t-call-context="renderingContext"/>
                </KanbanDropdownMenuWrapper>
            </Dropdown>
        </t>
    </t>

</templates>
```
  </example>

  <example id="owl_kanban_record_v18" title="OWL KanbanRecord template — v18">
```xml
<templates xml:space="preserve">

    <t t-name="web.KanbanRecord">
        <article
            t-att-class="getRecordClasses()"
            t-att-data-id="props.record.id"
            t-att-tabindex="props.record.model.useSampleModel ? -1 : 0"
            t-on-click="onGlobalClick"
            t-ref="root">
                <t t-call="{{ this.mainTemplate }}"
                   t-call-context="this.renderingContext"/>
                <t t-call="{{ this.constructor.menuTemplate }}"/>
        </article>
    </t>

    <t t-name="web.KanbanRecordMenu">
        <div t-if="showMenu"
             class="o_dropdown_kanban bg-transparent position-absolute end-0 top-0 w-auto">
            <Dropdown menuClass="getMenuClasses()" position="'bottom-end'">
                <button class="btn o-no-caret rounded-0" title="Dropdown menu">
                    <span class="fa fa-ellipsis-v"/>
                </button>
                <t t-set-slot="content">
                    <KanbanDropdownMenuWrapper>
                        <t t-call="{{ templates[this.menuTemplateName] }}"
                           t-call-context="renderingContext"/>
                    </KanbanDropdownMenuWrapper>
                </t>
            </Dropdown>
        </div>
    </t>

</templates>
```
  </example>

  <example id="owl_kanban_record_v19" title="OWL KanbanRecord template — v19">
```xml
<templates xml:space="preserve">

    <t t-name="web.KanbanRecord">
        <article
            role="link"
            t-att-class="getRecordClasses()"
            t-att-data-id="props.record.id"
            t-att-tabindex="props.record.model.useSampleModel ? -1 : 0"
            t-custom-click="onGlobalClick"
            t-on-touchstart="onTouchStart"
            t-on-touchmove="onTouchMoveOrCancel"
            t-on-touchcancel="onTouchMoveOrCancel"
            t-on-touchend="onTouchEnd"
            t-ref="root">
                <span t-if="props.selectionAvailable"
                      class="o_record_selection_tooltip d-none position-absolute p-2 rounded-3 start-50 top-50">
                    Click to select
                </span>
                <t t-call="{{ this.templates[this.constructor.KANBAN_CARD_ATTRIBUTE] }}"
                   t-call-context="this.renderingContext"/>
                <t t-call="{{ this.constructor.menuTemplate }}"/>
        </article>
    </t>

    <t t-name="web.KanbanRecordMenu">
        <div t-if="showMenu"
             class="o_dropdown_kanban bg-transparent position-absolute end-0 top-0 w-auto">
            <Dropdown menuClass="'o-dropdown--kanban-record-menu'" position="'bottom-end'">
                <button class="btn o-no-caret rounded-0 px-1" title="Dropdown menu">
                    <span class="oi oi-ellipsis-v"/>
                </button>
                <t t-set-slot="content">
                    <KanbanDropdownMenuWrapper>
                        <t t-call="{{ this.templates[this.constructor.KANBAN_MENU_ATTRIBUTE] }}"
                           t-call-context="renderingContext"/>
                    </KanbanDropdownMenuWrapper>
                </t>
            </Dropdown>
        </div>
    </t>

</templates>
```
  </example>

  <example id="pdf_template_inherit" title="Server PDF template — inherit pattern (v17/v18)">
```xml
<!-- Verified against sale_ir_actions_report_templates_17.xml and _18.xml -->
<!-- v17 differs from v18 only in removal of groups= attribute on one td -->
<template id="report_saleorder_document_inherit_sale_management"
          inherit_id="sale.report_saleorder_document">
    <xpath expr="//div[@name='signature']" position="after">
        <div t-if="not (doc.sale_order_option_ids and doc.state in ['draft', 'sent'])"
             class="oe_structure">​</div>
        <div t-else="">
            <t t-set="has_option_discount"
               t-value="any(option.discount != 0.0 for option in doc.sale_order_option_ids)"/>
            <table name="table_optional_products" class="table table-sm">
                <thead class="fw-bold">
                    <tr>
                        <td name="th_option_name" class="text-start">Description</td>
                        <td t-if="has_option_discount" name="th_option_discount"
                            class="text-start">Disc.%</td>
                        <td name="th_option_price_unit" class="text-end">Unit Price</td>
                    </tr>
                </thead>
                <tbody class="sale_tbody">
                    <tr t-foreach="doc.sale_order_option_ids" t-as="option">
                        <td name="td_option_name">
                            <span t-field="option.name">Extra Chips</span>
                        </td>
                        <td t-if="has_option_discount" name="td_option_discount">
                            <strong t-if="option.discount != 0.0" class="text-info">
                                <t t-out="((option.discount % 1) and '%s' or '%d') % option.discount">-</t>%
                            </strong>
                        </td>
                        <td name="td_option_price_unit">
                            <div t-field="option.price_unit"
                                 t-options='{"widget": "monetary", "display_currency": doc.currency_id}'
                                 t-att-style="option.discount and 'text-decoration: line-through' or None"
                                 t-att-class="option.discount and 'text-danger' or None">1.5</div>
                            <div t-if="option.discount">
                                <t t-out="((1-option.discount / 100.0) * option.price_unit)"
                                   t-options='{"widget": "monetary", "display_currency": doc.currency_id}'> </t>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </xpath>
</template>
```
  </example>

  <example id="pdf_template_full_v19" title="Server PDF template — full document structure (v19)">
```xml
<!-- Verified against sale_report_templates_19.xml -->
<template id="report_saleorder_document">
    <t t-call="web.external_layout">
        <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>
        <t t-set="forced_vat" t-value="doc.fiscal_position_id.foreign_vat"/>
        <t t-set="address">
            <div t-field="doc.partner_id"
                 t-options='{"widget": "contact", "fields": ["address", "name"], "no_marker": True}'/>
        </t>
        <div class="page">
            <t t-set="lines_to_report" t-value="doc._get_order_lines_to_report()"/>
            <t t-set="display_discount"
               t-value="any(l.discount > 0 for l in lines_to_report)"/>
            <table class="o_has_total_table table o_main_table table-borderless">
                <thead style="display: table-row-group">
                    <tr>
                        <th name="th_description" class="text-start">Description</th>
                        <th name="th_quantity" class="text-end text-nowrap">Quantity</th>
                        <th name="th_priceunit" class="text-end text-nowrap">Unit Price</th>
                        <th t-if="display_discount" name="th_discount" class="text-end">Disc.%</th>
                    </tr>
                </thead>
                <tbody class="sale_tbody">
                    <t t-foreach="lines_to_report" t-as="line">
                        <t t-set="is_section" t-value="line.display_type == 'line_section'"/>
                        <tr t-if="not is_section">
                            <td name="td_name">
                                <span t-field="line.name"/>
                            </td>
                            <td name="td_qty" class="text-end">
                                <span t-field="line.product_uom_qty"/>
                            </td>
                            <td name="td_price_unit" class="text-end">
                                <span t-field="line.price_unit"/>
                            </td>
                            <td t-if="display_discount" name="td_discount" class="text-end">
                                <span t-out="line.discount">0</span>%
                            </td>
                        </tr>
                    </t>
                </tbody>
            </table>
            <!-- Tax totals via t-call -->
            <t t-call="sale.document_tax_totals">
                <t t-set="tax_totals" t-value="doc.tax_totals"/>
                <t t-set="currency" t-value="doc.currency_id"/>
            </t>
        </div>
    </t>
</template>

<!-- Container template iterates docs, calls document template per record -->
<template id="report_saleorder_raw">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="sale.report_saleorder_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>
```
  </example>

  <example id="email_template_basic" title="Server email template — body_html (v17/v18/v19 identical)">
```xml
<!-- Verified against mail_template_data_17.xml, _18.xml, _19.xml -->
<record id="mail_template_data_project_task" model="mail.template">
    <field name="name">Project: Request Acknowledgment</field>
    <field name="model_id" ref="project.model_project_task"/>
    <field name="subject">Reception of {{ object.name }}</field>
    <field name="use_default_to" eval="True"/>
    <field name="body_html" type="html">
<div>
    Dear <t t-out="object.partner_id.name or 'customer'">Brandon Freeman</t>,<br/>
    Thank you for your enquiry.<br/>
    If you have any questions, please let us know.
    <br/><br/>
    Thank you,
    <t t-if="user.signature">
        <br/>
        <t t-out="user.signature or ''">--<br/>Mitchell Admin</t>
    </t>
</div>
    </field>
    <field name="lang">{{ object.partner_id.lang }}</field>
    <field name="auto_delete" eval="True"/>
</record>
```
  </example>

  <example id="email_template_complex" title="Server email template — conditional content with t-set and t-attf-href">
```xml
<!-- Verified against mail_template_data_17.xml rating template -->
<record id="rating_project_request_email_template" model="mail.template">
    <field name="name">Project: Task Rating Request</field>
    <field name="model_id" ref="project.model_project_task"/>
    <field name="email_from">
        {{ (object._rating_get_operator().email_formatted
            if object._rating_get_operator()
            else user.email_formatted) }}
    </field>
    <field name="body_html" type="html">
<div>
    <t t-set="access_token" t-value="object._rating_get_access_token()"/>
    <t t-set="partner" t-value="object._rating_get_partner()"/>
    <t t-if="partner.name">
        Hello <t t-out="partner.name or ''">Brandon Freeman</t>,<br/><br/>
    </t>
    <t t-else="">
        Hello,<br/><br/>
    </t>
    <table style="width:100%;text-align:center;margin-top:2rem;">
        <tr>
            <td>
                <a t-attf-href="/rate/{{ access_token }}/5">
                    <img alt="Satisfied" src="/rating/static/src/img/rating_5.png"/>
                </a>
            </td>
            <td>
                <a t-attf-href="/rate/{{ access_token }}/1">
                    <img alt="Dissatisfied" src="/rating/static/src/img/rating_1.png"/>
                </a>
            </td>
        </tr>
    </table>
    <t t-out="object.project_id.company_id.name or ''">YourCompany</t>
</div>
    </field>
    <field name="lang">{{ object._rating_get_partner().lang }}</field>
    <field name="auto_delete" eval="True"/>
</record>
```
  </example>

  <example id="email_qweb_template_snippet" title="Server email — standalone QWeb template snippet (v17+)">
```xml
<!-- Verified against mail_template_data_17.xml project_message_user_assigned -->
<template id="project_message_user_assigned">
<div>
    Dear <t t-esc="assignee_name"/>,
    <br/><br/>
    <span style="margin-top: 8px;">
        You have been assigned to the
        <t t-esc="model_description or 'document'"/>
        <t t-esc="object.display_name"/>.
    </span>
</div>
</template>
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
Using `t-raw` in email or report templates — outputs unescaped HTML which can cause XSS.
Use `t-out` for safe output (escaped by default) or `t-field` for field values.
```xml
<!-- WRONG: t-raw is unsafe -->
<t t-raw="object.description"/>

<!-- CORRECT: t-out for HTML-safe output -->
<t t-out="object.description or ''"/>
<!-- or for field rendering with widget support -->
<span t-field="object.description"/>
```
  </antipattern>

  <antipattern severity="HIGH">
Using `t-esc` for HTML content fields — `t-esc` escapes HTML entities, destroying markup.
Use `t-out` for values that may contain HTML.
```xml
<!-- WRONG for HTML fields -->
<t t-esc="user.signature"/>

<!-- CORRECT: t-out renders HTML content safely -->
<t t-out="user.signature or ''"/>
```
  </antipattern>

  <antipattern severity="HIGH">
Missing fallback value in `t-out` / `t-esc` causing template render errors when field is False.
```xml
<!-- WRONG: crashes if object.partner_id.name is False -->
<t t-out="object.partner_id.name"/>

<!-- CORRECT: always provide a fallback -->
<t t-out="object.partner_id.name or 'customer'">Brandon Freeman</t>
```
  </antipattern>

  <antipattern severity="MEDIUM">
Omitting `t-lang` on the container template call — report renders in server locale instead of partner's language.
```xml
<!-- WRONG: no language context -->
<t t-foreach="docs" t-as="doc">
    <t t-call="my_module.report_my_document"/>
</t>

<!-- CORRECT: pass partner language -->
<t t-foreach="docs" t-as="doc">
    <t t-call="my_module.report_my_document" t-lang="doc.partner_id.lang"/>
</t>
```
  </antipattern>

</antipatterns>

</pattern>