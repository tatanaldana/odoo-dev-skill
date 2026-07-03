---
name: odoo-skill-finder
description: Precise pattern lookup in the skills library — returns file path, section, and a focused code excerpt.
disable-model-invocation: true
---

Targeted lookup for a specific code pattern or snippet from the skills
library. Not a replacement for `odoo-context-gatherer` — use that for
full context before code generation.

---

## Step 1 — Reasoning block

Output this before the lookup:

```
SKILL LOOKUP:
- Query: [what the user needs]
- Keywords identified: [list]
- Candidate skill files: [list matched from SKILL.md pattern index]
- Strategy: [single file — return excerpt | multiple files — return paths only]
```

Completion criterion: at least one candidate file identified.

---

## Step 2 — Find the skill file

1. Read `SKILL.md` pattern index.
2. Match query keywords to `keywords` entries.
3. Identify the best-matching `skills/` file.
4. If a version-specific variant exists (`skills/{pattern}-{version}.md`),
   prefer it over the generic file.

Completion criterion: one file selected, or multiple candidates listed
for the user to choose from.

---

## Step 3 — Extract excerpt

1. Read the skill file.
2. Find the most relevant section for the query.
3. Extract only the relevant excerpt — never exceed 50 lines.
4. Note the section name.

Completion criterion: excerpt identified, section named, line range noted.

---

## Step 4 — Return result

Use the [Output format](#output-format) below.

Completion criterion: result delivered in the correct format.

---

## Output format

**Single match — return excerpt:**
```
FILE: skills/{file}.md
SECTION: {section name}

{20-50 lines of relevant content}
```

**Multiple matches — return paths only:**
```
MULTIPLE MATCHES FOUND:
- skills/file-a.md → {why relevant}
- skills/file-b.md → {why relevant}

Load the most specific one for your context.
```

**No match:**
```
NO DIRECT MATCH
Closest files:
- skills/{closest}.md → {partial relevance}

Suggestion: retry with keywords: [{alternative keywords}]
```