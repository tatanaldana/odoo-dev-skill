# fastapi-patterns.md

<pattern>

<description>
Patterns for building custom APIs in Odoo using FastAPI via the OCA
rest-framework addon (`fastapi`). Use when the task involves exposing
an HTTP API consumed by a decoupled frontend, third-party integrations,
or another product. Do NOT use native `http.Controller` for this purpose
— FastAPI provides schema validation, automatic OpenAPI/Swagger docs,
and Pydantic typing that controllers do not.

Dependency: `OCA/rest-framework` — `fastapi` addon.
Source: https://github.com/OCA/rest-framework/tree/18.0/fastapi

Use when:
- Building a REST API consumed by a frontend or external system
- Exposing Odoo data with schema validation and auto-documentation
- Creating versioned API endpoints (/api/v1/...)
- Extending an existing OCA FastAPI app from another module
</description>

<version_notes>
<version id="17">
OCA fastapi addon available for v17 (OCA/rest-framework 17.0 branch).
Core patterns identical to v18. Use `@odoo-module` in any JS test clients.
</version>
<version id="18">
Primary reference version. OCA fastapi addon stable on 18.0 branch.
Pydantic v2 used — use `model_validate()` not `from_orm()`.
`PagedCollection.total` deprecated in favour of `count`.
</version>
<version id="19">
OCA fastapi addon expected on 19.0 branch — verify availability before use.
Pydantic v2 patterns identical to v18.
`self.env._()` for translations inside route handlers.
</version>
</version_notes>

<examples>

<example id="module-structure" title="Directory structure for a FastAPI addon">
```
my_api/
├── __init__.py
├── __manifest__.py          # depends = ['fastapi']
├── README.rst
├── models/
│   ├── __init__.py
│   └── fastapi_endpoint.py  # inherits fastapi.endpoint, registers app
├── routers/
│   ├── __init__.py          # aggregates all routers
│   ├── sale_orders.py       # routes prefixed /sale_orders
│   └── partners.py
├── schemas/
│   ├── __init__.py
│   ├── sale_order.py        # Pydantic models for sale.order
│   └── partner.py
├── dependencies.py          # custom FastAPI dependencies
├── security/
│   ├── ir.model.access.csv
│   └── security.xml         # dedicated user + group + record rules
└── views/
    └── fastapi_endpoint_views.xml
```
</example>

<example id="manifest" title="__manifest__.py for a FastAPI addon">
```python
{
    'name': 'My API',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['fastapi'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fastapi_endpoint_views.xml',
    ],
}
```
</example>

<example id="endpoint-registration" title="Registering the app on fastapi.endpoint">
```python
# models/fastapi_endpoint.py
from typing import List
from fastapi import APIRouter
from odoo import fields, models
from odoo.addons.my_api.routers import router as my_api_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("my_api", "My API")],
        ondelete={"my_api": "cascade"},
    )
    # Prefix app-specific config fields with the app name to avoid conflicts
    my_api_auth_method = fields.Selection(
        selection=[("api_key", "API Key"), ("http_basic", "HTTP Basic")],
        string="Authentication Method",
    )

    def _get_fastapi_routers(self) -> List[APIRouter]:
        if self.app == "my_api":
            return [my_api_router]
        return super()._get_fastapi_routers()

    @api.model
    def _fastapi_app_fields(self) -> List[str]:
        """Declare fields that trigger app re-instantiation when changed."""
        fields_list = super()._fastapi_app_fields()
        fields_list.append("my_api_auth_method")
        return fields_list
```
</example>

<example id="pydantic-schemas" title="Pydantic schemas — input and output models">
```python
# schemas/sale_order.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SaleOrderLine(BaseModel):
    """Output schema for a single order line."""
    product_name: str
    quantity: float
    price_unit: float
    price_subtotal: float

    model_config = ConfigDict(from_attributes=True)


class SaleOrderOut(BaseModel):
    """Output schema for a sale order."""
    id: int
    name: str
    date_order: date
    partner_name: str
    amount_total: float
    lines: list[SaleOrderLine]

    model_config = ConfigDict(from_attributes=True)


class SaleOrderCreate(BaseModel):
    """Input schema for creating a sale order."""
    partner_id: int
    date_order: Optional[date] = None
    note: Optional[str] = None
    # Never expose raw ORM fields directly — define explicit input contracts
```
</example>

