# Narrative -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Implements computational narratology with archetypal character mapping (Campbell/Jung), structural arc definitions (Hero's Journey, Freytag's Pyramid, Fichtean Curve), narrative analysis from text, template-based generation, counter-narrative construction, and synthetic myth assembly.

## Architecture

Template-and-arc narrative engine pattern. `NarrativeEngine` analyzes text by extracting tension curves from punctuation density, detecting character archetypes via keyword matching, and inferring themes from word frequency. Pre-defined arc functions provide canonical tension and emotional valence curves. `synthesize_myth` assembles domain-specific myths using the Hero's Journey structure.

## Key Classes

### `NarrativeEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `analyze` | `text: str` | `Narrative` | Extract arc, characters, theme, and resonance from text |
| `generate` | `template: NarrativeTemplate, params: dict` | `str` | Generate story text from template stages and parameters |
| `insurgent_counter` | `narrative: Narrative` | `Narrative` | Deep-copy and invert a narrative to produce a counter-narrative |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `Narrative` | `title, theme, arc, characters, cultural_resonance, content_segments, metadata, id` | Full computational representation of a story |
| `NarrativeArc` | `name, tension_curve: list[float], emotional_valence: list[float]` | Structural progression with tension and emotion over time |
| `NarrativeTemplate` | `name, stages: list[str], roles: list[Archetype]` | Reusable template for narrative generation |
| `Archetype` | `HERO, SHADOW, MENTOR, TRICKSTER, HERALD, THRESHOLD_GUARDIAN, SHAPESHIFTER, ALLY` | Jungian/Campbellian character archetypes |

### Structure Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `heros_journey_arc` | none | `NarrativeArc` | 12-stage Monomyth tension and emotion curve |
| `freytag_pyramid_arc` | none | `NarrativeArc` | Classic 5-act dramatic structure |
| `fichtean_curve_arc` | none | `NarrativeArc` | Series of crises leading to climax (8 stages) |

### Myth Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `synthesize_myth` | `domain: str, archetypes: dict, theme: str` | `Narrative` | Assemble a Hero's Journey myth for a given domain with named archetypes |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`re`, `copy`, `time`, `uuid`, `collections.Counter`)

## Constraints

- `analyze` uses punctuation density heuristic for tension (exclamation marks, question marks, sentence length); no NLP.
- Character detection is keyword-based ("hero", "villain", "mentor", etc.); case-insensitive.
- Theme detection uses simple word frequency after stopword removal.
- `insurgent_counter` produces a deep copy with inverted title/theme and two hardcoded counter-segments.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `analyze` defaults theme to "unidentified" when no significant words are found.
- `synthesize_myth` defaults hero/shadow names to "The Hero"/"The Shadow" when archetypes lack those roles.
- Narrative IDs are auto-generated via `uuid4`.
