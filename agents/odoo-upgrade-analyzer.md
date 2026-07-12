---
name: odoo-upgrade-analyzer
description: Odoo module migration analysis and upgrade plan between versions 17, 18 and 19.
disable-model-invocation: true
---

Analyze an existing module for upgrade compatibility. Do not generate new code.

---

## Step 1 — Identify versions

- Source: from `__manifest__.py` version field
- Target: from user
- If either unknown, **stop and ask**.

## Step 2 — Reasoning block

```
UPGRADE ANALYSIS:
- Source: [X] → Target: [Y]
- Path: [X → Y or X → 18 → Y]
- Migration guides to load: [list]
- Breaking changes: [list]
```

## Step 3 — Load migration guides

**17→18:** `odoo-model-patterns-17-18.md`, `odoo-security-guide-17-18.md`, `odoo-module-generator-17-18.md`, `odoo-owl-components-17-18.md`

**18→19:** same pattern with `-18-19.md` files

**17→19:** load both sets in order.

## Step 4 — Systematic analysis

Check every category against module files. Flag with file + line.

**Categories:** Python (decorators, imports, APIs), XML (attrs, widgets, chatter, list tag), Security (record rules, company checks), JS/OWL (@odoo-module, services), Data file ordering.

## Step 5 — Output report

```
# Upgrade Analysis: {module_name}
## Path: {source} → {target}

### Summary
- Complexity: Low/Medium/High
- Breaking changes: N
- Files affected: N

### Breaking changes — must fix
#### BC-001: {title}
Category: Python/XML/JS | Severity: Critical/High
Files: file:line
Current: [old] | Required: [new]
Steps: 1. ... 2. ...

### Data file order check
security.xml → ir.model.access.csv → views → menus

### Migration checklist
Pre: [ ] Backup, [ ] Review BCs, [ ] Prepare scripts
During: [ ] Fix BC-001, [ ] Update manifest version
Post: [ ] Run tests, [ ] Fix deprecations, [ ] Verify functionality
```