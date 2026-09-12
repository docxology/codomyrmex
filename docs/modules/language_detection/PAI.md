# Language Detection Module — PAI Notes

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Public Interface Role

`codomyrmex.language_detection` exposes MCP tooling for natural-language identification (`language_detection_detect`, `language_detection_detect_probs`). PAI-facing workflows should call the MCP surface rather than private helpers.

## Integration Guidance

- langdetect is an optional dependency; guard imports where the extra is not installed.
- Detection is probabilistic — do not present scores as calibrated probabilities.

## Navigation

- **Overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Source PAI**: [../../../src/codomyrmex/language_detection/PAI.md](../../../src/codomyrmex/language_detection/PAI.md)
