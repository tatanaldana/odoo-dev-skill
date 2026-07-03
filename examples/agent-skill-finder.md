# `odoo-skill-finder`

File: [`agents/odoo-skill-finder.md`](../agents/odoo-skill-finder.md)

Use when: you're not sure which pattern file in `skills/` covers what you need, or you
want to explore the library itself rather than generate code immediately.

---

**Prompt:**
> ¿Qué archivo de `skills/` debería usar para implementar un dashboard con widgets
> personalizados en OWL?

**Prompt:**
> Lista todos los patrones disponibles relacionados con seguridad y control de acceso.

**Prompt:**
> No sé si esto es un caso de `onchange-dynamic-patterns` o `computed-field-patterns` —
> quiero mostrar/ocultar un campo según el valor de otro, sin guardarlo en base de
> datos.

---

**Expected behavior:** the agent walks `<pattern_index>` in `SKILL.md`, points to the
specific file and category, and — when the request is ambiguous between two
patterns — explains the distinction (e.g. `onchange-dynamic-patterns.md` for
non-persisted UI reactions vs. `computed-field-patterns.md` for stored/computed values)
instead of picking one silently.
