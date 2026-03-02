# Codomyrmex Agents -- src/codomyrmex/meme/narrative

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Implements computational narratology with Jungian/Campbellian archetypal character mapping, structural arc definitions (Hero's Journey, Freytag's Pyramid, Fichtean Curve), text-based narrative analysis, template-driven generation, counter-narrative construction, and synthetic myth assembly.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `NarrativeEngine` | Orchestrator: analyze text, generate from templates, produce counter-narratives |
| `models.py` | `Narrative` | Full computational representation of a story |
| `models.py` | `NarrativeArc` | Tension curve and emotional valence over time |
| `models.py` | `NarrativeTemplate` | Reusable template with stages and required archetypal roles |
| `models.py` | `Archetype` | HERO, SHADOW, MENTOR, TRICKSTER, HERALD, THRESHOLD_GUARDIAN, SHAPESHIFTER, ALLY |
| `structure.py` | `heros_journey_arc` | 12-stage Monomyth tension and emotion curve |
| `structure.py` | `freytag_pyramid_arc` | Classic 5-act dramatic structure |
| `structure.py` | `fichtean_curve_arc` | Series of crises leading to climax (8 stages) |
| `myth.py` | `synthesize_myth` | Assemble a Hero's Journey myth for a given domain |

## Operating Contracts

- `analyze` uses punctuation density for tension (no NLP dependency); exclamation and question marks drive scores.
- Character detection is keyword-based ("hero", "villain", "mentor"); case-insensitive.
- Theme detection uses word frequency after stopword removal; defaults to "unidentified".
- `insurgent_counter` deep-copies the narrative and inverts title/theme with hardcoded counter-segments.
- Narratives must be internally consistent; do not mix arc structures arbitrarily.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (standard library only: `re`, `copy`, `time`, `uuid`, `collections`)
- **Used by**: `meme.neurolinguistic` (framing reinforces narrative), `meme.hyperreality` (narratives build reality tunnels)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
