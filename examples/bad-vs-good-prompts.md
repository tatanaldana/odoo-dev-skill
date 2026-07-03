# Bad vs. Good Prompts

The skill matches keywords against `<activation_triggers>` and `<pattern_index>` in
`SKILL.md`. A vague prompt gives it nothing to match, so it falls back to generic
knowledge instead of the version-specific pattern file. These pairs show the difference.

---

### Adding a field

❌ **Weak:** "Agrega un campo a mi modelo."

✅ **Better:** "Agrega un campo `discount_percent` (Float) a `sale.order.line` en Odoo
18, que se recalcule automáticamente cuando cambie `price_unit` o `quantity`."

Why: names the model, the field, the version, and that it's a computed field —
enough to load `skills/computed-field-patterns.md` and the v18 breaking changes.

---

### Fixing a bug

❌ **Weak:** "Esto no funciona, arréglalo."

✅ **Better:** "El método `_compute_amount_total` en `account_move.py` lanza
`RecursionError` cuando hay más de 500 líneas de factura. Aquí está el código: [...]"

Why: gives the exact method, file, error type, and reproduction condition — the skill
can reason about the actual defect instead of guessing.

---

### Migration

❌ **Weak:** "Actualiza mi módulo a la nueva versión de Odoo."

✅ **Better:** "Migra este módulo de Odoo 17 a Odoo 18: reemplaza `group_operator=` por
`aggregator=`, convierte las vistas `<tree>` a `<list>`, y actualiza el `oe_chatter` div
al tag `<chatter/>`."

Why: names both versions so the skill loads the migration guide file
(`skills/{pattern}-17-18.md`) instead of a single-version file, and lists the exact
breaking changes to check.

---

### Code review

❌ **Weak:** "Revisa mi código."

✅ **Better:** "Ejecuta el agente de code review sobre `models/purchase_requisition.py`,
enfocándote en seguridad y en el orden de atributos de la clase."

Why: explicitly invokes `odoo-code-reviewer`, scopes the file, and tells it which
severity categories matter most for this pass.

---

### Security audit

❌ **Weak:** "¿Es seguro este módulo?"

✅ **Better:** "Valida `ir.model.access.csv` y las reglas de registro del módulo
`hr_expense_custom` contra las guías de seguridad de Odoo 19 — quiero saber si hay
modelos sin control de acceso."

Why: names the exact artifacts (`ir.model.access.csv`, record rules), the module, and
the version, so `skills/odoo-security-guide-19.md` is loaded with a concrete target
instead of a general sweep.
