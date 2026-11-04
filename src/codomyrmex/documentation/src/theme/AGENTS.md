# AGENTS.md — `codomyrmex/documentation/src/theme`

## Purpose

Theme overrides for the Docusaurus site (`src/codomyrmex/documentation/`), swizzled
from `@docusaurus/theme-classic`. Docusaurus prefers a file here over the theme's
own copy, so anything in this directory replaces upstream behaviour for the
deployed site.

## Key Files

- [`prism-include-languages.js`](prism-include-languages.js) — registers extra
  Prism grammars from `themeConfig.prism.additionalLanguages`. Ejected because
  upstream's template-literal `require` made webpack bundle every
  `prismjs/components/prism-*.js` file into the main chunk. Upstream source:
  `@docusaurus/theme-classic/lib/theme/prism-include-languages.js`.

## Development Guidelines

- Only swizzle what configuration cannot express; check
  `docusaurus.config.js` and theme options first.
- Eject (`--eject`), never wrap, when the point is to remove an upstream import
  or dependency. Swizzle with
  `node node_modules/@docusaurus/core/bin/docusaurus.mjs swizzle @docusaurus/theme-classic <component> --eject --javascript`
  from the docs project root; add `--danger` only when the theme marks the
  component's eject unsafe.
- Owning a copy here is a maintenance term, not a fork: 65 lines against
  upstream's 34, a body upstream changed once between 3.5.2 and 3.7.0 and not
  again through 3.10.2, and a diff against
  `@docusaurus/theme-classic/lib/theme/prism-include-languages.js` due at every
  theme upgrade, since a stale copy silently wins over the fixed upstream
  version. For this file upstream marks eject safe and wrap forbidden ("Not a
  component!" — `getSwizzleConfig.js`) and calls it "Meant to be ejected", so
  no lighter mechanism exists. Drop the copy entirely once upstream stops
  bundling the language registry.
- Verify bundle effects with a build: `npm run build`, then compare
  `build/assets/js/main.*.js` raw and gzip sizes before and after.
- Markdown files in this tree are documentation only; Docusaurus does not read
  them as site content.

## Dependencies

- Consumer: the Docusaurus build in `src/codomyrmex/documentation/`, published by
  `.github/workflows/documentation.yml`.
- Budget instrument: `.github/workflows/lighthouse-ci.yml`.
- Parent: [../AGENTS.md](../AGENTS.md) · Repository contract:
  [../../../../AGENTS.md](../../../../AGENTS.md)
