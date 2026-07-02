# portal-access-patterns.md

<pattern>

<description>
Patterns for exposing Odoo models in the customer portal. Covers the full
stack: portal.mixin on the model, CustomerPortal controller routes, portal home
registration, and QWeb templates using portal_layout / pager / breadcrumbs.
Also covers website public routes (auth='public') with request.render().

Use this file when:
- Adding a custom model to the portal (/my/... routes)
- Implementing document detail pages with access_token security
- Registering a section on the portal home (/my/home)
- Building public-facing routes with auth='public'
</description>

<version_notes>
<version id="17">
- portal.mixin._get_access_action uses check_access_rights + check_access_rule (two calls)
- _get_share_url does NOT call check_access before generating token
- portal_layout frontend_layout uses _lang_get_direction()
- language_selector uses `languages` list of tuples: [(code, url_code, name), ...]
- pager prev/next icons: fa fa-chevron-left / fa fa-chevron-right
- portal_my_home: only Connection & Security card in portal_common_category
- user_dropdown wrapped in t-nocache block
</version>
<version id="18">
- portal.mixin._get_access_action uses unified check_access('read') — single call
- _get_share_url adds self.check_access('read') before _portal_ensure_token()
- frontend_layout uses _get_data(code=request.env.lang).direction
- language_selector uses `frontend_languages` dict keyed by lang code
- portal_layout container adds pb-5 to inner div
- portal_record_sidebar: changed to d-flex wrapper with vr divider
- portal_searchbar buttons: btn-secondary → btn-light
- portal_my_home: removes o_portal_doc_spinner placeholder
- portal_my_details_fields: adds street2 field, reorders zip/state
- user_dropdown: keeps t-nocache block
</version>
<version id="19">
- Same as v18 for portal.mixin (check_access, _get_share_url)
- frontend_layout: removes t-cache from nav block; adds Skip to Content link
- language_selector: drops t-nocache; uses frontend_languages dict (same as v18)
- pager: adds ellipsis support — page['num'] can be '…' string, rendered as disabled
- pager prev/next icons: oi oi-chevron-left / oi oi-chevron-right
- portal_my_home: adds Addresses card before Connection & Security; moves spinner after docs
- user_dropdown: drops t-nocache entirely
- portal_breadcrumbs: adds my_addresses and address_form page_name cases
- portal_my_contact: new template for contact block in document sidebar
- http controller adds: werkzeug.exceptions.Forbidden, clean_context, str2bool, LazyTranslate
- Backend link href: /web → /odoo in user_dropdown
</version>
</version_notes>

<examples>

<example id="mixin-inherit" title="Adding portal.mixin to a custom model">
```python
# models/my_document.py
from odoo import fields, models

class MyDocument(models.Model):
    _name = 'my.document'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'My Document'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')

    def _compute_access_url(self):
        """Override to define the portal URL for this model."""
        super()._compute_access_url()
        for record in self:
            record.access_url = '/my/documents/%s' % record.id
```
</example>

<example id="portal-ensure-token" title="access_token field and _portal_ensure_token">
```python
# portal.mixin provides these automatically — do not redefine:
#   access_token = fields.Char('Security Token', copy=False)
#   access_url   = fields.Char(compute='_compute_access_url')

# To get or lazily generate a token:
token = record._portal_ensure_token()
# If access_token is empty, writes str(uuid.uuid4()) via sudo().write()
# Returns the existing or newly created token string.

# To build a full portal URL with token:
url = record.get_portal_url()
# Returns: /my/documents/42?access_token=<uuid>&...

# get_portal_url optional kwargs:
url = record.get_portal_url(
    suffix='/print',          # appended before query string
    report_type='pdf',        # adds &report_type=pdf
    download=True,            # adds &download=true
    query_string='&foo=bar',  # extra query params
    anchor='section1',        # adds #section1
)
```
</example>

<example id="portal-home-registration" title="Registering a section on the portal home">
```python
# controllers/portal.py
from odoo.addons.portal.controllers.portal import CustomerPortal

class MyPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'my_document_count' in counters:
            values['my_document_count'] = (
                request.env['my.document'].search_count([])
                if request.env['my.document'].check_access_rights('read', raise_exception=False)
                else 0
            )
        return values
```
</example>

