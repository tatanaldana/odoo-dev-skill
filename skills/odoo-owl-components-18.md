# OWL Components — v18 (OWL 2.x)

`@odoo-module` optional. New: `autocloseDelay`, `company` service, `registry.addValidation()`.

---

## Client action

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyDashboard extends Component {
    static template = "my_module.MyDashboard";
    static props = { action: { type: Object } };
    setup() {
        this.orm = useService("orm");
        this.company = useService("company");
        this.notification = useService("notification");
        this.state = useState({ records: [], loading: true });
        onWillStart(async () => {
            this.state.records = await this.orm.searchRead("my.model",
                [["company_id", "in", this.company.allowedCompanyIds]],
                ["name", "state"], { limit: 80 });
            this.state.loading = false;
        });
    }
}
registry.category("actions").add("my_module.dashboard", MyDashboard);
```

## Field widget

```javascript
import { standardFieldProps } from "@web/views/fields/standard_field_props";
export class StarRating extends Component {
    static template = "my_module.StarRating";
    static props = { ...standardFieldProps };
    get value() { return this.props.record.data[this.props.name] || 0; }
    setRating(r) { if (!this.props.readonly) this.props.record.update({ [this.props.name]: r }); }
}
registry.category("fields").add("star_rating", { component: StarRating, supportedTypes: ["integer"] });
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Import from `@odoo/owl` — not legacy `owl` or `web.owl` |
| HIGH | Use `useService()` in `setup()` — not `this.env.services` |
| HIGH | `onWillStart` for data loading — not `onMounted` (not awaited) |
| MEDIUM | Reassign Set/Map after mutation for OWL reactivity |