# OWL Components — Version Dispatcher

Route to version-specific file. Do NOT generate code from this file.

| Target | File |
|--------|------|
| v17 | `odoo-owl-components-17.md` |
| v18 | `odoo-owl-components-18.md` |
| v19 | `odoo-owl-components-19.md` |
| v17→v18 | `odoo-owl-components-17-18.md` |
| v18→v19 | `odoo-owl-components-18-19.md` |

## Component type routing

| Use case | Registry |
|----------|----------|
| Full page / dashboard | `registry.category("actions").add(tag, Component)` |
| Custom field | `registry.category("fields").add(name, { component, supportedTypes })` |
| Extend existing | `patch()` — no registry |
| Systray | `registry.category("systray").add(name, { Component })` |
| Main UI | `registry.category("main_components").add(name, { Component })` |

## Key differences

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| `@odoo-module` | REQUIRED | optional | optional |
| ORM constructor | `ORM(rpc, user)` | `ORM()` | `ORM()` |
| `readGroup()` | ✅ | ✅ | REMOVED → `formattedReadGroup()` |
| `autocloseDelay` | ❌ | ✅ | ✅ |
| `company` service | ❌ | ✅ | ✅ |
| OWL version | 2.x | 2.x | 2.x (NOT 3.x) |