<example id="portal-list-route" title="Portal document list route with pager">
```python
# controllers/portal.py
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class MyPortal(CustomerPortal):

    @http.route(['/my/documents', '/my/documents/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_my_documents(self, page=1, sortby=None, **kw):
        MyDocument = request.env['my.document']

        searchbar_sortings = {
            'date': {'label': 'Newest', 'order': 'create_date desc'},
            'name': {'label': 'Name', 'order': 'name asc'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        document_count = MyDocument.search_count([])
        pager = portal_pager(
            url='/my/documents',
            url_args={'sortby': sortby},
            total=document_count,
            page=page,
            step=self._items_per_page,
        )

        documents = MyDocument.search(
            [], order=order,
            limit=self._items_per_page,
            offset=pager['offset'],
        )

        return request.render('my_module.portal_my_documents', {
            'documents': documents,
            'page_name': 'my_documents',
            'pager': pager,
            'default_url': '/my/documents',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
```
</example>

<example id="portal-detail-route" title="Portal document detail route with access_token">
```python
# controllers/portal.py
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError

class MyPortal(CustomerPortal):

    @http.route('/my/documents/<int:doc_id>',
                type='http', auth='public', website=True)
    def portal_my_document_detail(self, doc_id, access_token=None, **kw):
        try:
            document_sudo = self._document_check_access(
                'my.document', doc_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._prepare_portal_layout_values()
        values.update({
            'document': document_sudo,
            'page_name': 'my_document',
            'access_token': access_token,
        })
        return request.render('my_module.portal_my_document', values)
```
</example>

<example id="document-check-access" title="_document_check_access — how it works">
```python
# Inherited from CustomerPortal — do NOT reimplement.
# Signature (identical v17/18/19):
#   _document_check_access(self, model_name, document_id, access_token=None)
#
# What it does internally:
#   1. document = env[model_name].browse(document_id)
#   2. document.check_access_rights('read')
#   3. document.check_access_rule('read')
#   4. if access_token: consteq(document.sudo().access_token, access_token)
#      — raises AccessError if token mismatch
#   5. Returns document.sudo() if access_token provided, else document
#
# Call pattern:
try:
    doc_sudo = self._document_check_access('my.document', doc_id, access_token)
except (AccessError, MissingError):
    return request.redirect('/my')
```
</example>

<example id="portal-layout-template" title="QWeb template using portal_layout">
```xml
<!-- views/portal_templates.xml -->
<odoo>
    <!-- Document list page -->
    <template id="portal_my_documents" name="My Documents">
        <t t-call="portal.portal_layout">
            <t t-set="breadcrumbs_searchbar" t-value="True"/>
            <t t-call="portal.portal_searchbar">
                <t t-set="title">My Documents</t>
            </t>
            <t t-if="not documents">
                <div class="alert alert-warning">No documents found.</div>
            </t>
            <t t-if="documents">
                <t t-call="portal.portal_table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <t t-foreach="documents" t-as="doc">
                            <tr>
                                <td><a t-att-href="doc.get_portal_url()" t-field="doc.name"/></td>
                                <td><span t-field="doc.create_date"/></td>
                                <td><span t-field="doc.state"/></td>
                            </tr>
                        </t>
                    </tbody>
                </t>
            </t>
        </t>
    </template>

    <!-- Document detail page -->
    <template id="portal_my_document" name="My Document Detail">
        <t t-call="portal.portal_layout">
            <t t-set="o_portal_fullwidth_alert" groups="account.group_account_manager">
                <t t-call="portal.portal_back_in_edit_mode">
                    <t t-set="backend_url"
                       t-value="'/odoo/my-documents/%s' % document.id"/>
                </t>
            </t>
            <div id="wrap" class="o_portal_wrap">
                <div class="container">
                    <div class="row">
                        <div class="col-12">
                            <h2 t-field="document.name"/>
                            <p>Status: <span t-field="document.state"/></p>
                        </div>
                    </div>
                </div>
            </div>
        </t>
    </template>
</odoo>
```
</example>

