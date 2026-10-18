# Language Detection API Specification

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Public API

### `detect_language(text: str) -> str`

Detect the language of the provided text. Returns an ISO 639-1 language code.
Raises on invalid input; prefer the MCP surface for status-dict semantics.

### `detect_languages_with_probabilities(text: str) -> dict[str, float]`

Return per-language probability scores from `langdetect`. Scores are heuristic
and must not be presented as calibrated probabilities.

## MCP Surface

| Tool | Signature | Description |
|:---|:---|:---|
| `language_detection_detect` | `(text: str) -> dict[str, Any]` | Status-dict wrapper around `detect_language`. |
| `language_detection_detect_probs` | `(text: str) -> dict[str, Any]` | Status-dict wrapper around `detect_languages_with_probabilities`. |

## Module Layout

| File | Purpose |
|:---|:---|
| `__init__.py` | Public exports (`detect_language`, `detect_languages_with_probabilities`). |
| `mcp_tools.py` | MCP tool surface. |

## Dependencies

`langdetect>=1.0.9` (declared in `pyproject.toml`). Import defensively when the
extra may be absent.

## Navigation

- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
- **MCP tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)