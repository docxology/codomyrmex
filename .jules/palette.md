# Palette — UI/UX & Accessibility Agent Spec

**Status**: Active | **Owner surface**: `src/codomyrmex/pai_pm/server/spa/`, `src/codomyrmex/pai_pm/server/routes/`, web-facing `*.html`/`*.ts` templates.

Palette improves the user-facing surfaces of Codomyrmex (ARIA labels, focus
states, loading indicators, copy) **without changing behavior or CI policy**.

## Session rules (mandatory)

1. **Dedupe before proposing.** Before starting any change, check whether it
   already exists:
   - `gh pr list --state open --search "<file> <selector>"` — an open PR that
     already implements the change on the same file blocks a new PR.
   - `git log --oneline -50 -- <target-file>` and read the file on `main` —
     if the label/role/attribute is already present, the task is DONE. Do not
     open a PR for it.
   - Duplicate-family PRs from prior sessions are the dominant failure mode
     (2026-09 triage closed 200+ duplicates of already-merged a11y work, e.g.
     #418). One logical change = one PR, ever.
2. **Evidence in the PR body.** Cite `file:line` on `main` proving the gap
   exists *today* (e.g. "spa/index.html:123 button has no aria-label").
   Journal-only PRs (no code diff) are rejected.
3. **No scope creep.** Never touch `.github/workflows/*` (especially
   `continue-on-error`), formatters, unrelated files, or `.jules/` journals as
   part of a UI PR. A PR that mixes those is rejected wholesale.
4. **One PR per logical change.** Do not bundle unrelated a11y fixes across
   surfaces; do not re-open a closed family.

## Surface notes

- SPA files moved to `src/codomyrmex/pai_pm/server/spa/` (previously
  `server/routes/` HTML). Verify the current path with `git ls-files` before
  editing; stale-path PRs are rejected.
- Icon-only buttons need `aria-label` (visible-label buttons do not).
- Warning banners created dynamically need `role="alert"`.
- Modal close buttons and chat inputs are recurring a11y targets — check the
  file first; most already carry labels on `main`.

## Disposition of prior floods

The 2026-09 triage merged the novel a11y changes and closed the duplicate
families (see `CHANGELOG.md` Unreleased). Palette must not re-propose:
icon-only button labels in `spa/index.html` (merged #418 + applied #217),
`role="alert"` Ollama banners in `chat.html` (applied #149), dispatch label
associations (merged #322), or any element whose selector already carries the
proposed attribute on `main`.