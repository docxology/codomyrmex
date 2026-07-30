# Documentation MCP tools

The implemented tools are
`codomyrmex.generate_module_docs` and
`codomyrmex.audit_rasp_compliance`. Older build/environment tool names are not
part of the current MCP surface.

## `codomyrmex.generate_module_docs`

Despite the compatibility name, this tool plans or generates only one module's
`PAI.md`.

| Input | Type | Default | Behavior |
| :--- | :--- | :---: | :--- |
| `module_name` | string | required | One lowercase top-level package name; traversal is rejected |
| `dry_run` | boolean | `true` | Hash proposed content without writing |

Success returns `status`, `message`, `operation`, portable `paths`,
`content_sha256`, `executed`, and `dry_run`. `dry_run=false` explicitly
replaces the target PAI file.

## `codomyrmex.audit_rasp_compliance`

The optional `module_name` selects one validated package; omission scans
`src/codomyrmex`. Success returns:

```json
{
  "status": "success",
  "compliant": false,
  "missing_count": 3,
  "modules_with_gaps": 1
}
```

The audit is read-only. It checks Python packages for README, AGENTS, SPEC, and
PAI. It does not replace the repository-level README/AGENTS or MkDocs gates.

## Source

See the full
[source MCP specification](../../../src/codomyrmex/documentation/MCP_TOOL_SPECIFICATION.md)
and [`mcp_tools.py`](../../../src/codomyrmex/documentation/mcp_tools.py).

## Navigation

- [Module overview](README.md)
- [API specification](API_SPECIFICATION.md)
- [Security](SECURITY.md)
