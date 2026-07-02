# widget-field-patterns.md

<pattern>

  <description>
    OWL 2.x field widget patterns for custom and built-in field components in Odoo v17/18/19.
    Covers three distinct implementation shapes: simple input fields (CharField), relational
    autocomplete fields (Many2OneField), and tag-list fields (Many2ManyTagsField). Also covers
    XML widget attribute usage in views. All three versions use OWL 2.x — OWL 3.x is not
    present in any v17/18/19 reference file.
  </description>

  <version_notes>
    <version id="17">
      `/** @odoo-module **/` required at the top of every JS file (decision #2).
      CharField uses `archParseBoolean` from `@web/views/utils`.
      CharField `extractProps` receives `{ attrs, options }`.
      Many2OneField: `BarcodeScanner` imported from `@web/webclient/barcode/barcode_scanner`.
      Many2OneField: `context` prop typed as `{ type: String, optional: true }`.
      Many2OneField: no `openActionContext` prop.
      Many2ManyTagsField: `/** @odoo-module **/` required.
      registry.category("fields").add() pattern identical across v17/18/19.
    </version>
    <version id="18">
      No `@odoo-module` — omit entirely (decision #2).
      CharField: `archParseBoolean` replaced by `exprToBoolean` from `@web/core/utils/strings`.
      CharField adds `placeholderField` prop; `onBlur`, `onDynamicPlaceholderOpen`,
      `onDynamicPlaceholderValidate` methods added; `this.dynamicPlaceholder` stored on instance.
      CharField `extractProps` receives `{ attrs, options }` (same shape as v17).
      Many2OneField: `BarcodeScanner` imported from `@web/core/barcode/barcode_dialog`;
      `isBarcodeScannerSupported` separately from `@web/core/barcode/barcode_video_scanner`.
      Many2OneField: `context` prop changed to `{ type: Object, optional: true }`.
      Many2OneField: `openActionContext: { type: String, optional: true }` added.
      Many2OneField: imports `getFieldDomain` from `@web/model/relational_model/utils`.
      Many2ManyTagsField: no `@odoo-module`.
    </version>
    <version id="19">
      No `@odoo-module` — omit entirely (decision #2).
      CharField: `placeholderField` prop removed; `extractProps` receives `{ attrs, options, placeholder }`
      (placeholder passed as third destructured argument); `supportedTypes` expands to `["char", "text"]`.
      Many2OneField: completely refactored — component now delegates to `Many2One` component via
      `computeM2OProps`. Exports `buildM2OFieldDescription`, `extractM2OFieldProps`,
      `m2oSupportedOptions`, `m2oSupportedTypes` for reuse. `searchThreshold` option added.
      registry.category("fields").add() uses spread: `{ ...buildM2OFieldDescription(Many2OneField) }`.
      Many2ManyTagsField: no structural change from v18.
    </version>
  </version_notes>

  <examples>

    <example id="char_field_v17" title="CharField widget — v17">
      ```javascript
      /** @odoo-module **/

      import { _t } from "@web/core/l10n/translation";
      import { registry } from "@web/core/registry";
      import { archParseBoolean } from "@web/views/utils";
      import { formatChar } from "../formatters";
      import { useInputField } from "../input_field_hook";
      import { standardFieldProps } from "../standard_field_props";
      import { TranslationButton } from "../translation_button";
      import { Component, useRef } from "@odoo/owl";

      export class CharField extends Component {
          static template = "web.CharField";
          static components = { TranslationButton };
          static props = {
              ...standardFieldProps,
              autocomplete: { type: String, optional: true },
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
              if (this.props.record.fields[this.props.name].trim && !this.props.isPassword) {
                  return value.trim();
              }
              return value;
          }
      }

      export const charField = {
          component: CharField,
          displayName: _t("Text"),
          supportedTypes: ["char"],
          extractProps: ({ attrs, options }) => ({
              isPassword: archParseBoolean(attrs.password),
              autocomplete: attrs.autocomplete,
              placeholder: attrs.placeholder,
          }),
      };

      registry.category("fields").add("char", charField);
      ```
    </example>

    <example id="char_field_v18_v19" title="CharField widget — v18/v19 (no @odoo-module)">
      ```javascript
      // v18/v19 — no @odoo-module
      // v18 extractProps: ({ attrs, options }) — includes placeholderField
      // v19 extractProps: ({ attrs, options, placeholder }) — placeholder passed directly;
      //     supportedTypes: ["char", "text"]

      import { _t } from "@web/core/l10n/translation";
      import { registry } from "@web/core/registry";
      import { exprToBoolean } from "@web/core/utils/strings";   // replaces archParseBoolean
      import { formatChar } from "../formatters";
      import { useInputField } from "../input_field_hook";
      import { standardFieldProps } from "../standard_field_props";
      import { TranslationButton } from "../translation_button";
      import { Component, useRef } from "@odoo/owl";

      export class CharField extends Component {
          static template = "web.CharField";
          static components = { TranslationButton };
          static props = {
              ...standardFieldProps,
              autocomplete: { type: String, optional: true },
              isPassword: { type: Boolean, optional: true },
              placeholder: { type: String, optional: true },
          };

          setup() {
              this.input = useRef("input");
              useInputField({
                  getValue: () => this.props.record.data[this.props.name] || "",
                  parse: (v) => this.parse(v),
              });
              this.selectionStart = this.props.record.data[this.props.name]?.length || 0;
          }

          get formattedValue() {
              return formatChar(this.props.record.data[this.props.name], {
                  isPassword: this.props.isPassword,
              });
          }

          parse(value) {
              if (this.props.record.fields[this.props.name].trim && !this.props.isPassword) {
                  return value.trim();
              }
              return value;
          }
      }

      // v19: supportedTypes includes "text"
      export const charField = {
          component: CharField,
          displayName: _t("Text"),
          supportedTypes: ["char"],  // v19: ["char", "text"]
          extractProps: ({ attrs, options }) => ({       // v19: also receives placeholder
              isPassword: exprToBoolean(attrs.password), // replaces archParseBoolean
              autocomplete: attrs.autocomplete,
              placeholder: attrs.placeholder,
          }),
      };

      registry.category("fields").add("char", charField);
      ```
    </example>

    <example id="many2one_field_v17_v18" title="Many2OneField registration — v17/v18">
      ```javascript
      // v17: /** @odoo-module **/  at top
      // v18: no @odoo-module

      // v17 barcode import:
      // import * as BarcodeScanner from "@web/webclient/barcode/barcode_scanner";
      // v18 barcode imports:
      // import * as BarcodeScanner from "@web/core/barcode/barcode_dialog";
      // import { isBarcodeScannerSupported } from "@web/core/barcode/barcode_video_scanner";

      import { registry } from "@web/core/registry";
      import { standardFieldProps } from "../standard_field_props";
      import { Many2XAutocomplete, useOpenMany2XRecord } from "@web/views/fields/relational_utils";
      import { Component, onWillUpdateProps, useState } from "@odoo/owl";

      export class Many2OneField extends Component {
          static template = "web.Many2OneField";
          static components = { Many2XAutocomplete };
          static props = {
              ...standardFieldProps,
              placeholder: { type: String, optional: true },
              canOpen: { type: Boolean, optional: true },
              canCreate: { type: Boolean, optional: true },
              canWrite: { type: Boolean, optional: true },
              canQuickCreate: { type: Boolean, optional: true },
              canCreateEdit: { type: Boolean, optional: true },
              // v17: context: { type: String, optional: true }
              // v18: context: { type: Object, optional: true }
              context: { type: String, optional: true },
              domain: { type: [Array, Function], optional: true },
              relation: { type: String, optional: true },
              string: { type: String, optional: true },
              canScanBarcode: { type: Boolean, optional: true },
              decorations: { type: Object, optional: true },
          };
          // ... setup, getters, event handlers ...
      }

      export const many2OneField = {
          component: Many2OneField,
          supportedTypes: ["many2one"],
          extractProps({ attrs, context, decorations, options, string }, dynamicInfo) {
              // ... permission checks ...
              return {
                  canOpen: !options.no_open,
                  context: context,
                  domain: dynamicInfo.domain,
                  string,
              };
          },
      };

      registry.category("fields").add("many2one", many2OneField);
      registry.category("fields").add("list.many2one", many2OneField);
      registry.category("fields").add("kanban.many2one", many2OneField);
      ```
    </example>

    <example id="many2one_field_v19" title="Many2OneField registration — v19 (refactored)">
      ```javascript
      // v19: Many2OneField delegates to Many2One component via computeM2OProps.
      // Exports helper functions for downstream reuse.

      import { Component } from "@odoo/owl";
      import { _t } from "@web/core/l10n/translation";
      import { registry } from "@web/core/registry";
      import { computeM2OProps, Many2One } from "./many2one";
      import { standardFieldProps } from "../standard_field_props";
      import { evaluateBooleanExpr } from "@web/core/py_js/py";

      export function extractM2OFieldProps(staticInfo, dynamicInfo) {
          const { attrs, context, decorations, options, string, placeholder } = staticInfo;
          const hasCreatePermission = attrs.can_create ? evaluateBooleanExpr(attrs.can_create) : true;
          const canCreate = options.no_create ? false : hasCreatePermission;
          return {
              canCreate,
              canCreateEdit: canCreate && !options.no_create_edit,
              canOpen: !options.no_open,
              canQuickCreate: canCreate && !options.no_quick_create,
              canScanBarcode: !!options.can_scan_barcode,
              canWrite: attrs.can_write ? evaluateBooleanExpr(attrs.can_write) : true,
              context: dynamicInfo.context,
              decorations,
              domain: dynamicInfo.domain,
              nameCreateField: options.create_name_field,
              openActionContext: context || "{}",
              placeholder,
              searchThreshold: options.search_threshold,  // new in v19
              string,
          };
      }

      export function buildM2OFieldDescription(component) {
          return {
              component,
              displayName: _t("Many2one"),
              extractProps: extractM2OFieldProps,
              supportedOptions: m2oSupportedOptions,
              supportedTypes: m2oSupportedTypes,
          };
      }

      export class Many2OneField extends Component {
          static template = "web.Many2OneField";
          static components = { Many2One };
          static props = {
              ...standardFieldProps,
              canCreate: { type: Boolean, optional: true },
              canCreateEdit: { type: Boolean, optional: true },
              canOpen: { type: Boolean, optional: true },
              canQuickCreate: { type: Boolean, optional: true },
              canScanBarcode: { type: Boolean, optional: true },
              canWrite: { type: Boolean, optional: true },
              context: { type: Object, optional: true },
              decorations: { type: Object, optional: true },
              domain: { type: [Array, Function], optional: true },
              nameCreateField: { type: String, optional: true },
              openActionContext: { type: String, optional: true },
              placeholder: { type: String, optional: true },
              searchThreshold: { type: Number, optional: true },  // new in v19
              string: { type: String, optional: true },
          };

          get m2oProps() {
              return computeM2OProps(this.props);
          }
      }

      registry.category("fields").add("many2one", {
          ...buildM2OFieldDescription(Many2OneField),
      });
      ```
    </example>

    <example id="many2many_tags_v17" title="Many2ManyTagsField registration — v17">
      ```javascript
      /** @odoo-module **/

      import { _t } from "@web/core/l10n/translation";
      import { Domain } from "@web/core/domain";
      import { evaluateBooleanExpr } from "@web/core/py_js/py";
      import {
          Many2XAutocomplete,
          useActiveActions,
          useX2ManyCrud,
      } from "@web/views/fields/relational_utils";
      import { registry } from "@web/core/registry";
      import { standardFieldProps } from "../standard_field_props";
      import { TagsList } from "@web/core/tags_list/tags_list";
      import { useService } from "@web/core/utils/hooks";
      import { Component, useRef } from "@odoo/owl";

      export class Many2ManyTagsField extends Component {
          static template = "web.Many2ManyTagsField";
          static components = { TagsList, Many2XAutocomplete };
          static props = {
              ...standardFieldProps,
              canCreate: { type: Boolean, optional: true },
              canQuickCreate: { type: Boolean, optional: true },
              canCreateEdit: { type: Boolean, optional: true },
              colorField: { type: String, optional: true },
              createDomain: { type: [Array, Boolean], optional: true },
              domain: { type: [Array, Function], optional: true },
              context: { type: Object, optional: true },
              placeholder: { type: String, optional: true },
              string: { type: String, optional: true },
              noSearchMore: { type: Boolean, optional: true },
          };
          static defaultProps = {
              canCreate: true,
              canQuickCreate: true,
              canCreateEdit: true,
              nameCreateField: "name",
              context: {},
          };

          setup() {
              this.orm = useService("orm");
              const { saveRecord, removeRecord } = useX2ManyCrud(
                  () => this.props.record.data[this.props.name],
                  true
              );
              this.activeActions = useActiveActions({
                  fieldType: "many2many",
                  crudOptions: {
                      create: this.props.canCreate && this.props.createDomain,
                      createEdit: this.props.canCreateEdit,
                      onDelete: removeRecord,
                  },
                  getEvalParams: (props) => ({
                      evalContext: this.props.record.evalContext,
                      readonly: props.readonly,
                  }),
              });
              if (this.props.canQuickCreate) {
                  this.quickCreate = async (name) => {
                      const created = await this.orm.call(this.relation, "name_create", [name], {
                          context: this.props.context,
                      });
                      return saveRecord([created[0]]);
                  };
              }
          }

          get relation() {
              return this.props.record.fields[this.props.name].relation;
          }

          getDomain() {
              const domain =
                  typeof this.props.domain === "function" ? this.props.domain() : this.props.domain;
              const currentIds = this.props.record.data[this.props.name].currentIds.filter(
                  (id) => typeof id === "number"
              );
              return Domain.and([domain, Domain.not([["id", "in", currentIds]])]).toList(
                  this.props.context
              );
          }
      }

      export const many2ManyTagsField = {
          component: Many2ManyTagsField,
          displayName: _t("Tags"),
          supportedTypes: ["many2many"],
          relatedFields: ({ options }) => {
              const relatedFields = [{ name: "display_name", type: "char" }];
              if (options.color_field) {
                  relatedFields.push({ name: options.color_field, type: "integer", readonly: false });
              }
              return relatedFields;
          },
          extractProps({ attrs, options, string }, dynamicInfo) {
              const hasCreatePermission = attrs.can_create
                  ? evaluateBooleanExpr(attrs.can_create)
                  : true;
              const canCreate = options.no_create ? false : hasCreatePermission;
              return {
                  colorField: options.color_field,
                  canCreate,
                  canQuickCreate: canCreate && !options.no_quick_create,
                  canCreateEdit: canCreate && !options.no_create_edit,
                  createDomain: options.create,
                  context: dynamicInfo.context,
                  domain: dynamicInfo.domain,
                  placeholder: attrs.placeholder,
                  string,
              };
          },
      };

      registry.category("fields").add("many2many_tags", many2ManyTagsField);
      registry.category("fields").add("form.many2many_tags", {
          ...many2ManyTagsField,
          // color-editable variant for form views
      });
      ```
    </example>

    <example id="xml_widget_attrs" title="XML widget attributes in views (v17/18/19)">
      ```xml
      <!-- widget= attribute selects the OWL field component from the registry -->
      <!-- These attributes are identical across v17/18/19 unless noted -->

      <!-- Status bar (selection field) -->
      <field name="state" widget="statusbar" statusbar_visible="draft,done"/>

      <!-- Many2many displayed as colored tags -->
      <field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>

      <!-- Badge (readonly colored label) -->
      <field name="priority" widget="badge"/>

      <!-- Monetary (amount + currency symbol) -->
      <field name="amount_total" widget="monetary" options="{'currency_field': 'currency_id'}"/>

      <!-- Handle (drag-and-drop reorder in list) -->
      <field name="sequence" widget="handle"/>

      <!-- Image -->
      <field name="image_1920" widget="image" class="oe_avatar"/>

      <!-- Binary file download -->
      <field name="document" widget="binary" filename="document_filename"/>

      <!-- Boolean as toggle switch -->
      <field name="active" widget="boolean_toggle"/>

      <!-- Password (masks input) -->
      <field name="password" widget="char" password="True"/>
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Using `@odoo-module` in v18 or v19 JS files.
      ```javascript
      // WRONG in v18/v19
      /** @odoo-module **/
      import { registry } from "@web/core/registry";
      ```
      `@odoo-module` is required only in v17. Omit it entirely in v18/v19 (decision #2).
    </antipattern>

    <antipattern severity="CRITICAL">
      Using `useRecordObserver` as the field widget hook — it is not used in any
      CharField, Many2OneField, or Many2ManyTagsField reference file. The correct
      hook for input binding is `useInputField`. Mark any claim about
      `useRecordObserver` as unverified against your codebase.
      ```javascript
      // NOT confirmed in char/m2o/m2m reference files:
      // useRecordObserver(...)
      // Use useInputField() for text input fields instead.
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Using `archParseBoolean` in v18/v19 — it was replaced by `exprToBoolean`.
      ```javascript
      // WRONG in v18/v19
      import { archParseBoolean } from "@web/views/utils";
      extractProps: ({ attrs }) => ({ isPassword: archParseBoolean(attrs.password) })

      // CORRECT in v18/v19
      import { exprToBoolean } from "@web/core/utils/strings";
      extractProps: ({ attrs }) => ({ isPassword: exprToBoolean(attrs.password) })
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Registering a custom field without `supportedTypes` — the registry uses this
      to determine which field types the component handles.
      ```javascript
      // WRONG — missing supportedTypes
      registry.category("fields").add("my_widget", { component: MyField });

      // CORRECT
      registry.category("fields").add("my_widget", {
          component: MyField,
          supportedTypes: ["char"],
          extractProps: ({ attrs }) => ({ ... }),
      });
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      Claiming OWL 3.x is used in v19 — all v17/18/19 reference files use OWL 2.x.
      OWL 3.x is expected in v20 (decision #8).
    </antipattern>

  </antipatterns>

</pattern>