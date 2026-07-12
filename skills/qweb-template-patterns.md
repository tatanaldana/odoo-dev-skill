# QWeb Template Patterns — v17/v18/v19

Three contexts: OWL client templates, PDF reports, email templates.

---

## Version differences

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| KanbanRecord root | `<div role="article">` | `<article>` | `<article role="link">` + touch handlers |
| KanbanRecord template ref | `KANBAN_BOX_ATTRIBUTE` | `this.mainTemplate` | `KANBAN_CARD_ATTRIBUTE` |
| KanbanMenu slot | `t-set-slot="toggler"` | button inside Dropdown, `t-set-slot="content"` | same + `oi oi-ellipsis-v` icon |
| PDF/email templates | identical | identical | `lines_to_report` pattern in sale |

---

## OWL client template (component)

```xml
<templates xml:space="preserve">
    <t t-name="my_module.MyComponent">
        <div class="my-component">
            <!-- Conditional rendering -->
            <div t-if="state.loading" class="text-center">Loading...</div>
            <div t-else="">
                <!-- Loop -->
                <t t-foreach="state.records" t-as="record" t-key="record.id">
                    <div t-att-class="{'active': record.selected}" t-on-click="() => this.select(record.id)">
                        <span t-out="record.name"/>
                        <span t-if="record.amount" t-out="formatAmount(record.amount)"/>
                    </div>
                </t>
            </div>
            <!-- Slot for child content -->
            <t t-slot="default"/>
        </div>
    </t>
</templates>
```

## Key directives

| Directive | Purpose |
|-----------|---------|
| `t-if` / `t-elif` / `t-else` | Conditional |
| `t-foreach` + `t-as` + `t-key` | Loop (key required for OWL) |
| `t-out` | Output value (HTML-safe) — replaces `t-esc` |
| `t-att-*` | Dynamic attribute (`t-att-class`, `t-att-style`) |
| `t-attf-*` | Format string attribute (`t-attf-href="/my/{{record.id}}"`) |
| `t-on-*` | Event handler (`t-on-click`) |
| `t-ref` | Template ref for useRef() |
| `t-call` | Include another template |
| `t-set` / `t-value` | Set variable |
| `t-slot` | Named slot for component composition |
| `t-field` | ORM field rendering (reports only — not OWL) |

---

## PDF report template

```xml
<!-- Container: iterates docs -->
<template id="report_my_raw">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="my_module.report_my_document" t-lang="doc.partner_id.lang"/>
        </t>
    </t>
</template>

<!-- Document: renders single doc -->
<template id="report_my_document">
    <t t-call="web.external_layout">
        <div class="page">
            <h2><span t-field="doc.name"/></h2>
            <table class="table table-sm">
                <thead><tr><th>Description</th><th class="text-end">Amount</th></tr></thead>
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

## Email template

```xml
<record id="mail_template_confirm" model="mail.template">
    <field name="name">Confirmation</field>
    <field name="model_id" ref="my_module.model_my_model"/>
    <field name="subject">Confirmation: {{ object.name }}</field>
    <field name="body_html" type="html">
<div>Dear <t t-out="object.partner_id.name or 'customer'"/>,<br/>
Your request <strong t-out="object.name or ''"/> has been confirmed.</div>
    </field>
    <field name="lang">{{ object.partner_id.lang }}</field>
    <field name="auto_delete" eval="True"/>
</record>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Use `t-out` not `t-esc` (deprecated) for output |
| CRITICAL | Always include `t-key` in `t-foreach` for OWL templates |
| HIGH | `t-field` only works with ORM fields — use `t-out` for computed values |
| HIGH | Separate container (iterates docs) from document (renders one doc) in reports |
| MEDIUM | Use `t-attf-` for interpolated strings, `t-att-` for dynamic values |