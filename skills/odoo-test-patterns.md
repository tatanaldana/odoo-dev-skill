<pattern>

  <description>
    Patterns for writing Odoo Python and JavaScript tests.
    Covers TransactionCase structure, @tagged decorator, access control assertions,
    setUpClass data setup, assertRecordValues, and the QUnit-to-Hoot migration
    from v17 to v18. Use when generating tests for any Odoo addon.
  </description>

  <version_notes>
    <version id="17">
      Python: check_access_rights() and check_access_rule() are the access
      assertion methods. Import tagged and new_test_user from odoo.tests.
      Call self._reset_bus() before assertBus to clear prior events.
      JS: QUnit framework — QUnit.module("name"), QUnit.test("name", async (assert) => {}).
      assert.step() and assert.verifySteps() for step tracking.
      Requires @odoo-module pragma at top of every JS test file.
      Test helpers imported from @web/../tests/helpers/utils and @mail/../tests/helpers/.
    </version>
    <version id="18">
      Python: has_access('read') replaces check_access_rights() + check_access_rule().
      Confirmed: test_18.py line 14 uses has_access(); _reset_bus() call retained.
      All other Python test APIs identical to v17.
      JS: QUnit replaced by Hoot. Import describe, expect, test from @odoo/hoot.
      Import assertSteps, step from @mail/../tests/mail_test_helpers (not from @web).
      No @odoo-module required. describe.current.tags("desktop") replaces QUnit.module.
      defineMailModels() call required at module level for mail-related tests.
      openDiscuss, openFormView, start imported as named functions from mail_test_helpers.
    </version>
    <version id="19">
      Python: @users("login") decorator available — import users from odoo.tests.
      Enables running the same test method as a specific user without with_user().
      Confirmed: test_19.py line 11-12 uses @users("employee").
      has_access() retained. _reset_bus() call dropped before assertBus in v19.
      self.mock_mail_gateway() context manager wraps message_post calls.
      JS: Hoot API identical to v18 for describe/test/expect.
      assertSteps/step replaced by asyncStep/waitForSteps from @web/../tests/web_test_helpers.
      listenStoreFetch and waitStoreFetch new helpers from mail_test_helpers.
      setupChatHub new import for chat hub initialization.
    </version>
  </version_notes>

  <examples>

    <example id="python_transaction_case" title="TransactionCase with setUpClass">
      ```python
      # tests/common.py
      from odoo.tests import TransactionCase, tagged

      class TestMyModuleCommon(TransactionCase):

          @classmethod
          def setUpClass(cls):
              super().setUpClass()
              cls.company = cls.env.ref('base.main_company')
              cls.partner = cls.env['res.partner'].create({
                  'name': 'Test Partner',
                  'email': 'test@example.com',
              })
              cls.user_manager = cls.env['res.users'].create({
                  'name': 'Test Manager',
                  'login': 'test_manager',
                  'groups_id': [(6, 0, [
                      cls.env.ref('base.group_user').id,
                      cls.env.ref('my_module.group_manager').id,
                  ])],
              })
      ```
    </example>

    <example id="python_tagged_test" title="Tagged test class">
      ```python
      # tests/test_my_model.py
      from odoo.tests import tagged
      from odoo.exceptions import ValidationError, UserError
      from .common import TestMyModuleCommon

      @tagged('post_install', '-at_install')
      class TestMyModel(TestMyModuleCommon):

          def test_create_record(self):
              record = self.env['my.model'].create({
                  'name': 'Test Record',
                  'partner_id': self.partner.id,
              })
              self.assertTrue(record.id)
              self.assertEqual(record.name, 'Test Record')
              self.assertEqual(record.state, 'draft')

          def test_confirm_without_lines_fails(self):
              record = self.env['my.model'].create({'name': 'No Lines'})
              with self.assertRaises(UserError):
                  record.action_confirm()
      ```
    </example>

    <example id="python_access_control_v17" title="Access control assertions (v17)">
      ```python
      # v17 — check_access_rights + check_access_rule
      from odoo.tests import tagged, new_test_user

      @tagged('post_install', '-at_install')
      class TestAccess(TestMyModuleCommon):

          def test_read_access_v17(self):
              inexisting = self.env['my.model'].with_user(
                  self.user_manager
              ).browse(-1)
              self.assertTrue(
                  inexisting.check_access_rights('read')
              )
              self.assertFalse(inexisting.exists())
              self.assertEqual(
                  inexisting.browse().check_access_rule('read'), None
              )

          def test_user_cannot_read_other_company(self):
              company2 = self.env['res.company'].create({'name': 'Company 2'})
              user_c2 = new_test_user(
                  self.env,
                  login='user_c2',
                  company_id=company2.id,
                  company_ids=[company2.id],
              )
              record = self.env['my.model'].create({
                  'name': 'Main Co Record',
                  'company_id': self.company.id,
              })
              result = self.env['my.model'].with_user(user_c2).search([])
              self.assertNotIn(record, result)
      ```
    </example>

    <example id="python_access_control_v18" title="Access control assertions (v18/v19)">
      ```python
      # v18/v19 — has_access() replaces check_access_rights + check_access_rule
      @tagged('post_install', '-at_install')
      class TestAccess(TestMyModuleCommon):

          def test_read_access_v18(self):
              inexisting = self.env['my.model'].with_user(
                  self.user_manager
              ).browse(-1)
              self.assertFalse(inexisting.exists())
              self.assertTrue(
                  inexisting.browse().has_access('read')
              )
      ```
    </example>

    <example id="python_users_decorator_v19" title="@users decorator (v19)">
      ```python
      # v19 — @users decorator runs the test as a specific user
      from odoo.tests import tagged, users

      @tagged('post_install', '-at_install')
      class TestMyModelV19(TestMyModuleCommon):

          @users('test_manager')
          def test_manager_can_confirm(self):
              # self.env.user is now test_manager
              record = self.env['my.model'].create({'name': 'Test'})
              self.assertTrue(record.has_access('write'))
      ```
    </example>

    <example id="python_assert_record_values" title="assertRecordValues for batch assertions">
      ```python
      def test_payment_values(self):
          records = self.env['my.model'].create([
              {'name': 'A', 'amount': 10.0},
              {'name': 'B', 'amount': 20.0},
          ])
          self.assertRecordValues(records, [
              {'name': 'A', 'amount': 10.0, 'state': 'draft'},
              {'name': 'B', 'amount': 20.0, 'state': 'draft'},
          ])
      ```
    </example>

    <example id="python_bus_assertion" title="assertBus for real-time notifications (v17/v18)">
      ```python
      # v17/v18: call _reset_bus() before assertBus
      def test_unlink_notifies_author(self):
          recipient = new_test_user(self.env, login='Bob', email='invalid@')
          message = self.env.user.partner_id.message_post(
              body='Hello!', partner_ids=recipient.partner_id.ids
          )
          self._reset_bus()
          with self.assertBus(
              [(self.cr.dbname, 'res.partner', self.env.user.partner_id.id)],
              [{'type': 'mail.message/delete',
                'payload': {'message_ids': [message.id]}}],
          ):
              message.unlink()
      ```
    </example>

    <example id="python_bus_assertion_v19" title="assertBus for real-time notifications (v19)">
      ```python
      # v19: no _reset_bus() call needed; mock_mail_gateway wraps message_post
      def test_unlink_notifies_author_v19(self):
          recipient = new_test_user(self.env, login='Bob', email='invalid@')
          with self.mock_mail_gateway():
              message = self.env.user.partner_id.message_post(
                  body='Hello!', partner_ids=recipient.partner_id.ids
              )
          with self.assertBus(
              [(self.cr.dbname, 'res.partner', self.env.user.partner_id.id)],
              [{'type': 'mail.message/delete',
                'payload': {'message_ids': [message.id]}}],
          ):
              message.unlink()
      ```
    </example>

    <example id="js_qunit_v17" title="QUnit JS test (v17)">
      ```javascript
      /* @odoo-module */

      import { startServer } from "@bus/../tests/helpers/mock_python_environment";
      import { start } from "@mail/../tests/helpers/test_utils";
      import { contains } from "@web/../tests/utils";

      QUnit.module("thread");

      QUnit.test("dragover files on thread with composer", async () => {
          const pyEnv = await startServer();
          const channelId = pyEnv["discuss.channel"].create({
              channel_type: "channel",
              name: "General",
          });
          const { openDiscuss } = await start();
          openDiscuss(channelId);
          await contains(".o-mail-Thread");
      });

      QUnit.test("verifies steps", async (assert) => {
          const { openDiscuss } = await start({
              mockRPC(route) {
                  if (route === "/discuss/channel/messages") {
                      assert.step("load messages");
                  }
              },
          });
          openDiscuss();
          assert.verifySteps(["load messages"]);
      });
      ```
    </example>

    <example id="js_hoot_v18" title="Hoot JS test (v18)">
      ```javascript
      // No @odoo-module in v18/v19
      import {
          click,
          contains,
          defineMailModels,
          openDiscuss,
          start,
          startServer,
          assertSteps,
          step,
          onRpcBefore,
      } from "@mail/../tests/mail_test_helpers";

      import { describe, expect, test } from "@odoo/hoot";
      import { Command, serverState } from "@web/../tests/web_test_helpers";

      describe.current.tags("desktop");
      defineMailModels();

      test("dragover files on thread with composer", async () => {
          const pyEnv = await startServer();
          const channelId = pyEnv["discuss.channel"].create({
              channel_type: "channel",
              name: "General",
          });
          await start();
          await openDiscuss(channelId);
          await contains(".o-mail-Thread");
      });

      test("verifies steps", async () => {
          const pyEnv = await startServer();
          const channelId = pyEnv["discuss.channel"].create({ name: "General" });
          onRpcBefore("/discuss/channel/messages", () => step("load messages"));
          await start();
          await openDiscuss(channelId);
          await assertSteps(["load messages"]);
      });
      ```
    </example>

    <example id="js_hoot_v19" title="Hoot JS test (v19)">
      ```javascript
      // v19: asyncStep + waitForSteps replace step + assertSteps
      import {
          click,
          contains,
          defineMailModels,
          listenStoreFetch,
          openDiscuss,
          start,
          startServer,
          waitStoreFetch,
      } from "@mail/../tests/mail_test_helpers";

      import { describe, expect, test } from "@odoo/hoot";
      import {
          asyncStep,
          Command,
          serverState,
          waitForSteps,
          withUser,
      } from "@web/../tests/web_test_helpers";

      describe.current.tags("desktop");
      defineMailModels();

      test("async step tracking (v19)", async () => {
          const pyEnv = await startServer();
          const channelId = pyEnv["discuss.channel"].create({ name: "General" });
          await start();
          await openDiscuss(channelId);
          // asyncStep is used for async event tracking
          await waitForSteps([]);
      });
      ```
    </example>

    <example id="running_tests" title="Running tests from CLI">
      ```bash
      # Run all tests for a module
      ./odoo-bin -d testdb -i my_module --test-enable --stop-after-init

      # Run a specific tagged test class
      ./odoo-bin -d testdb --test-tags my_module.TestMyModel

      # Run JS tests (v18/v19 with Hoot runner)
      ./odoo-bin -d testdb -i my_module --test-enable --stop-after-init \
          --test-tags /my_module:TestMyModel
      ```
    </example>

  </examples>

  <antipatterns>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG — test data inside individual test methods (N-fold DB writes)
      def test_create_record(self):
          company = self.env['res.company'].create({'name': 'Co'})
          user = self.env['res.users'].create({'name': 'U', 'login': 'u'})
          record = self.env['my.model'].create({'name': 'R'})
          # ...

      # CORRECT — shared data in setUpClass
      @classmethod
      def setUpClass(cls):
          super().setUpClass()
          cls.company = cls.env['res.company'].create({'name': 'Co'})
          cls.user = cls.env['res.users'].create({'name': 'U', 'login': 'u'})
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG — setUpClass without super() first
      @classmethod
      def setUpClass(cls):
          cls.partner = cls.env['res.partner'].create(...)  # env not ready yet
          super().setUpClass()

      # CORRECT — super() must be the very first call
      @classmethod
      def setUpClass(cls):
          super().setUpClass()
          cls.partner = cls.env['res.partner'].create(...)
      ```
    </antipattern>

    <antipattern severity="CRITICAL">
      ```python
      # WRONG — catching generic Exception for access control (misses the point)
      with self.assertRaises(Exception):
          self.env['my.model'].with_user(user).read([record.id])

      # CORRECT — assert the specific exception type
      from odoo.exceptions import AccessError
      with self.assertRaises(AccessError):
          self.env['my.model'].with_user(user).read([record.id])
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG — missing @tagged, test runs at_install before all modules load
      class TestMyModel(TransactionCase):
          def test_something(self):
              ...

      # CORRECT
      @tagged('post_install', '-at_install')
      class TestMyModel(TransactionCase):
          def test_something(self):
              ...
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```python
      # WRONG — v18 code using removed check_access_rule()
      result = record.check_access_rule('read')  # AttributeError in v18+

      # CORRECT for v18/v19
      has_read = record.has_access('read')
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```javascript
      // WRONG — QUnit API in v18/v19 (framework replaced by Hoot)
      QUnit.module("my tests");
      QUnit.test("something", async (assert) => {
          assert.step("called");
          assert.verifySteps(["called"]);
      });

      // CORRECT for v18/v19
      import { describe, test } from "@odoo/hoot";
      import { assertSteps, step } from "@mail/../tests/mail_test_helpers";
      describe.current.tags("desktop");
      test("something", async () => {
          step("called");
          await assertSteps(["called"]);
      });
      ```
    </antipattern>

    <antipattern severity="HIGH">
      ```javascript
      // WRONG — @odoo-module in v18/v19 (not required, ignored)
      /* @odoo-module */
      import { describe, test } from "@odoo/hoot";

      // CORRECT for v18/v19 — no pragma needed
      import { describe, test } from "@odoo/hoot";
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # WRONG — hardcoded database IDs
      record = self.env['my.model'].browse(42)

      # CORRECT — resolve by xml_id or search
      record = self.env.ref('my_module.my_demo_record')
      record = self.env['my.model'].search([('name', '=', 'Demo')], limit=1)
      ```
    </antipattern>

    <antipattern severity="MEDIUM">
      ```python
      # WRONG — test not registered in tests/__init__.py (will never run)
      # tests/__init__.py is empty or missing the import

      # CORRECT
      # tests/__init__.py
      from . import test_my_model
      from . import test_security
      ```
    </antipattern>

  </antipatterns>

</pattern>