<example id="portal-home-template" title="Registering a portal home section in QWeb">
```xml
<!-- views/portal_templates.xml -->
<odoo>
    <template id="portal_my_documents_entry"
              name="Portal My Documents"
              inherit_id="portal.portal_my_home">
        <xpath expr="//div[@id='portal_client_category']" position="before">
            <t t-call="portal.portal_docs_entry">
                <t t-set="title">My Documents</t>
                <t t-set="url" t-value="'/my/documents'"/>
                <t t-set="placeholder_count" t-value="'my_document_count'"/>
            </t>
        </xpath>
    </template>
</odoo>
```
</example>

<example id="portal-breadcrumbs" title="Portal breadcrumbs — page_name variable">
```xml
<!-- portal_breadcrumbs renders based on page_name variable.
     page_name='home' → no breadcrumbs rendered.
     Custom page_name → shows Home > (your label) if you extend the template.

     To add a custom breadcrumb entry, inherit portal_breadcrumbs: -->
<template id="portal_breadcrumbs_my_doc"
          inherit_id="portal.portal_breadcrumbs">
    <xpath expr="//ol" position="inside">
        <li t-if="page_name == 'my_documents'"
            class="breadcrumb-item active">
            My Documents
        </li>
        <li t-if="page_name == 'my_document'"
            class="breadcrumb-item">
            <a href="/my/documents">My Documents</a>
        </li>
        <li t-if="page_name == 'my_document'"
            class="breadcrumb-item active"
            t-field="document.name"/>
    </xpath>
</template>
```
</example>

<example id="pager-template" title="Pager dict structure and portal.pager template">
```python
# pager dict keys (produced by portal_pager() helper):
# {
#   'page_count': int,
#   'offset': int,             # use as search() offset
#   'page': {'num': int, 'url': str},
#   'page_previous': {'num': int, 'url': str},
#   'page_next': {'num': int, 'url': str},
#   'pages': [{'num': int|'…', 'url': str}, ...],
#             # v19: pages list may include {'num': '…', 'url': None} for ellipsis
# }

# In the template, render via portal_table (includes pager automatically):
#   <t t-call="portal.portal_table">...</t>
#
# Or render pager standalone:
#   <t t-call="portal.pager"/>
# (requires `pager` variable in context)
```
</example>

<example id="auth-public-route" title="Public route with auth='public' and request.render">
```python
# controllers/portal.py
from odoo import http
from odoo.http import request

class MyPublicController(http.Controller):

    @http.route('/share/<string:token>',
                type='http', auth='public', website=True)
    def shared_document(self, token, **kw):
        Document = request.env['my.document'].sudo()
        document = Document.search([('access_token', '=', token)], limit=1)
        if not document:
            return request.not_found()

        return request.render('my_module.shared_document_page', {
            'document': document,
            'page_name': 'shared_doc',
        })
```
</example>

<example id="v19-controller-imports" title="v19 controller additional imports">
```python
# v19 only — additional imports in portal controllers:
from werkzeug.exceptions import Forbidden
from odoo.tools import consteq, str2bool
from odoo.tools.translate import LazyTranslate
from odoo.addons.portal.controllers.portal import CustomerPortal

# LazyTranslate usage (v19):
_lt = LazyTranslate(__name__)

# clean_context usage (v19) — strips website/portal context keys
# before doing internal env operations:
# pattern — verify against your codebase
```
</example>

<example id="get-share-url" title="_get_share_url — building a shareable URL">
```python
# _get_share_url is defined on portal.mixin.
# Signature (v17/18/19):
#   _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=True)
#
# Returns: '{access_url}?access_token=<token>[&pid=N&hash=H][&signup_token=...]'
# or:      '/mail/view?model=my.document&res_id=42&access_token=...' if redirect=True
#
# v17: generates token without prior access check
# v18/v19: calls self.check_access('read') before _portal_ensure_token()

url = document._get_share_url()
url_with_partner_hash = document._get_share_url(pid=partner.id)
redirect_url = document._get_share_url(redirect=True)
```
</example>

</examples>

<antipatterns>

