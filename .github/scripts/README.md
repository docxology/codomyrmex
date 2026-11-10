# Scripts

## Overview

Helper scripts invoked by workflows under [`.github/workflows/`](../workflows/README.md).
They exist because the Lighthouse budget must measure the artifact that is actually
deployed: the Docusaurus build, served under its real base path, compressed the way
GitHub Pages compresses it.

| File | Caller | Purpose |
| --- | --- | --- |
| `serve_docs_site.sh` | `.github/workflows/lighthouse-ci.yml` (`startServerCommand`, and a `--check` step) | Symlink the built site as `codomyrmex/`, start the local server, run the artifact assertions, then print one readiness line. With `--check` it prints the assertions to the run log, stops, and takes no measurement |
| `serve_docs_site.py` | `serve_docs_site.sh` | `ThreadingHTTPServer` that gzips the text types Pages compresses |
| `verify_docs_site.py` | `serve_docs_site.sh` | The artifact assertions, each printed with what it measured: served HTML byte-identical to `build/index.html`, referenced assets resolve under the base path, gzip on a JS asset. Non-zero on any failure |
| `check_lighthouse_medians.js` | `.github/workflows/lighthouse-ci.yml` (assertion step) | The assertion of record: assert median performance and CLS across all runs; warn when the median LCP exceeds its ceiling |

## Why the checks print

LHCI captures the output of `startServerCommand`, so the artifact assertions run
silently in a green audit. The workflow runs `serve_docs_site.sh --check` before
the audit for the same reason the medians step exists: a pass should be able to
show what it verified, not only fail loudly when it does not.

```bash
bash .github/scripts/serve_docs_site.sh --check   # print the checks, measure nothing
```

**Status**: Active
**Last Updated**: November 2026
