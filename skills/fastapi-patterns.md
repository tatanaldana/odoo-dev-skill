# FastAPI Patterns — OCA rest-framework

Patterns for custom APIs via OCA `fastapi` addon.
Dependency: `OCA/rest-framework` — `fastapi` addon. Verified against the
real `fastapi` addon source, v19.0.1.3.0 (`addons/oca/fastapi`).

---

## Version notes

| | v17 | v18 | v19 |
|--|-----|-----|-----|
| Branch | OCA 17.0 | OCA 18.0 (primary ref) | verify availability |
| Pydantic | v2 | v2 | v2 |
| `PagedCollection.total` | field | **not removed** — kept as a deprecated computed property (`@computed_field` getter + a setter that warns and writes to `count`); `count` is the real field, `total` is a read/write compat shim | same as v18 |
| `odoo.addons.fastapi.depends` | n/a | n/a | deprecated shim — `import *` from `.dependencies` with a `DeprecationWarning`. Import from `odoo.addons.fastapi.dependencies`, not `.depends` |

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

`authenticated_partner`/`authenticated_partner_env` (used under
"Security" below) resolve to a base implementation that provides no
partner by default — the addon's own docstring is explicit that
`authenticated_partner_impl` "has to be overridden when you create your
fastapi app". Wire your actual auth mechanism (JWT, API key, HTTP Basic,
`fastapi_auth_jwt`...) by overriding it in `_get_app()`:

```python
    from odoo.addons.fastapi.dependencies import authenticated_partner_impl
    from .dependencies import my_api_authenticated_partner_impl

    def _get_app(self):
        app = super()._get_app()
        if self.app == "my_api":
            app.dependency_overrides[authenticated_partner_impl] = (
                my_api_authenticated_partner_impl
            )
        return app
```

---

## Pydantic schemas

Don't hand-roll a paging/collection wrapper — the `fastapi` addon already
ships a generic one in `odoo.addons.fastapi.schemas`: `PagedCollection[T]`
(a `count` + `items: list[T]` pair, with `total` kept as a deprecated
read/write alias for `count`) and `Paging` (`limit`/`offset`). Reuse them.

```python
# schemas/sale_order.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date

class SaleOrderOut(BaseModel):
    # from_attributes=True lets model_validate() read straight off the
    # recordset (o.id, o.name, ...) instead of listing every kwarg by hand.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    # sale.order has no "partner_name" attribute — validation_alias tells
    # model_validate() to read `order.partner_id` (the Many2one recordset)
    # into this field, and the validator below flattens it to `.name`.
    # A plain `from_attributes=True` getattr("partner_name", ...) would
    # raise AttributeError without the alias.
    partner_name: str = Field(validation_alias="partner_id")
    date_order: date
    amount_total: float
    state: str

    @field_validator("partner_name", mode="before")
    @classmethod
    def _flatten_partner(cls, v):
        return v.name if hasattr(v, "name") else v

class SaleOrderSearch(BaseModel):
    state: str | None = None
    partner_id: int | None = None
```

---

## Router with Odoo env

`paging` and `PagedCollection` come from the addon itself
(`odoo.addons.fastapi.dependencies` / `.schemas`) — don't redeclare
`limit`/`offset` on your own search schema.

```python
# routers/sale_orders.py
from typing import Annotated
from fastapi import APIRouter, Depends
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env, paging
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from ..schemas.sale_order import SaleOrderOut, SaleOrderSearch

router = APIRouter(tags=["sale_orders"])

@router.get(
    "/sale_orders",
    response_model=PagedCollection[SaleOrderOut],
    response_model_exclude_unset=True,
)
def list_orders(
    env: Annotated[Environment, Depends(odoo_env)],
    search: Annotated[SaleOrderSearch, Depends()],
    paging: Annotated[Paging, Depends(paging)],
) -> PagedCollection[SaleOrderOut]:
    domain = []
    if search.state:
        domain.append(("state", "=", search.state))
    if search.partner_id:
        domain.append(("partner_id", "=", search.partner_id))

    count = env["sale.order"].search_count(domain)
    orders = env["sale.order"].search(domain, limit=paging.limit, offset=paging.offset)
    return PagedCollection[SaleOrderOut](
        count=count,
        items=[SaleOrderOut.model_validate(o) for o in orders],
    )
```