<antipattern severity="CRITICAL">
```python
# WRONG — redefining access_token as a compute or with a default.
# portal.mixin already defines it as a plain stored Char field.
class MyDocument(models.Model):
    _inherit = ['portal.mixin', ...]
    access_token = fields.Char(default=lambda self: str(uuid.uuid4()))  # WRONG
    access_token = fields.Char(compute='_compute_token', store=True)    # WRONG

# CORRECT — do not redefine access_token at all.
# Call _portal_ensure_token() when you need a token; it lazy-generates one.
```
</antipattern>

<antipattern severity="CRITICAL">
```python
# WRONG — comparing access_token directly without consteq.
# Timing attacks possible.
if document.sudo().access_token == access_token:   # WRONG
    ...

# CORRECT — use consteq (available in odoo.tools):
from odoo.tools import consteq
if access_token and consteq(document.sudo().access_token or '', access_token):
    ...

# OR — just delegate to _document_check_access which handles this for you.
```
</antipattern>

<antipattern severity="CRITICAL">
```python
# WRONG — using check_access_rights + check_access_rule in v18/v19 code.
# v18/v19 unified these into check_access().
record.check_access_rights('read')   # v17 style
record.check_access_rule('read')     # v17 style

# CORRECT for v18/v19:
record.check_access('read')

# CORRECT for v17 only:
record.check_access_rights('read')
record.check_access_rule('read')
```
</antipattern>

<antipattern severity="HIGH">
```python
# WRONG — forgetting to call super() in _prepare_home_portal_values.
# Other modules add their counters too; skipping super() removes them all.
def _prepare_home_portal_values(self, counters):
    return {'my_count': ...}   # WRONG — no super()

# CORRECT:
def _prepare_home_portal_values(self, counters):
    values = super()._prepare_home_portal_values(counters)
    if 'my_count' in counters:
        values['my_count'] = ...
    return values
```
</antipattern>

<antipattern severity="HIGH">
```python
# WRONG — using auth='user' on a route that should also accept access_token.
# auth='user' rejects unauthenticated requests before the controller runs.
@http.route('/my/documents/<int:doc_id>', type='http', auth='user', website=True)
def portal_detail(self, doc_id, access_token=None, **kw):
    # access_token is useless here — unauthenticated users are blocked at auth layer
    ...

# CORRECT — use auth='public' when the route must accept access_token links:
@http.route('/my/documents/<int:doc_id>', type='http', auth='public', website=True)
def portal_detail(self, doc_id, access_token=None, **kw):
    doc_sudo = self._document_check_access('my.document', doc_id, access_token)
    ...
```
</antipattern>

<antipattern severity="HIGH">
```xml
<!-- WRONG — overriding portal_my_home without using portal_docs_entry t-call.
     Manually duplicating the card HTML breaks theming and the placeholder_count JS. -->
<template inherit_id="portal.portal_my_home">
    <xpath expr="//div[@id='portal_client_category']" position="before">
        <div class="col-md-6">
            <a href="/my/documents">My Documents ({{ count }})</a>
        </div>
    </xpath>
</template>

<!-- CORRECT — always use portal_docs_entry t-call: -->
<template inherit_id="portal.portal_my_home">
    <xpath expr="//div[@id='portal_client_category']" position="before">
        <t t-call="portal.portal_docs_entry">
            <t t-set="title">My Documents</t>
            <t t-set="url" t-value="'/my/documents'"/>
            <t t-set="placeholder_count" t-value="'my_document_count'"/>
        </t>
    </xpath>
</template>
```
</antipattern>

<antipattern severity="MEDIUM">
```python
# WRONG — calling _portal_ensure_token() on a recordset with multiple records.
# ensure_one() is not called internally — generates token for all, but access_url
# construction in get_portal_url calls ensure_one() and will raise.
tokens = documents._portal_ensure_token()   # WRONG — ambiguous

# CORRECT — always on a single record:
for doc in documents:
    token = doc._portal_ensure_token()
```
</antipattern>

<antipattern severity="MEDIUM">
```python
# WRONG — using allowed_company_ids in ir.rule domain_force for portal rules.
# Portal users do not have allowed_company_ids populated.
# Use company_ids instead (decision #19).
domain_force = "[('company_id', 'in', allowed_company_ids)]"   # WRONG

# CORRECT:
domain_force = "[('company_id', 'in', company_ids)]"
```
</antipattern>

</antipatterns>

</pattern>