# Agents MCP tool specification

This document mirrors the stable MCP surface implemented in
`src/codomyrmex/agents/mcp_tools.py`. Runtime dynamic tools are discovered
separately and are not represented as a fixed provider count here.

## Agent tools

| Invocation | Required input | Behavior |
| :--- | :--- | :--- |
| `execute_agent` | `agent_name`, `prompt` | Execute one registered agent request and return response metadata. |
| `list_agents` | none | Return registry descriptors and their declared capabilities. |
| `get_agent_memory` | `session_id` | Return the most recent messages for a persisted agent session. |

The decorated runtime names are the function names above. Older names such as
`execute_agent_request`, `list_available_agents`, `probe_agent_status`, and
`register_tool_with_agent` are not registered by this module and must not be
used for capability routing.

## Navigation tools

The navigation surface is read-only metadata. It does not construct clients,
probe credentials, invoke handlers, or claim endpoint operability:

| Tool | Purpose |
| :--- | :--- |
| `list_agent_capabilities` | List bounded agent, module, and tool records. |
| `search_agent_capabilities` | Search the complete catalog without page-limit false negatives. |
| `get_agent_capability` | Resolve an exact or unambiguous capability ID. |
| `agent_operability_status` | Report implementation metadata without live probes. |

Use `agent:<name>`, `module:<name>`, or `tool:<qualified-name>` IDs. A status
of `implementation_present` means only that the client module can be located;
credentials, network access, and live service health remain unverified.

## Operational and security contract

- Tool arguments are validated against their declared JSON Schema before a
  handler runs.
- MCP/PAI entrypoints apply trust classification and audit logging. Dynamic
  names containing mutation, VCS, deployment, or external-communication verbs
  require elevated trust.
- MCP filesystem paths are constrained to the current working tree by
  default. Additional roots must be explicitly listed in
  `CODOMYRMEX_MCP_ALLOWED_ROOTS`.
- Confirmation tokens for destructive calls are one-use and bound to the
  exact validated argument payload.
- Dynamic discovery and static definitions use a first-registration-wins
  collision policy so a discovered handler cannot silently replace a stable
  contract.

## Navigation links

- Parent: [Agents module](README.md)
- Module index: [All modules](../AGENTS.md)
- Root coordination: [AGENTS.md](../../../AGENTS.md)
