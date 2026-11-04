# `src/theme` — Docusaurus theme overrides

Swizzled copies of `@docusaurus/theme-classic` components that the site in
`src/codomyrmex/documentation/` must change rather than configure. A file here
takes precedence over the theme's own copy in the deployed build.

| File | Upstream | Why it is overridden |
| :--- | :--- | :--- |
| `prism-include-languages.js` | `@docusaurus/theme-classic/lib/theme/prism-include-languages.js` | Upstream's template-literal `require` for configured grammars made webpack bundle all 596 `prismjs/components/prism-*.js` files into the main chunk; this version loads them lazily. |

Verify a change with a production build in the docs project
(`npm run build`) and compare `build/assets/js/main.*.js` raw and gzip sizes.
The site is published by `.github/workflows/documentation.yml` and measured by
`.github/workflows/lighthouse-ci.yml`.

Theme overrides are not a styling surface: global CSS belongs in
[`../css/custom.css`](../css/custom.css).
