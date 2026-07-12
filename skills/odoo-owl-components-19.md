# OWL Components — v19 (OWL 2.x)

OWL remains 2.x — NOT 3.x. Component API identical to v18.
Main change: ORM service.

## ORM changes in v19

| Method | Status |
|--------|--------|
| `orm.readGroup()` | **REMOVED** |
| `orm.formattedReadGroup()` | new replacement |
| `orm.cache({ maxAge })` | new — cached ORM calls |
| `orm.webSaveMulti()` | new |
| `orm.webResequence()` | new |

## Client action skeleton

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyDashboard extends Component {
    static template = "my_module.MyDashboard";
    static props = { action: { type: Object } };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ records: [], grouped: [], loading: true });
        onWillStart(async () => { await this.loadData(); });
    }

    async loadData() {
        this.state.records = await this.orm.searchRead(
            "my.model", [], ["name", "state", "amount"], { limit: 80 }
        );
        // formattedReadGroup replaces readGroup
        this.state.grouped = await this.orm.formattedReadGroup(
            "my.model", [], ["state"], ["amount:sum", "__count"]
        );
        this.state.loading = false;
    }
}
registry.category("actions").add("my_module.dashboard", MyDashboard);
```

## orm.cache()

```javascript
this.cachedOrm = this.orm.cache({ maxAge: 60000 });
const products = await this.cachedOrm.searchRead("product.template", [], ["name"]);
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
| CRITICAL | `orm.readGroup()` removed in v19 — use `formattedReadGroup()` |
| CRITICAL | OWL 2.x — NOT 3.x |
| HIGH | Mutating Set/Map in-place — reassign: `this.state.ids = new Set(...)` |