# Common Task Prompts

Each example shows the prompt, the pattern file it should trigger, and what a good
response looks like.

---

## New model

**Prompt:**
> Crea un nuevo modelo `library.book` en el módulo `library_management` para Odoo 18,
> con campos `name`, `author_id` (Many2one a `res.partner`) y `available` (Boolean).

**Triggers:** `skills/odoo-model-patterns-18.md` via `<version_router>`.

**Expected behavior:** the skill runs the mandatory reasoning block (new model = complex
task), checks for an existing `library_management` module before generating anything,
and follows attribute ordering (`_name` → fields → constraints → compute → CRUD →
actions → business methods).

---

## Inherit an existing model

**Prompt:**
> Necesito heredar `sale.order` para agregar un campo `commission_rate` y recalcular
> `amount_total` cuando cambie. Estamos en Odoo 19.

**Triggers:** `skills/inheritance-patterns.md` + `skills/computed-field-patterns.md`.

**Expected behavior:** uses `_inherit` (never replaces the model), lists the full
`@api.depends` chain, and applies v19 conventions (e.g. `models.Constraint()` if a SQL
constraint is involved).

---

## XML view inheritance

**Prompt:**
> Agrega un botón "Enviar a revisión" en la vista formulario de `purchase.order`,
> visible solo cuando `state == 'draft'`. Odoo 18.

**Triggers:** `skills/xml-view-patterns.md`.

**Expected behavior:** uses `xpath` + `inherit_id`, uses `invisible=` (not `attrs=`),
names the view `purchase_order_view_form.inherit.module_name`.

---

## Wizard

**Prompt:**
> Crea un wizard transitorio para hacer un ajuste masivo de precios en
> `product.template`, seleccionable desde una acción en la vista lista.

**Triggers:** `skills/wizard-patterns.md`.

**Expected behavior:** transient model without "wizard" in the name (e.g.
`product.price.adjust`), `action_` method starts with `self.ensure_one()` where
applicable.

---

## Controller / API endpoint

**Prompt:**
> Expón un endpoint JSON-RPC en `/library/books/available` que devuelva los libros
> disponibles, protegido por autenticación de usuario.

**Triggers:** `skills/controller-api-patterns.md`.

**Expected behavior:** controller file named after the module (never `main.py`),
explicit `auth` parameter on the route, no direct `cr.execute` when ORM search suffices.

---

## Security / access rights

**Prompt:**
> Agrega `ir.model.access.csv` y una regla de registro para que solo el grupo
> `library_group_manager` pueda borrar `library.book`.

**Triggers:** `skills/odoo-security-guide-18.md` (or matching version).

**Expected behavior:** treats `ir.model.access.csv` as mandatory (not optional), splits
groups into `module_groups.xml` and record rules into `model_security.xml`.

---

## Performance issue

**Prompt:**
> Este método recorre `self` con un `for record in self:` y llama `search()` dentro del
> loop para cada línea de factura. ¿Cómo lo optimizo?

**Triggers:** `skills/odoo-performance-guide.md`.

**Expected behavior:** flags the N+1 pattern explicitly, replaces with `mapped()`/
`filtered()`/`read_group()`, and explains why the loop-based `search()` is the actual
CRITICAL/HIGH issue rather than a generic "add an index" answer.

---

## OWL component

**Prompt:**
> Crea un componente OWL para mostrar un dashboard con tarjetas de KPIs en el backend,
> usando `useService` para leer datos de `sale.order`. Odoo 17.

**Triggers:** `skills/odoo-owl-components-17.md`.

**Expected behavior:** includes `@odoo-module` (required in v17, unlike v18/v19), OWL
2.x syntax, PascalCase class name, one component per file.