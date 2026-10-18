# Language Detection Module — PAI Notes

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Public Interface Role

`codomyrmex.language_detection` gives agents a stable natural-language
identification boundary (`detect_language`,
`detect_languages_with_probabilities`) exposed through MCP tools
`language_detection_detect` and `language_detection_detect_probs`.

## Integration Guidance

- langdetect is an ordinary dependency; guard imports where the environment
  may not have it installed.
- Detection scores are heuristic — never present them as calibrated
  probabilities or expected free energy.
- Route routing decisions through ISO 639-1 codes returned by the tools.

## Navigation

- **Overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **API spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)