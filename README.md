# Odoo Development Universal Skill

A universal Odoo development skill for AI agents compatible with `skills.sh`. It provides fast code indexing, intelligent patterns, and strict adherence to Odoo Community Association (OCA) standards for versions **17, 18 and 19**.

This repository is a fork and adaptation of the Odoo plugin from [letzdoo/claude-marketplace](https://github.com/letzdoo/claude-marketplace), restructured to be 100% agnostic and compatible with any IDE that supports `skills.sh` (like Windsurf, Cursor, Cline, etc.).

---

## Features

- **Version Awareness**: Covers Odoo 17, 18 and 19, including all breaking changes and deprecated methods per version.
- **OCA Standards Strict Adherence**: Enforces PEP8, DRY, KISS, and SOLID principles.
- **OWL Compatibility**: Complete knowledge of OWL 2.x (v17-19) — `@odoo-module` required in v17, optional in v18/v19.
- **Specialized Agents**: 5 workflows for Context Gathering, Code Review, Upgrade Analysis, Skill Discovery, and Coding Guidelines Validation.
- **55 Skill Files**: Pattern families organized by feature domain, each with version-specific variants (v17, v18, v19, v17-18, v18-19) and a dispatcher.
- **XML Semantic Structure**: All files use semantic XML tags that help AI agents navigate content efficiently without reading everything.
- **Spanish by Default**: The agent communicates in Spanish (or the user's preferred language); code, variables, and docstrings are always in English.

---

## Installation

The skill installs directly from GitHub — no npm publish needed. Requires the repository to be public.

Install globally (available in all your projects):

```bash
npx skills add tatanaldana/odoo-dev-skill --global
```

Or install for a specific project only:

```bash
npx skills add tatanaldana/odoo-dev-skill
```

Once installed, the AI agent automatically reads `SKILL.md` when Odoo-related tasks are detected. You can verify the installation with:

```bash
npx skills list
```

### How it works

`npx skills add owner/repo` fetches `SKILL.md` and all referenced files from the GitHub repository. The frontmatter in `SKILL.md` registers the skill:

```yaml
name: odoo-dev-skill       # identifier used by the skill manager
versions: "17,18,19"       # metadata — which Odoo versions are covered
lang: es                   # the agent communicates in Spanish by default
```

No `package.json` or additional config files are required.

---

## Architecture

```text
odoo-development-skill/
├── SKILL.md                              # Main entrypoint — XML semantic structure
├── README.md                             # This documentation
├── agents/                               # 5 specialized workflow agents
│   ├── odoo-context-gatherer.md          # Gather context before generating complex code
│   ├── odoo-code-reviewer.md             # Quality and security audit
│   ├── odoo-upgrade-analyzer.md          # Migration analysis between versions
│   ├── odoo-skill-finder.md              # Navigate the pattern library
│   └── odoo-coding-guidelines-validator.md  # Validate against official Odoo guidelines
└── skills/                               # 55 pattern files (families + dispatchers)
    ├── odoo-version-knowledge.md         # dispatcher → v17 / v17-18 / v18 / v18-19 / v19
    ├── odoo-model-patterns.md            # dispatcher → v17 / v17-18 / v18 / v18-19 / v19
    ├── odoo-module-generator.md          # dispatcher → v17 / v17-18 / v18 / v18-19 / v19
    ├── odoo-owl-components.md            # dispatcher → v17 / v17-18 / v18 / v18-19 / v19
    ├── odoo-security-guide.md            # dispatcher → v17 / v17-18 / v18 / v18-19 / v19
    ├── odoo-performance-guide.md
    ├── odoo-test-patterns.md
    ├── inheritance-patterns.md
    ├── xml-view-patterns.md
    ├── qweb-template-patterns.md
    ├── wizard-patterns.md
    ├── workflow-state-patterns.md
    ├── controller-api-patterns.md
    ├── portal-access-patterns.md         # portal.mixin, CustomerPortal, pager, access tokens
    ├── mail-notification-patterns.md
    ├── report-patterns.md
    ├── external-api-patterns.md
    ├── widget-field-patterns.md
    ├── computed-field-patterns.md
    ├── constraint-patterns.md
    ├── domain-filter-patterns.md
    ├── context-environment-patterns.md
    ├── onchange-dynamic-patterns.md
    ├── assets-bundling-patterns.md
    ├── sequence-numbering-patterns.md
    ├── cron-automation-patterns.md
    ├── config-settings-patterns.md
    ├── multi-company-patterns.md
    ├── error-handling-patterns.md
    └── translation-i18n-patterns.md
```

---

## Optimization Techniques Applied

This fork applies 6 optimization techniques to make the AI agent more precise and efficient:

### 1. XML Semantic Structure
All files use semantic XML tags so the agent navigates content without reading everything:
```xml
<forbidden>        — what NEVER to do, with severity
<version_router>   — lazy load only the needed version file
<pattern_index>    — grouped by category, not a flat list
<severity_rules>   — CRITICAL / HIGH / MEDIUM priority
<fetch_strategy>   — when to fetch from the official repo
```

### 2. Explicit Negative Rules (`<forbidden>`)
Every file declares what NOT to do before what to do:
```xml
<forbidden>
  <never severity="CRITICAL">Use attrs= in v17+ — use invisible= instead</never>
  <never severity="HIGH">Call browse() inside a loop — use mapped() or filtered()</never>
  <never severity="MEDIUM">Omit _description in new models</never>
</forbidden>
```

### 3. Version Router with Lazy Loading
Loads only the knowledge file for the detected version — not all versions at once:
```xml
<version_router>
  <load version="17" file="skills/odoo-model-patterns-17.md"/>
  <breaking_changes>
    <change from="17" to="18">group_operator= → aggregator= | tree → list | oe_chatter div → chatter tag</change>
    <change from="18" to="19">models.Constraint() | models.Index() | SQL import from odoo.tools</change>
  </breaking_changes>
</version_router>
```

### 4. Mandatory Reasoning Block
The agent shows its analysis BEFORE writing any code:
```
ANALYSIS:
- Odoo version detected: 18
- Existing module found: yes → sale/models/sale_order.py
- Pattern to apply: skills/computed-field-patterns.md
- Breaking changes: group_operator= → aggregator= (v18)
- Files to modify: models/sale_order.py
```

### 5. Severity Rules
Rules are classified by impact so the agent prioritizes correctly in long conversations:
```
CRITICAL = breaks the module or causes data loss
HIGH     = silent bug, hard to detect in testing
MEDIUM   = OCA standards violation
```

### 6. v19 Base Examples + Dynamic Adaptation
Pattern files use v19 as the canonical reference and specify precisely which API changed in each version, so the agent adapts examples without guessing:
```
User on v19 → use inline example directly
User on v18 → apply v18 breaking changes (e.g. aggregator= not group_operator=)
User on v17 → apply v17 API (e.g. @odoo-module required, oe_chatter div)
```

---

## Agents

| Agent | File | When to use |
|---|---|---|
| Context Gathering | `agents/odoo-context-gatherer.md` | Before generating complex code |
| Code Review | `agents/odoo-code-reviewer.md` | Quality and security audit |
| Upgrade Analysis | `agents/odoo-upgrade-analyzer.md` | Migration between versions |
| Skill Discovery | `agents/odoo-skill-finder.md` | Navigate the pattern library |
| Guidelines Validator | `agents/odoo-coding-guidelines-validator.md` | Validate against official Odoo v19 guidelines |

### Guidelines Validator — what it checks

| Section | Rules | What it validates |
|---|---|---|
| Module structure | MS-01 to MS-04 | Directories, manifest, README.rst |
| Python naming | NP-01 to NP-05 | PascalCase, _id/_ids suffixes, method prefixes |
| Class structure | CS-01 to CS-03 | Attribute order, super() |
| ORM idioms | OI-01 to OI-08 | Raw SQL, loops, filtered/mapped, with_context |
| XML views | XV-01 to XV-05 | inherit/xpath, attrs vs invisible by version |
| Security | SEC-01 to SEC-04 | ir.model.access.csv, sudo(), SQL injection |
| JavaScript/OWL | JS-01 to JS-04 | File structure, OWL version per Odoo version |

---

## Usage

Once installed, your AI assistant automatically reads `SKILL.md` when Odoo-related tasks are requested. The assistant will:

1. **Detect** your Odoo version from `__manifest__.py`
2. **Show a reasoning block** before writing any code
3. **Search** existing Enterprise or Community modules before reinventing the wheel
4. **Load** the exact pattern needed from `skills/`
5. **Adapt** examples to your version, applying the correct breaking changes
6. **Validate** generated code against OCA and Odoo coding guidelines

### Running the Guidelines Validator

```
"Valida este código contra las guías de codificación de Odoo"
"Revisa si este modelo sigue los estándares OCA"
"Verifica este archivo por violaciones de guías"
```

The agent outputs a structured report:
```
## Validation Report — Odoo Coding Guidelines v19
| Severity | Count |
|----------|-------|
| CRITICAL | 1     |
| HIGH     | 2     |
| MEDIUM   | 1     |
| OK       | 14 rules |

### [CRITICAL] OI-01 — Raw SQL when ORM can do the same
Line: 45
Problem: self.env.cr.execute(...)
Fix: use search() or read_group() instead
Official rule: "Never use the database cursor directly when the ORM can do the same thing"
```

---

## Version Coverage

| Odoo Version | Status | OWL | Key Breaking Changes |
|---|---|---|---|
| 17 | Covered | 2.x | `attrs=` removed → `invisible=` \| `@api.model_create_multi` mandatory \| `@odoo-module` required in JS |
| 18 | Covered | 2.x | `group_operator=` → `aggregator=` \| `tree` → `list` \| `oe_chatter` div → `chatter` tag \| Hoot test framework |
| 19 | Covered | 2.x | `models.Constraint()` \| `models.Index()` \| `SQL` from `odoo.tools` \| `Domain` class \| `self.env._()` |

> Versions 15 and 16 were excluded — the breaking changes between v16 and v17 are significant enough that mixing them would reduce code quality rather than improve it.

---

## Contributing

Contributions, issues, and feature requests are welcome!

When contributing, please:
- Follow the [Odoo Coding Guidelines v19](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)
- Use the XML semantic structure defined in `OPTIMIZATION_GUIDE.md`
- Run the Guidelines Validator agent on any new pattern files before submitting

---

## References

| Resource | URL |
|---|---|
| Odoo Coding Guidelines v19 | https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html |
| Odoo ORM API v19 | https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html |
| Odoo Community (GitHub) | https://github.com/odoo/odoo |
| OCA Repositories | https://github.com/orgs/OCA/repositories |
| Original repo | https://github.com/fhidalgodev/odoo-development-skill |

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
