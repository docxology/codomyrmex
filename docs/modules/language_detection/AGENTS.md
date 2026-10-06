<!-- agents: curated -->

# Language Detection Module — Agent Coordination

## Purpose

Reader-facing mirror for `codomyrmex.language_detection`, which identifies the
natural language of text with `langdetect` and exposes that through two MCP
tools. Normative behavior lives in
[`src/codomyrmex/language_detection/`](../../../src/codomyrmex/language_detection/AGENTS.md).

## Key Capabilities

- `detect_language(text) -> str`: ISO 639-1 code, or `"unknown"` for empty,
  whitespace-only, or undetectable text.
- `detect_languages_with_probabilities(text) -> list[dict]`: `{"lang", "prob"}`
  entries from `langdetect`, or `[]` when nothing is detectable.
- MCP tools `language_detection_detect` and `language_detection_detect_probs`
  wrap them in status dictionaries (`{"status": "success", ...}` or
  `{"status": "error", "message": ...}`).

## Agent Usage Patterns

```python
from codomyrmex.language_detection import detect_language

detect_language("Bonjour, c'est un test.")  # 'fr'
detect_language("12345 67890")  # 'unknown'
```

## Integration Points

- **Source**: [src/codomyrmex/language_detection/](../../../src/codomyrmex/language_detection/)
- **MCP contract**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/language_detection/MCP_TOOL_SPECIFICATION.md)
- **Tests**: [tests/unit/language_detection/test_mcp_tools.py](../../../tests/unit/language_detection/test_mcp_tools.py)
- **Docs**: [Module Documentation](README.md) · [PAI notes](PAI.md)
- **Spec**: [Technical Specification](SPEC.md)
- **Module index**: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Treat the source module and its tests as authoritative; update this mirror
  when a signature, return shape, or MCP tool name changes.
- The package defines no `__all__`; import the two functions by name.
- Probability scores are `langdetect` heuristics, not calibrated probabilities;
  short or mixed-language text can give different answers between runs unless
  `langdetect.DetectorFactory.seed` is fixed.
- This file is hand-reviewed (`agents: curated`), so the module enricher
  (`scripts/documentation/enrich_module_docs.py`) leaves it alone; edit it by
  hand and re-run `make docs-check`.
