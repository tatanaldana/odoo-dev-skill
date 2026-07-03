# XML-Structured Prompts

The natural-language prompts in [`common-tasks.md`](common-tasks.md) work well for
quick, single-shot requests. For larger or more precise specs — several fields, several
files, or anything you want the skill to follow exactly without ambiguity — you can
write the request using the same XML tag vocabulary `SKILL.md` itself uses
(`<task>`, `<field>`, `<version>`, etc.). This gives the assistant a spec it can parse
deterministically instead of inferring intent from prose.

Use this style when:
- the request has more than ~4-5 fields/parameters and prose would get unwieldy
- you're generating several related artifacts at once (model + views + security)
- you want to remove any ambiguity about types, versions, or breaking changes in scope

Otherwise, prefer natural language — it's faster to write and the skill parses it fine
for everyday tasks (see [`common-tasks.md`](common-tasks.md)).

---

## New model (compare with the prose version in `common-tasks.md`)

**Prose:**
> Crea un nuevo modelo `library.book` en el módulo `library_management` para Odoo 18,
> con campos `name`, `author_id` (Many2one a `res.partner`) y `available` (Boolean).

**XML-structured:**
```xml
<request>
  <task>new_model</task>
  <odoo_version>18</odoo_version>
  <module>library_management</module>
  <model name="library.book" description="Library book catalog entry">
    <field name="name" type="Char" required="true"/>
    <field name="author_id" type="Many2one" comodel="res.partner"/>
    <field name="available" type="Boolean" default="true"/>
  </model>
</request>
```

Both should produce the same result — the XML form just removes any guesswork about
field types or the target module.

---

## Inherit + computed field

```xml
<request>
  <task>inherit_model</task>
  <odoo_version>19</odoo_version>
  <target_model>sale.order</target_model>
  <add_field name="commission_rate" type="Float"/>
  <recompute field="amount_total" on_change_of="commission_rate"/>
</request>
```

---

## View inheritance

```xml
<request>
  <task>view_inherit</task>
  <odoo_version>18</odoo_version>
  <target_view>purchase.order.form</target_view>
  <change>
    <add_button string="Enviar a revisión"/>
    <visible_when>state == 'draft'</visible_when>
  </change>
</request>
```

---

## Migration between versions

```xml
<request>
  <task>migration_analysis</task>
  <from_version>17</from_version>
  <to_version>18</to_version>
  <module>sale_commission_custom</module>
  <check_for>
    <item>group_operator to aggregator</item>
    <item>tree to list views</item>
    <item>oe_chatter div to chatter tag</item>
  </check_for>
</request>
```

---

## Guidelines validation

```xml
<request>
  <task>validate_guidelines</task>
  <odoo_version>19</odoo_version>
  <target_file>models/crm_lead_scoring.py</target_file>
  <focus_sections>
    <section>OI</section> <!-- ORM idioms -->
    <section>SEC</section> <!-- Security -->
  </focus_sections>
</request>
```
