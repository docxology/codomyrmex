# Codomyrmex Agents -- src/codomyrmex/meme/epistemic

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models epistemic states for truth verification and disinformation defense. Maintains a knowledge base of facts and beliefs, verifies claims by aggregating weighted evidence (penalizing fabricated sources), and detects contradictions between beliefs and established facts.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `EpistemicEngine` | Orchestrator managing epistemic state, claim assessment, contradiction detection |
| `truth.py` | `verify_claim` | Aggregate evidence weights to produce a Fact with confidence score |
| `truth.py` | `calculate_certainty` | Compute average certainty across a set of beliefs |
| `models.py` | `Evidence` | A piece of evidence with type, weight, and validity |
| `models.py` | `EvidenceType` | EMPIRICAL, LOGICAL, TESTIMONIAL, ANECDOTAL, FABRICATED |
| `models.py` | `Fact` | A verified claim with confidence score (0-1) |
| `models.py` | `Belief` | A held conviction with certainty and emotional investment |
| `models.py` | `EpistemicState` | Aggregate epistemic status: facts, beliefs, entropy |

## Operating Contracts

- Claims assessed via `assess_claim` are auto-accepted as facts when confidence exceeds 0.8.
- Fabricated evidence receives a 2x negative weight penalty in `verify_claim`.
- Contradiction detection uses naive string-negation matching (`"not {fact}"` in belief text).
- `verify_claim` returns 0.5 (neutral) confidence when no evidence is provided.
- Operate with probabilistic confidence intervals; absolute truth is rarely attainable.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (self-contained within `meme` package)
- **Used by**: `meme.hyperreality` (epistemic checks distinguish real from simulacrum), `meme.memetics` (meme fitness often depends on perceived truth value)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
