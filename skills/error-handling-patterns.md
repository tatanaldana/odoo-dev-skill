# Error Handling Patterns — v17/v18/v19

---

## Exception types

| Exception | Use case |
|-----------|----------|
| `UserError` | Business logic errors (shown in dialog) |
| `ValidationError` | Data constraints (`@api.constrains`) |
| `AccessError` | Permission violations |
| `MissingError` | Record not found (usually automatic) |
| `RedirectWarning` | Error with corrective action button |

## UserError

```python
if not self.line_ids:
    raise UserError(_("Cannot confirm without lines."))
```

## ValidationError (in @api.constrains)

```python
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for rec in self:
        if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
            raise ValidationError(_("Start must be before end."))
```

## RedirectWarning

```python
if not self.env.company.x_config_complete:
    action = self.env.ref('my_module.action_config_wizard')
    raise RedirectWarning(_("Config incomplete."), action.id, _("Go to Config"))
```

## Savepoints for batch

```python
for record in self:
    try:
        with self.env.cr.savepoint():
            record._process_single()
    except Exception as e:
        _logger.error("Failed %s: %s", record.id, e)
```

## Pre-action validation (collect errors)

```python
def _validate_confirm(self):
    errors = []
    for rec in self:
        if not rec.partner_id:
            errors.append("[%s] Partner required." % rec.name)
    if errors:
        raise UserError("\n".join(errors))
```

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No bare `except: pass` — swallows all errors silently |
| CRITICAL | No `except UserError: pass` — user never sees the error |
| HIGH | Include original exception in UserError: `raise UserError("Failed: %s" % e)` |
| HIGH | Use `ValidationError` in `@api.constrains`, not `UserError` |
| HIGH | Use savepoints for batch — one failure shouldn't abort all |
| MEDIUM | No `cr.commit()` in regular methods — only in cron batch jobs |