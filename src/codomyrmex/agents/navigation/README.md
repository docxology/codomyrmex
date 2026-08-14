# Agent Navigation

The navigation package provides a deterministic capability index for agents.
It exposes stable records for:

- provider declarations and client implementation paths;
- top-level Codomyrmex modules and documentation/test surface gaps;
- static and dynamic MCP tools when tool inventory is explicitly requested.

```python
from codomyrmex.agents.navigation import build_capability_catalog

catalog = build_capability_catalog(include_tools=True)
for record in catalog.search("dispatch", kind="agent"):
    print(record.id, record.status, record.documentation)
```

The catalog is metadata-only. `implementation_present` means the Python client
module can be located; it does not mean a key, CLI binary, endpoint, or model is
available, and it does not prove construction succeeds. Every serialized record
includes provenance for its discovery source. Use `AgentRegistry.probe_agent()`
for an explicit health check. Navigation methods reject malformed limits and
empty searches so a failed request cannot look like an arbitrary successful
result page. Documentation links are emitted only when their files exist.
MCP tool trust labels use the same dependency-free destructive-name policy as
the trust gateway, including explicit deserialization restrictions and
side-effect name patterns. A `restricted` label is metadata, not authorization
or a live trust decision.
`CapabilityCatalog.find()` exposes all exact or bare-name matches; `get()`
returns one only when the match is unambiguous or a capability kind is given.

## Navigation

- **Agents**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **MCP tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent**: [../README.md](../README.md)
- **Documentation**: [docs/agents/navigation/README.md](../../../../docs/agents/navigation/README.md)
