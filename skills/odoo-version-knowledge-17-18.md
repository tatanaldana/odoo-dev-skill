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
    <change version="18" type="breaking">&lt;div class="oe_chatter"&gt; block replaced by &lt;chatter reload_on_attachment="True"/&gt; widget</change>
    <change version="18" type="breaking">company_ids replaced by allowed_company_ids in record rules</change>
    <change version="18" type="breaking">group_operator renamed to aggregator on field definitions — confirmed in model_18.py</change>
    <change version="18" type="breaking">@odoo-module comment no longer required in JS — use direct ES module imports</change>
    <change version="18" type="new">_check_company_auto = True — automatic company validation on write()</change>
    <change version="18" type="new">check_company=True on relational fields — automatic cross-company validation</change>
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

    <example id="record_rule" title="Record Rule — allowed_company_ids">
      ```xml
      <!-- v17 -->
      <field name="domain_force">[('company_id', '=', company_id)]</field>

      <!-- v18 -->
      <field name="domain_force">[
          '|',
          ('company_id', '=', False),
          ('company_id', 'in', allowed_company_ids)
      ]</field>
      ```
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

      <!-- v18 -->
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
    <item priority="CRITICAL">Replace &lt;div class="oe_chatter"&gt; blocks with &lt;chatter reload_on_attachment="True"/&gt;</item>
    <item priority="CRITICAL">Update record rules from company_ids to allowed_company_ids</item>
    <item priority="HIGH">Add _check_company_auto = True to multi-company models</item>
    <item priority="HIGH">Add check_company=True to relational fields on multi-company models</item>
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
      <chatter reload_on_attachment="True"/>
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