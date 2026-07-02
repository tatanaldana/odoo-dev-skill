# Odoo OWL Components - Version Dispatcher

<pattern>

<description>
Version dispatcher for the Odoo OWL Components skill family.
Routes to the correct version-specific file before any OWL component code is generated.
Do NOT use this file to generate actual component code — load the version-specific file first.
</description>

<version_notes>
  <version id="17">
    OWL 2.x. @odoo-module REQUIRED. ORM constructor ORM(rpc, user).
    orm.readGroup() available. notification has no autocloseDelay option.
    Load: odoo-owl-components-17.md
  </version>
  <version id="18">
    OWL 2.x. @odoo-module optional. ORM constructor ORM() no args.
    notification gains autocloseDelay option. registry gains addValidation().
    New "company" service available.
    Load: odoo-owl-components-18.md
  </version>
  <version id="19">
    OWL 2.x — NOT OWL 3.x. orm.readGroup() REMOVED, use formattedReadGroup().
    New: orm.cache(), webSaveMulti(), webResequence().
    Load: odoo-owl-components-19.md
  </version>
</version_notes>

<examples>

  <example id="version_routing" title="Version-specific files">

Version-specific files:

| Target Version | OWL | File to Load |
|----------------|-----|--------------|
| Odoo 17.0 | 2.x | `odoo-owl-components-17.md` |
| Odoo 18.0 | 2.x | `odoo-owl-components-18.md` |
| Odoo 19.0 | 2.x | `odoo-owl-components-19.md` |

Migration guides:

| Migration Path | File to Load |
|----------------|--------------|
| 17.0 → 18.0 | `odoo-owl-components-17-18.md` |
| 18.0 → 19.0 | `odoo-owl-components-18-19.md` |

  </example>

  <example id="architecture_decision" title="Which component type to use">

Before loading the version file, identify the correct pattern:

| Use case | Pattern | Registry |
|----------|---------|----------|
| Full page, standalone dashboard | Client Action | `registry.category("actions").add(tag, Component)` |
| Custom field in form/list/kanban | Field Widget | `registry.category("fields").add(name, { component, supportedTypes })` |
| Extend existing Odoo component | patch() | No registry — modifies the class on import |
| Item in top bar | Systray | `registry.category("systray").add(name, { Component })` |
| Persistent root UI component | Main Component | `registry.category("main_components").add(name, { Component })` |

  </example>

  <example id="version_detection" title="Version detection from existing code">

| Code indicator | Version |
|----------------|---------|
| `/** @odoo-module **/` present and required | v17 |
| `/** @odoo-module **/` absent and works | v18+ |
| `orm.readGroup(...)` in use | v17 or v18 |
| `orm.formattedReadGroup(...)` in use | v19 |
| `orm.cache(...)` in use | v19 |
| `notification.add(..., { autocloseDelay })` | v18+ |
| `registry.category(...).addValidation(...)` | v18+ |
| `useService("company")` | v18+ |

  </example>

  <example id="version_diff" title="Critical differences by version">

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| OWL version | 2.x | 2.x | 2.x |
| @odoo-module | REQUIRED | optional | optional |
| ORM constructor | ORM(rpc, user) | ORM() no args | ORM() no args |
| orm.readGroup() | available | available | REMOVED |
| orm.formattedReadGroup() | not available | not available | new |
| orm.cache() | not available | not available | new |
| notification autocloseDelay | not available | new | available |
| registry.addValidation() | not available | new | available |
| "company" service | not available | new | available |

  </example>

  <example id="workflow" title="How to use this skill">

Step 1 — Identify the target version.
If the user does not specify, ask before generating any code:
"What Odoo version are you targeting? (17.0, 18.0, 19.0)"

Step 2 — Identify the component type (see architecture_decision example).

Step 3 — Load the correct version-specific file.

Step 4 — Apply only the patterns from the loaded file.
Never mix patterns from different versions.

  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
    Generating OWL component code without loading the version-specific file first.
    This dispatcher file does not contain generation patterns.
  </antipattern>

  <antipattern severity="CRITICAL">
    Assuming v19 uses OWL 3.x — v19 uses OWL 2.x. There is no OWL 3.x in v17/v18/v19.
  </antipattern>

  <antipattern severity="CRITICAL">
    Mixing patterns from different versions in the same generated component.
    Every generated file must use only patterns from its target version.
  </antipattern>

  <antipattern severity="HIGH">
    Proceeding with component generation without knowing the Odoo target version.
    Always ask before generating any code.
  </antipattern>

</antipatterns>

</pattern>