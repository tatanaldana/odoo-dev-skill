# Session Context & History Log

`odoo-dev-skill` documents a convention for two files that let an assistant (Claude
Code or otherwise) keep track of what it's working on and leave a trail of what it did.
Full lifecycle rules live in [`SKILL.md`](../SKILL.md) under `<context_management>`.
Blank templates live in [`templates/context_session.xml`](../templates/context_session.xml)
and [`templates/history_context.xml`](../templates/history_context.xml).

| File | Scope | Size | Purpose |
|---|---|---|---|
| `context_session.xml` | one task/session | capped ~12,000 chars | working memory for the *current* task — module, models, patterns loaded, decisions, open questions |
| `history_context.xml` | across sessions | unbounded, append-only | one compact `<session>` entry per finished task — an audit trail, and eventually a dataset for fine-tuning or RAG |

Both live at `.claude/odoo-dev-skill/` in the project where the skill is being used
(not inside this skill repo). Add that folder to `.gitignore` unless your team wants a
shared, versioned audit trail.

---

## Starting a session

**Prose:**
> Antes de seguir, revisa si existe `.claude/odoo-dev-skill/context_session.xml`. Si
> describe la misma tarea, retómala desde ahí en vez de que me repitas preguntas que ya
> respondí.

**XML-structured:**
```xml
<request>
  <task>resume_or_init_session</task>
  <session_file>.claude/odoo-dev-skill/context_session.xml</session_file>
</request>
```

---

## Updating it mid-task

**Prose:**
> Ya creamos el modelo `library.book` y la vista de formulario. Actualiza
> `context_session.xml` con esos dos archivos y la decisión de usar `Many2one` a
> `res.partner` para el autor.

A filled-in `context_session.xml` after a couple of steps looks like:

```xml
<context_session id="lib-mgmt-2026-07-02" started="2026-07-02T10:15:00-05:00"
                  odoo_version="18" max_chars="12000">
  <task>
    <description>Build library management module</description>
    <module>library_management</module>
    <models>library.book, library.author</models>
  </task>
  <state>
    <patterns_loaded>
      <pattern file="skills/odoo-model-patterns-18.md"/>
      <pattern file="skills/xml-view-patterns.md"/>
    </patterns_loaded>
    <files_touched>
      <file path="models/library_book.py" action="created"/>
      <file path="views/library_book_views.xml" action="created"/>
    </files_touched>
    <decisions>
      <decision>author_id is Many2one to res.partner, not a new library.author model.</decision>
    </decisions>
    <open_questions>
      <question>Should "available" be computed from stock.quant or a manual toggle?</question>
    </open_questions>
  </state>
</context_session>
```

---

## Closing a session

**Prose:**
> Terminamos con este módulo. Agrega un resumen a `history_context.xml` y reinicia
> `context_session.xml` para la próxima tarea.

**XML-structured:**
```xml
<request>
  <task>close_session</task>
  <session_file>.claude/odoo-dev-skill/context_session.xml</session_file>
  <history_file>.claude/odoo-dev-skill/history_context.xml</history_file>
</request>
```

The resulting entry appended to `history_context.xml`:

```xml
<session id="lib-mgmt-2026-07-02" started="2026-07-02T10:15:00-05:00"
         ended="2026-07-02T11:40:00-05:00" odoo_version="18">
  <summary>Created library_management module with library.book model, form/list views and access rights.</summary>
  <module>library_management</module>
  <patterns_used>
    <pattern file="skills/odoo-model-patterns-18.md"/>
    <pattern file="skills/xml-view-patterns.md"/>
  </patterns_used>
  <files_changed>
    <file path="models/library_book.py" action="created"/>
    <file path="views/library_book_views.xml" action="created"/>
  </files_changed>
  <outcome status="completed"/>
</session>
```

---

## Making it stick: the optional Stop hook

The lifecycle above depends on the assistant remembering to update these
files — which, in long sessions, it will eventually forget. `hooks/context_session_guard.py`
is a Claude-Code-specific, stdlib-only Stop hook that closes that gap
mechanically:

- Blocks stopping if `context_session.xml` exceeds the ~12,000 char budget.
- Blocks stopping if any tracked/untracked file changed more recently than
  `context_session.xml` was last written (via `git status --porcelain`),
  asking the assistant to update it — and archive into `history_context.xml`
  if the task is actually done — before finishing.
- Fails open: no `context_session.xml` present, no git repo, or git missing
  → it allows the stop silently. It only enforces discipline once you've
  opted in by creating the file for a task.

Wire it in the consuming project's `.claude/settings.json`, using the
**absolute path** to wherever the skill was installed (global installs live
outside the project, so a bare relative path like `hooks/context_session_guard.py`
won't resolve from the project's cwd):

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [{ "type": "command", "command": "python3 /absolute/path/to/odoo-dev-skill/hooks/context_session_guard.py" }] }
    ]
  }
}
```

This is optional — nothing else in the skill depends on it — and it's the
only piece of this convention that's Claude-Code-specific rather than
IDE-agnostic. Like `checks/odoo_lint.py`, it assumes an assistant that can
read files and run shell commands — the norm for coding-focused agents, but
worth calling out explicitly since not every `skills.sh`-compatible surface
guarantees it.

---

## Why this matters long-term

Every finished `<session>` in `history_context.xml` is a compact, structured record of
a real task: the request, the patterns applied, the files touched, and the outcome.
That's exactly the shape of data needed to later evaluate how well the skill performs,
or to build a fine-tuning / RAG dataset from real usage instead of synthetic examples.
Keeping entries terse and structured now is what makes that possible later.
