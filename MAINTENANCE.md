---
current_window: "17,18,19"
next_trigger_version: 21
last_reviewed: 2026-07-02
cadence: "batch refresh every 2 new Odoo major releases"
---

# Version Maintenance Plan

`odoo-dev-skill` covers a **rolling 3-version window** (currently 17, 18, 19),
following the same reasoning already used to exclude v15/v16: "the breaking
changes between v16 and v17 are significant enough that mixing them would
reduce code quality rather than improve it." Applying that reasoning on
every single Odoo release would mean touching every pattern file every
year. Instead, this skill updates its version window in a **single batch,
every 2 new Odoo major releases**, and stays frozen in between.

## Why every 2 versions, not every 1

- Odoo ships one major version per year. Refreshing on every release means
  constant partial-coverage churn (add one version, maybe drop one, repeat
  annually) with no natural checkpoint to also re-validate the whole window
  for consistency.
- Batching two releases into one refresh means: fewer, larger, more
  deliberate updates; a natural point to re-validate the whole
  the "Pattern index" and "Breaking changes" tables in `SKILL.md` at once instead of
  incrementally drifting; and a skill that's explicitly "stable, no action
  needed" for a full release cycle — which is what should be communicated to
  anyone installing it.
- The tradeoff: for one release's worth of time, the skill won't have
  same-day coverage of the newest Odoo version. That's an acceptable cost
  for a community skill; adjust the cadence to "every release" if this ever
  needs to track Odoo day-one.

## Current state

| | |
|---|---|
| Current window | 17, 18, 19 (see `current_window` above) |
| Status | **Stable — no action needed** until the trigger condition below is met |
| Next trigger | Odoo **21** GA release (see `next_trigger_version` above) |
| Last reviewed | 2026-07-02 |

## Trigger condition

> Run the refresh checklist below when Odoo **21** reaches general
> availability. Until then, this skill's version coverage does not change.

When that happens, update the frontmatter of this file
(`current_window`, `next_trigger_version`, `last_reviewed`) as part of the
refresh, so the next trigger point is always visible at a glance.

## Refresh checklist (run once, when triggered)

1. **Research** — for both new versions (v20 and v21), gather the official
   breaking changes from the Odoo developer changelog
   (`https://www.odoo.com/documentation/{version}.0/developer/reference/backend/orm.html#changelog`)
   and release notes. Use `odoo-context-gatherer`'s principle here too:
   check what Odoo core already changed before writing new pattern guidance.
2. **Add new version files** — for every family in
   `<versioned_families>` (`odoo-version-knowledge`, `odoo-model-patterns`,
   `odoo-module-generator`, `odoo-owl-components`, `odoo-security-guide`),
   create `skills/{family}-20.md`, `skills/{family}-21.md`, and migration
   guides `skills/{family}-19-20.md` and `skills/{family}-20-21.md`.
3. **Drop the floor version** — since the window stays at 3 versions, retire
   v17: remove `skills/{family}-17.md` and `skills/{family}-17-18.md` from
   active coverage. Don't delete them outright in the same commit — move
   them to a clearly-marked `skills/archive/` or note in the PR that they're
   superseded, so anyone still on v17 can find them in git history.
4. **Update `SKILL.md`** — the "Pattern index" table's versioned-families
   note and the "Breaking changes (quick ref)" table, and the `versions:`
   frontmatter field.
5. **Update `README.md`** — the "Version Coverage" table and the versions
   listed in Features/Installation.
6. **Update `agents/odoo-code-reviewer.md` and
   `agents/odoo-coding-guidelines-validator.md`** — their `<version_checks>`
   blocks and frontmatter `version:`/`versions:` fields.
7. **Self-validate** — run `odoo-coding-guidelines-validator` against a
   couple of the new pattern files' code examples as a sanity check that
   they're internally consistent (correct imports, no stale-version syntax).
8. **Update this file's frontmatter** — new `current_window`,
   `next_trigger_version` (+2 from the version just added), `last_reviewed`.

## Kicking it off

Example prompt to drive step 1-2 with `odoo-upgrade-analyzer` and
`odoo-skill-finder` once the trigger condition is met:

> Odoo 21 ya salió. Sigue el checklist de `MAINTENANCE.md` para actualizar
> el skill: investiga los breaking changes de v20 y v21, y dime qué archivos
> de `skills/` necesitan una versión nueva antes de que empecemos a escribirlos.
