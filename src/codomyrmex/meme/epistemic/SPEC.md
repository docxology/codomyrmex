# Epistemic -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models epistemic states -- facts, beliefs, and evidence -- for truth verification and contradiction detection. Provides evidence-weighted claim assessment, certainty calculation across belief sets, and a simple contradiction detector comparing facts against beliefs.

## Architecture

Evidence-aggregation verification pattern. `EpistemicEngine` maintains an `EpistemicState` containing facts and beliefs. Claims are verified by `verify_claim` which aggregates weighted evidence (penalizing fabricated sources) and produces a `Fact` with a confidence score. High-confidence facts (>0.8) are automatically accepted.

## Key Classes

### `EpistemicEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_fact` | `fact: Fact` | `None` | Register a verified fact in the state |
| `assess_claim` | `statement: str, evidence: list[Evidence]` | `Fact` | Verify claim against evidence; auto-accept if confidence >0.8 |
| `detect_contradictions` | none | `list[str]` | Find beliefs that negate known facts (string-negation heuristic) |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `Evidence` | `content, source, evidence_type, weight, validity` | A piece of evidence with type and strength |
| `EvidenceType` | `EMPIRICAL, LOGICAL, TESTIMONIAL, ANECDOTAL, FABRICATED` | Evidence strength classification |
| `Fact` | `statement, verification_method, confidence` | A verified claim with confidence score (0-1) |
| `Belief` | `statement, adherent, certainty, emotional_investment, supporting_evidence` | A held conviction with attachment metrics |
| `EpistemicState` | `facts, beliefs, entropy` | Aggregate epistemic status of a system |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `verify_claim` | `statement: str, evidence: list[Evidence]` | `Fact` | Aggregate evidence weights, penalize FABRICATED type, normalize to 0-1 confidence |
| `calculate_certainty` | `beliefs: list[Belief]` | `float` | Simple average of individual belief certainty values |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`dataclasses`, `enum`)

## Constraints

- Contradiction detection uses naive string-negation matching (`"not {fact}"` in belief); no semantic analysis.
- Fabricated evidence receives a 2x negative weight penalty in `verify_claim`.
- Confidence is normalized to 0-1 using `(support_score / total_weight + 1) / 2`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `verify_claim` returns 0.5 (neutral) confidence when no evidence is provided.
- `calculate_certainty` returns 0.0 for empty belief lists.
