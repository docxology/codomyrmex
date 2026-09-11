# Technical Specification: Language Detection Module

## Responsibilities
- Identify the primary language of provided textual content.
- Support probability-based multi-language detection for ambiguous inputs.
- Expose MCP tools for integration with agents and orchestration flows.

## Core Functions
- `detect_language(text: str) -> str`: Returns ISO 639-1 code or "unknown".
- `detect_languages_with_probabilities(text: str) -> list[dict[str, float]]`: Returns a list of language probabilities.

## MCP Tools
- `language_detection_detect`: Wraps `detect_language`.
- `language_detection_detect_probs`: Wraps `detect_languages_with_probabilities`.

## Error Handling
Exceptions from the underlying library (e.g., `LangDetectException`) are handled by returning "unknown" or empty results without crashing.
