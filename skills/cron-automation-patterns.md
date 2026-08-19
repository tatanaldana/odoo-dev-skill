# Cron & Automation Patterns — v17/v18/v19

---

## ir.cron XML

```xml
<odoo noupdate="1">
    <record id="my_cron" model="ir.cron">
        <field name="name">My Module: Process Records</field>
        <field name="model_id" ref="my_module.model_my_model"/>
        <field name="state">code</field>
        <field name="code">model._cron_process_records()</field>
        <field name="user_id" ref="base.user_root"/>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="active">False</field>
        <!-- numbercall/doall: v17 only. Fields REMOVED (not just deprecated) from
             ir.cron in v18+ — setting them in v18/v19 XML raises a ValueError
             (unknown field). v18+ replaced them with automatic failure tracking
             (failure_count, first_failure_date) instead of a fixed call limit. -->
        <!-- v17-only: <field name="numbercall">-1</field> -->
        <!-- v17-only: <field name="doall">False</field> -->
    </record>
</odoo>
```

`interval_type`: `minutes`, `hours`, `days`, `weeks`, `months`

## Python method

```python
@api.model
def _cron_process_records(self):
    records = self.search([('state', '=', 'pending')])
    for record in records:
        try:
            record._do_process()
        except Exception:
            _logger.exception("Error processing record %s", record.id)
```

## base.automation triggers (identical v17/v18/v19)

`on_create_or_write`, `on_unlink`, `on_time`, `on_time_created`, `on_time_updated`, `on_change`, `on_webhook`, `on_state_set`, `on_priority_set`, `on_stage_set`, `on_tag_set`

```xml
<record id="auto_rule" model="base.automation">
    <field name="name">On Record Write</field>
    <field name="model_id" ref="my_module.model_my_model"/>
    <field name="trigger">on_create_or_write</field>
    <field name="filter_domain">[('state', '=', 'confirmed')]</field>
    <field name="action_server_ids" eval="[(4, ref('my_module.server_action'))]"/>
</record>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `@api.model` required on cron methods |
| CRITICAL | v18+: `numbercall`/`doall` fields REMOVED from `ir.cron` (present v17 only) — don't reference them in XML/code targeting v18+ |
| HIGH | `on_write`/`on_create` are deprecated (not removed) in v17/v18/v19 — prefer `on_create_or_write`, but existing code using them still works on all three |
| HIGH | `noupdate="1"` required on cron records |
| MEDIUM | Batch heavy cron operations to avoid timeouts |