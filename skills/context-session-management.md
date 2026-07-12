# Context Session Management

Automatic behavior — no special prompts required from the user.

---

## Step 1 — Resolve the skill installation path (once per task)

| Platform | Path |
|---|---|
| Linux / macOS | `$HOME/.claude/skills/odoo-dev-skill` |
| Windows | `%USERPROFILE%\.claude\skills\odoo-dev-skill` |

Used only to build the warning message in Step 2 if hooks are missing. If
the environment variable is unavailable, omit the path and direct the user
to run `npx github:tatanaldana/odoo-dev-skill init` from the project root.

## Step 2 — Verify hooks are configured in this project

Read `.claude/settings.json` in the project root and check whether
`context_session_guard.py` and `odoo_edit_guard.py` are already declared.

- **Both present** → proceed silently.
- **File missing or hooks absent** → inform the user once, briefly, then
  continue without blocking:

> "Los hooks de odoo-dev-skill no están configurados en este proyecto.
> Para activarlos desde la próxima sesión de Claude Code, ejecuta este
> comando desde la raíz del proyecto y reinicia Claude Code:
> `npx github:tatanaldana/odoo-dev-skill init`"

Do not write or modify `settings.json` — that's `init`'s job. Do not repeat
the warning later in the same session.

## Step 3 — Load or initialize `context_session.xml`

Check `.claude/odoo-dev-skill/context_session.xml`:
- Exists, same task → read once and resume; don't re-ask answered questions.
- Exists, different task → ask before overwriting.
- Missing → create `.claude/odoo-dev-skill/` if needed, then create
  `context_session.xml` from `templates/context_session.xml`, filling `id`
  (short slug), `started` (ISO timestamp), `odoo_version`.

## During the task

Hold state in memory. Write `context_session.xml` only at **logical
checkpoints** (a coherent unit of work complete — model + its views, not
file by file), setting `status="checkpoint"`. Don't re-read the file between
checkpoints; one read at session start is enough.

**Before responding**, if the user's message signals task completion, set
`status="completed"` and write the file — don't wait for the Stop hook.
The hook is a safety net, not the primary mechanism.

## Status lifecycle

| status | Set by | Stop hook behavior |
|---|---|---|
| `in_progress` | Default; task active | Checks char budget + stale files; blocks if either fails |
| `checkpoint` | Logical block just finished | Allows clean stop |
| `completed` | Agent detected task end | Archives to `history_context.xml`, resets file, allows stop |

**Signals for `completed`:**
- Explicit: "terminamos", "listo", "perfecto así", "esto es todo", "abre el PR",
  "mergea", "done", "ship it", "that's all"
- Implicit: user asks for a full module review, the final `__manifest__.py`
  with all files listed, or a lint run over the whole module

Keep `context_session.xml` under ~12,000 characters. Compress `<decisions>`
and `<files_touched>` into denser summaries if it grows too large.
