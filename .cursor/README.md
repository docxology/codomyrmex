# `.cursor/`

**Purpose:** Cursor IDE project configuration.

| Path | Version control |
|------|-----------------|
| `rules/*.mdc` | **Committed** — native Cursor rules (see root `.gitignore` exceptions). |
| Anything else under `.cursor/` | **Ignored** — local/editor state; do not rely on it for team behavior. |

Add new shared rules as `.mdc` files under `rules/` with YAML frontmatter (`description`, `alwaysApply` or `globs`). See Cursor docs on Project Rules.

**Also:** `cursorrules/` holds legacy `.cursorrules`-style fragments for editors or copy/paste.

## Navigation

- [Cursor integration](../../docs/development/cursor-integration.md)
- [cursorrules/README.md](../../cursorrules/README.md)
