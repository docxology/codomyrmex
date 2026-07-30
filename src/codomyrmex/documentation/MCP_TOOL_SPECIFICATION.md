# Documentation MCP tool specification

The documentation module exposes two tools through
`@mcp_tool(category="documentation")`. Their registered names are namespaced
with `codomyrmex.`.

## `codomyrmex.generate_module_docs`

Plans or generates one top-level module's source-derived `PAI.md`. Despite the
legacy function name, it does not generate README, AGENTS, or SPEC files.

### Input

| Field | Type | Required | Default | Contract |
| :--- | :--- | :---: | :---: | :--- |
| `module_name` | string | yes | — | Lowercase Python package name under `src/codomyrmex`; separators and traversal are rejected |
| `dry_run` | boolean | no | `true` | When true, generate and hash proposed content without writing |

### Success

```json
{
  "status": "success",
  "message": "PAI documentation planned for documentation",
  "operation": "generate_pai_md",
  "paths": ["src/codomyrmex/documentation/PAI.md"],
  "content_sha256": "<64 lowercase hexadecimal characters>",
  "executed": false,
  "dry_run": true
}
```

With `dry_run=false`, `executed` is true only after `PAI.md` is written.

### Error

```json
{
  "status": "error",
  "message": "<bounded error description>",
  "executed": false,
  "dry_run": true
}
```

### Trust and idempotency

- Default dry-run calls are read-only.
- `dry_run=false` replaces the target module's `PAI.md` and therefore requires
  explicit write authority.
- A repeated dry run is deterministic for unchanged source inputs.
- A repeated apply is content-idempotent for unchanged inputs, but still
  performs a filesystem write.
- The tool must not be invoked in apply mode during the active broad
  README/AGENTS hand-pass without a reviewed module-specific reason.

## `codomyrmex.audit_rasp_compliance`

Checks Python packages for the package-native RASP quartet: README, AGENTS,
SPEC, and PAI.

### Input

| Field | Type | Required | Contract |
| :--- | :--- | :---: | :--- |
| `module_name` | string or null | no | Omit for `src/codomyrmex`; otherwise use one validated top-level package name |

### Success

```json
{
  "status": "success",
  "compliant": false,
  "missing_count": 3,
  "modules_with_gaps": 1
}
```

`missing_count` is the number of individual missing RASP files, not the
underlying `audit_rasp()` exit code. `modules_with_gaps` counts affected
packages.

### Error

```json
{
  "status": "error",
  "message": "<bounded error description>"
}
```

The audit is read-only. It does not use the broader repository RASP exclusions
or replace the strict README/AGENTS and MkDocs gate.

## Compatibility change

The generation tool now defaults to `dry_run=true`, reports execution state and
a content hash, validates package names, and accurately describes its PAI-only
scope. The audit tool now returns a real missing-file count plus the number of
packages with gaps.

## Navigation

- [Package overview](README.md)
- [API specification](API_SPECIFICATION.md)
- [Functional specification](SPEC.md)
- [Security](SECURITY.md)
