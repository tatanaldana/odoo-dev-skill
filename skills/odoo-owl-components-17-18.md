# Odoo OWL Migration Guide: 17.0 → 18.0

<pattern>

<description>
OWL migration guide from v17 to v18. OWL remains 2.x — no breaking changes
in the component API. Changes are in JS infrastructure: @odoo-module stops
being required, the ORM constructor changes, and new options are added to
existing services.
</description>

<version_notes>
  <version id="17">
    @odoo-module REQUIRED. ORM constructor: ORM(rpc, user).
    notification has no autocloseDelay. registry has no addValidation().
  </version>
  <version id="18">
    @odoo-module optional. ORM constructor: ORM() — imports rpc/user at module level.
    notification gains autocloseDelay (ms, default 4000).
    registry.category().addValidation(schema) available.
    New "company" service with currentCompany and allowedCompanyIds.
  </version>
</version_notes>

<examples>

  <example id="no_breaking_changes" title="v17 components work in v18 without modification">

v17 OWL components are 100% compatible with v18. There are no breaking changes
in the Component API, useState, lifecycle hooks, static props, or registry registration.

The @odoo-module pragma still works in v18 even though it is no longer mandatory.
Keeping it causes no problems and maintains v17 compatibility.

  </example>

  <example id="odoo_module_pragma" title="@odoo-module: from REQUIRED to optional">

```javascript
// v17 — REQUIRED, omitting it breaks module loading
/** @odoo-module **/
import { Component } from "@odoo/owl";

// v18 — optional, Odoo 18 detects ES modules automatically
import { Component } from "@odoo/owl";

// v18 — also valid, maintains v17 compatibility
/** @odoo-module **/
import { Component } from "@odoo/owl";
```

Keep `/** @odoo-module **/` in files that must also run on v17.
Only omit it in modules exclusively targeting v18+.

  </example>

  <example id="notification_autoclose" title="notification.add() — new autocloseDelay in v18">

```javascript
// v17 — fixed 4000ms hardcoded, not configurable
this.notification.add("Saved", { type: "success" });
this.notification.add("Warning", { type: "warning", sticky: true });

// v18 — autocloseDelay configurable (milliseconds)
this.notification.add("Saved", {
    type: "success",
    autocloseDelay: 2000,
});

this.notification.add("Long message", {
    type: "info",
    autocloseDelay: 10000,
});

// Available in both versions: title, type, sticky, className, onClose, buttons
// autocloseDelay: v18+ only
```

  </example>

  <example id="company_service" title="company service — new in v18">

```javascript
// v17 — access company data from user service or session
setup() {
    this.user = useService("user");
    // this.user.context.allowed_company_ids
}

// v18 — new company service
setup() {
    this.company = useService("company");
    // this.company.currentCompany      → { id, name, ... }
    // this.company.allowedCompanies    → [{ id, name }, ...]
    // this.company.allowedCompanyIds   → [1, 2, ...]
}
```

  </example>

  <example id="registry_validation" title="registry.addValidation() — new in v18">

```javascript
// v18 — validate entry schema for a registry category
const fieldsRegistry = registry.category("fields");

fieldsRegistry.addValidation({
    component: { validate: (val) => typeof val === "function" },
    supportedTypes: { optional: true },
    extractProps: { optional: true },
    isEmpty: { optional: true },
});

// v17 — addValidation does not exist, registry accepts any value
```

  </example>

</examples>

<antipatterns>

  <antipattern severity="HIGH">
    Omitting @odoo-module in a module that must also run on v17.

```javascript
// wrong for shared v17/v18 modules
import { Component } from "@odoo/owl";  // breaks in v17

// correct for shared modules
/** @odoo-module **/
import { Component } from "@odoo/owl";  // works in v17 and v18
```
  </antipattern>

  <antipattern severity="MEDIUM">
    Using autocloseDelay option in code targeting v17 — the option is silently ignored.

```javascript
// wrong when targeting v17
this.notification.add("msg", { autocloseDelay: 2000 });

// correct for v17 — use default 4000ms or sticky
this.notification.add("msg", { type: "success" });
```
  </antipattern>

</antipatterns>

</pattern>