# Odoo OWL Components - Version 18.0 (OWL 2.x)

<pattern>

<description>
OWL component patterns for Odoo 18. OWL 2.x — same framework as v17 with
infrastructure changes. @odoo-module is no longer required (still works if
included). ORM constructor refactored. notification gains autocloseDelay.
registry gains addValidation(). New "company" service.
</description>

<version_notes>
  <version id="17">
    @odoo-module REQUIRED. ORM constructor: ORM(rpc, user).
    notification has no autocloseDelay. See odoo-owl-components-17.md.
  </version>
  <version id="18">
    @odoo-module optional (no longer required). ORM constructor: ORM() no args —
    imports rpc/user directly at module level. notification.add() gains
    autocloseDelay option (number ms, default 4000). registry.category().addValidation()
    available. New "company" service.
  </version>
  <version id="19">
    OWL remains 2.x. orm.readGroup() REMOVED — use formattedReadGroup().
    See odoo-owl-components-19.md.
  </version>
</version_notes>

<examples>

  <example id="client_action" title="Client Action — full pattern v18">

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
        this.company = useService("company");  // new in v18

        this.state = useState({
            records: [],
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
                [["company_id", "in", this.company.allowedCompanyIds]],
                ["name", "state", "amount"],
                { order: "create_date DESC", limit: 80 }
            );
        } catch (err) {
            this.state.error = err.message;
            this.notification.add("Error loading data", {
                type: "danger",
                autocloseDelay: 8000,  // new in v18
            });
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

  <example id="notification_autoclose" title="notification.add() — new autocloseDelay in v18">

```javascript
// v17 — fixed 4000ms, not configurable
this.notification.add("Saved", { type: "success" });

// v18 — autocloseDelay configurable (milliseconds)
this.notification.add("Saved", {
    type: "success",
    autocloseDelay: 2000,
});

this.notification.add("Warning: check configuration", {
    type: "warning",
    sticky: true,
    buttons: [
        {
            name: "Fix now",
            onClick: () => this.openSettings(),
            primary: true,
        },
    ],
});

// Options available in both versions: title, type, sticky, className, onClose, buttons
// autocloseDelay: v18+ only
```

  </example>

  <example id="field_widget" title="Field Widget — pattern v18">

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

  <example id="dialog" title="Dialog component v18">

```javascript
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class ConfirmActionDialog extends Component {
    static template = "my_module.ConfirmActionDialog";
    static components = { Dialog };
    static props = {
        close: { type: Function },
        title: { type: String, optional: true },
        message: { type: String, optional: true },
        onConfirm: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ processing: false });
    }

    async onConfirm() {
        this.state.processing = true;
        try {
            await this.props.onConfirm?.();
            this.props.close();
        } finally {
            this.state.processing = false;
        }
    }
}
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Importing OWL from legacy paths.

```javascript
// wrong
const { Component } = owl;
import { Component } from "web.owl";

// correct
import { Component } from "@odoo/owl";
```
  </antipattern>

  <antipattern severity="HIGH">
    Accessing services via `this.env.services` — always use `useService()` inside `setup()`.

```javascript
// wrong
async myMethod() {
    const result = await this.env.services.orm.searchRead(...);
}

// correct
setup() {
    this.orm = useService("orm");
}
```
  </antipattern>

  <antipattern severity="HIGH">
    Using `onMounted` for initial data loading — not awaited during render.

```javascript
// wrong
onMounted(async () => {
    this.state.data = await this.orm.searchRead(...);
});

// correct
onWillStart(async () => {
    this.state.data = await this.orm.searchRead(...);
});
```
  </antipattern>

  <antipattern severity="MEDIUM">
    Mutating Set/Map in-place — OWL 2.x (v17/v18) does not trigger re-render on in-place mutation.

```javascript
// wrong — UI does not update
this.state.selectedIds.add(id);

// correct in v17/v18
this.state.selectedIds.add(id);
this.state.selectedIds = new Set(this.state.selectedIds);
```
  </antipattern>

</antipatterns>

</pattern>