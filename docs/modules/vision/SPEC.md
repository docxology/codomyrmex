# Vision Module Specification

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: April 2026

## Purpose

The `codomyrmex.vision` module supports visual document processing and VLM-backed extraction workflows. It converts image/PDF inputs into typed, agent-consumable structures while keeping provider calls behind a clear client boundary.

## Source of Truth

- Source implementation: [../../../src/codomyrmex/vision/](../../../src/codomyrmex/vision/)
- Source specification: [../../../src/codomyrmex/vision/SPEC.md](../../../src/codomyrmex/vision/SPEC.md)
- API specification: [../../../src/codomyrmex/vision/API_SPECIFICATION.md](../../../src/codomyrmex/vision/API_SPECIFICATION.md)

## Design Constraints

1. Keep extraction and provider-call boundaries separate.
2. Validate file paths and input types before processing untrusted visual documents.
3. Return typed models rather than loosely structured dictionaries where public callers depend on the result.
4. Document provider credentials and optional dependencies when adding new VLM backends.

## Navigation

- **Overview**: [README.md](README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Parent**: [../README.md](../README.md)
