# odoo-security-guide-18-19.md

<pattern>

  <description>
    Migration guide for Odoo security code upgrading from 18.0 to 19.0.
    Documents what changes are required, recommended, or unchanged.
    Use this file when upgrading an existing v18 module to v19.
  </description>

  <version_notes>
    <version id="18">
      Type hints recommended.
      SQL() builder required — from odoo.tools.sql import SQL.
      Record rules use company_ids in domain_force.
      _check_company_auto = True available.
      group_operator= already replaced by aggregator= (from v17-18 migration).
    </version>
    <version id="19">
      Type hints mandatory on all fields and method signatures.
      SQL() builder mandatory — import path changed: from odoo.tools import SQL.
      models.Constraint() replaces _sql_constraints tuple list.
      models.Index() replaces index= on fields.
      Record rules use company_ids in domain_force — no change from v18.
      Python 3.12+ required.
    </version>
  </version_notes>

  <examples>

    <example id="migration_overview" title="Migration overview table">
      ```
      Component               v18                       v19                      Action
      ----------------------  ------------------------  -----------------------  ----------
      Type hints              recommended               mandatory                REQUIRED
      SQL() builder           required (tools.sql)      required (tools)         REQUIRED (path change)
      SQL import path         odoo.tools.sql            odoo.tools               REQUIRED
      models.Constraint()     _sql_constraints list     models.Constraint()      recommended
      models.Index()          index= on fields          models.Index()           recommended
      Python                  3.11+                     3.12+                    check
      Record rules            company_ids               company_ids              no change
      _check_company_auto     available                 available                no change
      View syntax             invisible= expression     invisible= expression    no change
      ```
    </example>

    <example id="type_hints_migration" title="Type hints — from recommended to mandatory">
      ```python
      # v18: type hints recommended
      class MyModel(models.Model):
          _name = 'my.model'

          name = fields.Char(required=True)
          partner_id = fields.Many2one('res.partner')
          line_ids = fields.One2many('my.line', 'parent_id')
          tag_ids = fields.Many2many('my.tag')

      # v19: type hints mandatory
      from __future__ import annotations
      from datetime import date, datetime

      class MyModel(models.Model):
          _name = 'my.model'

          name: str = fields.Char(required=True)
          partner_id: int = fields.Many2one('res.partner')
          line_ids: list[int] = fields.One2many('my.line', 'parent_id')
          tag_ids: list[int] = fields.Many2many('my.tag')
      ```
    </example>

    <example id="method_type_hints" title="Method type hints (v19 mandatory)">
      ```python
      from __future__ import annotations
      from typing import Any

      class MyModel(models.Model):
          _name = 'my.model'

          @api.model_create_multi
          def create(self, vals_list: list[dict[str, Any]]) -> MyModel:
              return super().create(vals_list)

          def write(self, vals: dict[str, Any]) -> bool:
              return super().write(vals)

          def unlink(self) -> bool:
              return super().unlink()

          def action_confirm(self) -> dict[str, Any] | bool:
              self.write({'state': 'confirmed'})
              return True

          def _compute_total(self) -> None:
              for record in self:
                  record.total = sum(record.line_ids.mapped('amount'))
      ```
    </example>

    <example id="sql_import_migration" title="SQL import path change v18 → v19">
      ```python
      # v18: import from odoo.tools.sql
      from odoo.tools.sql import SQL

      # v19: import from odoo.tools
      from odoo.tools import SQL
      ```
    </example>

    <example id="sql_migration" title="SQL builder examples (v19)">
      ```python
      from odoo.tools import SQL  # v19 import path

      # Simple query
      def _get_records(self) -> list[tuple[int, str]]:
          query = SQL(
              "SELECT id, name FROM %(table)s WHERE active = %(active)s",
              table=SQL.identifier('my_table'),
              active=True,
          )
          self.env.cr.execute(query)
          return self.env.cr.fetchall()

      # Dynamic table with company filter
      def _get_model_records(self) -> list[tuple[int]]:
          query = SQL(
              "SELECT id FROM %(table)s WHERE company_id = %(company_id)s",
              table=SQL.identifier(self._table),
              company_id=self.env.company.id,
          )
          self.env.cr.execute(query)
          return self.env.cr.fetchall()

      # Complex join query
      def _get_report_data(self) -> list[dict[str, Any]]:
          query = SQL(
              """
              SELECT m.id, m.name, COALESCE(SUM(l.amount), 0) AS total_amount
              FROM %(main_table)s m
              LEFT JOIN %(line_table)s l ON l.parent_id = m.id
              WHERE m.company_id IN %(company_ids)s
                AND m.state = %(state)s
              GROUP BY m.id, m.name
              """,
              main_table=SQL.identifier(self._table),
              line_table=SQL.identifier('my_model_line'),
              company_ids=tuple(self.env.companies.ids) or (0,),
              state='confirmed',
          )
          self.env.cr.execute(query)
          return self.env.cr.dictfetchall()
      ```
    </example>

    <example id="constraint_index_migration" title="Constraint and index migration (recommended in v19)">
      ```python
      # v18: _sql_constraints and index= on fields
      class MyModel(models.Model):
          _name = 'my.model'

          name: str = fields.Char(required=True, index=True)
          company_id: int = fields.Many2one('res.company', index=True)

          _sql_constraints = [
              ('unique_name_company', 'UNIQUE(name, company_id)',
               'Name must be unique per company.'),
          ]

      # v19: models.Constraint() and models.Index()
      class MyModel(models.Model):
          _name = 'my.model'

          name: str = fields.Char(required=True)
          company_id: int = fields.Many2one('res.company')

          _sql_constraints = [
              models.Constraint(
                  'unique_name_company',
                  'UNIQUE(name, company_id)',
                  'Name must be unique per company.',
              ),
          ]

          _indexes = [
              models.Index('idx_my_model_company', ['company_id']),
              models.Index('idx_my_model_name_company', ['name', 'company_id']),
          ]
      ```
    </example>

    <example id="record_rule_no_change" title="Record rules — no change needed v18 to v19">
      ```xml
      <!-- v18 record rule — no migration needed for v19 -->
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
      <!-- company_ids is the correct variable in v18 and v19 -->
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: missing type hints in v19
      class MyModel(models.Model):
          name = fields.Char(required=True)
          partner_id = fields.Many2one('res.partner')

      # CORRECT
      from __future__ import annotations
      class MyModel(models.Model):
          name: str = fields.Char(required=True)
          partner_id: int = fields.Many2one('res.partner')
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: v18 SQL import path in v19
      from odoo.tools.sql import SQL  # v18 path — fails in v19

      # CORRECT
      from odoo.tools import SQL  # v19 path
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: raw SQL in v19 (SQL() builder mandatory)
      self.env.cr.execute(
          "SELECT id FROM my_table WHERE active = %s",
          [True]
      )

      # CORRECT
      from odoo.tools import SQL
      self.env.cr.execute(SQL(
          "SELECT id FROM %(t)s WHERE active = %(active)s",
          t=SQL.identifier('my_table'),
          active=True,
      ))
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG: f-string table name interpolation
      query = f"SELECT id FROM {self._table} WHERE company_id = %s"

      # CORRECT: SQL.identifier() for table/column names
      from odoo.tools import SQL
      query = SQL(
          "SELECT id FROM %(t)s WHERE company_id = %(cid)s",
          t=SQL.identifier(self._table),
          cid=self.env.company.id,
      )
      ```
    </antipattern>

  </antipatterns>

</pattern>