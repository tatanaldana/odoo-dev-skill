# OWL Migration — v18 → v19

OWL stays 2.x (NOT 3.x). Component API identical to v18. Only breaking change: ORM service.

---

## Breaking: orm.readGroup() removed

```javascript
// WRONG in v19 — throws runtime error
const groups = await this.orm.readGroup("sale.order", domain, ["partner_id"], ["amount_total:sum"]);

// CORRECT in v19
const groups = await this.orm.formattedReadGroup(
    "sale.order", domain, ["partner_id"], ["amount_total:sum", "__count"]
);
// groups[i].partner_id           → [id, display_name]
// groups[i]["amount_total:sum"]  → aggregate
// groups[i]["__count"]           → count
```

**Key difference:** `formattedReadGroup` keys results by the FULL groupby spec including granularity — `groupby=["date:month"]` → key is `"date:month"`, NOT `"date"`.

## New ORM methods

| Method | Purpose |
|--------|---------|
| `orm.formattedReadGroup()` | replaces `readGroup()` |
| `orm.formattedReadGroupingSets()` | multiple dimensions in one query |
| `orm.cache({ maxAge })` | cached ORM calls |
| `orm.webSaveMulti()` | save multiple records in one call |
| `orm.webResequence()` | resequence records |

## orm.cache()

```javascript
this.cachedOrm = this.orm.cache({ maxAge: 30000 });
const products = await this.cachedOrm.searchRead("product.template", [], ["name"]);
```

## Migration checklist

1. Search `orm.readGroup` → replace with `formattedReadGroup`
2. Adjust result key access (full groupby spec, `__count` not `*_count`)
3. Everything else unchanged — Component, useState, hooks, props, registry

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | `orm.readGroup()` removed in v19 — use `formattedReadGroup()` |
| HIGH | OWL 2.x — no "OWL 3.x migration" needed |