<!-- agents: curated -->
# Colony Kernel research coordination

## Purpose

This directory contains offline-first research adapters, not production
actuation. Preserve the boundary between deterministic runtime contracts and
research interpretations.

- Keep cases, traces, manifests, and hashes versioned and serializable.
- Use paired seeds and identical case assignments for baseline/mediated runs.
- Treat confidence, calibration, causal effect, optimality, and safety as
  unestablished until independent outcomes and uncertainty artifacts exist.
- Do not contact external providers or download benchmark data from unit tests
  or ordinary CI. External adapters receive caller-supplied fixtures only.
- Record environment, commit, lockfile, configuration, seed, and artifact
hashes for performance or manuscript-facing results.

See [README.md](README.md) and [SPEC.md](SPEC.md) for the active contract.

## Key Files

- `schemas.py` — versioned cases, traces, manifests, hashes, and leakage reports
- `benchmark.py` — deterministic paired synthetic baseline/mediated runner
- `metrics.py` — descriptive log loss, Brier, calibration, selective-risk, and bootstrap metrics
- `persistent_store.py` — SQLite WAL persistence adapter with crash-injection boundaries
- `probabilistic.py` — explicit generative-model declaration and adapter boundary

## Dependencies

The research package uses the existing Colony Kernel and stigmergy contracts,
Python standard-library persistence and statistics facilities, and optional
solver/provider adapters only when a caller supplies them. It does not bundle
external datasets or make network calls.

## Development Guidelines

- Keep all default fixtures deterministic and provider-free.
- Preserve the distinction between descriptive gate scores and probabilities.
- Add a focused test and a provenance field for each new metric or artifact.
- Record negative, unavailable, and inconclusive states instead of filling them
  with plausible values.
