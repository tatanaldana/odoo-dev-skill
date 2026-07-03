# `odoo-coding-guidelines-validator`

File: [`agents/odoo-coding-guidelines-validator.md`](../agents/odoo-coding-guidelines-validator.md)

Use when: validating code against the official Odoo Coding Guidelines (v19), covering
module structure, Python naming, class structure, ORM idioms, XML views, security and
JS/OWL.

---

**Prompt:**
> Valida este código contra las guías de codificación de Odoo:
> ```python
> class saleorderextra(models.Model):
>     _name = 'sale.order.extra'
>     def compute_total(self):
>         self.env.cr.execute("SELECT ...")
> ```

**Prompt:**
> Revisa si el módulo `crm_lead_scoring` sigue los estándares OCA — enfócate en la
> sección ORM idioms (OI-01 a OI-08).

**Prompt:**
> Verifica `views/res_partner_views.xml` por violaciones de la guía XV (attrs vs
> invisible, xpath vs reemplazo completo).

---

**Expected behavior:** a structured report with a severity table (CRITICAL/HIGH/MEDIUM/
OK counts) followed by one block per violation citing the rule code (e.g. `OI-01`,
`NP-02`, `SEC-03`, `DC-01`, `LG-03`, `SR-01`), the line, the problem, the fix, and the
official rule text — matching the format shown in the README's "Guidelines Validator"
section. Sections covered: module structure (MS), naming (NP), class structure (CS),
ORM idioms (OR), XML views (XV), security (SEC), JavaScript/OWL (JS), docstrings and
method size (DC), performance (SR), logging (LG).
