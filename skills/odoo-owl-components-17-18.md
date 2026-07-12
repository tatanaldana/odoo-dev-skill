# OWL Migration — v17 → v18

OWL stays 2.x. No breaking changes in component API.

## Changes

| Feature | v17 | v18 |
|---------|-----|-----|
| `@odoo-module` | REQUIRED | optional |
| ORM constructor | `ORM(rpc, user)` | `ORM()` no args |
| `notification.autocloseDelay` | not available | new (ms) |
| `registry.addValidation()` | not available | new |
| `useService("company")` | not available | new |

## Key points

- v17 components work in v18 without modification
- Keep `@odoo-module` in shared v17/v18 files
- `autocloseDelay` silently ignored in v17

```javascript
// v18 new features
this.notification.add("Saved", { type: "success", autocloseDelay: 2000 });
this.company = useService("company");  // currentCompany, allowedCompanyIds
```