# Odoo Version Knowledge: 17 to 18 Migration

<pattern>

  <description>
    Migration guide from Odoo 17.0 to 18.0. Covers breaking changes, new patterns,
    and deprecated features. Use alongside odoo-version-knowledge-17.md and
    odoo-version-knowledge-18.md for full context.
  </description>


  <!-- ============================================================
       BREAKING CHANGES SUMMARY
       ============================================================ -->
  <version_notes>
    <!-- Source: ORM changelog + confirmed in codebase -->
    <change version="18" type="breaking">&lt;tree&gt; tag renamed to &lt;list&gt; in XML views — use odoo-bin upgrade_code --from 17.0 --to 18.0</change>
    <change version="18" type="breaking">&lt;div class="oe_chatter"&gt; block replaced by the bare, self-closing &lt;chatter/&gt; tag (optional reload_on_attachment/reload_on_follower/reload_on_post attributes exist for specific views but are not required)</change>
    <change version="18" type="not-a-change">Record rules keep using company_ids in domain_force — allowed_company_ids does NOT replace it (confirmed against real addons/account/security/account_security.xml in 18.0/19.0; a previous version of this file incorrectly claimed this as a breaking change)</change>
    <change version="18" type="breaking">group_operator renamed to aggregator on field definitions — confirmed in model_18.py</change>
    <change version="18" type="breaking">@odoo-module comment no longer required in JS — use direct ES module imports</change>
    <change version="17" type="already-available">_check_company_auto = True — confirmed present in v17 source (account.move.line line 25), NOT a new v18 feature. Still worth adopting on multi-company models that don't use it yet.</change>
    <change version="17" type="already-available">check_company=True on relational fields — same as above, already available in v17</change>
    <change version="18" type="new">read_group() deprecated (v18.2) — use _read_group() / formatted_read_group()</change>
    <change version="18" type="new">@api.private introduced (v18.2) — marks methods not exposed to RPC</change>
    <change version="18" type="new">check_access(), has_access(), _filtered_access() — new access methods</change>
    <change version="18" type="new">_search_display_name replaces name_get() (deprecated since v16.4)</change>
    <change version="18" type="new">odoo.Domain API for domain manipulation (v18.1)</change>
    <change version="18" type="recommended">SQL() builder for safer SQL composition</change>
    <change version="18" type="recommended">Type hints on method signatures</change>
  </version_notes>


  <!-- ============================================================
       MULTI-COMPANY MIGRATION
       ============================================================ -->
  <examples category="multi_company">

    <example id="company_before_after" title="Multi-Company — v17 vs v18">
      ```python
      # v17: manual company validation
      class MyModelV17(models.Model):
          _name = 'my.model'

          company_id = fields.Many2one('res.company')
          partner_id = fields.Many2one('res.partner')

          @api.constrains('partner_id', 'company_id')
          def _check_company(self):
              for record in self:
                  if record.partner_id.company_id and \
                     record.partner_id.company_id != record.company_id:
                      raise ValidationError("Partner company mismatch!")

      # v18: automatic validation
      class MyModelV18(models.Model):
          _name = 'my.model'
          _check_company_auto = True  # handles validation automatically

          company_id = fields.Many2one('res.company', required=True)
          partner_id = fields.Many2one('res.partner', check_company=True)
          warehouse_id = fields.Many2one('stock.warehouse', check_company=True)
          # No manual constraint needed
      ```
    </example>

    <example id="record_rule" title="Record Rule — company_ids unchanged in v18 (corrected)">
      ```xml
      <!-- v17 -->
      <field name="domain_force">[('company_id', '=', company_id)]</field>

      <!-- v18 — same variable, no change. Confirmed against real
           addons/account/security/account_security.xml (18.0/19.0 branches). -->
      <field name="domain_force">[
          '|',
          ('company_id', '=', False),
          ('company_id', 'in', company_ids)
      ]</field>
      ```
      `allowed_company_ids` is a real v18+ context variable, but it belongs to view-level
      field `domain=` attributes (client-side, evaluated against the user's currently
      selected companies) — a different context from `ir.rule.domain_force`, which is
      evaluated server-side and has always used `company_ids`.
    </example>

  </examples>


  <!-- ============================================================
       XML VIEW MIGRATION
       ============================================================ -->
  <examples category="xml_views">

    <example id="tree_to_list" title="tree tag renamed to list">
      ```xml
      <!-- v17 -->
      <tree string="Records" decoration-info="state == 'draft'">
          <field name="name"/>
          <field name="state"/>
      </tree>

      <!-- v18 -->
      <list string="Records" decoration-info="state == 'draft'">
          <field name="name"/>
          <field name="state"/>
      </list>
      ```
    </example>

    <example id="chatter_widget" title="Chatter block replaced by widget">
      ```xml
      <!-- v17 -->
      <div class="oe_chatter">
          <field name="message_follower_ids" groups="base.group_user"/>
          <field name="activity_ids"/>
          <field name="message_ids"/>
      </div>

      <!-- v18 — bare, self-closing tag is the dominant form in real source (65+
           occurrences with no attributes across 18.0/19.0 addons) -->
      <chatter/>

      <!-- v18 — optional attributes exist for specific reload behaviors, add only
           when actually needed (confirmed in account_move_views.xml, hr_employee_views.xml) -->
      <chatter reload_on_attachment="True"/>
      ```
    </example>

  </examples>


  <!-- ============================================================
       FIELD DEFINITION MIGRATION
       ============================================================ -->
  <examples category="fields">

    <example id="aggregator" title="group_operator renamed to aggregator">
      ```python
      # v17
      date = fields.Date(group_operator='min')
      amount = fields.Float(group_operator='sum')

      # v18
      date = fields.Date(aggregator='min')
      amount = fields.Float(aggregator='sum')
      ```
    </example>

    <example id="indexing" title="Enhanced index types — available in both v17 and v18">
      ```python
      name = fields.Char(index='trigram')       # GIN trigram for ILIKE searches
      code = fields.Char(index='btree_not_null') # exclude NULLs from index
      date = fields.Date(index=True)             # standard btree
      ```
    </example>

  </examples>


  <!-- ============================================================
       SQL MIGRATION
       ============================================================ -->
  <examples category="sql">

    <example id="sql_builder" title="SQL() builder — recommended in v18">
      ```python
      # v17: string SQL — still works but discouraged
      self.env.cr.execute("""
          SELECT id, name FROM my_model
          WHERE state = %s AND company_id = %s
      """, ('confirmed', self.env.company.id))

      # v18: SQL() builder — recommended
      from odoo.tools.sql import SQL

      self.env.cr.execute(SQL(
          """
          SELECT id, name FROM my_model
          WHERE state = %s AND company_id = %s
          """,
          'confirmed', self.env.company.id
      ))

      # Composable queries
      base = SQL("SELECT * FROM my_model WHERE active = %s", True)
      filtered = SQL("%s AND company_id = %s", base, self.env.company.id)

      # Safe identifiers
      table = SQL.identifier('my_model')
      query = SQL("SELECT * FROM %s", table)
      ```
    </example>

  </examples>


  <!-- ============================================================
       ORM API MIGRATION
       ============================================================ -->
  <examples category="orm">

    <example id="read_group" title="read_group deprecated in v18.2">
      ```python
      # v17 / early v18 — deprecated
      result = self.env['my.model'].read_group(
          domain=[('state', '=', 'confirmed')],
          fields=['partner_id', 'total_amount:sum'],
          groupby=['partner_id'],
      )

      # v18.2+ — use _read_group for backend
      result = self.env['my.model']._read_group(
          domain=[('state', '=', 'confirmed')],
          groupby=['partner_id'],
          aggregates=['total_amount:sum'],
      )
      ```
    </example>

    <example id="name_get" title="_search_display_name replaces name_get">
      ```python
      # v17 — deprecated since v16.4
      def name_get(self):
          return [(record.id, record.name) for record in self]

      # v18 — use display_name field or _search_display_name
      def _search_display_name(self, operator, value):
          return [('name', operator, value)]
      ```
    </example>

  </examples>


  <!-- ============================================================
       JAVASCRIPT MIGRATION
       ============================================================ -->
  <examples category="javascript">

    <example id="odoo_module" title="@odoo-module no longer required in v18">
      ```javascript
      // v17 — @odoo-module required
      /** @odoo-module **/
      import { Component } from "@odoo/owl";

      // v18 — direct ES module imports
      import { Component, useState, onWillStart } from "@odoo/owl";
      import { useService } from "@web/core/utils/hooks";
      import { registry } from "@web/core/registry";

      export class MyComponent extends Component {
          static template = "my_module.MyComponent";
          static props = { recordId: { type: Number, optional: true } };

          setup() {
              this.orm = useService("orm");
              this.state = useState({ data: [], loading: true });

              onWillStart(async () => {
                  this.state.data = await this.orm.searchRead(
                      "my.model", [], ["name", "state"]
                  );
                  this.state.loading = false;
              });
          }
      }

      registry.category("actions").add("my_module.my_action", MyComponent);
      ```
    </example>

  </examples>


  <!-- ============================================================
       MIGRATION CHECKLIST
       ============================================================ -->
  <migration_checklist>
    <item priority="CRITICAL">Replace all &lt;tree&gt; tags with &lt;list&gt; in XML views</item>
    <item priority="CRITICAL">Replace &lt;div class="oe_chatter"&gt; blocks with the bare &lt;chatter/&gt; tag (add reload_on_attachment/reload_on_follower/reload_on_post only if that specific behavior is needed)</item>
    <item priority="NONE">Record rules: no action needed — company_ids in domain_force is unchanged in v18 (do NOT replace with allowed_company_ids)</item>
    <item priority="HIGH">Adopt _check_company_auto = True on multi-company models that don't use it yet (available since v17, not new — just good practice if missing)</item>
    <item priority="HIGH">Adopt check_company=True on relational fields on multi-company models that don't use it yet (same — available since v17)</item>
    <item priority="HIGH">Rename group_operator to aggregator on all field definitions</item>
    <item priority="HIGH">Remove /** @odoo-module **/ from JS files</item>
    <item priority="HIGH">Migrate read_group() to _read_group() / formatted_read_group()</item>
    <item priority="MEDIUM">Start migrating raw SQL to SQL() builder</item>
    <item priority="MEDIUM">Review and test all multi-company scenarios</item>
  </migration_checklist>


  <!-- ============================================================
       ANTIPATTERNS
       ============================================================ -->
  <antipatterns>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: tree tag in v18 -->
      <tree string="Records">...</tree>

      <!-- CORRECT -->
      <list string="Records">...</list>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: oe_chatter div in v18 -->
      <div class="oe_chatter">
          <field name="message_follower_ids"/>
          <field name="activity_ids"/>
          <field name="message_ids"/>
      </div>

      <!-- CORRECT -->
      <chatter/>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      Claiming `allowed_company_ids` replaces `company_ids` in record rule `domain_force`
      in v18 — FALSE, confirmed against real 18.0/19.0 source.

      ```xml
      <!-- WRONG — allowed_company_ids is not valid in ir.rule domain_force, in any version -->
      <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

      <!-- CORRECT in both v17 and v18 -->
      <field name="domain_force">[('company_id', 'in', company_ids)]</field>
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: group_operator in v18
      date = fields.Date(group_operator='min')

      # CORRECT
      date = fields.Date(aggregator='min')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```javascript
      // WRONG: @odoo-module in v18
      /** @odoo-module **/
      import { Component } from "@odoo/owl";

      // CORRECT
      import { Component } from "@odoo/owl";
      ```
    </antipattern>

  </antipatterns>

</pattern>