<pattern>

<description>
Mail and notification patterns for Odoo: inheriting mail.thread and mail.activity.mixin on models,
chatter view integration (version-specific), message_post usage, activity scheduling,
email template rendering via mail.template, and JS toast notifications.
Verified against mail_template_data_17/18/19.xml, project_task_17/18/19.py,
and notification_service_17/18.js.
</description>

<version_notes>
  <version id="17">
    Chatter view: `<div class="oe_chatter">` block with three child fields.
    JS notification: `this.notification.add(message, { type, sticky, title })` — no `autocloseDelay`.
    Python: `message_post()` API identical across v17/v18/v19.
  </version>
  <version id="18">
    Chatter view: `<chatter reload_on_attachment="True"/>` (document pattern) or
    `<chatter reload_on_follower="True"/>` (task/follower pattern) — self-closing tag.
    JS notification: `autocloseDelay` option added — controls ms before auto-close (0 = sticky).
    Confirmed via notification_service_18.js.
  </version>
  <version id="19">
    Chatter view syntax identical to v18.
    JS notification API identical to v18.
    Python: `self.env._()` preferred over `from odoo import _` for translation in v19.
  </version>
</version_notes>

<examples>

  <example id="model_mixin" title="Model with mail.thread and mail.activity.mixin">
```python
from odoo import api, fields, models


class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned To',
        tracking=True,
    )
```
  </example>

  <example id="chatter_view_v17" title="Form view chatter — v17 (oe_chatter div)">
```xml
<form>
    <sheet>
        <!-- ... fields ... -->
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```
  </example>

  <example id="chatter_view_v18" title="Form view chatter — v18/v19 (chatter tag)">
```xml
<form>
    <sheet>
        <!-- ... fields ... -->
    </sheet>
    <!-- For document models (account.move pattern): -->
    <chatter reload_on_attachment="True"/>
    <!-- For task/follower models (project.task pattern): -->
    <!-- <chatter reload_on_follower="True"/> -->
</form>
```
  </example>

  <example id="message_post_python" title="message_post — sending messages from Python (v17/v18/v19)">
```python
def action_confirm(self):
    self.write({'state': 'confirmed'})
    # Post a note in the chatter
    self.message_post(
        body=self.env._('Order %s confirmed.') % self.name,
        message_type='comment',
        subtype_xmlid='mail.mt_note',
    )

def action_send_email(self):
    # Send email to followers
    template = self.env.ref('my_module.mail_template_confirm')
    template.send_mail(self.id, force_send=True)

def action_notify_partner(self):
    # Post message with partner notification
    self.message_post(
        body=self.env._('Please review this document.'),
        message_type='comment',
        subtype_xmlid='mail.mt_comment',
        partner_ids=[self.partner_id.id],
    )
```
  </example>

  <example id="activity_schedule" title="Activity scheduling — Python">
```python
def action_request_approval(self):
    # Schedule an activity for the responsible user
    self.activity_schedule(
        activity_type_xmlid='mail.mail_activity_data_todo',
        summary='Please approve this record',
        note='The record requires your approval before proceeding.',
        user_id=self.user_id.id,
        date_deadline=fields.Date.today() + timedelta(days=3),
    )
```
  </example>

  <example id="mail_template_xml" title="Email template definition (v17/v18/v19 identical syntax)">
```xml
<!-- Verified against mail_template_data_17/18/19.xml -->
<record id="mail_template_my_model_confirm" model="mail.template">
    <field name="name">My Model: Confirmation</field>
    <field name="model_id" ref="my_module.model_my_model"/>
    <field name="subject">Confirmation of {{ object.name }}</field>
    <field name="use_default_to" eval="True"/>
    <field name="body_html" type="html">
<div>
    Dear <t t-out="object.partner_id.name or 'customer'">Customer</t>,<br/><br/>
    Your request <strong t-out="object.name or ''">REF</strong> has been confirmed.
    <t t-if="user.signature">
        <br/>
        <t t-out="user.signature or ''">--<br/>Admin</t>
    </t>
</div>
    </field>
    <field name="lang">{{ object.partner_id.lang }}</field>
    <field name="auto_delete" eval="True"/>
</record>
```
  </example>

  <example id="js_notification_v17" title="JS toast notification — v17 (no autocloseDelay)">
```javascript
// v17 — notification service, no autocloseDelay option
// Verified against notification_service_17.js

import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    setup() {
        this.notification = useService("notification");
    }

    showSuccess() {
        this.notification.add("Record saved successfully.", {
            type: "success",
            title: "Success",
            sticky: false,
        });
    }

    showWarning() {
        this.notification.add("Please check your input.", {
            type: "warning",
            sticky: true,
        });
    }
}
```
  </example>

  <example id="js_notification_v18" title="JS toast notification — v18/v19 (autocloseDelay added)">
```javascript
// v18+ — autocloseDelay option available
// Verified against notification_service_18.js (decision #35)

import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    setup() {
        this.notification = useService("notification");
    }

    showSuccess() {
        this.notification.add("Record saved successfully.", {
            type: "success",
            title: "Success",
            sticky: false,
            autocloseDelay: 4000,  // ms — v18+ only; omit in v17
        });
    }

    showSticky() {
        this.notification.add("Action required.", {
            type: "warning",
            sticky: true,
            autocloseDelay: 0,  // 0 = never auto-close
        });
    }
}
```
  </example>

</examples>

<antipatterns>

  <antipattern severity="CRITICAL">
Using `autocloseDelay` notification option in v17 code — option did not exist until v18.
```javascript
// WRONG in v17
this.notification.add("Done.", { type: "success", autocloseDelay: 3000 });

// CORRECT in v17
this.notification.add("Done.", { type: "success", sticky: false });
```
  </antipattern>

  <antipattern severity="HIGH">
Using `oe_chatter` div block in v18+ forms — replaced by the `<chatter/>` tag.
```xml
<!-- WRONG in v18+ -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>

<!-- CORRECT in v18+ -->
<chatter reload_on_attachment="True"/>
```
  </antipattern>

  <antipattern severity="HIGH">
Calling `send_mail` with `force_send=True` in a loop or bulk operation — triggers one SMTP
connection per record and blocks the request.
```python
# WRONG: blocks on every record
for record in self:
    template.send_mail(record.id, force_send=True)

# CORRECT: queue emails for background sending
for record in self:
    template.send_mail(record.id, force_send=False)
```
  </antipattern>

  <antipattern severity="MEDIUM">
Posting messages with `message_type='email'` for internal notes — use `'comment'` with
`subtype_xmlid='mail.mt_note'` for notes, `'email'` only for outgoing emails.
```python
# WRONG for internal note
self.message_post(body="Internal note.", message_type='email')

# CORRECT for internal note
self.message_post(
    body="Internal note.",
    message_type='comment',
    subtype_xmlid='mail.mt_note',
)
```
  </antipattern>

</antipatterns>

</pattern>