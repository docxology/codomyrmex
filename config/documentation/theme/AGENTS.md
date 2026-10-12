# Documentation theme guidance

## Purpose

Maintain the small Material theme override used by the canonical MkDocs site.

## Operating Contracts

- Preserve upstream search markup and behavior, including component attributes.
- Escape the translated accessible name; render it without requiring JavaScript.
- Check generated dialog names after dependency updates.
- Keep contrast checks scoped to light and dark palettes.

## Key Files

- `main.html` — localized search dialog name in the upstream header
- [Overview](README.md) — verification and stylesheet location

## Navigation

- [Overview](README.md)
- [Parent guidance](../AGENTS.md)
