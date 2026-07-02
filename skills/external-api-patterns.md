<pattern>

<description>
External API integration patterns for Odoo: calling third-party REST APIs, storing credentials
securely in ir.config_parameter, webhook endpoint definition and HMAC signature verification,
retry with exponential backoff, and queuing heavy sync operations via ir.cron or mail.thread.
Verified against http_controller_17/18/19.py for controller patterns;
credential storage via ir.config_parameter is a stable Odoo API across v17/v18/v19.
Patterns not confirmed against a reference file are marked accordingly.
</description>

<version_notes>
  <version id="17">
    `requests` library is available in Odoo's vendor dependencies.
    `ir.config_parameter` API (`get_param`, `set_param`) unchanged across all versions.
    Webhook endpoints use `@http.route(..., type='http', auth='none', csrf=False)`.
    `request.httprequest.data` gives raw request body bytes for signature verification.
  </version>
  <version id="18">
    External API patterns unchanged from v17.
  </version>
  <version id="19">
    `from odoo.tools.translate import LazyTranslate` available for lazy translation in modules.
    External API patterns otherwise unchanged.
  </version>
</version_notes>

<examples>

  <example id="credential_storage" title="Credential storage via ir.config_parameter">
```python
# pattern — verify against your codebase for exact param names

class MyExternalService(models.Model):
    _name = 'my.external.service'
    _description = 'My External Service'

    def _get_api_key(self):
        """Retrieve API key from system parameters.
        Never hardcode credentials; always use ir.config_parameter.
        """
        param = self.env['ir.config_parameter'].sudo()
        api_key = param.get_param('my_module.api_key')
        if not api_key:
            raise UserError(
                _('API key not configured. Go to Settings > Technical > Parameters.')
            )
        return api_key

    def _get_api_base_url(self):
        param = self.env['ir.config_parameter'].sudo()
        return param.get_param('my_module.api_base_url', default='https://api.example.com')
```
  </example>

  <example id="credential_config_model" title="Dedicated config model for external service settings">
```python
# pattern — verify against your codebase

class MyServiceConfig(models.TransientModel):
    """Settings stored in res.config.settings; displayed under Settings menu."""
    _inherit = 'res.config.settings'

    my_service_api_key = fields.Char(
        string='My Service API Key',
        config_parameter='my_module.api_key',
    )
    my_service_base_url = fields.Char(
        string='My Service URL',
        config_parameter='my_module.api_base_url',
        default='https://api.example.com',
    )
```
  </example>

  <example id="rest_api_call" title="Making a REST API call with error handling and timeout">
```python
import requests
from odoo import _, models
from odoo.exceptions import UserError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    def _call_external_api(self, endpoint, payload=None, method='GET'):
        """Call external REST API with timeout and error handling.
        pattern — verify base URL / header names against your target API.
        """
        api_key = self.env['ir.config_parameter'].sudo().get_param('my_module.api_key')
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'my_module.api_base_url', default='https://api.example.com'
        )

        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        url = '%s/%s' % (base_url.rstrip('/'), endpoint.lstrip('/'))

        try:
            response = requests.request(
                method,
                url,
                json=payload,
                headers=headers,
                timeout=30,  # always set a timeout to prevent hanging
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise UserError(_('External API request timed out. Please try again.'))
        except requests.exceptions.ConnectionError:
            raise UserError(_('Cannot connect to external service. Check network or URL.'))
        except requests.exceptions.HTTPError as e:
            raise UserError(_('API error %s: %s') % (e.response.status_code, e.response.text))
```
  </example>

  <example id="retry_backoff" title="Retry with exponential backoff">
```python
import time
import requests
from odoo import _, models
from odoo.exceptions import UserError


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    def _call_with_retry(self, url, headers, payload=None, max_retries=3):
        """Call external API with exponential backoff for transient failures.
        pattern — verify against your codebase for retry strategy.
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url, json=payload, headers=headers, timeout=30
                )
                if response.status_code == 429:
                    # Rate limited — honor Retry-After header if present
                    retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
                    time.sleep(retry_after)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 1s, 2s, 4s...

        raise UserError(_('API call failed after %d attempts: %s') % (max_retries, last_error))
```
  </example>

  <example id="webhook_endpoint" title="Webhook endpoint with HMAC signature verification">
