# `odoo-context-gatherer`

File: [`agents/odoo-context-gatherer.md`](../agents/odoo-context-gatherer.md)

Use when: before generating complex code (new module, new model, multi-file change) so
the skill searches for existing Enterprise/Community/OCA implementations before
reinventing the wheel.

---

**Prompt:**
> Antes de crear el módulo, revisa si Odoo Community o Enterprise ya tienen algo similar
> a un sistema de reservas de salas de reunión.

**Prompt:**
> Necesito extender la facturación electrónica para Colombia. Reúne el contexto de cómo
> está implementado `l10n_co_edi` antes de proponer cambios.

**Prompt:**
> Voy a crear un módulo de control de flota vehicular. Busca en OCA si existe un
> repositorio similar antes de que empecemos a modelar desde cero.

---

**Expected behavior:** the agent searches core/OCA modules relevant to the domain,
reports what already exists and what gaps remain, and only then proceeds to the
`mandatory_reasoning` analysis block defined in `SKILL.md` step 2.
