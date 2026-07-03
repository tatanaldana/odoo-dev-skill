# `odoo-code-reviewer`

File: [`agents/odoo-code-reviewer.md`](../agents/odoo-code-reviewer.md)

Use when: quality and security audits of existing code.

---

**Prompt:**
> Ejecuta un code review sobre `models/hr_expense_sheet.py`, revisando especialmente
> las reglas CRITICAL y HIGH del skill (SQL crudo, `cr.commit()` manual, `browse()` en
> loops).

**Prompt:**
> Revisa este pull request completo antes de mergear: `models/`, `views/` y `security/`
> del módulo `stock_picking_batch_custom`. Odoo 18.

**Prompt:**
> ¿Este método viola algún principio SOLID? Aquí está el código: [...]

---

**Expected behavior:** output grouped by severity (CRITICAL / HIGH / MEDIUM), citing the
specific rule from `<forbidden>` in `SKILL.md`, with the file and line referenced —
not a generic "looks fine" or unstructured prose review.
