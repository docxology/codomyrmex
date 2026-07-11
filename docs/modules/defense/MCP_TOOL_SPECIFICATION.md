# defense - MCP Tool Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Tools

| Tool | Inputs | Output |
| :--- | :--- | :--- |
| `defense_detect_exploit` | `text: str` | Detection result dictionary |
| `defense_process_request` | `source_id: str`, `payload: dict` | Allow/deny result and threats |
| `defense_threat_report` | none | Active-defense report dictionary |

## Safety Contract

The tools are read-only with respect to the filesystem and operate on supplied
strings or in-memory defense state. They are suitable for local agent safety
checks and should remain bounded and deterministic.