<example id="router-with-pagination" title="Router with pagination using PagedCollection">
```python
# routers/sale_orders.py
from typing import Annotated
from fastapi import APIRouter, Depends
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import (
    authenticated_partner_env,
    paging,
)
from odoo.addons.fastapi.schemas import PagedCollection, Paging
from odoo.addons.my_api.schemas import SaleOrderOut

router = APIRouter(tags=["sale_orders"])


@router.get("/sale_orders", response_model=PagedCollection[SaleOrderOut])
def list_sale_orders(
    paging: Annotated[Paging, Depends(paging)],
    env: Annotated[Environment, Depends(authenticated_partner_env)],
) -> PagedCollection[SaleOrderOut]:
    """Return paginated sale orders for the authenticated partner."""
    domain = [("partner_id", "=", env.context.get("authenticated_partner_id"))]
    count = env["sale.order"].search_count(domain)
    orders = env["sale.order"].search(
        domain,
        limit=paging.limit,
        offset=paging.offset,
        order="date_order desc",
    )
    return PagedCollection[SaleOrderOut](
        count=count,
        items=[
            SaleOrderOut(
                id=o.id,
                name=o.name,
                date_order=o.date_order,
                partner_name=o.partner_id.name,
                amount_total=o.amount_total,
                lines=[
                    {
                        "product_name": l.product_id.name,
                        "quantity": l.product_uom_qty,
                        "price_unit": l.price_unit,
                        "price_subtotal": l.price_subtotal,
                    }
                    for l in o.order_line
                ],
            )
            for o in orders
        ],
    )
```
</example>

<example id="business-logic-delegation" title="Delegating business logic to an abstract model">
```python
# routers/sale_orders.py — route handler is thin, delegates to model
from typing import Annotated
from fastapi import APIRouter, Depends
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import authenticated_partner_env
from odoo.addons.my_api.schemas import SaleOrderCreate, SaleOrderOut

router = APIRouter(tags=["sale_orders"])


@router.post("/sale_orders", response_model=SaleOrderOut, status_code=201)
def create_sale_order(
    payload: SaleOrderCreate,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
) -> SaleOrderOut:
    """Create a sale order. Business logic lives in the service model."""
    order = env["my.api.sale.service"].create_order(payload)
    return SaleOrderOut.model_validate(order)


# models/my_api_sale_service.py — business logic lives here, testable independently
from odoo import models
from odoo.addons.my_api.schemas import SaleOrderCreate


class MyApiSaleService(models.AbstractModel):
    _name = "my.api.sale.service"
    _description = "My API Sale Order Service"

    def create_order(self, payload: SaleOrderCreate):
        """Create a sale order from API payload.

        :param payload: validated SaleOrderCreate schema instance.
        :return: sale.order record.
        """
        return self.env["sale.order"].create({
            "partner_id": payload.partner_id,
            "date_order": payload.date_order,
            "note": payload.note,
        })
```
</example>

<example id="authentication" title="API key authentication via dependency override">
```python
# dependencies.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.base.models.res_partner import Partner


def api_key_authenticated_partner(
    api_key: Annotated[
        str,
        Depends(APIKeyHeader(name="X-API-Key", description="User API key")),
    ],
    env: Annotated[Environment, Depends(odoo_env)],
) -> Partner:
    """Resolve the authenticated partner from an API key header."""
    user = env["res.users"].sudo().search(
        [("api_key_ids.key", "=", api_key)], limit=1
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return user.partner_id


# models/fastapi_endpoint.py — wire the override
from odoo.addons.fastapi.dependencies import authenticated_partner_impl
from odoo.addons.my_api.dependencies import api_key_authenticated_partner


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    def _get_app(self):
        app = super()._get_app()
        if self.app == "my_api":
            app.dependency_overrides[authenticated_partner_impl] = (
                api_key_authenticated_partner
            )
        return app
```
</example>

