# `odoo-upgrade-analyzer`

File: [`agents/odoo-upgrade-analyzer.md`](../agents/odoo-upgrade-analyzer.md)

Use when: analyzing a migration between Odoo versions before touching code.

---

**Prompt:**
> Analiza qué breaking changes afectan al módulo `sale_commission_custom` al migrar de
> Odoo 17 a 18.

**Prompt:**
> Tengo 12 módulos personalizados en Odoo 18. Antes de migrar a Odoo 19, dime cuáles
> usan `_sql_constraints` o `orm.readGroup()` para saber el alcance del esfuerzo.

**Prompt:**
> ¿Qué cambia en las vistas XML entre v17 y v18 que me obligaría a tocar
> `purchase_approval/views/purchase_order_views.xml`?

---

**Expected behavior:** the agent references `<breaking_changes>` from `SKILL.md`'s
`<version_router>` for the exact `from`/`to` pair, lists affected files/patterns, and
does not silently assume a single-version file when two versions are in scope — it
should load the `{pattern}-{vA}-{vB}.md` migration guide file instead.
