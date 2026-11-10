# Documentation module security

Report vulnerabilities through the process in the repository
[SECURITY.md](../../../SECURITY.md). Do not disclose unpatched vulnerabilities
in public issues.

## Threat surface

The documentation module processes repository paths and Markdown, launches
package-manager commands, copies trees, writes generated files, starts local
servers, and can open a browser. Relevant risks include:

- path traversal or writes outside the intended module;
- overwriting concurrent or curated documentation;
- following untrusted symlinks during aggregation;
- command execution through unvalidated package-manager selection or
  environment state;
- malicious Markdown, HTML, JavaScript, or plugin content entering a built
  site;
- credentials or absolute home paths leaking into examples and receipts;
- dependency and supply-chain compromise in Node and Python build tools;
- serving internal documentation on a network-visible interface.

## Dependency overrides

`package.json` pins three transitive packages with npm `overrides`, because the
advisories live in packages pinned by `@docusaurus/core` and its webpack plugins
rather than in our own direct dependencies:

| Package | Pinned | Pulled in by | Advisory |
| :--- | :--- | :--- | :--- |
| `serialize-javascript` | 7.1.4 | `copy-webpack-plugin`, `css-minimizer-webpack-plugin` | `GHSA-m5mm-p8h7-m29v`, `GHSA-qj8w-gfj5-8c6v`, `GHSA-5c6j-r48x-rmvq` (3 alerts) |
| `tinypool` | 2.2.0 | `@docusaurus/core`'s own worker pool | `GHSA-85c8-ppgw-ccpr`, `GHSA-5gmw-xhrv-c9v3` (2 alerts) |
| `uuid` | 11.1.1 | `sockjs`, via `webpack-dev-server` (development only) | `GHSA-w5hq-g745-h8pq` |

Docusaurus 3.10.2 is the newest published release, so no upstream upgrade fixes
these; drop an override when its parent declares the patched range. Verified
before landing: `npm ci`, `npm run build` (unchanged artifact size and file
count), and `docusaurus start` — the `uuid` consumer is CommonJS and 11.1.1
still ships a `require` entry point, but that was tested rather than assumed.

## Known unpatched advisories

| Advisory | Package | Status |
| :--- | :--- | :--- |
| `GHSA-gcqx-w48m-w2h4` | `deepmerge` 4.3.1, via `@svgr/plugin-svgo` | **No patched release exists** — 4.3.1 is the latest published version. `mergeObject()` prototype poisoning needs attacker-controlled merge keys, while this tree merges build configuration and SVG metadata. Leave the Dependabot alert open as an upstream wait and re-check when `deepmerge` publishes; do not re-triage it each quarter. |

## Required controls

- Validate module identifiers before path construction and resolve targets
  beneath an explicit trusted root.
- Default MCP generation to dry-run and report `executed` and `dry_run`.
- Review the complete target set before any broad write.
- Preserve curated markers, dirty-worktree content, and submodule boundaries.
- Use argument arrays for subprocess execution; do not interpolate untrusted
  shell text.
- Bind development servers to loopback unless broader exposure is explicitly
  required and secured.
- Treat repository Markdown and copied assets as untrusted input when rendering
  HTML.
- Keep credentials in environment or secret stores, never documentation,
  manifests, QR payloads, logs, or examples.
- Use locked dependency groups and the repository security audit before release.

## Operation classes

| Operation | Default classification |
| :--- | :--- |
| Quality, consistency, and RASP scans | Read-only, aside from explicitly named report files |
| `generate_module_docs(..., dry_run=True)` | Read-only proposal |
| `generate_module_docs(..., dry_run=False)` | Source mutation |
| `write_pai_md`, maintenance helpers, aggregation | Source or destination mutation |
| dependency installation, build, start, serve, browser assessment | External process and/or network side effects |

## Publication boundary

Local rendering, checksums, and structural PDF validation do not prove that an
artifact was published, externally attested, accessible, or safe to deploy.
Keep release receipts, publication plans, DOI state, and external conformance
results explicit and separate.

## Validation

```bash
uv run --locked bandit -r src/codomyrmex/documentation \
  -x src/codomyrmex/documentation/docs
uv run --locked pytest -q tests/unit/documentation tests/integration/documentation
make docs-check
```

## Navigation

- [Repository security policy](../../../SECURITY.md)
- [Functional specification](SPEC.md)
- [MCP tool specification](MCP_TOOL_SPECIFICATION.md)
