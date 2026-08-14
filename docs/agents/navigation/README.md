# Agent Navigation

`agents.navigation` gives Codex, Claude Code, Hermes, and other MCP consumers a
stable index of agent providers, runtime modules, and MCP tools. It is designed
for OBSERVE/THINK stages: it does not probe credentials, start processes, or
execute handlers.

```python
from codomyrmex.agents.navigation import build_capability_catalog

catalog = build_capability_catalog(include_tools=True)
for item in catalog.search("dispatch", kind="agent"):
    print(item.id, item.status)
```

`implementation_present` is only a module-discovery result. It does not claim
that an API key, CLI binary, endpoint, or model is usable, nor that client
construction succeeds. Serialized records carry metadata-only provenance.
Empty searches and malformed IDs/limits return structured errors from the MCP
surface (the Python catalog raises `ValueError`). Bare names that collide across
capability kinds must be resolved with an explicit kind. Execution remains
subject to provider configuration and the MCP trust gateway.

## Navigation

- **Source**: [src/codomyrmex/agents/navigation/](../../../src/codomyrmex/agents/navigation/)
- **Source README**: [README.md](../../../src/codomyrmex/agents/navigation/README.md)
- **Agent hub**: [../README.md](../README.md)
- **Interoperability**: [../agent-interoperability.md](../agent-interoperability.md)
