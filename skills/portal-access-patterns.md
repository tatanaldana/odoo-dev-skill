# Portal Access Patterns — v17/v18/v19

Full stack: portal.mixin on model, CustomerPortal controller, portal home, QWeb templates.

---

## Version differences

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| `_get_access_action` | `check_access_rights` + `check_access_rule` (2 calls) | `check_access('read')` (1 call) | same as v18 |
| `_get_share_url` | no access check before token | adds `check_access('read')` | same as v18 |
| Language selector | `languages` list of tuples | `frontend_languages` dict | same as v18 |
| Pager icons | `fa fa-chevron-*` | same | `oi oi-chevron-*` |
| Pager ellipsis | not available | not available | `page['num']` can be `'…'` |
| Backend link | `/web` | same | `/odoo` |
| Portal home | only Connection & Security | removes spinner | adds Addresses card |
| `t-nocache` on dropdown | yes | yes | removed |

---

## 1. Add portal.mixin to model

```python
class MyDocument(models.Model):
    _name = 'my.document'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')

    def _compute_access_url(self):
        super()._compute_access_url()
        for record in self:
            record.access_url = '/my/documents/%s' % record.id
```

Token is automatic via `portal.mixin`: `access_token = fields.Char(copy=False)`
Get/generate: `record._portal_ensure_token()`
Build URL: `record.get_portal_url(suffix='/print', report_type='pdf')`

---

## 2. CustomerPortal controller

```python
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request, route
from odoo.exceptions import AccessError, MissingError

class MyPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'document_count' in counters:
            values['document_count'] = request.env['my.document'].search_count(
                self._get_document_domain()
            )
        return values

    def _get_document_domain(self):
        return [('partner_id', '=', request.env.user.partner_id.id)]

    @route(['/my/documents', '/my/documents/page/<int:page>'],
           type='http', auth='user', website=True)
    def portal_my_documents(self, page=1, sortby=None, **kw):
        domain = self._get_document_domain()
        count = request.env['my.document'].search_count(domain)
        pager_values = portal_pager(
            url='/my/documents', total=count, page=page, step=10,
        )
        docs = request.env['my.document'].search(
            domain, limit=10, offset=pager_values['offset'],
        )
        return request.render('my_module.portal_my_documents', {
            'documents': docs, 'pager': pager_values, 'page_name': 'documents',
        })

    @route(['/my/documents/<int:doc_id>'], type='http', auth='public', website=True)
    def portal_document_detail(self, doc_id, access_token=None, **kw):
        try:
            doc_sudo = self._document_check_access('my.document', doc_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.render('my_module.portal_document_detail', {
            'document': doc_sudo, 'page_name': 'documents',
        })
```

---

## 3. Portal home registration

```xml
<!-- Register counter on portal home -->
<template id="portal_my_home_document" name="Documents"
          inherit_id="portal.portal_my_home" priority="40">
    <xpath expr="//div[hasclass('o_portal_docs')]" position="before">
        <t t-call="portal.portal_docs_entry">
            <t t-set="icon" t-value="'/my_module/static/description/icon.png'"/>
            <t t-set="title">Documents</t>
            <t t-set="url" t-value="'/my/documents'"/>
            <t t-set="text">View your documents</t>
            <t t-set="placeholder_count" t-value="'document_count'"/>
        </t>
    </xpath>
</template>
```

---

## 4. QWeb templates (list + detail)

```xml
<!-- List page -->
<template id="portal_my_documents">
    <t t-call="portal.portal_layout">
        <t t-set="breadcrumbs_searchbar" t-value="True"/>
        <t t-call="portal.portal_table">
            <thead><tr>
                <th>Name</th><th>State</th><th>Date</th>
            </tr></thead>
            <t t-foreach="documents" t-as="doc">
                <tr>
                    <td><a t-att-href="doc.get_portal_url()"><t t-out="doc.name"/></a></td>
                    <td><t t-out="doc.state"/></td>
                    <td><t t-out="doc.create_date" t-options='{"widget": "date"}'/></td>
                </tr>
            </t>
        </t>
    </t>
</template>

<!-- Detail page with access_token -->
<template id="portal_document_detail">
    <t t-call="portal.portal_layout">
        <div class="card">
            <div class="card-header"><h5 t-out="document.name"/></div>
            <div class="card-body">
                <div class="row">
                    <div class="col-6">Partner: <span t-out="document.partner_id.name"/></div>
                    <div class="col-6">State: <span t-out="document.state"/></div>
                </div>
            </div>
        </div>
        <div class="mt-3" t-call="portal.message_thread">
            <t t-set="object" t-value="document"/>
        </div>
    </t>
</template>
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Never skip `_document_check_access` on detail routes — security bypass |
| CRITICAL | Always use `auth='public'` + `access_token` for shareable detail pages |
| HIGH | Don't redefine `access_token` field — `portal.mixin` provides it |
| HIGH | Use `portal_pager` helper — don't build pagination manually |
| MEDIUM | v19: pager icons changed to `oi oi-chevron-*` |