# git_analysis/vendor — Behavioral Specification

## Purpose

Contains vendored third-party tools required by `git_analysis`. Currently houses
the GitNexus git submodule.

## Vendor Policy

### What Gets Vendored

A dependency is vendored here if:
1. It is a standalone tool (not a Python package) consumed via subprocess
2. Vendoring provides offline availability or version pinning benefits
3. The tool has a stable API that does not require frequent updates

Python packages (including Node.js packages installed via npm) are NOT vendored —
they are declared as dependencies in `pyproject.toml` or `package.json`.

### Submodule Management

| Operation | Command |
|-----------|---------|
| Initialize after clone | `git submodule update --init src/codomyrmex/git_analysis/vendor/gitnexus` |
| Update to latest | `git submodule update --remote src/codomyrmex/git_analysis/vendor/gitnexus` |
| Pin to specific commit | `cd vendor/gitnexus && git checkout <sha>` |
| Check status | `git submodule status` |

### Pinning Policy

1. **Always pin to a specific commit** — never track `HEAD` of an external branch.
2. **Document the pin** in the commit message when updating: `chore: update gitnexus to <sha> (<reason>)`.
3. **Test before updating** — run the affected MCP tools after updating.
4. **Review changelogs** — check the upstream changelog for breaking API changes.

## GitNexus Submodule Specification

| Property | Value |
|----------|-------|
| Source | `https://github.com/abhigyanpatwari/GitNexus` |
| Type | git submodule |
| Usage | Invoked via `npx gitnexus` or `node vendor/gitnexus/dist/index.js` |
| Build required? | Only for vendor fallback (`npm install && npm run build`) |

## Behavioral Constraints

1. **No RASP docs inside `gitnexus/`**: The submodule is external code. We do not
   add or modify files inside `gitnexus/` — any missing RASP docs there are intentional.

2. **Graceful degradation**: The `git_analysis` module MUST handle `gitnexus/` being
   absent or uninitialized without crashing. All GitNexus tools return error dicts.

3. **No auto-build in CI**: CI does not build `vendor/gitnexus/dist/`. It uses `npx`
   which downloads on first run, or skips if Node.js is unavailable.

4. **Submodule initialized on clone**: The `.gitmodules` file at project root registers
   this submodule. New contributors must run `git submodule update --init` after cloning.
