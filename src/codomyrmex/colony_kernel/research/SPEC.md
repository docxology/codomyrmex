# Colony Kernel research specification

The research package has four boundaries:

1. `schemas.py` defines versioned cases, policy traces, manifests, hashes, and
   conservative train/held-out leakage reports.
2. `benchmark.py` runs paired baseline/mediated synthetic cases with an explicit
   task manifest, identical task assignments, and descriptive paired-bootstrap
   intervals. Runtime is measured only when explicitly requested; the seed applies
   to resampling and is recorded separately from deterministic case execution.
3. `persistent_store.py` adapts the existing `PheromoneStore` contract to
   SQLite WAL, reloads authoritative state inside a write transaction before
   each mutation, and exposes transaction-boundary crash injection for restart
   and concurrency experiments. A failed transaction does not leave the in-memory
   adapter ahead of durable state.
4. `probabilistic.py` declares priors, likelihoods, transitions, preferences,
   actions, horizon, and seed. Its output is an adapter observation, not a
   safety probability or a replacement for the deterministic gate.

External datasets and services are caller-supplied and opt-in. No result may
be described as calibrated, causal, optimal, safe, or biologically equivalent
without the corresponding artifact, falsifier, uncertainty estimate, and
reproduction record.
