<pattern>

<description>
XML view definitions for Odoo form, list/tree, kanban, search, pivot, and graph views.
Covers view inheritance with XPath, visibility expressions (v17+ inline syntax),
chatter integration version differences, and actions/menus.
</description>

<version_notes>
  <version id="17">
    - List view tag: `<tree>`
    - Chatter: `<div class="oe_chatter">` block containing message_follower_ids, activity_ids, message_ids
    - Visibility: `invisible=`, `readonly=`, `required=` inline expressions only — `attrs=` removed in v17
  </version>
  <version id="18">
    - List view tag renamed to `<list>` — `<tree>` no longer valid
    - Chatter: bare, self-closing `<chatter/>` is the dominant form (65+ occurrences with
      no attributes in real 18.0/19.0 source). Optional attributes exist for specific
      views: `reload_on_attachment="True"` (account.move pattern), `reload_on_follower="True"`
      (project.task pattern) — add only if that behavior is actually needed
    - Visibility syntax unchanged from v17
  </version>
  <version id="19">
    - List and chatter syntax identical to v18
    - No view-layer changes from v18
  </version>
</version_notes>

<examples>

  <example id="form_v17" title="Form view — v17 (oe_chatter div, tree inside One2many)">
```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_confirm"
                        type="object"
                        string="Confirm"
                        class="btn-primary"
                        invisible="state != 'draft'"/>
                <button name="action_cancel"
                        type="object"
                        string="Cancel"
                        invisible="state not in ('draft', 'confirmed')"/>
                <field name="state" widget="statusbar"
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="action_view_invoices"
                            type="object"
                            class="oe_stat_button"
                            icon="fa-pencil-square-o">
                        <field name="invoice_count" widget="statinfo"
                               string="Invoices"/>
                    </button>
                </div>
                <widget name="web_ribbon" title="Archived"
                        bg_color="bg-danger"
                        invisible="active"/>
                <div class="oe_title">
                    <h1><field name="name" placeholder="Name"/></h1>
                </div>
                <group>
                    <group string="General">
                        <field name="partner_id"/>
                        <field name="date"/>
                        <field name="user_id"/>
                    </group>
                    <group string="Details">
                        <field name="company_id" groups="base.group_multi_company"/>
                        <field name="currency_id" invisible="1"/>
                        <field name="amount"/>
                    </group>
                </group>
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <tree editable="bottom">
                                <field name="sequence" widget="handle"/>
                                <field name="name"/>
                                <field name="quantity"/>
                                <field name="price_unit"/>
                                <field name="subtotal"/>
                            </tree>
                        </field>
                    </page>
                    <page string="Notes" name="notes">
                        <field name="notes" placeholder="Internal notes..."/>
                    </page>
                </notebook>
            </sheet>
            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```
  </example>

  <example id="form_v18" title="Form view — v18/v19 (chatter tag, list inside One2many)">
```xml
<record id="my_model_view_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <header>
                <button name="action_confirm"
                        type="object"
                        string="Confirm"
                        class="btn-primary"
                        invisible="state != 'draft'"/>
                <button name="action_cancel"
                        type="object"
                        string="Cancel"
                        invisible="state not in ('draft', 'confirmed')"/>
                <field name="state" widget="statusbar"
                       statusbar_visible="draft,confirmed,done"/>
            </header>
            <sheet>
                <div class="oe_button_box" name="button_box">
                    <button name="action_view_invoices"
                            type="object"
                            class="oe_stat_button"
                            icon="fa-pencil-square-o">
                        <field name="invoice_count" widget="statinfo"
                               string="Invoices"/>
                    </button>
                </div>
                <widget name="web_ribbon" title="Archived"
                        bg_color="bg-danger"
                        invisible="active"/>
                <div class="oe_title">
                    <h1><field name="name" placeholder="Name"/></h1>
                </div>
                <group>
                    <group string="General">
                        <field name="partner_id"/>
                        <field name="date"/>
                        <field name="user_id"/>
                    </group>
                    <group string="Details">
                        <field name="company_id" groups="base.group_multi_company"/>
                        <field name="currency_id" invisible="1"/>
                        <field name="amount"/>
                    </group>
                </group>
                <notebook>
                    <page string="Lines" name="lines">
                        <field name="line_ids">
                            <list editable="bottom">
                                <field name="sequence" widget="handle"/>
                                <field name="name"/>
                                <field name="quantity"/>
                                <field name="price_unit"/>
                                <field name="subtotal"/>
                            </list>
                        </field>
                    </page>
                    <page string="Notes" name="notes">
                        <field name="notes" placeholder="Internal notes..."/>
                    </page>
                </notebook>
            </sheet>
            <chatter/>
        </form>
    </field>
</record>
```
  </example>

  <example id="visibility_v17" title="Visibility expressions — v17+ inline syntax">
