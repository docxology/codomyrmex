# Codomyrmex Agents -- src/codomyrmex/meme/semiotic

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Implements computational semiotics based on Peircean sign theory. Provides sign extraction from text (icon/index/symbol classification), semiotic drift measurement between corpora, semantic territory mapping, synonym-based linguistic steganography for embedding hidden payloads, and mnemonic device construction using the Method of Loci.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `analyzer.py` | `SemioticAnalyzer` | Decode text into signs, measure drift, map semantic territories |
| `encoding.py` | `SemioticEncoder` | Meaning-level steganography via synonym substitution |
| `mnemonics.py` | `MnemonicDevice` | Memory palace structure with anchors and associations |
| `mnemonics.py` | `build_memory_palace` | Construct Method of Loci device linking items to locations |
| `models.py` | `Sign` | Fundamental semiotic unit: signifier, signified, Peircean type |
| `models.py` | `SignType` | ICON, INDEX, SYMBOL (Peircean trichotomy) |
| `models.py` | `SemanticTerritory` | Mapped region of semantic space with density metric |
| `models.py` | `DriftReport` | Semiotic drift analysis with stability_ratio property |

## Operating Contracts

- Sign type inference uses heuristics: emoji unicode ranges for ICON, deictic words for INDEX, default SYMBOL.
- Drift threshold is fixed at Jaccard < 0.3 for meaning shift; not configurable.
- Steganography uses a fixed 8-word synonym map; proof-of-concept only.
- Words shorter than 2 characters are excluded from sign extraction.
- Meaning is context-dependent; a Sign valid in one SemanticTerritory may be invalid in another.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (standard library only: `hashlib`, `time`, `re`, `collections`)
- **Used by**: `meme.memetics` (validate mutated memes retain intended signifier), `meme.neurolinguistic` (semiotic analysis identifies framing mechanisms)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