<example id="security-xml" title="Security — dedicated user, group, and record rules">
```xml
<!-- security/security.xml -->
<odoo>
    <!-- Dedicated user for this API — no access rights by default -->
    <record id="my_api_user" model="res.users"
            context="{'no_reset_password': True}">
        <field name="name">My API User</field>
        <field name="login">my_api_user</field>
        <field name="groups_id" eval="[(6, 0, [])]"/>
    </record>

    <!-- Group implies FastAPI Endpoint Runner (minimum rights) -->
    <record id="my_api_group" model="res.groups">
        <field name="name">My API Group</field>
        <field name="users" eval="[(4, ref('my_api_user'))]"/>
        <field name="implied_ids"
               eval="[(4, ref('fastapi.group_fastapi_endpoint_runner'))]"/>
    </record>

    <!-- Record rule: partner can only access their own sale orders -->
    <record id="my_api_sale_order_rule" model="ir.rule">
        <field name="name">My API: own sale orders only</field>
        <field name="model_id" ref="sale.model_sale_order"/>
        <field name="domain_force">
            [('partner_id', '=', authenticated_partner_id)]
        </field>
        <field name="groups" eval="[(4, ref('my_api_group'))]"/>
    </record>
</odoo>
```

```csv
<!-- security/ir.model.access.csv -->
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_my_api,sale.order my_api,sale.model_sale_order,my_api_group,1,0,0,0
```
</example>

<example id="versioning" title="API versioning — /api/v1/ prefix">
```python
# routers/__init__.py
from fastapi import APIRouter
from odoo.addons.my_api.routers.sale_orders import router as sale_orders_router
from odoo.addons.my_api.routers.partners import router as partners_router

# All routes under /api/v1/
router = APIRouter(prefix="/api/v1")
router.include_router(sale_orders_router)
router.include_router(partners_router)

# When a breaking change is needed, create /api/v2/ — never modify v1 in production.
```
</example>

<example id="testing" title="Testing a FastAPI route with FastAPITransactionCase">
```python
# tests/test_sale_orders.py
from requests import Response
from starlette import status
from odoo.fastapi.tests.common import FastAPITransactionCase
from odoo.addons.my_api.routers import router as my_api_router


class TestSaleOrdersAPI(FastAPITransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_running_user = cls.env.ref("my_api.my_api_user")
        cls.default_fastapi_authenticated_partner = cls.env["res.partner"].create(
            {"name": "Test Partner"}
        )

    def test_list_sale_orders_empty(self):
        with self._create_test_client(router=my_api_router) as client:
            response: Response = client.get("/api/v1/sale_orders")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["items"], [])

    def test_list_sale_orders_returns_own_only(self):
        """Partner can only see their own orders — record rule enforced."""
        self.env["sale.order"].create({
            "partner_id": self.default_fastapi_authenticated_partner.id,
        })
        with self._create_test_client(router=my_api_router) as client:
            response: Response = client.get("/api/v1/sale_orders")
        self.assertEqual(response.json()["count"], 1)
```
</example>

<example id="error-response" title="Consistent error responses">
```python
# The OCA fastapi addon automatically maps Odoo exceptions to HTTP status codes:
# UserError           → 400 Bad Request
# AccessError         → 403 Forbidden
# MissingError        → 404 Not Found
# ValidationError     → 400 Bad Request

# In route handlers, raise Odoo exceptions — do not return error dicts manually:
from odoo.exceptions import UserError, MissingError
from odoo import _

@router.get("/sale_orders/{order_id}", response_model=SaleOrderOut)
def get_sale_order(
    order_id: int,
    env: Annotated[Environment, Depends(authenticated_partner_env)],
) -> SaleOrderOut:
    order = env["sale.order"].browse(order_id)
    if not order.exists():
        raise MissingError(_("Sale order not found."))
    return SaleOrderOut.model_validate(order)
```
</example>

</examples>

<antipatterns>

<antipattern severity="CRITICAL">
```python
# WRONG — using http.Controller for APIs that should use FastAPI.
# Controllers lack schema validation, auto-docs, and versioning.
class MySaleAPI(http.Controller):
    @http.route('/api/sale_orders', type='json', auth='user')
    def list_orders(self, **kwargs):
        orders = request.env['sale.order'].search([])
        return {'orders': [{'id': o.id} for o in orders]}

# CORRECT — use FastAPI + OCA fastapi addon for all custom APIs.
# Reserve http.Controller for portal pages and web client extensions only.
```
</antipattern>