```xml
<!-- All versions v17+ -- inline expression syntax only -->
<field name="partner_id"
       invisible="state == 'draft'"
       readonly="state != 'draft'"
       required="type == 'customer'"/>

<button name="action" invisible="state != 'draft'"/>

<group invisible="not show_details">
    <field name="detail"/>
</group>

<!-- AND condition -->
<field name="x" invisible="state == 'draft' and not is_manager"/>

<!-- OR condition -->
<field name="x" invisible="state == 'done' or state == 'cancel'"/>

<!-- Parent access in One2many -->
<field name="x" invisible="parent.state != 'draft'"/>

<!-- Context access -->
<field name="x" invisible="context.get('hide_field')"/>
```
  </example>

  <example id="list_v17" title="List view — v17 (tree tag)">
```xml
<record id="my_model_view_list" model="ir.ui.view">
    <field name="name">my.model.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree string="My Models"
              decoration-danger="state == 'cancel'"
              decoration-warning="state == 'draft'"
              decoration-success="state == 'done'"
              default_order="date desc">
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="state" widget="badge"
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-warning="state == 'draft'"/>
            <field name="amount" sum="Total"/>
            <field name="company_id" column_invisible="True"/>
            <field name="internal_notes" optional="hide"/>
        </tree>
    </field>
</record>
```
  </example>

  <example id="list_v18" title="List view — v18/v19 (list tag)">
```xml
<record id="my_model_view_list" model="ir.ui.view">
    <field name="name">my.model.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Models"
              decoration-danger="state == 'cancel'"
              decoration-warning="state == 'draft'"
              decoration-success="state == 'done'"
              default_order="date desc">
            <field name="sequence" widget="handle"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date"/>
            <field name="state" widget="badge"
                   decoration-success="state == 'done'"
                   decoration-info="state == 'confirmed'"
                   decoration-warning="state == 'draft'"/>
            <field name="amount" sum="Total"/>
            <field name="company_id" column_invisible="True"/>
            <field name="internal_notes" optional="hide"/>
        </list>
    </field>
</record>
```
  </example>

  <example id="kanban_basic" title="Kanban view (v17+)">
```xml
<record id="my_model_view_kanban" model="ir.ui.view">
    <field name="name">my.model.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state">
            <field name="id"/>
            <field name="name"/>
            <field name="partner_id"/>
            <field name="state"/>
            <field name="color"/>
            <templates>
                <t t-name="kanban-box">
                    <div t-attf-class="oe_kanban_card oe_kanban_global_click #{kanban_color(record.color.raw_value)}">
                        <div class="oe_kanban_content">
                            <div class="o_kanban_record_top">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <field name="name"/>
                                    </strong>
                                </div>
                            </div>
                            <div class="o_kanban_record_body">
                                <field name="partner_id"/>
                            </div>
                            <div class="o_kanban_record_bottom">
                                <div class="oe_kanban_bottom_left">
                                    <field name="priority" widget="priority"/>
                                </div>
                                <div class="oe_kanban_bottom_right">
                                    <field name="user_id" widget="many2one_avatar_user"/>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```
  </example>

  <example id="search_view" title="Search view with filters, group-by, and searchpanel">
