# Widget Field Patterns — v17/v18/v19

OWL 2.x field widget patterns. Three shapes: simple input (CharField),
relational autocomplete (Many2OneField), tag-list (Many2ManyTagsField).

---

## Version differences (quick ref)

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| `@odoo-module` | REQUIRED | omit | omit |
| CharField boolean parse | `archParseBoolean` (`@web/views/utils`) | `exprToBoolean` (`@web/core/utils/strings`) | `exprToBoolean` |
| CharField `extractProps` | `({ attrs, options })` | `({ attrs, options })` + `placeholderField` prop | `({ attrs, options, placeholder })` — placeholder as arg |
| CharField `supportedTypes` | `["char"]` | `["char"]` | `["char", "text"]` |
| M2O BarcodeScanner import | `@web/webclient/barcode/barcode_scanner` | `@web/core/barcode/barcode_dialog` | same as v18 |
| M2O `context` prop type | `String` | `Object` | `Object` |
| M2O `openActionContext` | not available | added | available |
| M2O architecture | monolithic component | monolithic component | delegates to `Many2One` via `computeM2OProps` |
| M2O `searchThreshold` | not available | not available | new option |
| M2O registry pattern | `add("many2one", many2OneField)` | same | `add("many2one", { ...buildM2OFieldDescription(Many2OneField) })` |
| M2M Tags | no structural diff | no structural diff | no structural diff |

---

## Registration pattern (all versions)

```javascript
// Required structure for every field widget
export const myField = {
    component: MyFieldComponent,
    displayName: _t("My Widget"),
    supportedTypes: ["char"],           // REQUIRED — registry uses this
    extractProps: ({ attrs, options }) => ({
        myProp: attrs.my_attr,
    }),
};
registry.category("fields").add("my_widget", myField);
```

View-specific registration (optional):
```javascript
registry.category("fields").add("list.my_widget", myField);
registry.category("fields").add("kanban.my_widget", myField);
```

---

## CharField skeleton

```javascript
// v17: add /** @odoo-module **/ at top
// v17: import { archParseBoolean } from "@web/views/utils";
// v18+: import { exprToBoolean } from "@web/core/utils/strings";

import { registry } from "@web/core/registry";
import { useInputField } from "../input_field_hook";  // NOT useRecordObserver
import { standardFieldProps } from "../standard_field_props";
import { Component, useRef } from "@odoo/owl";

export class CharField extends Component {
    static template = "web.CharField";
    static props = {
        ...standardFieldProps,
        isPassword: { type: Boolean, optional: true },
        placeholder: { type: String, optional: true },
    };
    setup() {
        this.input = useRef("input");
        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            parse: (v) => this.parse(v),
        });
    }
    get formattedValue() {
        return formatChar(this.props.record.data[this.props.name], {
            isPassword: this.props.isPassword,
        });
    }
    parse(value) {
        const field = this.props.record.fields[this.props.name];
        return field.trim && !this.props.isPassword ? value.trim() : value;
    }
}

export const charField = {
    component: CharField,
    supportedTypes: ["char"],  // v19: ["char", "text"]
    extractProps: ({ attrs, options }) => ({
        // v17: archParseBoolean(attrs.password)
        // v18+: exprToBoolean(attrs.password)
        isPassword: exprToBoolean(attrs.password),
        placeholder: attrs.placeholder,
    }),
};
registry.category("fields").add("char", charField);
```

---

## Many2OneField skeleton

### v17/v18 (monolithic)

```javascript
// v17: add /** @odoo-module **/
import { Many2XAutocomplete, useOpenMany2XRecord } from "@web/views/fields/relational_utils";
import { standardFieldProps } from "../standard_field_props";

export class Many2OneField extends Component {
    static template = "web.Many2OneField";
    static components = { Many2XAutocomplete };
    static props = {
        ...standardFieldProps,
        canOpen: { type: Boolean, optional: true },
        canCreate: { type: Boolean, optional: true },
        context: { type: String, optional: true },  // v18: { type: Object }
        domain: { type: [Array, Function], optional: true },
        // ... standard m2o props
    };
}
export const many2OneField = {
    component: Many2OneField,
    supportedTypes: ["many2one"],
    extractProps({ attrs, context, decorations, options, string }, dynamicInfo) {
        return { canOpen: !options.no_open, context, domain: dynamicInfo.domain, string };
    },
};
registry.category("fields").add("many2one", many2OneField);
```

### v19 (delegated — refactored)

```javascript
import { computeM2OProps, Many2One } from "./many2one";

// Helper functions exported for reuse
export function extractM2OFieldProps(staticInfo, dynamicInfo) {
    const { attrs, options, placeholder } = staticInfo;
    return {
        canCreate: options.no_create ? false : hasCreatePermission,
        canOpen: !options.no_open,
        searchThreshold: options.search_threshold,  // NEW in v19
        domain: dynamicInfo.domain,
        // ...
    };
}

export function buildM2OFieldDescription(component) {
    return {
        component,
        extractProps: extractM2OFieldProps,
        supportedOptions: m2oSupportedOptions,
        supportedTypes: m2oSupportedTypes,
    };
}

export class Many2OneField extends Component {
    static components = { Many2One };  // delegates rendering
    get m2oProps() { return computeM2OProps(this.props); }
}

// v19 spread pattern
registry.category("fields").add("many2one", { ...buildM2OFieldDescription(Many2OneField) });
```

---

## Many2ManyTagsField skeleton

```javascript
// v17: add /** @odoo-module **/
import { Many2XAutocomplete, useActiveActions, useX2ManyCrud } from "@web/views/fields/relational_utils";
import { TagsList } from "@web/core/tags_list/tags_list";

export class Many2ManyTagsField extends Component {
    static template = "web.Many2ManyTagsField";
    static components = { TagsList, Many2XAutocomplete };
    static props = {
        ...standardFieldProps,
        colorField: { type: String, optional: true },
        canCreate: { type: Boolean, optional: true },
        domain: { type: [Array, Function], optional: true },
    };
    setup() {
        const { saveRecord, removeRecord } = useX2ManyCrud(
            () => this.props.record.data[this.props.name], true
        );
        this.activeActions = useActiveActions({ fieldType: "many2many", /* ... */ });
    }
}

export const many2ManyTagsField = {
    component: Many2ManyTagsField,
    supportedTypes: ["many2many"],
    relatedFields: ({ options }) => {
        const fields = [{ name: "display_name", type: "char" }];
        if (options.color_field) fields.push({ name: options.color_field, type: "integer", readonly: false });
        return fields;
    },
    extractProps({ attrs, options, string }, dynamicInfo) {
        return { colorField: options.color_field, domain: dynamicInfo.domain, string };
    },
};
registry.category("fields").add("many2many_tags", many2ManyTagsField);
```

---

## Common XML widget attributes (all versions)

```xml
<field name="state" widget="statusbar" statusbar_visible="draft,done"/>
<field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
<field name="amount" widget="monetary" options="{'currency_field': 'currency_id'}"/>
<field name="sequence" widget="handle"/>
<field name="image" widget="image" class="oe_avatar"/>
<field name="doc" widget="binary" filename="doc_filename"/>
<field name="active" widget="boolean_toggle"/>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `@odoo-module` in v18/v19 |
| CRITICAL | Use `useInputField()` for input binding — NOT `useRecordObserver` |
| HIGH | v18+: `exprToBoolean` replaces `archParseBoolean` |
| HIGH | Always include `supportedTypes` in registry registration |
| MEDIUM | OWL 2.x in all v17/v18/v19 — NOT OWL 3.x |