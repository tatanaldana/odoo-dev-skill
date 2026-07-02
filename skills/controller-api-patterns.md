<pattern>

<description>
HTTP controller patterns for Odoo: defining routes with @http.route(), JSON vs HTTP endpoints,
auth levels, request handling, portal controllers, and rendering QWeb responses.
Verified against http_controller_17/18/19.py (portal.CustomerPortal pattern).
</description>

<version_notes>
  <version id="17">
    Imports: `from odoo import http, tools, _, SUPERUSER_ID`
    `from odoo.http import content_disposition, Controller, request, route`
    `base64` and `json` imports present in portal controller.
    `request.update_context()` for updating request context.
    `document.check_access_rights('read')` + `document.check_access_rule('read')` for access checks.
  </version>
  <version id="18">
    Imports simplified: `base64` and `json` removed from portal controller (moved elsewhere).
    Otherwise identical to v17.
  </version>
  <version id="19">
    New imports: `from werkzeug.exceptions import Forbidden`
    `from odoo.tools import clean_context, consteq, single_email_re, str2bool`
    `from odoo.tools.translate import LazyTranslate` — `_lt = LazyTranslate(__name__)` for lazy translation.
    `json` re-added for specific routes.
    Route syntax and `@http.route` decorator unchanged across all versions.
    Access check pattern (`check_access_rights` + `check_access_rule`) unchanged in v19 portal code.
    Note: `has_access()` is a test helper introduced in v18, not a controller pattern.
  </version>
</version_notes>

<examples>

  <example id="basic_controller" title="Basic controller structure (v17/v18/v19)">
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my_module/hello', type='http', auth='public')
    def hello(self):
        """Simple public endpoint returning plain text."""
        return "Hello, World!"

    @http.route('/my_module/data', type='json', auth='user')
    def get_data(self):
        """JSON endpoint requiring user authentication.
        type='json': request body and response are JSON; no explicit return serialization needed.
        """
        records = request.env['my.model'].search([])
        return {
            'status': 'success',
            'count': len(records),
            'data': records.read(['id', 'name', 'state']),
        }

    @http.route('/my_module/public_data', type='json', auth='none')
    def public_data(self):
        """Endpoint accessible without any authentication."""
        return {'version': '1.0'}
```
  </example>

  <example id="portal_controller" title="Portal controller — CustomerPortal pattern (verified v17/v18/v19)">
```python
# Verified against http_controller_17/18/19.py
from odoo import http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import Controller, request, route
from odoo.tools import consteq


