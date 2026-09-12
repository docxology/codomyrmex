# Preprocessing Module — PAI Notes

**Version**: v1.3.1 | **Status**: Active | **Last Updated**: September 2026

## Public Interface Role

`codomyrmex.preprocessing` exposes MCP tooling for text preprocessing (`preprocess_data`). PAI-facing workflows should call the MCP surface rather than private helpers.

## Integration Guidance

- Register through the module MCP tool registry; keep preprocessing deterministic and side-effect free.
- Validate input size limits before processing untrusted text.

## Navigation

- **Overview**: [README.md](README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **Source PAI**: [../../../src/codomyrmex/preprocessing/PAI.md](../../../src/codomyrmex/preprocessing/PAI.md)
