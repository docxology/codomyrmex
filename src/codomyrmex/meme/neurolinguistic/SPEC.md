# Neurolinguistic -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models neurolinguistic programming concepts including cognitive framing (Lakoff), linguistic pattern libraries (Milton Model, Meta Model), pattern detection, frame analysis, and content reframing. Provides tools for auditing text for persuasive patterns and cognitive biases.

## Architecture

Frame-and-pattern detection engine. `NeurolinguisticEngine` maintains a registry of `CognitiveFrame` objects and performs full text audits combining frame analysis with pattern detection. Frame analysis matches registered frame keywords against input text. Pattern detection identifies linguistic constructs (universal quantifiers, hypnotic patterns) via keyword heuristics.

## Key Classes

### `NeurolinguisticEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_frame` | `frame: CognitiveFrame` | `None` | Add a frame to the engine's registry |
| `audit` | `text: str` | `dict` | Full audit returning active frames, detected patterns, and impact score |
| `spin` | `text: str, target_frame: str` | `str` | Spin content toward a specific registered frame by injecting keywords |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `CognitiveFrame` | `name, keywords, roles, logic, strength` | A cognitive frame defining context and meaning |
| `LinguisticPattern` | `name, pattern_type, template, description` | A detected or generated linguistic pattern |
| `PatternType` | `HYPNOTIC, CLARIFYING, PERSUASIVE, DECEPTIVE` | Linguistic pattern classification |
| `PersuasionAttempt` | `target, technique, content, success_prob, timestamp` | Record of a persuasive communication attempt |
| `BiasInstance` | `bias_name, trigger, impact_score` | A detected instance of cognitive bias |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `analyze_frames` | `text: str, known_frames: list[CognitiveFrame]` | `list[CognitiveFrame]` | Identify active frames via keyword matching |
| `reframe` | `content, source_frame, target_frame` | `str` | Translate content between frames via primary keyword substitution |
| `milton_model_patterns` | none | `list[LinguisticPattern]` | Library of 3 hypnotic patterns (Mind Read, Lost Performative, Cause-Effect) |
| `meta_model_patterns` | none | `list[LinguisticPattern]` | Library of 2 clarifying patterns (Universal Quantifier Challenge, Specify Verb) |
| `detect_patterns` | `text: str` | `list[LinguisticPattern]` | Detect patterns via keyword heuristic ("always", "never") |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`time`, `dataclasses`, `enum`)

## Constraints

- Frame analysis is keyword-hit-count only; no semantic similarity or embedding comparison.
- `reframe` performs simple string replacement of primary keywords (first keyword only).
- `detect_patterns` currently only detects Universal Quantifier usage ("always"/"never").
- `spin` appends a single keyword phrase rather than restructuring content.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `spin` returns original text unchanged if target frame is not registered.
- `reframe` returns original content if either frame has no keywords.
- `analyze_frames` returns empty list when no frames match.
