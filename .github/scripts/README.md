# Scripts

## Overview

Helper scripts invoked by workflows under [`.github/workflows/`](../workflows/README.md).
They exist because the Lighthouse budget must measure the artifact that is actually
deployed: the Docusaurus build, served under its real base path, compressed the way
GitHub Pages compresses it.

| File | Caller | Purpose |
| --- | --- | --- |
| `serve_docs_site.sh` | `.github/workflows/lighthouse-ci.yml` (`startServerCommand`) | Symlink the built site as `codomyrmex/`, start the local server, print one readiness line once it answers |
| `serve_docs_site.py` | `serve_docs_site.sh` | `ThreadingHTTPServer` that gzips the text types Pages compresses |
| `check_lighthouse_medians.js` | `.github/workflows/lighthouse-ci.yml` (assertion step) | Assert median performance and CLS across all runs; warn when the median LCP exceeds its ceiling |

**Status**: Active
**Last Updated**: November 2026
