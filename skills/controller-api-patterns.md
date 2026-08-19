# Controller & API Patterns — v17/v18/v19

---

## Version differences

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| Imports | `base64`, `json` in portal | simplified | `Forbidden`, `LazyTranslate`, `str2bool` added |
| `type='json'` routes | works | works | **deprecated alias** for `type='jsonrpc'` (warning, still works) |
| Access check | `check_access_rights` + `check_access_rule` | **deprecated**, use `check_access(operation)` | same as v18 (old methods still work but warn) |

---

## Basic controller

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    @http.route('/my/data', type='json', auth='user')  # v19: type='jsonrpc' is the non-deprecated name (odoo/http.py, 19.0); 'json' still works as alias
    def get_data(self):
        records = request.env['my.model'].search([])
        return {'data': records.read(['id', 'name', 'state'])}

    @http.route('/my/page', type='http', auth='user', website=True)
    def my_page(self, **kw):
        return request.render('my_module.my_template', {'records': request.env['my.model'].search([])})
```

## Auth levels

| Auth | Env | Use case |
|------|-----|----------|
| `'user'` | full env | backend endpoints |
| `'public'` | env with public user | portal/website pages |
| `'none'` | NO env | healthchecks, webhooks |

## Portal pattern (_document_check_access)

```python
from odoo.addons.portal.controllers.portal import CustomerPortal

class MyPortal(CustomerPortal):
    @route('/my/docs/<int:doc_id>', type='http', auth='public', website=True)
    def doc_detail(self, doc_id, access_token=None, **kw):
        try:
            doc_sudo = self._document_check_access('my.model', doc_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render('my_module.portal_doc', {'document': doc_sudo})
```

## Report rendering from controller

```python
@http.route('/my/report/<int:doc_id>', type='http', auth='user')
def download(self, doc_id, report_type='pdf', **kw):
    doc = request.env['my.model'].browse(doc_id)
    doc.check_access('read')  # v17: use check_access_rights('read') + check_access_rule('read') instead —
                               # check_access() didn't exist yet (odoo/models.py, 17.0); both old calls are
                               # deprecated since 18.0 (odoo/models.py 18.0 / odoo/orm/models.py 19.0)
    report = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
        'my_module.action_report', [doc.id])[0]
    return request.make_response(report, headers=[
        ('Content-Type', 'application/pdf'),
        ('Content-Disposition', content_disposition('%s.pdf' % doc.name)),
    ])
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Don't return dicts from `type='http'` routes — use `type='json'` or `render()` |
| CRITICAL | Never accept arbitrary model names from user input — whitelist |
| HIGH | `auth='none'` has no env — use `'public'` minimum for env access |
| MEDIUM | Add `website=True` on portal routes using website templates |
| MEDIUM | v18+: prefer `check_access(operation)` over `check_access_rights()`/`check_access_rule()` (deprecated since 18.0, still functional but warn) |
| LOW | v19: prefer `type='jsonrpc'` over `type='json'` in new code — `'json'` is a deprecated alias |