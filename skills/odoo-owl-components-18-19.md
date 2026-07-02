# Odoo OWL Migration Guide: 18.0 → 19.0

<pattern>

<description>
OWL migration guide from v18 to v19. OWL remains 2.x in v19 — NOT OWL 3.x.
The component API (Component, useState, hooks, static props, registry) is
identical to v18. The only breaking change affecting components is in the
ORM service: orm.readGroup() was removed.
</description>

<version_notes>
  <version id="18">
    OWL 2.x. orm.readGroup() available. @odoo-module optional.
    ORM constructor: ORM() no args.
  </version>
  <version id="19">
    OWL 2.x — component API identical to v18.
    orm.readGroup() REMOVED — use orm.formattedReadGroup().
    New ORM methods: formattedReadGroup(), formattedReadGroupingSets(),
    cache(), webSaveMulti(), webResequence().
    v18 components work in v19 without modification unless they call readGroup().
  </version>
</version_notes>

<examples>

  <example id="orm_read_group_breaking" title="BREAKING: orm.readGroup() removed in v19">

This is the only breaking change for most OWL components when migrating from v18 to v19.
Search all usages of `orm.readGroup` and replace.

```javascript
// wrong in v19 — throws runtime error
const groups = await this.orm.readGroup(
    "sale.order",
    [["state", "=", "sale"]],
    ["partner_id"],
    ["amount_total:sum"],
    { orderby: "partner_id" }
);
// groups[i].partner_id_count, groups[i].amount_total

// correct in v19 — formattedReadGroup()
const groups = await this.orm.formattedReadGroup(
    "sale.order",
    [["state", "=", "sale"]],           // domain
    ["partner_id"],                      // groupby
    ["amount_total:sum", "id:count"],    // aggregates — "field:aggregate" syntax
    { orderBy: [{ name: "partner_id", asc: true }] }
);
// groups[i].partner_id              → [id, display_name]
// groups[i]["amount_total:sum"]     → aggregate value
// groups[i]["id:count"]             → count
```

  </example>

  <example id="read_group_sets" title="formattedReadGroupingSets() — new in v19">

```javascript
// v19 — grouping sets for multiple dimensions in a single query
const result = await this.orm.formattedReadGroupingSets(
    "sale.order",
    [],
    [["partner_id"], ["state"], []],
    ["amount_total:sum", "id:count"],
);
```

  </example>

  <example id="orm_cache" title="orm.cache() — new in v19">

```javascript
setup() {
    this.orm = useService("orm");
    this.cachedOrm = this.orm.cache({ maxAge: 30000 });
}

async loadProducts() {
    // first call hits the server; identical calls within maxAge return cached result
    return await this.cachedOrm.searchRead(
        "product.template",
        [["active", "=", true]],
        ["name", "list_price"],
    );
}
```

  </example>

  <example id="orm_web_save_multi" title="orm.webSaveMulti() — new in v19">

```javascript
// v19 — save multiple records in a single call
await this.orm.webSaveMulti("my.model", [
    { id: 1, state: "confirmed" },
    { id: 2, state: "confirmed" },
    { id: 3, state: "cancelled" },
], { state: {} });
```

  </example>

  <example id="component_compatibility" title="v18 component compatibility in v19">

v18 OWL components work in v19 without modification as long as they do not
call orm.readGroup(). Migration checklist:

1. Search `orm.readGroup` — replace with `orm.formattedReadGroup`
2. Adjust result structure (see orm_read_group_breaking example)
3. Everything else — Component, useState, hooks, props, registry — unchanged

```javascript
// v18 component that does NOT use readGroup — works identically in v19
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class MyWidget extends Component {
    static template = "my_module.MyWidget";
    static props = {
        record: { type: Object },
        name: { type: String },
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ loading: false });
    }

    async triggerAction() {
        this.state.loading = true;
        try {
            await this.orm.call("my.model", "action_do_something", [
                [this.props.record.resId]
            ]);
        } finally {
            this.state.loading = false;
        }
    }
}
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Using orm.readGroup() in v19 — removed, throws runtime error.

```javascript
// wrong in v19
await this.orm.readGroup("my.model", [], ["state"], ["amount:sum"]);

// correct in v19
await this.orm.formattedReadGroup("my.model", [], ["state"], ["amount:sum"]);
```
  </antipattern>

  <antipattern severity="HIGH">
    Rewriting v18 components assuming "OWL 3.x requires changes" — there is no OWL 3.x
    in v19. The component API is identical to v18. static props, lifecycle hooks,
    and registry patterns are unchanged.
  </antipattern>

</antipatterns>

</pattern>