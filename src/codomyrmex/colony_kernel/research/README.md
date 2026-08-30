# Colony Kernel research harness

This package is an offline-first research substrate, separate from production
actuation. It provides versioned task/trace/provenance schemas, deterministic
paired adversarial fixtures, descriptive safety--utility metrics, a SQLite WAL
signal-store adapter, and an explicitly named probabilistic adapter.

The default benchmark uses synthetic cases only. It does not contact
AgentDojo, InjecAgent, ToolEmu, model providers, or benchmark download hosts.
Those integrations are protocols for caller-supplied adapters and must be
enabled in a separate, explicitly named live lane.

All numerical parameters are example/initial configurable values. They are
research settings, not calibrated constants or universal safety thresholds.
Every promoted result needs a manifest, artifact hash, seed, configuration,
environment, falsifier, and uncertainty analysis. A deterministic gate score is
not a probability, and the probabilistic adapter does not retroactively change
the deterministic gate's semantics.

`ResearchProgramOrchestrator` executes a validated dependency DAG and retains
failed tracks and blocked dependants as explicit results. It does not infer that
an available adapter supplies empirical evidence: roadmap entries separately
record implementation and evidence status.

## Local checks

```bash
uv run pytest tests/unit/colony_kernel/test_research_harness.py -q
uv run python scripts/run_colony_research.py \
  --output output/research/colony_kernel_offline.json --seed 0
```
