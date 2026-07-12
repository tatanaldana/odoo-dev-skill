# Assets Bundling Patterns — v17/v18/v19

---

## Version differences

| Feature | v17 | v18 | v19 |
|---------|-----|-----|-----|
| Unit tests bundle | `web.qunit_suite_tests` | `web.assets_unit_tests` (Hoot) | `web.assets_unit_tests` |
| `@odoo-module` in JS | required | optional | optional |
| `kpi_providers` | — | — | new top-level manifest key |
| Frontend structure | `static/src/js/` | same | `static/src/interactions/` |

---

## Manifest examples

```python
# v17
'assets': {
    'web.assets_backend': ['my_module/static/src/**/*'],
    'web.qunit_suite_tests': ['my_module/static/tests/**/*.js'],
}

# v18
'assets': {
    'web.assets_backend': ['my_module/static/src/**/*'],
    'web.assets_unit_tests': [
        'my_module/static/tests/**/*',
        ('remove', 'my_module/static/tests/tours/**/*'),
    ],
    'web.assets_tests': ['my_module/static/tests/tours/**/*'],
}

# v19 — same as v18 + top-level kpi_providers
'kpi_providers': ['models.kpi_provider:get_kpi_summary'],
```

## Tuple operations (all versions)

```python
('prepend', 'my_module/static/src/scss/override.scss'),
('after', 'web/static/src/core/registry.js', 'my_module/static/src/registry_ext.js'),
('remove', 'web/static/src/views/list/list_controller.js'),
```

## Available bundles

`web.assets_backend`, `web.assets_frontend`, `web._assets_primary_variables`, `web.assets_tests`, `web.report_assets_common`, `web.report_assets_pdf`

---

## Antipatterns

| Severity | Rule |
|----------|------|
| CRITICAL | No `@odoo-module` in v18/v19 JS |
| HIGH | Use `web.assets_unit_tests` for Hoot tests in v18+ (not `qunit_suite_tests`) |
| HIGH | `kpi_providers` is top-level manifest key, not inside `assets` |
| MEDIUM | Use `**/*` not `**/*.js` to include XML/SCSS with JS |