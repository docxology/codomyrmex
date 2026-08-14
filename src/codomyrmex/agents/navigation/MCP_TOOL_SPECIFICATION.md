# Agent Navigation — MCP Tool Specification

All tools are read-only and tagged for `agents` discovery:

| Tool | Required input | Output |
| --- | --- | --- |
| `list_agent_capabilities` | none | bounded capability records and summary |
| `search_agent_capabilities` | `query` | ranked deterministic records and summary |
| `get_agent_capability` | `capability_id`; optional `kind` | one record, ambiguity, or structured lookup error |
| `agent_operability_status` | none | declaration/implementation counts; no live probes |

`kind` accepts `agent`, `module`, or `tool`. `include_tools` is false by
default, and requesting `kind="tool"` enables it automatically. Tool records
carry a descriptive `trust` field but are still subject to the PAI trust
gateway when executed. Every record also carries metadata-only `provenance`.

Malformed limits, kinds, IDs, and queries return structured errors with
`status="error"` and an `error_code`; blank searches never return an arbitrary
first page. `agent_operability_status` includes
`implementation_present_agents`, explicitly reports
`dispatchability_verified=false`, and reports zero
`verified_dispatchable_agents` because this surface never constructs clients.
Its `dispatchability_note` states that configuration, construction, and health
remain unverified.

`get_agent_capability` accepts an optional `kind` to resolve a bare name shared
by multiple capability kinds. Ambiguous lookups return
`CAPABILITY_ID_AMBIGUOUS` with deterministic candidate IDs.
