# Semiotic -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Implements computational semiotics based on Peircean sign theory. Provides sign extraction from text (icon/index/symbol classification), semiotic drift measurement between corpora via Jaccard similarity, semantic territory mapping from word frequency, synonym-based linguistic steganography, and mnemonic device construction (Method of Loci).

## Architecture

Sign-extraction and drift-analysis pattern. `SemioticAnalyzer` decodes text into `Sign` objects using context windows and deictic/emoji heuristics, measures drift between corpora by comparing signified contexts, and maps semantic territories via frequency clustering. `SemioticEncoder` implements meaning-level steganography using synonym substitution. `mnemonics.py` constructs memory palace associations.

## Key Classes

### `SemioticAnalyzer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `decode` | `text: str` | `list[Sign]` | Extract signs with context-window signifieds and Peircean type classification |
| `drift` | `corpus_a: list[str], corpus_b: list[str]` | `DriftReport` | Measure semiotic drift via Jaccard similarity of signified contexts (threshold 0.3) |
| `territory_map` | `corpus: list[str], n_domains: int` | `list[SemanticTerritory]` | Map top-N semantic territories from frequency analysis |

### `SemioticEncoder`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `encode` | `carrier: str, payload: str` | `str` | Embed payload via synonym selection driven by payload byte values |
| `decode` | `encoded: str` | `list[int]` | Extract embedded bit pattern from synonym choices |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `Sign` | `signifier, signified, sign_type, cultural_context, stability, id` | Fundamental semiotic unit with Peircean classification |
| `SignType` | `ICON, INDEX, SYMBOL` | Peircean sign trichotomy |
| `SemanticTerritory` | `domain, signs, boundaries, contested` | A mapped region of semantic space with `density` property |
| `DriftReport` | `shifted_signs, stable_signs, new_signs, lost_signs, drift_magnitude, timestamp` | Semiotic drift analysis result with `stability_ratio` property |
| `MnemonicDevice` | `name, anchors, associations, encoding_strength` | Memory palace structure |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `build_memory_palace` | `items: list[str], locations: list[str]` | `MnemonicDevice` | Construct Method of Loci device; strength = items/locations ratio |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`hashlib`, `time`, `re`, `collections.Counter`, `dataclasses`, `enum`)

## Constraints

- Sign type inference uses simple heuristics: emoji/symbol unicode ranges for ICON, deictic words for INDEX, everything else SYMBOL.
- Drift threshold is fixed at Jaccard < 0.3 (meaning shift); not configurable.
- Steganography uses a fixed 8-word synonym map; real deployment would need larger vocabulary.
- `_to_bits` converts payload bytes mod 4 (2-bit encoding per byte).
- Words shorter than 2 characters are excluded from sign extraction.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `drift` returns `stability_ratio` of 1.0 when no shared signs exist.
- `decode` skips words not in `_SYNONYM_MAP` values.
- `build_memory_palace` marks overflow items when locations run out.
- Sign IDs are SHA-256 hashes of `signifier:signified` truncated to 16 characters.
