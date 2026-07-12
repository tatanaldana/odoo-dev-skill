# External API Patterns — v17/v18/v19

REST calls, credential storage, webhooks, retry, async sync.

---

## Credential storage

```python
# In res.config.settings
my_api_key = fields.Char(config_parameter='my_module.api_key')
my_base_url = fields.Char(config_parameter='my_module.api_url', default='https://api.example.com')

# In business logic
api_key = self.env['ir.config_parameter'].sudo().get_param('my_module.api_key')
```

## REST API call with error handling

```python
import requests

def _call_api(self, endpoint, payload=None, method='GET'):
    api_key = self.env['ir.config_parameter'].sudo().get_param('my_module.api_key')
    base_url = self.env['ir.config_parameter'].sudo().get_param('my_module.api_url')
    try:
        resp = requests.request(method, f'{base_url}/{endpoint}',
            json=payload, headers={'Authorization': f'Bearer {api_key}'},
            timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        raise UserError(_('API timed out.'))
    except requests.exceptions.HTTPError as e:
        raise UserError(_('API error %s: %s') % (e.response.status_code, e.response.text))
```

## Webhook with HMAC verification

```python
@http.route('/webhook/my_service', type='http', auth='none', methods=['POST'], csrf=False)
def webhook(self, **kw):
    raw = request.httprequest.data
    secret = request.env['ir.config_parameter'].sudo().get_param('my_module.webhook_secret')
    sig = request.httprequest.headers.get('X-Signature-256', '')
    expected = 'sha256=' + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return request.make_response('Invalid signature', status=401)
    payload = json.loads(raw)
    request.env['my.model'].sudo()._process_webhook(payload)
    return request.make_response('OK', status=200)
```

## Async sync via cron

```python
def action_schedule_sync(self):
    self.write({'sync_status': 'pending'})  # cron picks it up

@api.model
def _cron_sync(self):
    for rec in self.search([('sync_status', '=', 'pending')], limit=50):
        try:
            rec._call_api('/sync', payload={'name': rec.name})
            rec.write({'sync_status': 'synced', 'last_sync': fields.Datetime.now()})
        except Exception as e:
            rec.write({'sync_status': 'error'})
            rec.message_post(body='Sync error: %s' % e)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Never hardcode credentials — use `ir.config_parameter` |
| CRITICAL | Always verify HMAC on webhooks before processing |
| HIGH | Don't make blocking API calls in `write()`/`create()` — queue via cron |
| HIGH | Always HTTPS, never HTTP |
| MEDIUM | Always set `timeout=` on requests calls |