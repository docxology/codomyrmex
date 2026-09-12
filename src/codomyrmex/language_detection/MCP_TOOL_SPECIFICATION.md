# Language Detection MCP Tool Specification

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Current MCP Surface

| Tool | Signature | Description |
|:---|:---|:---|
| `language_detection_detect` | `(text: str) -> dict[str, Any]` | Detect the primary language; returns `{"status": "success", "language": "<ISO 639-1 code>"}`. |
| `language_detection_detect_probs` | `(text: str) -> dict[str, Any]` | Return per-language probabilities from `langdetect`; scores are heuristic, not calibrated. |

## Error Contract

On failure the tools return `{"status": "error", "error": "<message>"}` rather
than raising. `langdetect` must be installed (`pyproject.toml` dependency);
detection requires enough text to be reliable.

## Registration

Tools are declared with `@mcp_tool(category="language_detection")` and are
served through the shared MCP tool registry
([model_context_protocol](../model_context_protocol/)).

## Navigation

- **Source tools**: [mcp_tools.py](mcp_tools.py)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Docs overview**: [../../docs/modules/language_detection/README.md](../../docs/modules/language_detection/README.md)