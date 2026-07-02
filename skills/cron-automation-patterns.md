# cron-automation-patterns.md

<pattern>

  <description>
    Patterns for scheduled actions (ir.cron) and automation rules (base.automation)
    in Odoo v17/18/19. Covers XML record definitions and the Python model methods
    they invoke. Verified against ir_cron_17/18/19.xml and base_automation_17/18/19.xml.
  </description>

  <version_notes>
    <version id="17">
      ir.cron: `numbercall=-1` field present — sets the cron to run indefinitely.
      base.automation trigger values confirmed: `on_create_or_write`, `on_unlink`,
      `on_time`, `on_time_created`, `on_time_updated`, `on_change`, `on_webhook`,
      `on_state_set`, `on_priority_set`, `on_stage_set`, `on_tag_set`.
    </version>
    <version id="18">
      ir.cron: `numbercall` field absent from reference XML — verify against your
      codebase whether the field was removed or simply not set in this example.
      base.automation trigger values: identical to v17 — no renames confirmed.
    </version>
    <version id="19">
      ir.cron: same structure as v18 (no `numbercall` in reference).
      base.automation: trigger values identical. Webhook logs button in form view
      restricted to `base.group_no_one` group (minor UI change). Placeholder text
      changed from "e.g. Support flow" to "Set an explicit name".
    </version>
  </version_notes>

  <examples>

    <example id="ir_cron_xml_v17" title="ir.cron XML definition — v17">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo noupdate="1">

          <record id="my_module_cron_job" model="ir.cron">
              <field name="name">My Module: Process Records</field>
              <field name="model_id" ref="my_module.model_my_model"/>
              <field name="state">code</field>
              <field name="code">model._cron_process_records()</field>
              <field name="user_id" ref="base.user_root"/>
              <field name="interval_number">1</field>
              <field name="interval_type">days</field>
              <field name="numbercall">-1</field>
              <field name="active">False</field>
          </record>

      </odoo>
      ```
      `numbercall=-1` means run indefinitely. `active=False` means the cron is
      installed but disabled by default — users enable it in Settings > Technical.
      `model_id` ref must match the `model_` + underscore-prefixed model name
      (e.g. `model_sale_order` for `sale.order`).
    </example>

    <example id="ir_cron_xml_v18_v19" title="ir.cron XML definition — v18/v19">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo noupdate="1">

          <record id="my_module_cron_job" model="ir.cron">
              <field name="name">My Module: Process Records</field>
              <field name="model_id" ref="my_module.model_my_model"/>
              <field name="state">code</field>
              <field name="code">model._cron_process_records()</field>
              <field name="user_id" ref="base.user_root"/>
              <field name="interval_number">1</field>
              <field name="interval_type">days</field>
              <field name="active">False</field>
          </record>

      </odoo>
      ```
      `interval_type` values: `minutes`, `hours`, `days`, `weeks`, `months`.
    </example>

    <example id="cron_python_method" title="Python method called by ir.cron (all versions)">
      ```python
      from odoo import api, models
      import logging

      _logger = logging.getLogger(__name__)

      class MyModel(models.Model):
          _name = 'my.model'

          @api.model
          def _cron_process_records(self):
              """Called by ir.cron: code = model._cron_process_records()"""
              records = self.search([('state', '=', 'pending')])
              for record in records:
                  try:
                      record._do_process()
                  except Exception:
                      _logger.exception("Error processing record %s", record.id)
      ```
      The method must be decorated with `@api.model` — the cron executes it as
      `model.method_name()` with no record in context. Wrap per-record logic in
      try/except to prevent one failure from aborting the entire cron run.
    </example>

    <example id="base_automation_xml" title="base.automation rule (v17/18/19 triggers identical)">
      ```xml
      <?xml version="1.0" encoding="utf-8"?>
      <odoo noupdate="1">

          <!-- Trigger on record create or write -->
          <record id="automation_on_write" model="base.automation">
              <field name="name">My Module: On Record Write</field>
              <field name="model_id" ref="my_module.model_my_model"/>
              <field name="trigger">on_create_or_write</field>
              <field name="filter_domain">[('state', '=', 'confirmed')]</field>
              <field name="action_server_ids" eval="[(4, ref('my_module.server_action_id'))]"/>
              <field name="active">True</field>
          </record>

          <!-- Trigger on time (date field + delay) -->
          <record id="automation_on_time" model="base.automation">
              <field name="name">My Module: 7 Days After Deadline</field>
              <field name="model_id" ref="my_module.model_my_model"/>
              <field name="trigger">on_time</field>
              <field name="trg_date_id" ref="my_module.field_my_model__deadline"/>
              <field name="trg_date_range">7</field>
              <field name="trg_date_range_type">day</field>
              <field name="active">True</field>
          </record>

      </odoo>
      ```
      Confirmed trigger values (identical v17/18/19):
      `on_create_or_write`, `on_unlink`, `on_time`, `on_time_created`,
      `on_time_updated`, `on_change`, `on_webhook`, `on_state_set`,
      `on_priority_set`, `on_stage_set`, `on_tag_set`.
    </example>

    <example id="cron_interval_types" title="ir.cron interval_type reference">
      ```xml
      <!-- Valid interval_type values (all versions) -->
      <field name="interval_type">minutes</field>
      <field name="interval_type">hours</field>
      <field name="interval_type">days</field>
      <field name="interval_type">weeks</field>
      <field name="interval_type">months</field>

      <!-- Common combinations -->
      <!-- Every 15 minutes -->
      <field name="interval_number">15</field>
      <field name="interval_type">minutes</field>

      <!-- Every day at the scheduler's next run -->
      <field name="interval_number">1</field>
      <field name="interval_type">days</field>
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Forgetting `@api.model` on the cron method — the cron executes `model.method()`
      with no recordset, so the method must be a model-level method.
      ```python
      # WRONG — missing @api.model, will fail or have undefined behavior
      def _cron_process_records(self):
          records = self.search([...])

      # CORRECT
      @api.model
      def _cron_process_records(self):
          records = self.search([...])
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Using `on_write` or `on_create` as trigger values — these were removed in v17.
      Use `on_create_or_write` instead. No v17/18/19 reference file shows separate
      `on_write` / `on_create` triggers.
      ```xml
      <!-- WRONG in v17/18/19 -->
      <field name="trigger">on_write</field>

      <!-- CORRECT -->
      <field name="trigger">on_create_or_write</field>
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Omitting `noupdate="1"` on cron records — without it, module updates will
      reset interval settings and active state customized by the customer.
      ```xml
      <!-- WRONG -->
      <odoo>
          <record id="my_cron" model="ir.cron">...</record>
      </odoo>

      <!-- CORRECT -->
      <odoo noupdate="1">
          <record id="my_cron" model="ir.cron">...</record>
      </odoo>
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      Running expensive operations without batching inside a cron — if a cron
      processes thousands of records in one transaction it risks timeout and memory
      issues. Use `cr.commit()` between batches or split into multiple cron runs.
    </antipattern>

  </antipatterns>

</pattern>