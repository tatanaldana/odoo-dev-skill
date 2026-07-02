# Odoo OWL Components - Version 19.0 (OWL 2.x)

<pattern>

<description>
OWL component patterns for Odoo 19. OWL remains 2.x — NOT OWL 3.x.
The main change is in the ORM service: orm.readGroup() was removed, replaced
by orm.formattedReadGroup(). New methods: orm.cache(), orm.webSaveMulti(),
orm.webResequence(). The component API (props, hooks, lifecycle) is identical to v18.
</description>

<version_notes>
  <version id="17">
    ORM constructor: ORM(rpc, user). orm.readGroup() available.
    @odoo-module REQUIRED. See odoo-owl-components-17.md.
  </version>
  <version id="18">
    ORM constructor: ORM() no args. orm.readGroup() available.
    @odoo-module optional. notification gains autocloseDelay.
    See odoo-owl-components-18.md.
  </version>
  <version id="19">
    OWL 2.x — component API identical to v18. @odoo-module optional.
    orm.readGroup() REMOVED — use orm.formattedReadGroup().
    New: orm.cache(), orm.webSaveMulti(), orm.webResequence(),
    orm.formattedReadGroupingSets().
  </version>
</version_notes>

<examples>

  <example id="client_action" title="Client Action — full pattern v19">

```javascript
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyDashboard extends Component {
    static template = "my_module.MyDashboard";
    static props = {
        action: { type: Object },
        actionService: { type: Object },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            records: [],
            groupedData: [],
            loading: true,
            error: null,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            this.state.records = await this.orm.searchRead(
                "my.model",
                [],
                ["name", "state", "amount"],
                { order: "create_date DESC", limit: 80 }
            );

            // formattedReadGroup replaces readGroup() in v19
            this.state.groupedData = await this.orm.formattedReadGroup(
                "my.model",
                [],
                ["state"],
                ["amount:sum", "id:count"],
            );
        } catch (err) {
            this.state.error = err.message;
            this.notification.add("Error loading data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async openRecord(id) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "my.model",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("my_module.my_dashboard", MyDashboard);
```

  </example>

  <example id="orm_read_group_migration" title="readGroup() → formattedReadGroup() — breaking change v19">

```javascript
// wrong in v19 — readGroup() was removed
const groups = await this.orm.readGroup(
    "sale.order",
    [["state", "=", "sale"]],
    ["partner_id"],
    ["amount_total:sum"],
);

// correct in v19 — formattedReadGroup()
const groups = await this.orm.formattedReadGroup(
    "sale.order",
    [["state", "=", "sale"]],      // domain
    ["partner_id"],                 // groupby
    ["amount_total:sum", "id:count"],  // aggregates — "field:aggregate" syntax
);
// groups[i].partner_id        → group value
// groups[i]["amount_total:sum"] → aggregate value
// groups[i]["id:count"]         → count
```

  </example>

  <example id="orm_cache" title="orm.cache() — new in v19">

```javascript
setup() {
    this.orm = useService("orm");
    this.cachedOrm = this.orm.cache({ maxAge: 60000 });
}

async loadCatalog() {
    // second identical call within maxAge returns cached result without server roundtrip
    const products = await this.cachedOrm.searchRead(
        "product.template",
        [["active", "=", true]],
        ["name", "list_price"],
    );
    return products;
}
```

  </example>

  <example id="field_widget" title="Field Widget — pattern v19">

```javascript
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class StarRatingWidget extends Component {
    static template = "my_module.StarRatingWidget";
    static props = {
        ...standardFieldProps,
    };

    get value() {
        return this.props.record.data[this.props.name] || 0;
    }

    get isReadonly() {
        return this.props.readonly;
    }

    setRating(rating) {
        if (this.isReadonly) return;
        this.props.record.update({ [this.props.name]: rating });
    }
}

registry.category("fields").add("star_rating", {
    component: StarRatingWidget,
    supportedTypes: ["integer"],
});
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using orm.readGroup() in v19 — it was removed and throws a runtime error.

```javascript
// wrong in v19
const groups = await this.orm.readGroup("sale.order", [], ["state"], ["amount_total:sum"]);

// correct in v19
const groups = await this.orm.formattedReadGroup(
    "sale.order", [], ["state"], ["amount_total:sum"]
);
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Assuming v19 uses OWL 3.x — the component API is identical to v18 (OWL 2.x).
    There are no new requirements for static props or lifecycle hooks compared to v18.
  </antipattern>

  <antipattern severity="HIGH">
    Mutating Set/Map in-place — OWL 2.x in v19 has the same behavior as v18.

```javascript
// wrong in v17/v18/v19
this.state.selectedIds.add(id);

// correct in v17/v18/v19
this.state.selectedIds.add(id);
this.state.selectedIds = new Set(this.state.selectedIds);
```
  </antipattern>

</antipatterns>

</pattern>