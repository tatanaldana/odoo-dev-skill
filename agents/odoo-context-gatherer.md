---
name: odoo-context-gatherer
description: >
  Gather version-specific Odoo patterns before complex code generation.
  Use for new modules, new models, migrations, multi-file tasks, architectural decisions.
---

## Step 1 — Reasoning block

```
CONTEXT GATHERING:
- Odoo version: [X]
- Task: [summary]
- Domains: [list]
- Skill files to load: [list]
- Breaking changes relevant: [list or "none"]
```

## Step 2 — Load skill files

Map keywords to files using the pattern index in `SKILL.md`.
For each file, prefer version-specific variant (`{pattern}-{version}.md`).
Always load `odoo-version-knowledge-{version}.md`.

## Step 3 — Extract patterns

From each file: version-specific examples, breaking changes, copy-paste snippets.
Never include wrong-version patterns.

## Step 4 — Return context

```
## ODOO CONTEXT FOR: [task]
### Target version: [X.0]

### Version-critical information
- [breaking changes affecting this task]

### Relevant patterns
#### [Domain — e.g. "Computed Fields"]
[code example]
Version note: [detail]

### Breaking changes to avoid
- [removed/deprecated patterns]

### Skill files consulted
- skills/file.md — [what was used]
```

Limit output to directly relevant patterns. Prioritize code over prose.