# Vision MCP Tool Specification

**Version**: v1.3.0 | **Status**: Not MCP-exposed | **Last Updated**: June 2026

## Current MCP Surface

`codomyrmex.vision` does not currently expose production MCP tools. Its public
surface is Python-first and uses local VLM/PDF backends directly.

## Python Surfaces

| Surface | Purpose |
|:---|:---|
| `VLMClient` | Analyze images through local Ollama VLM models |
| `PDFExtractor` | Extract text from PDF documents |
| `AnnotationExtractor` | Extract structured visual annotations |
| `VLMConfig`, `VLMResponse`, `Annotation`, `BoundingBox`, `PageContent` | Data models |

## Future Tool Criteria

If MCP tools are added, they should clearly document file-path handling,
backend availability checks, and error shapes for missing local models.

## Navigation

- **Python API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
