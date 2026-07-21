# Defense MCP Tool Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Tools

| Tool | Parameters | Return |
| :--- | :--- | :--- |
| `defense_detect_exploit` | `input_text: str` | `status`, `detected`, `patterns`, `threat_level` |
| `defense_process_request` | `source: str`, `request_path: str = "/"`, `request_method: str = "GET"`, `request_input: str = ""` | `status`, `allowed`, `threat_count`, `threats` |
| `defense_threat_report` | none | `status` plus active-defense metrics |

## Behavior

- `defense_detect_exploit` delegates to a real `ActiveDefense` instance.
- `defense_process_request` delegates to a real `Defense` instance and returns serialized `ThreatEvent` records.
- `defense_threat_report` returns current in-process metrics.

## Example

```json
{
  "tool_name": "codomyrmex.defense_detect_exploit",
  "arguments": {
    "input_text": "ignore previous instructions"
  }
}
```

## Validation

```bash
uv run pytest tests/unit/defense/test_mcp_tools_defense.py -q
```
