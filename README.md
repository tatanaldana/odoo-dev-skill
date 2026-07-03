# Odoo Development Universal Skill

A universal Odoo development skill for AI agents compatible with Claude Code. It provides fast code indexing, intelligent patterns, and strict adherence to Odoo Community Association (OCA) standards for versions **17, 18 and 19**.

This repository is a fork and adaptation of the Odoo plugin from [letzdoo/claude-marketplace](https://github.com/letzdoo/claude-marketplace), restructured to be 100% agnostic and compatible with any IDE that supports `skills.sh` (like Windsurf, Cursor, Cline, etc.).

---

## Features

- **Version Awareness**: Covers Odoo 17, 18 and 19, including all breaking changes and deprecated methods per version.
- **OCA Standards Strict Adherence**: Enforces PEP8, DRY, KISS, and SOLID principles.
- **OWL Compatibility**: Complete knowledge of OWL 2.x (v17/v18/v19 — confirmed in v19 source). `@odoo-module` required in v17, optional in v18/v19.
- **Specialized Agents**: 5 workflows for Context Gathering, Code Review, Upgrade Analysis, Skill Discovery, and Coding Guidelines Validation. 4 of 5 are user-invoked (zero context load); only the Context Gatherer is model-invoked.
- **31 Skill Files**: Pattern families organized by feature domain, each with version-specific variants (v17, v18, v19, v17-18, v18-19) and a dispatcher. Includes `fastapi-patterns.md` for OCA FastAPI integration.
- **XML Semantic Structure**: All `skills/` and `agents/` files use semantic XML tags that help AI agents navigate content efficiently. `SKILL.md` is plain markdown for immediate execution.
- **Spanish by Default**: The agent communicates in Spanish (or the user's preferred language); code, variables, and docstrings are always in English.

---

## Installation

### Step 1 — Install the skill globally (once)

```bash
npx github:tatanaldana/odoo-dev-skill
```

This copies `SKILL.md`, `agents/`, `skills/`, `hooks/`, and `templates/` into
`~/.claude/skills/odoo-dev-skill/` and `~/.agents/skills/odoo-dev-skill/`.
Claude Code picks up the skill automatically in every project from this point on.

Options:

```bash
# Install to Claude only
npx github:tatanaldana/odoo-dev-skill --target claude

# Install to ~/.agents only
npx github:tatanaldana/odoo-dev-skill --target agents

# Preview what would be installed without touching anything
npx github:tatanaldana/odoo-dev-skill --dry-run
```

### Step 2 — Initialize hooks in each Odoo project (once per project)

The skill works without this step, but the enforcement hooks
(`context_session_guard.py` and `odoo_edit_guard.py`) require a one-time
setup per project. Run this from the **root of each Odoo project**:

```bash
cd /path/to/my-odoo-project
npx github:tatanaldana/odoo-dev-skill init
```

Then **restart Claude Code** so it picks up the new hooks.

What `init` does:
- Resolves the absolute path to the globally installed hooks
- Creates `.claude/settings.json` if it does not exist, or merges the hooks
  into it if it does — never overwrites existing keys
- Works on Linux, macOS, and Windows

```bash
# Preview what would be written without touching anything
npx github:tatanaldana/odoo-dev-skill init --dry-run
```

> **Note:** You only need to run `init` once per project. The global install
> is done once for all projects. When you start a new Odoo project, `cd` into
> it and run `init` again before your first Claude Code session.

### Local development — clone and link

If you want to edit the skill and see changes immediately without reinstalling:

```bash
git clone https://github.com/tatanaldana/odoo-dev-skill
cd odoo-dev-skill
chmod +x link_skills.sh
./link_skills.sh
```

This creates symlinks from `~/.claude/skills/odoo-dev-skill/` and
`~/.agents/skills/odoo-dev-skill/` to your local repo. Any edit to `agents/`,
`skills/`, or `hooks/` is picked up by Claude Code immediately.

Then run `init` in each project as usual:

```bash
cd /path/to/my-odoo-project
npx github:tatanaldana/odoo-dev-skill init
```

---

## Architecture

```text
odoo-dev-skill/
├── SKILL.md                              # Main entrypoint — plain markdown, executes immediately
├── README.md                             # This documentation
├── package.json                          # npm installer declaration
├── bin/
│   └── install.js                        # npx installer — copies agents/ and skills/ on install
├── scripts/
│   └── link-skills.sh                    # local dev — symlinks repo into ~/.claude/skills/
├── agents/                               # 5 specialized workflow agents
│   ├── odoo-context-gatherer.md          # model-invoked — gather context before complex code
│   ├── odoo-code-reviewer.md             # user-invoked — quality and security audit
│   ├── odoo-upgrade-analyzer.md          # user-invoked — migration analysis between versions
│   ├── odoo-skill-finder.md              # user-invoked — navigate the pattern library
│   └── odoo-coding-guidelines-validator.md  # user-invoked — validate against official Odoo guidelines
├── examples/                              # Sample prompts for each agent/pattern
├── templates/                             # context_session.xml / history_context.xml starters
├── checks/                                # odoo_lint.py — stdlib-only static pre-check
├── hooks/                                 # optional Claude Code Stop hook (context discipline)
└── skills/                               # 31 pattern files (families + dispatchers)
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
    ├── fastapi-patterns.md               # FastAPI + OCA rest-framework, Pydantic schemas, versioned APIs
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

## Design Principles

### SKILL.md — plain markdown for immediate execution

The orchestrator (`SKILL.md`) is written in plain markdown so Claude Code
reads and executes it immediately on load. It classifies every task into one
of two branches:

- **Simple** — single file, single field, quick fix: applies forbidden rules,
  looks up the pattern index, writes code.
- **Complex** — new module, migration, multiple files, architectural decision:
  delegates to `agents/odoo-context-gatherer.md` which drives from there.

### skills/ and agents/ — XML semantic structure

Pattern files and agent files use semantic XML tags so the agent navigates
their content without reading everything:

```xml
<pattern>          — root of every skills/ file
<description>      — what the pattern does and when to use it
<version_notes>    — per-version differences
<examples>         — verified code snippets
<antipatterns>     — what not to do, with severity
```

```xml
<agent>            — root of every agents/ file
<use_when>         — when to invoke this agent
<workflow>         — sequential steps with completion criteria
<review_categories>— checklist items per category
<output_format>    — exact structure of the report
```

### Agent invocation model

| Agent | Type | Why |
|---|---|---|
| `odoo-context-gatherer` | model-invoked | SKILL.md calls it on complex tasks |
| `odoo-code-reviewer` | user-invoked | only fires when user asks for a review |
| `odoo-upgrade-analyzer` | user-invoked | only fires when user asks for a migration |
| `odoo-skill-finder` | user-invoked | only fires on explicit pattern lookup |
| `odoo-coding-guidelines-validator` | user-invoked | only fires on explicit validation request |

User-invoked agents carry `disable-model-invocation: true` in their
frontmatter — they pay zero context load per turn.

---

## Agents

| Agent | File | When to use |
|---|---|---|
| Context Gathering | `agents/odoo-context-gatherer.md` | Before generating complex code |
| Code Review | `agents/odoo-code-reviewer.md` | Quality and security audit |
| Upgrade Analysis | `agents/odoo-upgrade-analyzer.md` | Migration between versions |
| Skill Discovery | `agents/odoo-skill-finder.md` | Navigate the pattern library |
| Guidelines Validator | `agents/odoo-coding-guidelines-validator.md` | Validate against official Odoo guidelines |

### Static pre-check (`checks/odoo_lint.py`)

Both `odoo-code-reviewer` and `odoo-coding-guidelines-validator` run this
stdlib-only Python script before their own analysis. It mechanically catches
raw SQL (`cr.execute`), possible SQL injection, `attrs=` in views, missing
`self.ensure_one()`, `browse()`/`search()` inside loops, manual
`cr.commit()`/`cr.rollback()`, `super()` with arguments, `print()`, and
models missing an `ir.model.access.csv` entry. It never blocks anything
(exit code always 0); its output is a checklist of candidates for the agent
to confirm.

```bash
python3 /path/to/odoo-dev-skill/checks/odoo_lint.py path/to/module --odoo-version 18
python3 /path/to/odoo-dev-skill/checks/odoo_lint.py path/to/module --format json
```

### Real-time CRITICAL feedback (`hooks/odoo_edit_guard.py`)

An optional Claude-Code-specific `PostToolUse` hook that runs
`checks/odoo_lint.py` against a file right after it is edited — not the
whole project, just that file — and only interrupts when a **CRITICAL** issue
was just introduced (SQL injection, raw SQL, manual commit/rollback, `attrs=`).
HIGH/MEDIUM findings are left for the full review agents.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 /absolute/path/to/odoo-dev-skill/hooks/odoo_edit_guard.py" }]
      }
    ]
  }
}
```

### Guidelines Validator — what it checks

| Section | Rules | What it validates |
|---|---|---|
| Module structure | MS-01 to MS-04 | Directories, manifest, README.rst |
| Python naming | NP-01 to NP-05 | PascalCase, _id/_ids suffixes, method prefixes |
| Class structure | CS-01 to CS-03 | Attribute order, super() |
| ORM idioms | OI-01 to OI-08 | Raw SQL, loops, filtered/mapped, with_context |
| XML views | XV-01 to XV-05 | inherit/xpath, invisible= (attrs= removed in v17) |
| Security | SEC-01 to SEC-04 | ir.model.access.csv, sudo(), SQL injection |
| JavaScript/OWL | JS-01 to JS-04 | File structure, OWL 2.x for v17/v18/v19 |
| Docstrings & method size | DC-01 to DC-02 | Docstring on non-trivial methods, 50-60 line alert |
| Performance | SR-01 to SR-03 | search_read over N+1, depends subfield path, index=True |
| Logging | LG-01 to LG-04 | Logger at module level, correct levels, no empty except, error message quality |

---

## Usage

Once installed, Claude Code automatically reads `SKILL.md` when Odoo-related
tasks are requested. The assistant will:

1. **Detect** your Odoo version from `__manifest__.py`
2. **Classify** the task as simple or complex
3. **Simple tasks** — check forbidden rules, Read the relevant pattern file, write code
4. **Complex tasks** — Read `agents/odoo-context-gatherer.md` which loads relevant
   skill files and compiles version-specific patterns before any code is written
5. **Validate** generated code against OCA and Odoo coding guidelines on request

### Running the agents

```
# Code review
"Review this module for quality and security issues"

# Upgrade analysis
"Analyze this module for migration from v17 to v18"

# Guidelines validation
"Validate this code against the Odoo coding guidelines"

# Pattern lookup
"Find the pattern for a computed field with inverse"

# FastAPI API development
"Create a FastAPI endpoint to expose sale orders"
```

---

## Context Management

`SKILL.md` defines a convention for two files that track the assistant's
work over time:

- **`context_session.xml`** — working memory for the current task, capped at
  ~12,000 characters. Read at session start to resume prior context.
- **`history_context.xml`** — append-only log, one compact entry per finished
  session. Auditable over time; intended as raw material for future fine-tuning
  or RAG datasets.

Blank starters live in [`templates/`](templates/). An optional Claude-Code-specific
Stop hook ([`hooks/context_session_guard.py`](hooks/context_session_guard.py))
enforces the convention mechanically.

---

## Version Coverage

| Odoo Version | Status | OWL | Key Breaking Changes |
|---|---|---|---|
| 17 | Covered | 2.x | `attrs=` removed → `invisible=` \| `@api.model_create_multi` mandatory \| `@odoo-module` required in JS |
| 18 | Covered | 2.x | `group_operator=` → `aggregator=` \| `<tree>` → `<list>` \| `oe_chatter` div → `<chatter/>` tag \| Hoot test framework |
| 19 | Covered | 2.x | `models.Constraint()` \| `models.Index()` \| `SQL` from `odoo.tools` \| `Domain` class \| `self.env._()` |

OWL 3.x is expected in v20 — not in v19. Confirmed against v19 source code.

Versions below 17 are excluded — the breaking changes between v16 and v17
are significant enough that mixing them would reduce code quality.

This coverage window is intentionally frozen between refreshes — see
[`MAINTENANCE.md`](MAINTENANCE.md) for the update policy.

---

## Contributing

Contributions, issues, and feature requests are welcome.

When contributing, please:
- Follow the [Odoo Coding Guidelines v19](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)
- `SKILL.md` must stay in plain markdown — no XML in the orchestrator body
- `skills/` files use `<pattern>` root with `description`, `version_notes`, `examples`, `antipatterns`
- `agents/` files use `<agent>` root with `use_when`, `workflow`, and completion criteria on each step
- Run the Guidelines Validator on any new pattern files before submitting

---

## References

| Resource | URL |
|---|---|
| Odoo Coding Guidelines v19 | https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html |
| Odoo ORM API v19 | https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html |
| Odoo Community (GitHub) | https://github.com/odoo/odoo |
| OCA Repositories | https://github.com/orgs/OCA/repositories |
| OCA FastAPI addon | https://github.com/OCA/rest-framework/tree/18.0/fastapi |
| Original repo | https://github.com/fhidalgodev/odoo-development-skill |

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.