class CustomerPortal(Controller):

    @route(['/my', '/my/home'], type='http', auth='user', website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render('portal.portal_my_home', values)

    @route(['/my/counters'], type='json', auth='user', website=True)
    def counters(self, counters, **kw):
        return self._prepare_home_portal_values(counters)

    def _prepare_portal_layout_values(self):
        """Base values for portal pages."""
        return {'page_name': 'home'}

    def _prepare_home_portal_values(self, counters):
        """Override to add record counts for portal badges."""
        return {}

    def _document_check_access(self, model_name, document_id, access_token=None):
        """Check access to a specific record, optionally via access token.
        Returns sudoed record if access granted; raises AccessError or MissingError.
        Verified: pattern identical in v17/v18/v19.
        """
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if (
                not access_token
                or not document_sudo.access_token
                or not consteq(document_sudo.access_token, access_token)
            ):
                raise
        return document_sudo
```
  </example>

  <example id="http_route_types" title="Route type and auth combinations">
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    # type='http' — returns HTML response, renders QWeb templates
    @http.route('/my/page', type='http', auth='user', website=True)
    def my_page(self, **kw):
        values = {'records': request.env['my.model'].search([])}
        return request.render('my_module.portal_my_page', values)

    # type='json' — body/response as JSON; auth='user' requires login
    @http.route('/api/data', type='json', auth='user')
    def api_data(self, model, domain=None, **kw):
        domain = domain or []
        records = request.env[model].search(domain)
        return records.read(['id', 'name'])

    # auth='public' — logged-in users AND public user; website portal pages
    @http.route('/public/info', type='http', auth='public', website=True)
    def public_info(self):
        return request.render('my_module.public_info_template', {})

    # auth='none' — no env setup; used for raw endpoints, healthchecks
    @http.route('/health', type='http', auth='none')
    def health(self):
        return request.make_response('OK', headers=[('Content-Type', 'text/plain')])

    # Multi-route with wildcard
    @http.route([
        '/orders',
        '/orders/page/<int:page>',
    ], type='http', auth='user', website=True)
    def orders_list(self, page=1, **kw):
        per_page = 20
        orders = request.env['sale.order'].search(
            [], limit=per_page, offset=(page - 1) * per_page
        )
        return request.render('my_module.orders_list', {'orders': orders, 'page': page})
```
  </example>

  <example id="report_render_controller" title="Rendering reports from controller (verified pattern)">
```python
# Verified: _show_report pattern from http_controller_17.py
import re
from odoo import http
from odoo.http import content_disposition, request


class MyController(http.Controller):

    @http.route('/my/report/<int:document_id>', type='http', auth='user')
    def download_report(self, document_id, report_type='pdf', download=False, **kw):
        document = request.env['my.model'].browse(document_id)
        document.check_access_rights('read')
        document.check_access_rule('read')
        return self._show_report(
            model=document,
            report_type=report_type,
            report_ref='my_module.action_report_my_model',
            download=download,
        )

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            from odoo.exceptions import UserError
            raise UserError('Invalid report type: %s' % report_type)

        ReportAction = request.env['ir.actions.report'].sudo()
        if hasattr(model, 'company_id') and len(model.company_id) == 1:
            ReportAction = ReportAction.with_company(model.company_id)

        method_name = '_render_qweb_%s' % report_type
        report = getattr(ReportAction, method_name)(
            report_ref, list(model.ids), data={'report_type': report_type}
        )[0]

        headers = {
            'Content-Type': 'application/pdf' if report_type == 'pdf' else 'text/html',
            'Content-Length': len(report),
        }
        if report_type == 'pdf':
            filename = '%s.pdf' % re.sub(r'\W+', '-', model._get_report_base_filename())
            headers['Content-Disposition'] = content_disposition(
                filename,
                disposition_type='attachment' if download else 'inline',
            )
        return request.make_response(report, headers=list(headers.items()))
```
  </example>

  <example id="request_context" title="Working with request context and environment">
```python
from odoo import http
from odoo.http import request


class MyController(http.Controller):

    @http.route('/my/action', type='json', auth='user')
    def my_action(self, record_id, **kw):
        # Access current user
        user = request.env.user
        company = request.env.company

        # Update request context
        request.update_context(my_context_key='value')

        # Use sudo for privilege escalation with explicit re-check
        record = request.env['my.model'].sudo().browse(record_id)

        # Read session data
        session_key = request.session.get('my_session_key', default_value=[])

        return {'user': user.name, 'company': company.name}
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
Returning Python dicts from `type='http'` routes without explicit serialization — HTTP routes
must return a Response, rendered template, or `request.make_response()`.
```python
# WRONG: dict return in http route causes 500
@http.route('/my/data', type='http', auth='user')
def my_data(self):
    return {'key': 'value'}  # TypeError

# CORRECT: use type='json' for dict responses
@http.route('/my/data', type='json', auth='user')
def my_data(self):
    return {'key': 'value'}  # auto-serialized

# CORRECT: for http, render a template or make_response
@http.route('/my/page', type='http', auth='user')
def my_page(self):
    return request.render('my_module.my_template', {})
```
  </antipattern>

  <antipattern severity="CRITICAL">
Accepting arbitrary `model` names from user input without validation — allows access to any model.
```python
# WRONG: user-controlled model name
@http.route('/api/read', type='json', auth='user')
def read(self, model, ids):
    return request.env[model].browse(ids).read()  # can access any model

# CORRECT: whitelist allowed models
ALLOWED_MODELS = {'sale.order', 'purchase.order', 'res.partner'}

@http.route('/api/read', type='json', auth='user')
def read(self, model, ids):
    if model not in ALLOWED_MODELS:
        raise ValueError('Model not allowed: %s' % model)
    return request.env[model].browse(ids).read()
```
  </antipattern>

  <antipattern severity="HIGH">
Using `auth='none'` for routes that access `request.env` — env is not set up without auth.
```python
# WRONG: env access with auth='none' raises RuntimeError
@http.route('/data', type='json', auth='none')
def data(self):
    return request.env['res.users'].browse(1).name  # RuntimeError

# CORRECT: use auth='public' minimum for env access
@http.route('/data', type='json', auth='public')
def data(self):
    return request.env['res.users'].browse(1).sudo().name
```
  </antipattern>

  <antipattern severity="MEDIUM">
Forgetting `website=True` on portal routes that use `request.render()` with website templates —
website context (multilang, theme) is missing.
```python
# WRONG: website template without website=True
@http.route('/my/portal', type='http', auth='user')
def portal(self):
    return request.render('website.template_portal', {})  # no website context

# CORRECT: add website=True
@http.route('/my/portal', type='http', auth='user', website=True)
def portal(self):
    return request.render('website.template_portal', {})
```
  </antipattern>

</antipatterns>

</pattern>