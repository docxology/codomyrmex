<!-- agents: curated -->

# .github/scripts — AI Agent Guide

**Status**: Active | **Last Updated**: November 2026

## Purpose

Helper scripts invoked by workflows in [`.github/workflows/`](../workflows/README.md).
Today they serve one purpose: make the Lighthouse budget measure the artifact that is
actually deployed — the Docusaurus build, under its real base path, compressed the way
GitHub Pages compresses it.

## Key Files

| File | Called by | Purpose |
| --- | --- | --- |
| `serve_docs_site.sh` | `lighthouse-ci.yml` (`startServerCommand`) | Symlink the build as `codomyrmex/` in a temporary root, start the server, print one readiness line after the URL answers |
| `serve_docs_site.py` | `serve_docs_site.sh` | `ThreadingHTTPServer` that gzips HTML, JS, CSS, JSON, SVG, XML, text and source maps |
| `check_lighthouse_medians.js` | `lighthouse-ci.yml` | Read every run LHCI wrote and assert median performance and CLS; warn when the median LCP exceeds its ceiling |

## Development Guidelines

- **Serve under the deployed base path.** The build declares an absolute `baseUrl`
  (`/codomyrmex/`). Serving `build/` at the server root makes every asset request 404,
  and Lighthouse then reports a near-perfect score for a page that shipped no CSS or
  JavaScript. That measurement is worse than no measurement.
- **Keep gzip on.** GitHub Pages compresses text responses; `http.server` does not.
  Without it the emulated link measures compressibility instead of the site — the same
  artifact reads 337 KB compressed and 1,759 KB uncompressed.
- **Print the readiness line last and only after a successful request.** LHCI starts
  counting when `startServerCommand` prints; a line emitted before the port answers
  becomes a startup timeout.
- **Assert medians here, not through `lhci assert`.** `lhci assert` evaluates a single
  representative run, and it picks the most favourable one: with runs of LCP 3,445 /
  2,549 / 2,527 ms it reported `found: 2527.09`, so a site that breaches two runs in
  three reads green. Median behaviour belongs in `check_lighthouse_medians.js`.
- **Keep the LCP ceiling a warning** until the site meets it, as decided in
  `.github/lighthouse-ci.json`; performance (90) and CLS (0.1) are errors.

## Validation

```bash
# Median assertion against a completed LHCI run directory
node .github/scripts/check_lighthouse_medians.js .lighthouseci 90 2500

# Server: the readiness line names the URL to request
bash .github/scripts/serve_docs_site.sh
```

## Navigation

- [Scripts README](README.md)
- [Workflows guide](../workflows/AGENTS.md) | [.github guide](../AGENTS.md)
- [Root agent contract](../../AGENTS.md)
