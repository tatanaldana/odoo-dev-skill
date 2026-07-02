# Odoo OWL Components - Version 17.0 (OWL 2.x)

<pattern>

<description>
OWL component patterns for Odoo 17. OWL 2.x — same API as v16 with minor
enhancements to error handling and services. @odoo-module is REQUIRED in v17.
</description>

<version_notes>
  <version id="17">
    OWL 2.x — same API as v16. @odoo-module REQUIRED. static props recommended.
    ORM constructor: ORM(rpc, user). orm.readGroup() available.
    notification has no autocloseDelay option.
  </version>
  <version id="18">
    @odoo-module no longer required (optional). ORM constructor changes to ORM() no args.
    notification gains autocloseDelay. registry gains addValidation().
    See odoo-owl-components-18.md.
  </version>
  <version id="19">
    OWL remains 2.x (not 3.x). orm.readGroup() REMOVED — use formattedReadGroup().
    See odoo-owl-components-19.md.
  </version>
</version_notes>

<examples>

  <example id="client_action" title="Client Action — full pattern v17">

```javascript
/** @odoo-module **/

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

Register the action in XML:
```xml
<record id="action_my_dashboard" model="ir.actions.client">
    <field name="name">My Dashboard</field>
    <field name="tag">my_module.my_dashboard</field>
</record>
```

Add to assets in `__manifest__.py`:
```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/components/my_dashboard/my_dashboard.js',
        'my_module/static/src/components/my_dashboard/my_dashboard.xml',
    ],
},
```

  </example>

  <example id="field_widget" title="Field Widget — pattern v17">

```javascript
/** @odoo-module **/

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

Usage in XML view:
```xml
<field name="rating" widget="star_rating"/>
```

  </example>

  <example id="patch" title="patch() — extend existing component">

```javascript
/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async beforeExecuteActionButton(clickParams) {
        if (clickParams.special === "my_special") {
            await this._myCustomCheck();
        }
        return super.beforeExecuteActionButton(clickParams);
    },

    async _myCustomCheck() {
        // custom validation
    },
});
```

  </example>

  <example id="dialog" title="Dialog component v17">

```javascript
/** @odoo-module **/

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

Invoke from another component:
```javascript
// in setup()
this.dialog = useService("dialog");

// in a method
this.dialog.add(ConfirmActionDialog, {
    title: "Confirm",
    message: "Are you sure?",
    onConfirm: () => this.doAction(),
});
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Omitting `/** @odoo-module **/` in v17 — the asset bundler will not resolve the ES module.

```javascript
// wrong in v17
import { Component } from "@odoo/owl";

// correct in v17
/** @odoo-module **/
import { Component } from "@odoo/owl";
```
  </antipattern>

  <antipattern severity="CRITICAL">
    Importing OWL from legacy paths — removed since v16.

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
async loadData() {
    const orm = this.env.services.orm;
}

// correct
setup() {
    this.orm = useService("orm");
}
```
  </antipattern>

  <antipattern severity="HIGH">
    Loading data inside `onMounted` — not awaited during render; use `onWillStart` for data
    that must be ready before the first render.

```javascript
// wrong — may cause empty content flash
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
    Mutating a Set/Map in-place — in OWL 2.x (v17/v18) in-place mutation does not
    trigger a re-render; reassign the collection.

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