```python
# Verified pattern: @http.route with auth='none', csrf=False for webhooks
# request.httprequest.data for raw body — confirmed available in http_controller_17.py context

import hashlib
import hmac
import json
from odoo import http
from odoo.http import request


class WebhookController(http.Controller):

    @http.route(
        '/webhook/my_service',
        type='http',
        auth='none',
        methods=['POST'],
        csrf=False,
    )
    def receive_webhook(self, **kw):
        """Receive and verify webhook from external service.
        Always verify HMAC signature before processing payload.
        """
        # Read raw body BEFORE any parsing
        raw_body = request.httprequest.data

        # Retrieve webhook secret
        secret = request.env['ir.config_parameter'].sudo().get_param(
            'my_module.webhook_secret', ''
        )
        if not secret:
            return request.make_response('Webhook secret not configured', status=500)

        # Verify HMAC signature
        signature_header = request.httprequest.headers.get('X-Signature-256', '')
        expected = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature_header, expected):
            return request.make_response('Invalid signature', status=401)

        # Process payload
        try:
            payload = json.loads(raw_body)
        except (ValueError, TypeError):
            return request.make_response('Invalid JSON', status=400)

        # Queue processing to avoid blocking the webhook response
        request.env['my.model'].sudo().with_delay()._process_webhook(payload)
        return request.make_response('OK', status=200)
```
  </example>

  <example id="queue_heavy_sync" title="Queuing heavy sync operations via ir.cron">
```python
# pattern — verify cron XML definition against your codebase

from odoo import fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    sync_status = fields.Selection(
        selection=[('pending', 'Pending'), ('synced', 'Synced'), ('error', 'Error')],
        default='pending',
    )

    def action_schedule_sync(self):
        """Mark record for sync; actual sync runs via cron to avoid blocking UI."""
        self.write({'sync_status': 'pending'})

    def _cron_sync_records(self):
        """Called by ir.cron — process pending records in batch."""
        pending = self.search([('sync_status', '=', 'pending')], limit=50)
        for record in pending:
            try:
                record._sync_to_external()
                record.last_sync = fields.Datetime.now()
                record.sync_status = 'synced'
            except Exception as e:
                record.sync_status = 'error'
                record.message_post(body='Sync error: %s' % str(e))

    def _sync_to_external(self):
        """Perform the actual external API call."""
        data = self._call_external_api('/sync', payload={'name': self.name})
        return data
```

Cron definition:
```xml
<record id="ir_cron_sync_records" model="ir.cron">
    <field name="name">My Module: Sync Records</field>
    <field name="model_id" ref="my_module.model_my_model"/>
    <field name="state">code</field>
    <field name="code">model._cron_sync_records()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
    <field name="numbercall">-1</field>
    <field name="active" eval="True"/>
</record>
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
Hardcoding API credentials in source code — must use `ir.config_parameter` or a
dedicated config model with `groups='base.group_system'`.
```python
# WRONG: hardcoded credential
API_KEY = 'sk-abc123...'
headers = {'Authorization': 'Bearer sk-abc123...'}

# CORRECT: read from system parameters at runtime
api_key = self.env['ir.config_parameter'].sudo().get_param('my_module.api_key')
```
  </antipattern>

  <antipattern severity="CRITICAL">
Skipping webhook signature verification — always verify HMAC before processing any webhook payload.
```python
# WRONG: no signature check
@http.route('/webhook', type='http', auth='none', csrf=False)
def webhook(self):
    payload = request.httprequest.json
    self._process(payload)  # could be spoofed

# CORRECT: verify HMAC first (see webhook_endpoint example above)
```
  </antipattern>

  <antipattern severity="HIGH">
Making blocking external API calls synchronously during user actions — long calls freeze
the UI and can cause request timeouts.
```python
# WRONG: blocking call in write() override
def write(self, vals):
    result = super().write(vals)
    self._call_external_api('/update', payload=vals)  # blocks user
    return result

# CORRECT: mark as pending and process via cron or queue
def write(self, vals):
    result = super().write(vals)
    self.sync_status = 'pending'  # cron picks it up
    return result
```
  </antipattern>

  <antipattern severity="HIGH">
Using `http://` (not HTTPS) for external API calls — always use HTTPS to protect credentials
and data in transit.
```python
# WRONG: insecure HTTP
url = 'http://api.example.com/data'

# CORRECT: always HTTPS
url = 'https://api.example.com/data'
```
  </antipattern>

  <antipattern severity="MEDIUM">
Making external API requests without a timeout — a slow or unresponsive API will hang
the Odoo worker process indefinitely.
```python
# WRONG: no timeout
response = requests.get(url, headers=headers)

# CORRECT: always set a timeout (seconds)
response = requests.get(url, headers=headers, timeout=30)
```
  </antipattern>

</antipatterns>

</pattern>