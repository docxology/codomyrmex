# AGENTS: Language Detection Module

## Conventions
- Use `langdetect` for language detection.
- All MCP tools must be exposed in `mcp_tools.py` using the `@mcp_tool(category="language_detection")` decorator.
- Ensure any exception thrown by `langdetect` is caught and handled gracefully, returning status "error" and the message, or defaulting to "unknown" as appropriate.
- Tests should cover regular text in different languages, empty strings, and text with no recognizable language (e.g., just numbers).

## Test
Unit tests for the module are found in `src/codomyrmex/tests/unit/language_detection/test_mcp_tools.py` and must follow the strictly zero-mock policy (since the network isn't used by `langdetect`).
