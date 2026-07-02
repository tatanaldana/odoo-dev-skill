# assets-bundling-patterns.md

<pattern>

  <description>
    Asset bundle declaration patterns in `__manifest__.py` for Odoo v17/18/19.
    Covers bundle keys, glob patterns, include/exclude/prepend/after syntax,
    and version-specific additions. Verified against manifest_17/18/19.py.
  </description>

  <version_notes>
    <version id="17">
      Available bundles: `web.assets_backend`, `web.assets_frontend`,
      `web.assets_tests`, `web.qunit_suite_tests`, `web.report_assets_common`,
      `web.report_assets_pdf`, `web._assets_primary_variables`.
      No `web.assets_unit_tests`. JS files require `/** @odoo-module **/` (decision #2).
      `web.qunit_suite_tests` is the bundle for QUnit unit test files.
    </version>
    <version id="18">
      `web.assets_unit_tests` introduced — replaces `web.qunit_suite_tests` for
      Hoot-based unit tests (decision #21). `web.qunit_suite_tests` still present
      for legacy QUnit files. JS files no longer require `@odoo-module` (decision #2).
      Tuple syntax `('remove', 'path/**/*')` used to exclude subpaths from globs.
    </version>
    <version id="19">
      `web.assets_unit_tests` continues. `web.qunit_suite_tests` absent from
      v19 reference manifest. `kpi_providers` key added at manifest top level
      (not inside `assets`) (decision #22). `author` key added. JS files: no `@odoo-module`.
      `web.assets_frontend` shifts to `interactions/` subdirectory structure.
    </version>
  </version_notes>

  <examples>

    <example id="basic_backend_bundle" title="Basic backend bundle declaration (all versions)">
      ```python
      # __manifest__.py
      {
          'name': 'My Module',
          'version': '17.0.1.0.0',   # or 18.0 / 19.0
          'depends': ['web'],
          'assets': {
              'web.assets_backend': [
                  'my_module/static/src/components/**/*',
                  'my_module/static/src/views/**/*',
                  'my_module/static/src/scss/main.scss',
              ],
          },
      }
      ```
    </example>

    <example id="full_bundle_v17" title="Full bundle declaration — v17">
      ```python
      # __manifest__.py  (v17)
      {
          'name': 'My Module',
          'version': '17.0.1.0.0',
          'depends': ['web'],
          'assets': {
              'web._assets_primary_variables': [
                  'my_module/static/src/scss/variables.scss',
              ],
              'web.assets_backend': [
                  'my_module/static/src/css/main.css',
                  'my_module/static/src/components/**/*',
                  'my_module/static/src/services/*.js',
                  'my_module/static/src/views/**/*.js',
              ],
              'web.assets_frontend': [
                  'my_module/static/src/js/portal.js',
              ],
              # v17: QUnit unit tests
              'web.qunit_suite_tests': [
                  'my_module/static/tests/helpers/*.js',
                  'my_module/static/tests/*.js',
              ],
              'web.assets_tests': [
                  'my_module/static/tests/tours/**/*',
              ],
              'web.report_assets_common': [
                  'my_module/static/src/css/report.css',
              ],
              'web.report_assets_pdf': [
                  'my_module/static/src/css/report.css',
              ],
          },
          'license': 'LGPL-3',
      }
      ```
    </example>

    <example id="full_bundle_v18" title="Full bundle declaration — v18">
      ```python
      # __manifest__.py  (v18)
      {
          'name': 'My Module',
          'version': '18.0.1.0.0',
          'depends': ['web'],
          'assets': {
              'web._assets_primary_variables': [
                  'my_module/static/src/scss/variables.scss',
              ],
              'web.assets_backend': [
                  'my_module/static/src/css/main.css',
                  'my_module/static/src/components/**/*',
                  'my_module/static/src/services/*.js',
                  'my_module/static/src/views/**/*',
              ],
              'web.assets_frontend': [
                  'my_module/static/src/js/portal.js',
              ],
              # v18: Hoot unit tests (new in v18 — decision #21)
              'web.assets_unit_tests': [
                  'my_module/static/tests/**/*',
                  ('remove', 'my_module/static/tests/legacy/**/*'),
                  ('remove', 'my_module/static/tests/tours/**/*'),
              ],
              'web.assets_tests': [
                  'my_module/static/tests/tours/**/*',
              ],
              'web.report_assets_common': [
                  'my_module/static/src/css/report.css',
              ],
          },
          'license': 'LGPL-3',
      }
      ```
    </example>

    <example id="full_bundle_v19" title="Full bundle declaration — v19">
      ```python
      # __manifest__.py  (v19)
      {
          'name': 'My Module',
          'version': '19.0.1.0.0',
          'author': 'My Company',   # new top-level key in v19
          'depends': ['web'],
          'assets': {
              'web._assets_primary_variables': [
                  'my_module/static/src/scss/variables.scss',
              ],
              'web.assets_backend': [
                  'my_module/static/src/css/main.css',
                  'my_module/static/src/components/**/*',
                  'my_module/static/src/services/*.js',
                  'my_module/static/src/views/**/*',
                  'my_module/static/src/js/tours/*',
              ],
              # v19: interactions/ replaces plain js/ in frontend
              'web.assets_frontend': [
                  'my_module/static/src/interactions/**/*',
              ],
              # v19: assets_unit_tests continues; qunit_suite_tests absent
              'web.assets_unit_tests': [
                  'my_module/static/tests/**/*',
                  ('remove', 'my_module/static/tests/tours/**/*'),
              ],
              'web.assets_tests': [
                  'my_module/static/tests/tours/**/*',
              ],
              'web.report_assets_common': [
                  'my_module/static/src/css/report.css',
              ],
              'web.report_assets_pdf': [
                  'my_module/static/src/css/report.css',
              ],
          },
          # kpi_providers: new top-level key in v19 (decision #22)
          'kpi_providers': [
              'models.kpi_provider:get_kpi_summary',
          ],
          'license': 'LGPL-3',
      }
      ```
    </example>

    <example id="tuple_operations" title="Tuple operations: prepend, after, remove">
      ```python
      # These tuple operations work the same in v17/18/19
      'assets': {
          'web.assets_backend': [
              # Prepend — load before all other entries in the bundle
              ('prepend', 'my_module/static/src/scss/override_variables.scss'),

              # After — load after a specific file
              ('after', 'web/static/src/core/registry.js',
               'my_module/static/src/core/registry_extension.js'),

              # Remove — exclude a file or glob from the bundle
              ('remove', 'web/static/src/views/list/list_controller.js'),

              # Include — standard glob (implicit default)
              'my_module/static/src/components/**/*',
          ],
      }
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      Adding `/** @odoo-module **/` to JS files when targeting v18 or v19.
      It is required only in v17 (decision #2).
      ```javascript
      // WRONG for v18/v19
      /** @odoo-module **/
      import { registry } from "@web/core/registry";
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Using `web.qunit_suite_tests` for Hoot tests in v18/v19 — this bundle is
      for legacy QUnit tests only. Use `web.assets_unit_tests` instead (decision #21).
      ```python
      # WRONG for v18/v19 Hoot tests
      'web.qunit_suite_tests': ['my_module/static/tests/*.js']

      # CORRECT for v18/v19
      'web.assets_unit_tests': ['my_module/static/tests/**/*']
      ```
    </antipattern>

    <antipattern severity="HIGH">
      Placing `kpi_providers` inside the `assets` dict — it is a top-level manifest
      key in v19, not an asset bundle (decision #22).
      ```python
      # WRONG
      'assets': {
          'kpi_providers': ['models.kpi_provider:get_kpi_summary'],
      }

      # CORRECT
      'kpi_providers': ['models.kpi_provider:get_kpi_summary'],
      'assets': { ... }
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      Using `**/*.js` glob when the bundle should include non-JS files (XML templates,
      SCSS). Use `**/*` (no extension filter) to include all file types in a directory.
      ```python
      # WRONG — misses .xml and .scss files
      'web.assets_backend': ['my_module/static/src/components/**/*.js']

      # CORRECT
      'web.assets_backend': ['my_module/static/src/components/**/*']
      ```
    </antipattern>

  </antipatterns>

</pattern>