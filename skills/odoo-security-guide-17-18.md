# odoo-security-guide-17-18.md

<pattern>

  <description>
    Migration guide for Odoo security code upgrading from 17.0 to 18.0.
    Documents what changes are required, recommended, or unchanged.
    Use this file when upgrading an existing v17 module to v18.
  </description>

  <version_notes>
    <version id="17">
      SQL via parameterized self.env.cr.execute(query, params).
      Type hints optional.
      _check_company_auto = True available.
      check_company=True on Many2one available.
      Record rules use company_ids in domain_force.
      group_operator= on fields.
    </version>
    <version id="18">
      SQL() builder required — from odoo.tools.sql import SQL.
      Type hints recommended.
      _check_company_auto = True available (same as v17 — not a new feature).
      check_company=True on Many2one available (same as v17).
      Record rules use company_ids in domain_force — no change from v17.
      aggregator= replaces group_operator= on fields.
    </version>
  </version_notes>

  <examples>

    <example id="migration_overview" title="Migration overview table">
      ```
      Component            v17                         v18                    Action
      -------------------  --------------------------  ---------------------  -----------
      SQL queries          cr.execute(q, params)       SQL() builder          REQUIRED
      Field aggregation    group_operator=             aggregator=            REQUIRED
      Type hints           optional                    recommended            optional
      _check_company_auto  available                   available (no change)  no action
      check_company=True   available                   available (no change)  no action
      Record rules         company_ids                 company_ids (no change) no action
      View syntax          invisible= expression       invisible= expression  no change
      ```
    </example>

    <example id="sql_migration" title="SQL query migration — parameterized to SQL builder">
      ```python
      # v17: parameterized query
      def _get_data_v17(self):
          self.env.cr.execute(
              """
              SELECT id, name
              FROM %s
              WHERE company_id = %%s AND active = %%s
              """ % self._table,
              [self.env.company.id, True]
          )
          return self.env.cr.dictfetchall()

      # v18: SQL() builder (required)
      from odoo.tools.sql import SQL

      def _get_data_v18(self):
          query = SQL(
              """
              SELECT id, name
              FROM %(table)s
              WHERE company_id = %(company_id)s AND active = %(active)s
              """,
              table=SQL.identifier(self._table),
              company_id=self.env.company.id,
              active=True,
          )
          self.env.cr.execute(query)
          return self.env.cr.dictfetchall()
      ```
    </example>

    <example id="aggregator_migration" title="Field aggregation migration">
      ```python
      # v17: group_operator=
      amount = fields.Float(string='Amount', group_operator='sum')

      # v18: aggregator= (replaces group_operator=)
      amount: float = fields.Float(string='Amount', aggregator='sum')
      ```
    </example>

    <example id="type_hints_migration" title="Adding recommended type hints (v18)">
      ```python
      # v17: no type hints required
      class MyModel(models.Model):
          name = fields.Char(required=True)
          partner_id = fields.Many2one('res.partner', check_company=True)

      # v18: type hints recommended
      class MyModel(models.Model):
          name: str = fields.Char(required=True)
          partner_id: int = fields.Many2one('res.partner', check_company=True)
      ```
    </example>

    <example id="record_rule_no_change" title="Record rules — no change needed v17 to v18">
      ```xml
      <!-- v17 record rule — no migration needed for v18 -->
      <record id="rule_model_company" model="ir.rule">
          <field name="name">Model: Multi-Company</field>
          <field name="model_id" ref="model_custom_model"/>
          <field name="global" eval="True"/>
          <field name="domain_force">[
              '|',
              ('company_id', '=', False),
              ('company_id', 'in', company_ids)
          ]</field>
      </record>
      <!-- company_ids is the correct variable in both v17 and v18 -->
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```xml
      <!-- WRONG: allowed_company_ids is not a valid domain_force variable in any version -->
      <field name="domain_force">[('company_id', 'in', allowed_company_ids)]</field>

      <!-- CORRECT: company_ids in both v17 and v18 -->
      <field name="domain_force">[('company_id', 'in', company_ids)]</field>
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: treating _check_company_auto as a new v18 feature
      # It is available in v17 as well — no migration needed.

      # No migration action required for _check_company_auto or check_company=True.
      # Both are available in v17 and v18 unchanged.
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: keeping group_operator= in v18
      amount = fields.Float(group_operator='sum')  # deprecated in v18

      # CORRECT
      amount: float = fields.Float(aggregator='sum')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG: parameterized SQL in v18 (should use SQL builder)
      self.env.cr.execute(
          "SELECT id FROM %s WHERE company_id = %%s" % self._table,
          [self.env.company.id]
      )

      # CORRECT in v18
      from odoo.tools.sql import SQL
      self.env.cr.execute(SQL(
          "SELECT id FROM %(t)s WHERE company_id = %(cid)s",
          t=SQL.identifier(self._table),
          cid=self.env.company.id,
      ))
      ```
    </antipattern>

  </antipatterns>

</pattern>