`env` here is scoped to the `fastapi.endpoint`'s configured user (default:
public user) — `search()`/`browse()`/`read()` already go through that
user's ACL + `ir.rule`. For a single-record-by-id endpoint you almost
always want per-caller scoping instead of one shared user — see the
`get_order` example under "Security" below, which uses
`authenticated_partner_env` instead of plain `odoo_env`.

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

The addon's own recommended pattern (`readme/USAGE.md` → "Managing
security into the route handlers") is **ACL + `ir.rule`, not manual
`check_access()` calls in the handler**: give the endpoint's run-as user
*no* access rights of its own, add it to a dedicated group that implies
`group_fastapi_endpoint_runner` (minimal rights to authenticate), grant
that group read access per model via `ir.model.access`, and scope the
actual per-caller visibility with an `ir.rule` domain using
`authenticated_partner_id` — a context key the addon injects for you once
a handler depends on `authenticated_partner`/`authenticated_partner_env`.
The ORM then enforces the rule automatically on every `browse()`/`read()`
— no explicit check needed in the route.

**Caveat found while verifying this against OCA's own docs:** the XML
snippet in `readme/USAGE.md` itself is stale — it still shows
`<field name="groups_id" eval="[(6, 0, [])]"/>` and
`<field name="users" eval="[...]"/>` on `res.groups`, which are the
pre-v19 field names. The addon's actual demo file
(`demo/fastapi_endpoint_demo.xml`) already uses the correct v19 names
(`group_ids` on `res.users`, `user_ids` on `res.groups`) with an explicit
comment noting the rename. Use the v19 names below — don't copy the
`readme/USAGE.md` snippet verbatim on v19.

```xml
<record id="group_my_api_runner" model="res.groups">
    <field name="name">My API Runner</field>
    <field name="implied_ids" eval="[(4, ref('fastapi.group_fastapi_endpoint_runner'))]"/>
</record>

<!-- run-as user: no access rights beyond what the runner group implies -->
<record id="user_my_api" model="res.users" context="{'no_reset_password': True}">
    <field name="name">My API Service Account</field>
    <field name="login">my_api_service</field>
    <field name="group_ids" eval="[(6, 0, [ref('group_my_api_runner')])]"/>
</record>

<!-- read access to the model for that group -->
<record id="access_sale_order_my_api" model="ir.model.access">
    <field name="name">My API: read sale.order</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="group_id" ref="group_my_api_runner"/>
    <field name="perm_read" eval="True"/>
</record>

<!-- scope visibility to the authenticated caller's own orders -->
<record id="rule_sale_order_my_api" model="ir.rule">
    <field name="name">My API: own sale orders only</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="domain_force">[('partner_id', '=', authenticated_partner_id)]</field>
    <field name="groups" eval="[(4, ref('group_my_api_runner'))]"/>
</record>
```

```python
# router — force authentication by depending on authenticated_partner_env
from odoo.addons.fastapi.dependencies import authenticated_partner_env

@router.get("/sale_orders/{order_id}", response_model=SaleOrderOut)
def get_order(
    order_id: int,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
) -> SaleOrderOut:
    # ir.rule (authenticated_partner_id) + ir.model.access already scope
    # this — no manual check_access() needed for the common case.
    return SaleOrderOut.model_validate(env["sale.order"].browse(order_id))
```

Endpoint config in UI: Settings → Technical → FastAPI Endpoints → set app="my_api", user=user_my_api, root_path="/api/v1"

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Never use `sudo()` in routes without explicit security check first |
| CRITICAL | Don't grant the endpoint's run-as user broad access "to keep it simple" — give it only `group_fastapi_endpoint_runner` + narrow `ir.model.access`/`ir.rule`, and scope reads with `authenticated_partner_id` in the rule domain |
| HIGH | Use Pydantic `model_validate()` not `from_orm()` (Pydantic v2) |
| HIGH | Don't hand-roll a paging/collection schema — import `PagedCollection`/`Paging` from `odoo.addons.fastapi.schemas`/`.dependencies` |
| HIGH | Import from `odoo.addons.fastapi.dependencies`, not `.depends` (deprecated shim, warns) |
| MEDIUM | Don't put routes in `models/` — use `routers/` directory |
| MEDIUM | `count` is the real `PagedCollection` field; `total` still works (deprecated compat alias) but don't write new code against it |