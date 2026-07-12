---
name: odoo-skill-finder
description: Precise pattern lookup in the skills library — returns file path, section, and a focused code excerpt.
disable-model-invocation: true
---

Targeted lookup for a specific code pattern. Not a replacement for `odoo-context-gatherer`.

---

## Step 1 — Reasoning block

```
SKILL LOOKUP:
- Query: [what needed]
- Keywords: [list]
- Candidate files: [from SKILL.md pattern index]
- Strategy: [single → excerpt | multiple → paths only]
```

## Step 2 — Find file

Match query keywords to SKILL.md pattern index. Prefer version-specific variant if it exists.

## Step 3 — Extract excerpt (max 50 lines)

## Step 4 — Return result

**Single match:**
```
FILE: skills/{file}.md
SECTION: {section}
{20-50 lines}
```

**Multiple matches:**
```
MULTIPLE MATCHES:
- skills/file-a.md → {why}
- skills/file-b.md → {why}
```

**No match:**
```
NO DIRECT MATCH
Closest: skills/{file}.md → {partial relevance}
Retry with: [{alt keywords}]
```