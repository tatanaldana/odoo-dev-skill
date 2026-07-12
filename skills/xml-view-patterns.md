# XML View Patterns — v17/v18/v19

---

## Version differences

| Feature | v17 | v18/v19 |
|---------|-----|---------|
| List tag | `<tree>` | `<list>` |
| Chatter | `<div class="oe_chatter">` + 3 fields | `<chatter/>` (bare tag dominant) |
| Visibility | `invisible="expr"` (no `attrs=`) | same |
| `aggregator=` | `group_operator=` | `aggregator=` |

---

## Form view skeleton

```xml
<form>
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                class="btn-primary" invisible="state != 'draft'"/>
        <button name="action_cancel" type="object" string="Cancel"
                invisible="state in ('done', 'cancelled')"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
    </header>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button name="action_view_lines" type="object"
                    class="oe_stat_button" icon="fa-list" invisible="line_count == 0">
                <field name="line_count" widget="statinfo" string="Lines"/>
            </button>
        </div>
        <widget name="web_ribbon" title="Archived" invisible="active"/>
        <div class="oe_title"><h1><field name="name" readonly="state == 'done'"/></h1></div>
        <group>
            <group><field name="partner_id"/><field name="user_id"/></group>
            <group><field name="date"/><field name="company_id" groups="base.group_multi_company"/></group>
        </group>
        <notebook>
            <page string="Lines" name="lines">
                <field name="line_ids" readonly="state == 'done'">
                    <!-- v17: <tree>, v18+: <list> -->
                    <list editable="bottom">
                        <field name="sequence" widget="handle"/>
                        <field name="name"/><field name="amount" sum="Total"/>
                    </list>
                </field>
            </page>
        </notebook>
    </sheet>
    <!-- v17: <div class="oe_chatter"><field name="message_follower_ids"/>...</div> -->
    <!-- v18+: -->
    <chatter/>
</form>
```

## List view

```xml
<!-- v17: <tree>, v18+: <list> -->
<list decoration-danger="state == 'cancelled'" decoration-success="state == 'done'">
    <field name="sequence" widget="handle"/>
    <field name="name"/>
    <field name="partner_id"/>
    <field name="total_amount" sum="Total"/>
    <field name="state" widget="badge"
           decoration-success="state == 'done'"
           decoration-info="state == 'confirmed'"
           decoration-danger="state == 'cancelled'"/>
    <field name="company_id" groups="base.group_multi_company" optional="hide"/>
</list>
```

## Search view

```xml
<search>
    <field name="name" filter_domain="['|', ('name', 'ilike', self), ('code', 'ilike', self)]"/>
    <field name="partner_id"/>
    <separator/>
    <filter name="filter_my" string="My Records" domain="[('user_id', '=', uid)]"/>
    <filter name="filter_draft" string="Draft" domain="[('state', '=', 'draft')]"/>
    <separator/>
    <filter name="filter_archived" string="Archived" domain="[('active', '=', False)]"/>
    <group expand="0" string="Group By">
        <filter name="groupby_state" string="State" context="{'group_by': 'state'}"/>
        <filter name="groupby_partner" string="Partner" context="{'group_by': 'partner_id'}"/>
        <filter name="groupby_date" string="Date" context="{'group_by': 'date:month'}"/>
    </group>
</search>
```

## View inheritance (xpath)

```xml
<record id="view_inherit_my_module" model="ir.ui.view">
    <field name="name">model.form.inherit.my_module</field>
    <field name="model">target.model</field>
    <field name="inherit_id" ref="base_module.view_id"/>
    <field name="arch" type="xml">
        <!-- Add field after existing -->
        <field name="partner_id" position="after">
            <field name="x_custom_field"/>
        </field>
        <!-- Add to button box -->
        <xpath expr="//div[@name='button_box']" position="inside">
            <button class="oe_stat_button" type="object" name="action_view_custom" icon="fa-star">
                <field name="custom_count" widget="statinfo" string="Custom"/>
            </button>
        </xpath>
        <!-- Conditional field (v17+: no attrs=) -->
        <field name="name" position="after">
            <field name="x_notes" invisible="state not in ['confirmed', 'done']"/>
        </field>
    </field>
</record>
```

## Kanban view

```xml
<kanban default_group_by="stage_id" class="o_kanban_small_column">
    <field name="color"/>
    <templates>
        <t t-name="card">
            <field name="name" class="fw-bold"/>
            <field name="partner_id"/>
            <field name="state" widget="badge"/>
        </t>
    </templates>
</kanban>
```

## Menu and actions

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form,kanban</field>
    <field name="context">{'search_default_filter_my': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">Create your first record</p>
    </field>
</record>

<menuitem id="menu_root" name="My Module" sequence="10"/>
<menuitem id="menu_my_model" name="My Models" parent="menu_root"
          action="action_my_model" sequence="10"/>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `attrs=` in v17+ — use `invisible=`/`readonly=`/`required=` directly |
| CRITICAL | v18+: `<tree>` → `<list>` |
| CRITICAL | v18+: `<div class="oe_chatter">` → `<chatter/>` |
| HIGH | Never use `string=` as xpath selector — use `name=` or specific xpath |
| HIGH | Never use positional xpath (`//field[3]`) — use named selectors |
| MEDIUM | Always provide `name=` on `<page>` elements for xpath targeting |