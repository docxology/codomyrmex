# Vision Module

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: April 2026

## Overview

`codomyrmex.vision` provides visual document processing utilities: image annotation extraction, PDF extraction, VLM client integration, and shared data models. The source package lives in [src/codomyrmex/vision/](../../../src/codomyrmex/vision/).

## Key Surfaces

- `models.py` — typed data models for visual extraction results.
- `annotation_extractor.py` — annotation parsing and extraction helpers.
- `pdf_extractor.py` — PDF-to-visual/document extraction utilities.
- `vlm_client.py` — VLM provider client boundary.
- Source-level docs: [README](../../../src/codomyrmex/vision/README.md), [SPEC](../../../src/codomyrmex/vision/SPEC.md), [API](../../../src/codomyrmex/vision/API_SPECIFICATION.md), [PAI](../../../src/codomyrmex/vision/PAI.md), and [AGENTS](../../../src/codomyrmex/vision/AGENTS.md).

## Usage Pattern

Use this module when workflows need structured information from images, PDFs, or visual-language model calls. Keep extraction logic deterministic where possible, isolate provider calls behind `vlm_client.py`, and document any provider-specific credentials or runtime assumptions.

## Navigation

- **Parent**: [../README.md](../README.md)
- **Source**: [../../../src/codomyrmex/vision/](../../../src/codomyrmex/vision/)
- **Spec**: [SPEC.md](SPEC.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
