# Codomyrmex Agents -- src/codomyrmex/meme/neurolinguistic

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models neurolinguistic programming concepts including cognitive framing (Lakoff), linguistic pattern libraries (Milton Model hypnotic patterns, Meta Model clarifying patterns), pattern detection in text, frame analysis via keyword matching, and content reframing between cognitive frames.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `NeurolinguisticEngine` | Orchestrator: register frames, audit text, spin content toward target frame |
| `framing.py` | `analyze_frames` | Identify active cognitive frames via keyword matching |
| `framing.py` | `reframe` | Translate content between frames via primary keyword substitution |
| `patterns.py` | `milton_model_patterns` | Library of 3 hypnotic patterns (Mind Read, Lost Performative, Cause-Effect) |
| `patterns.py` | `meta_model_patterns` | Library of 2 clarifying patterns (Universal Quantifier Challenge, Specify Verb) |
| `patterns.py` | `detect_patterns` | Detect linguistic patterns via keyword heuristic |
| `models.py` | `CognitiveFrame` | A Lakoff-style cognitive frame with keywords and semantic roles |
| `models.py` | `LinguisticPattern` | A detected or generated linguistic pattern with type and template |
| `models.py` | `PatternType` | HYPNOTIC, CLARIFYING, PERSUASIVE, DECEPTIVE |
| `models.py` | `PersuasionAttempt` | Record of a persuasive communication attempt |
| `models.py` | `BiasInstance` | A detected instance of cognitive bias |

## Operating Contracts

- Frame analysis uses keyword-hit-count matching; no semantic similarity or embeddings.
- `reframe` substitutes only the first keyword from each frame; naive string replacement.
- `detect_patterns` currently detects only "always"/"never" (Universal Quantifier) usage.
- `spin` appends a keyword phrase rather than restructuring content.
- `spin` returns original text unchanged if target frame is not registered.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (self-contained within `meme` package)
- **Used by**: `meme.memetics` (NLP patterns increase meme virality), `meme.narrative` (framing reinforces narrative moral)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
