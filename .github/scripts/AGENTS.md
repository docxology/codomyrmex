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
| `serve_docs_site.sh` | `lighthouse-ci.yml` (`startServerCommand`) | Symlink the build as `codomyrmex/` in a temporary root, start the server, **assert the served artifact**, then print one readiness line |
| `serve_docs_site.py` | `serve_docs_site.sh` | `ThreadingHTTPServer` that gzips HTML, JS, CSS, JSON, SVG, XML, text and source maps |
| `check_lighthouse_medians.js` | `lighthouse-ci.yml` | The assertion of record: read every run LHCI wrote, assert median performance and CLS, warn when the median LCP exceeds its ceiling |

## Development Guidelines

- **Serve under the deployed base path.** The build declares an absolute `baseUrl`
  (`/codomyrmex/`). Serving `build/` at the server root makes every asset request 404,
  and Lighthouse then reports a near-perfect score for a page that shipped no CSS or
  JavaScript. That measurement is worse than no measurement.
- **Keep gzip on.** GitHub Pages compresses text responses; `http.server` does not.
  Without it the emulated link measures compressibility instead of the site — the same
  artifact reads 337 KB compressed and 1,759 KB uncompressed (live Pages measures
  332 KB, so the local figure is faithful).
- **The harness asserts the artifact before reporting a number.** `serve_docs_site.sh`
  requires the served HTML to be byte-identical to `build/index.html`, every JS/CSS
  asset the page references to return 200 under the base path, and a text asset to come
  back gzip-encoded. Each of those three failures has produced a published number once;
  now they exit non-zero instead. Treat the assertions as the fix for that class of
  error, not as decoration — removing one re-opens the hazard.
- **Print the readiness line last and only after the assertions pass.** LHCI starts
  counting when `startServerCommand` prints; a line emitted before the port answers
  becomes a startup timeout.
- **Assert medians here, not through `lhci assert`.** `lhci assert` evaluates a single
  run out of the set and reports the most favourable: with LCP 3,445 / 2,549 / 2,527 ms
  it printed `found: 2527.09`, and with 2,333 / 2,935 / 2,931 ms it printed `found:
  2332.9`. Both times the ceiling it "checked" was missed by the median. Median
  behaviour belongs in `check_lighthouse_medians.js`, which is the gate; the LHCI
  assertion is evidence.
- **Five runs, not three.** On identical bytes, LCP varies 978–2,987 ms across live
  passes and 2,412–3,445 ms across CI runners. A three-run median is close to a coin
  flip; the extra two runs cost seconds and make the median mean something.
- **Keep the LCP ceiling a warning** until several `main` runs agree it is met, as
  decided in `.github/lighthouse-ci.json`; performance (90) and CLS (0.1) are errors.

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
