# AGENTS: Language Detection Module

## Purpose

Identify the natural language of text for Codomyrmex agents and pipelines.
The package wraps `langdetect` in two pure functions and exposes them as MCP
tools so agents can route on ISO 639-1 codes without importing internals.

## Key Files

- `__init__.py` — `detect_language(text) -> str` (ISO 639-1 code, or
  `"unknown"` for empty or undetectable text) and
  `detect_languages_with_probabilities(text) -> list[dict[str, float]]`
  (`{"lang", "prob"}` entries, or `[]`); both catch `LangDetectException`.
  No `__all__` is defined.
- `mcp_tools.py` — `language_detection_detect` and
  `language_detection_detect_probs`, each returning
  `{"status": "success", ...}` or `{"status": "error", "message": ...}`.
- [`API_SPECIFICATION.md`](API_SPECIFICATION.md), [`MCP_TOOL_SPECIFICATION.md`](MCP_TOOL_SPECIFICATION.md),
  [`SPEC.md`](SPEC.md), [`PAI.md`](PAI.md), [`README.md`](README.md) — interface,
  MCP, design, PAI, and overview documentation.
- `py.typed` — PEP 561 marker.

## Dependencies

- `langdetect>=1.0.9`, a core entry in `[project.dependencies]` of
  [`pyproject.toml`](../../../pyproject.toml); it is imported at module import
  time, so the package fails to import without it.
- `codomyrmex.model_context_protocol.decorators.mcp_tool` registers the tools;
  the PAI MCP bridge auto-discovers `mcp_tools.py`, so no manual registration exists.
- Reader-facing mirror: [docs/modules/language_detection/](../../../docs/modules/language_detection/AGENTS.md).
- Parent: [../README.md](../README.md)

## Conventions

- Use `langdetect` for language detection.
- All MCP tools must be exposed in `mcp_tools.py` using the `@mcp_tool(category="language_detection")` decorator.
- Ensure any exception thrown by `langdetect` is caught and handled gracefully, returning status "error" and the message, or defaulting to "unknown" as appropriate.
- Tests should cover regular text in different languages, empty strings, and text with no recognizable language (e.g., just numbers).
- The code and tests are authoritative: error dictionaries use the `message`
  key, `detect_language` returns `"unknown"` instead of raising, and the
  probability function returns a list. Keep the specification files consistent
  with that when editing them.
- `langdetect` is non-deterministic for short or ambiguous text unless
  `DetectorFactory.seed` is fixed; assert exact codes only on unambiguous inputs.

## Test

Unit tests for the module are in
[`tests/unit/language_detection/test_mcp_tools.py`](../../../tests/unit/language_detection/test_mcp_tools.py)
and must follow the zero-mock policy (`langdetect` runs offline, so no network
guard is needed):

```bash
uv run pytest tests/unit/language_detection/
```
