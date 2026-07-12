# Mail & Notification Patterns — v17/v18/v19

---

## Version differences

| Feature | v17 | v18/v19 |
|---------|-----|---------|
| Chatter view | `<div class="oe_chatter">` + 3 fields | `<chatter/>` (bare tag; `reload_on_attachment`/`reload_on_follower` only where needed) |
| JS notification `autocloseDelay` | not available | available (ms, 0=sticky) |
| `message_post()` API | identical across all versions | — |
| `from odoo import _` | valid | valid (also `self.env._()` in v18+) |

---

## Model with mail.thread

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(tracking=True)
    state = fields.Selection([...], tracking=True)
    partner_id = fields.Many2one('res.partner', tracking=True)
```

## message_post

```python
# Internal note
self.message_post(body=_('Document confirmed.'), message_type='comment', subtype_xmlid='mail.mt_note')

# Notify partner
self.message_post(body=_('Please review.'), message_type='comment',
    subtype_xmlid='mail.mt_comment', partner_ids=[self.partner_id.id])
```

## Activity scheduling

```python
self.activity_schedule('mail.mail_activity_data_todo', user_id=approver.id,
    summary='Approval Required', date_deadline=fields.Date.today() + timedelta(days=3))
```

## Email template (XML — identical v17/v18/v19)

```xml
<record id="mail_template_confirm" model="mail.template">
    <field name="name">My Model: Confirmation</field>
    <field name="model_id" ref="my_module.model_my_model"/>
    <field name="subject">Confirmation of {{ object.name }}</field>
    <field name="use_default_to" eval="True"/>
    <field name="body_html" type="html">
<div>Dear <t t-out="object.partner_id.name or 'customer'"/>,<br/>
Your request <strong t-out="object.name or ''"/> has been confirmed.</div>
    </field>
    <field name="lang">{{ object.partner_id.lang }}</field>
    <field name="auto_delete" eval="True"/>
</record>
```

## JS toast notifications

```javascript
// v17: no autocloseDelay
this.notification.add("Saved.", { type: "success", sticky: false });

// v18+: autocloseDelay available
this.notification.add("Saved.", { type: "success", autocloseDelay: 4000 });
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `autocloseDelay` in v17 |
| HIGH | v18+: `<div class="oe_chatter">` → `<chatter/>` |
| HIGH | No `send_mail(force_send=True)` in loops — use `force_send=False` |
| MEDIUM | `message_type='comment'` + `subtype_xmlid='mail.mt_note'` for internal notes, not `'email'` |