<antipattern severity="CRITICAL">
```python
# WRONG — exposing raw ORM fields without a Pydantic schema.
# Couples API contract directly to internal Odoo data model.
@router.get("/sale_orders")
def list_orders(env: Annotated[Environment, Depends(odoo_env)]):
    orders = env["sale.order"].search([])
    return [o.read(['name', 'amount_total'])[0] for o in orders]

# CORRECT — always use an explicit Pydantic response_model.
@router.get("/sale_orders", response_model=list[SaleOrderOut])
def list_orders(env: Annotated[Environment, Depends(authenticated_partner_env)]):
    ...
```
</antipattern>

<antipattern severity="CRITICAL">
```python
# WRONG — business logic inside the route handler.
# Makes the logic untestable without going through HTTP.
@router.post("/sale_orders", response_model=SaleOrderOut)
def create_order(payload: SaleOrderCreate, env: ...):
    if not env["res.partner"].browse(payload.partner_id).exists():
        raise HTTPException(status_code=400, detail="Partner not found")
    order = env["sale.order"].create({...})
    order.action_confirm()
    self.env["account.move"]._generate_from_sale(order)
    return SaleOrderOut.model_validate(order)

# CORRECT — delegate to an abstract model, test the model independently.
@router.post("/sale_orders", response_model=SaleOrderOut)
def create_order(payload: SaleOrderCreate, env: ...):
    order = env["my.api.sale.service"].create_and_confirm(payload)
    return SaleOrderOut.model_validate(order)
```
</antipattern>

<antipattern severity="CRITICAL">
```python
# WRONG — modifying an existing v1 route contract in production.
# Breaks all existing clients silently.
@router.get("/api/v1/sale_orders", response_model=SaleOrderOutV2)  # changed schema
def list_orders(...):
    ...

# CORRECT — create /api/v2/ for breaking changes, keep /api/v1/ unchanged.
@router.get("/api/v2/sale_orders", response_model=SaleOrderOutV2)
def list_orders_v2(...):
    ...
```
</antipattern>

<antipattern severity="HIGH">
```python
# WRONG — adding a route directly to an existing addon's router.
# The route is added unconditionally to all databases, even those
# where your new addon is not installed.
from odoo.addons.other_api.routers import existing_router

@existing_router.get("/new_route")
def new_route(...):
    ...

# CORRECT — define a new router in your addon and add it via
# _get_fastapi_routers(), guarded by self.app check.
class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    def _get_fastapi_routers(self):
        routers = super()._get_fastapi_routers()
        if self.app == "other_api":
            routers.append(my_additional_router)
        return routers
```
</antipattern>

<antipattern severity="HIGH">
```python
# WRONG — no pagination on list endpoints.
# Drains server resources on large datasets.
@router.get("/sale_orders", response_model=list[SaleOrderOut])
def list_orders(env: ...):
    return env["sale.order"].search([])  # unbounded search

# CORRECT — always paginate with PagedCollection and the paging dependency.
@router.get("/sale_orders", response_model=PagedCollection[SaleOrderOut])
def list_orders(
    paging: Annotated[Paging, Depends(paging)],
    env: ...,
):
    count = env["sale.order"].search_count([])
    orders = env["sale.order"].search([], limit=paging.limit, offset=paging.offset)
    return PagedCollection[SaleOrderOut](count=count, items=[...])
```
</antipattern>

<antipattern severity="HIGH">
```python
# WRONG — no dedicated security user/group for the API.
# Using the public user or an admin user exposes all data.
# endpoint.user_id = env.ref('base.user_admin')  # never do this

# CORRECT — create a dedicated user with no rights, a group that implies
# group_fastapi_endpoint_runner, and explicit ir.model.access + ir.rule
# for every model the API needs to access.
# See the security XML example above.
```
</antipattern>

<antipattern severity="MEDIUM">
```python
# WRONG — using Odoo field names directly in the JSON schema.
# Couples client to internal naming; 'order_line' is confusing.
class SaleOrderOut(BaseModel):
    order_line: list[SaleOrderLineOut]  # internal Odoo name leaked

# CORRECT — use descriptive, API-facing names.
class SaleOrderOut(BaseModel):
    lines: list[SaleOrderLineOut]  # clean API name
```
</antipattern>

</antipatterns>

</pattern>