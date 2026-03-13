# Collaboration — MCP Tool Specification

**Version**: v1.3.0 | **Last Updated**: March 2026

Tools are registered via `@mcp_tool(category="collaboration")` and auto-discovered by the PAI MCP bridge.

---

## Tool: `collaboration_attest_task`

Create a cryptographic attestation proving an agent completed a task.

- **Category**: collaboration
- **Parameters**:
  - `task_id` (string, required): Identifier of the completed task.
  - `agent_id` (string, required): Identifier of the attesting agent.
  - `result_data` (string, required): Result data string to bind into the attestation.
- **Returns**: `{"status": "success", "attestation": {"task_id": <string>, "agent_id": <string>, "result_hash": <string>, "timestamp": <string>, "signature": <string>}}`

---

## Tool: `collaboration_verify_attestation`

Verify a cryptographic task attestation against result data.

- **Category**: collaboration
- **Parameters**:
  - `attestation_dict` (object, required): Serialized attestation (as returned by `collaboration_attest_task`).
  - `result_data` (string, required): The original result data string.
- **Returns**: `{"status": "success", "valid": <bool>, "task_id": <string>}`

---

## Error Handling

All tools return `{"status": "error", "message": "<message>"}` on failure.

For additional collaboration tools (swarm management, agent listing), see `mcp_tools.py`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