```xml
<record id="my_model_view_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="My Model">
            <field name="name" string="Name"/>
            <field name="partner_id"/>
            <separator/>
            <filter name="confirmed" string="Confirmed"
                    domain="[('state', '=', 'confirmed')]"/>
            <filter name="my_records" string="My Records"
                    domain="[('user_id', '=', uid)]"/>
            <group expand="0" string="Group By">
                <filter name="group_state" string="Status"
                        context="{'group_by': 'state'}"/>
                <filter name="group_partner" string="Partner"
                        context="{'group_by': 'partner_id'}"/>
                <filter name="group_date" string="Date"
                        context="{'group_by': 'date:month'}"/>
            </group>
            <searchpanel>
                <field name="state" icon="fa-filter" enable_counters="1"/>
                <field name="category_id" icon="fa-folder" enable_counters="1"/>
            </searchpanel>
        </search>
    </field>
</record>
```
  </example>

  <example id="inheritance_xpath" title="View inheritance with XPath">
```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.my_module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- Add field after existing field -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="x_custom_field"/>
        </xpath>
        <!-- Add field before existing field -->
        <xpath expr="//field[@name='phone']" position="before">
            <field name="x_another_field"/>
        </xpath>
        <!-- Replace field -->
        <xpath expr="//field[@name='website']" position="replace">
            <field name="website" widget="url"/>
        </xpath>
        <!-- Add attributes -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="required">1</attribute>
        </xpath>
        <!-- Add new page to notebook -->
        <xpath expr="//notebook" position="inside">
            <page string="Custom" name="custom">
                <group>
                    <field name="x_custom_field"/>
                </group>
            </page>
        </xpath>
    </field>
</record>
```
  </example>

  <example id="action_menu" title="Window action and menu items">
```xml
<record id="my_model_action" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form,kanban</field>
    <field name="domain">[('active', '=', True)]</field>
    <field name="context">{'search_default_my_records': 1}</field>
</record>

<menuitem id="my_module_menu_root"
          name="My Module"
          sequence="10"
          web_icon="my_module,static/description/icon.png"/>

<menuitem id="my_module_menu_main"
          name="Main Menu"
          parent="my_module_menu_root"
          sequence="10"/>

<menuitem id="my_model_menu"
          name="My Models"
          parent="my_module_menu_main"
          action="my_model_action"
          sequence="10"/>
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
Using `attrs=` in any v17+ view — removed in v17, use inline expressions instead.
```xml
<!-- WRONG: attrs= removed in v17 -->
<field name="partner_id"
       attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- CORRECT: v17+ inline expression -->
<field name="partner_id" invisible="state == 'draft'"/>
```
  </antipattern>

  <antipattern severity="CRITICAL">
Using `<tree>` tag in v18+ top-level list views — renamed to `<list>`.
```xml
<!-- WRONG in v18+: tree is only valid as embedded editable in v17 One2many -->
<arch type="xml">
    <tree string="My Models"> ... </tree>
</arch>

<!-- CORRECT in v18+ -->
<arch type="xml">
    <list string="My Models"> ... </list>
</arch>
```
  </antipattern>

  <antipattern severity="HIGH">
Using `oe_chatter` div block in v18+ — replaced by the `<chatter/>` tag.
```xml
<!-- WRONG in v18+: old div-based chatter -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>

<!-- CORRECT in v18+ — bare tag, no attributes needed for most models -->
<chatter/>
<!-- optional attributes for specific views that need them -->
<!-- <chatter reload_on_attachment="True"/> (account.move pattern) -->
<!-- <chatter reload_on_follower="True"/> (project.task pattern) -->
```
  </antipattern>

  <antipattern severity="HIGH">
Writing XPath expressions without reading the parent view structure first.
```xml
<!-- WRONG: assuming structure that may not exist -->
<xpath expr="//div[hasclass('flex-row')]" position="inside">
    <field name="x_custom_field"/>
</xpath>
<!-- The actual view might use QWeb t-name templates, groups, or different class names -->

<!-- CORRECT: read the parent view XML first, then write the matching XPath -->
```
  </antipattern>

  <antipattern severity="MEDIUM">
Using `view_mode` with `tree` in v18+ window actions.
```xml
<!-- WRONG in v18+ -->
<field name="view_mode">tree,form</field>

<!-- CORRECT in v18+ -->
<field name="view_mode">list,form</field>
```
  </antipattern>

</antipatterns>

</pattern>