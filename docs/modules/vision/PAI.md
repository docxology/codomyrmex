# Vision Module — PAI Notes

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: April 2026

## Public Interface Role

`codomyrmex.vision` gives agents a stable boundary for visual document extraction and VLM-assisted interpretation. PAI-facing workflows should call the module's public APIs and client boundaries rather than private extraction helpers.

## Integration Guidance

- Use typed models from [../../../src/codomyrmex/vision/models.py](../../../src/codomyrmex/vision/models.py) for cross-module exchange.
- Keep provider credentials out of docs and code; read them through configured environment or settings layers.
- Validate local paths before processing PDFs or images from external sources.

## Navigation

- **Overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Source PAI**: [../../../src/codomyrmex/vision/PAI.md](../../../src/codomyrmex/vision/PAI.md)
