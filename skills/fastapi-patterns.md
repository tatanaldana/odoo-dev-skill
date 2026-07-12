# FastAPI Patterns — OCA rest-framework

Patterns for custom APIs via OCA `fastapi` addon.
Dependency: `OCA/rest-framework` — `fastapi` addon.

---

## Version notes

| | v17 | v18 | v19 |
|--|-----|-----|-----|
| Branch | OCA 17.0 | OCA 18.0 (primary ref) | verify availability |
| Pydantic | v2 | v2 | v2 |
| `PagedCollection.total` | available | deprecated → `count` | `count` |

---

## Directory structure

```
my_api/
├── __init__.py
├── __manifest__.py          # depends = ['fastapi']
├── models/
│   └── fastapi_endpoint.py  # inherits fastapi.endpoint, registers app
├── routers/
│   ├── __init__.py          # aggregates all routers
│   └── sale_orders.py
├── schemas/
│   └── sale_order.py        # Pydantic models
├── dependencies.py          # custom FastAPI dependencies
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
└── views/
    └── fastapi_endpoint_views.xml
```

---

## Endpoint registration

```python
# models/fastapi_endpoint.py
from odoo import fields, models
from odoo.addons.my_api.routers import router as my_api_router

class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app = fields.Selection(
        selection_add=[("my_api", "My API")],
        ondelete={"my_api": "cascade"},
    )

    def _get_fastapi_routers(self):
        if self.app == "my_api":
            return [my_api_router]
        return super()._get_fastapi_routers()
```

---

## Pydantic schemas

```python
# schemas/sale_order.py
from pydantic import BaseModel
from datetime import date

class SaleOrderOut(BaseModel):
    id: int
    name: str
    partner_name: str
    date_order: date
    amount_total: float
    state: str

class SaleOrderSearch(BaseModel):
    state: str | None = None
    partner_id: int | None = None
    limit: int = 20
    offset: int = 0

class PagedCollection(BaseModel):
    count: int               # v18+: use count, not total
    items: list[SaleOrderOut]
```

---

## Router with Odoo env

```python
# routers/sale_orders.py
from typing import Annotated
from fastapi import APIRouter, Depends
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from ..schemas.sale_order import SaleOrderOut, SaleOrderSearch, PagedCollection

router = APIRouter(tags=["sale_orders"])

@router.get("/sale_orders", response_model=PagedCollection)
def list_orders(
    env: Annotated[Environment, Depends(odoo_env)],
    params: Annotated[SaleOrderSearch, Depends()],
):
    domain = []
    if params.state:
        domain.append(("state", "=", params.state))
    if params.partner_id:
        domain.append(("partner_id", "=", params.partner_id))

    count = env["sale.order"].search_count(domain)
    orders = env["sale.order"].search(domain, limit=params.limit, offset=params.offset)
    return PagedCollection(
        count=count,
        items=[SaleOrderOut(
            id=o.id, name=o.name, partner_name=o.partner_id.name,
            date_order=o.date_order, amount_total=o.amount_total, state=o.state,
        ) for o in orders],
    )

@router.get("/sale_orders/{order_id}", response_model=SaleOrderOut)
def get_order(
    order_id: int,
    env: Annotated[Environment, Depends(odoo_env)],
):
    order = env["sale.order"].browse(order_id)
    order.check_access("read")
    return SaleOrderOut(
        id=order.id, name=order.name, partner_name=order.partner_id.name,
        date_order=order.date_order, amount_total=order.amount_total, state=order.state,
    )
```

---

## Router aggregation

```python
# routers/__init__.py
from fastapi import APIRouter
from .sale_orders import router as sale_orders_router

router = APIRouter()
router.include_router(sale_orders_router, prefix="/sale_orders")
```

---

## Security

```xml
<!-- Dedicated group for API access -->
<record id="group_api_user" model="res.groups">
    <field name="name">API User</field>
</record>

<!-- Dedicated user for API auth -->
<record id="user_api" model="res.users">
    <field name="name">API Service Account</field>
    <field name="login">api@example.com</field>
    <field name="groups_id" eval="[(4, ref('group_api_user'))]"/>
</record>
```

Endpoint config in UI: Settings → Technical → FastAPI Endpoints → set app="my_api", user=api user, root_path="/api/v1"

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Never skip `check_access('read')` on single-record endpoints |
| CRITICAL | Never use `sudo()` in routes without explicit security check first |
| HIGH | Use Pydantic `model_validate()` not `from_orm()` (Pydantic v2) |
| HIGH | Use `count` not `total` in PagedCollection (v18+) |
| MEDIUM | Don't put routes in `models/` — use `routers/` directory |