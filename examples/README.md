# Examples

Sample prompts that get the best results out of `odoo-dev-skill`. They're grouped by
scenario so you can copy the closest match and adapt it to your case.

Prompts are written in Spanish because the skill communicates in Spanish by default
(`lang: es` in `SKILL.md`). Generated code, variables and docstrings stay in English
regardless of the prompt language.

## Why this matters

The skill relies on keyword matching against the "Pattern index" table in
[`SKILL.md`](../SKILL.md) to decide which pattern file to load and whether to route to
`agents/odoo-context-gatherer.md`. A vague prompt gives it less to match against, so it
may load the wrong pattern file or skip version-specific breaking changes. See
[`bad-vs-good-prompts.md`](bad-vs-good-prompts.md) for a direct comparison.

## Index

| File | Covers |
|---|---|
| [`common-tasks.md`](common-tasks.md) | Everyday prompts: new model, inheritance, views, wizards, controllers, security, performance |
| [`bad-vs-good-prompts.md`](bad-vs-good-prompts.md) | Side-by-side of weak vs. well-formed prompts and why the difference matters |
| [`xml-structured-prompts.md`](xml-structured-prompts.md) | XML-tagged prompts for precise, unambiguous specs (developer-oriented alternative to prose) |
| [`context-session-and-history.md`](context-session-and-history.md) | How to use `context_session.xml` and `history_context.xml` to track work across turns and sessions |
| [`agent-context-gatherer.md`](agent-context-gatherer.md) | Prompts that trigger `odoo-context-gatherer` before complex code generation |
| [`agent-code-reviewer.md`](agent-code-reviewer.md) | Prompts that trigger `odoo-code-reviewer` for quality/security audits |
| [`agent-upgrade-analyzer.md`](agent-upgrade-analyzer.md) | Prompts that trigger `odoo-upgrade-analyzer` for version migrations |
| [`agent-skill-finder.md`](agent-skill-finder.md) | Prompts that trigger `odoo-skill-finder` to navigate the pattern library |
| [`agent-guidelines-validator.md`](agent-guidelines-validator.md) | Prompts that trigger `odoo-coding-guidelines-validator` |

## General tips for writing prompts

1. **State the Odoo version** if `__manifest__.py` isn't in reach or you want to force a
   specific version file (`skills/{pattern}-{version}.md`).
2. **Name the model or module** you're working on — it helps the skill decide whether to
   search for existing code before generating new code.
3. **Say what kind of change it is** (new model, inherited view, wizard, controller,
   migration) — this maps directly to a row in the "Pattern index" table.
4. **For migrations**, mention both versions explicitly (e.g. "de v17 a v18") so the
   skill loads the migration guide file instead of a single-version file.
5. **For reviews/validation**, point at the file or module, not just "revisa mi código".
