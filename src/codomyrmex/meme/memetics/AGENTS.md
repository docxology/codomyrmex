# Codomyrmex Agents -- src/codomyrmex/meme/memetics

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Core memetic engine providing data structures and algorithms for modeling memes as discrete replicable information units. Implements text dissection into atomic meme units, evolutionary selection (tournament/truncation), mutation operators (semantic drift, recombination, splicing), fitness evaluation, and population-level analysis.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `MemeticEngine` | High-level orchestrator: dissect, synthesize, evolve, select |
| `models.py` | `Meme` | Discrete information unit with fidelity, fecundity, longevity |
| `models.py` | `Memeplex` | Co-adapted meme complex with synergy bonus and mutation/recombination |
| `models.py` | `MemeticCode` | Ordered meme sequence with splice, excise, and fitness operations |
| `models.py` | `MemeType` | BELIEF, NORM, STRATEGY, AESTHETIC, NARRATIVE, SYMBOL, RITUAL, SLOGAN |
| `models.py` | `FitnessMap` | Population fitness snapshot with summary statistics |
| `fitness.py` | `virality_score` | Estimate virality from fecundity, brevity, and network scaling |
| `fitness.py` | `robustness_score` | Coefficient-of-variation based robustness metric for memeplexes |
| `fitness.py` | `decay_rate` | Exponential decay constant adjusted by longevity |
| `mutation.py` | `semantic_drift` | Token-level perturbation with fidelity degradation |
| `mutation.py` | `recombine` | Content crossover with averaged properties |
| `mutation.py` | `splice` | Horizontal gene transfer: inject foreign content |
| `mutation.py` | `batch_mutate` | Apply mutations to population at configurable rate |

## Operating Contracts

- Fitness dimensions (fidelity, fecundity, longevity) are clamped to [0, 1] on construction.
- Type classification uses keyword matching; defaults to BELIEF when no keywords match.
- High mutation rates (>0.3) risk semantic drift where original meaning is lost.
- `evolve` currently uses cloning instead of crossover recombination for offspring.
- Meme IDs are SHA-256 truncated to 16 chars; not collision-free at scale.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: None (standard library only: `hashlib`, `time`, `uuid`, `math`, `random`, `re`)
- **Used by**: `meme.semiotic` (validate mutated memes retain intended signifier), `meme.contagion` (evolved memes feed contagion simulation), `meme.narrative` (narrative meme type classification)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
