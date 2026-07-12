# OWL Components — v17 (OWL 2.x)

`/** @odoo-module **/` REQUIRED. ORM: `ORM(rpc, user)`. No `autocloseDelay`.

---

## Client action

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyDashboard extends Component {
    static template = "my_module.MyDashboard";
    static props = { action: { type: Object } };
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ records: [], loading: true });
        onWillStart(async () => {
            this.state.records = await this.orm.searchRead("my.model", [],
                ["name", "state"], { limit: 80 });
            this.state.loading = false;
        });
    }
}
registry.category("actions").add("my_module.dashboard", MyDashboard);
```

## Field widget

```javascript
/** @odoo-module **/
import { standardFieldProps } from "@web/views/fields/standard_field_props";
export class StarRating extends Component {
    static props = { ...standardFieldProps };
    get value() { return this.props.record.data[this.props.name] || 0; }
}
registry.category("fields").add("star_rating", { component: StarRating, supportedTypes: ["integer"] });
```

## patch()

```javascript
/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
patch(FormController.prototype, {
    async beforeExecuteActionButton(clickParams) {
        if (clickParams.special === "my_special") await this._myCheck();
        return super.beforeExecuteActionButton(clickParams);
    },
});
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `@odoo-module` REQUIRED in v17 — omitting breaks module loading |
| CRITICAL | Import from `@odoo/owl` — not legacy paths |
| HIGH | `useService()` in `setup()` — not `this.env.services` |
| HIGH | `onWillStart` for data — not `onMounted` |
| MEDIUM | Reassign Set/Map after mutation |