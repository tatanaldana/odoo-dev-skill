# Context & Environment Patterns — v17/v18/v19

---

## Version differences

| Feature | v17/v18 | v19 |
|---------|---------|-----|
| Translation | `from odoo import _` | both `_()` and `self.env._()` valid |
| `bypass_search_access` | — | new on M2O fields |
| Everything else | identical | identical |

---

## Reading context

```python
project_id = self.env.context.get('default_project_id')  # always .get() with default
```

## with_context

```python
# Disable active filter
all_records = self.with_context(active_test=False).search([])

# Set defaults for action
return {'type': 'ir.actions.act_window', 'context': {'default_parent_id': self.id}}
```

## Building action context

```python
ctx = dict(self.env.context)  # copy frozendict first!
ctx['active_ids'] = self.ids
action['context'] = ctx
```

## sudo() — elevate specific calls only

```python
# WRONG: self = self.sudo()  — elevates everything
# CORRECT: targeted
followers = self.sudo().message_follower_ids
```

## with_user() — run as specific user

```python
if self.with_user(portal_user).has_access('read'):
    # user has access
```

## env.ref() — resolve XML ID

```python
stage = self.env.ref('project.project_stage_progress')
action = self.env['ir.actions.act_window']._for_xml_id('module.action_id')
```

## Translation

```python
# v17/v18/v19 — all valid
from odoo import _
raise UserError(_("Cannot delete %s") % record.name)

# v18/v19 alternative
raise UserError(self.env._("Cannot delete %s") % record.name)

# WRONG: f-strings, concatenation
# _(f"Cannot delete {name}")
# _("Cannot delete " + name)
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | Never mutate `self.env.context` directly — it's a frozendict |
| CRITICAL | `_()` only on literal strings — no f-strings or concatenation |
| HIGH | Don't blanket `sudo()` an entire method — target specific calls |
| MEDIUM | No hardcoded IDs — use `env.ref()` |