# Codomyrmex Agents — src/codomyrmex/colony_kernel

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Colony Kernel is a proposal-evaluation control plane for codomyrmex's artificial ecology. It runs adversarial checks, budget evaluation, trust lookup, and a ternary actuation gate; stores caller-reported outcomes in SQLite; and maintains a process-local stigmergic field. The MCP adapter exposes this path, but the kernel does not itself enforce downstream tool execution or attest submitted outcomes.

## Active Components

- `models.py` — Shared value-object and enum contract for subsystem exchange
- `kernel.py` — `ColonyKernel` integration class plus compatibility re-exports for subsystem classes
- `mcp_tools.py` — Eight `@mcp_tool`-decorated functions; thin wrappers over the kernel singleton; includes a standalone `FalsificationWorker` for pre-flight plan evaluation
- `config_loader.py` — YAML config loading from `config/colony_kernel/` (kernel.yaml, roles.yaml, decay_rates.yaml)
- `resource_ledger.py` — Standalone `ResourceLedger` / `ResourceBudget` (used by kernel.py and independently)
- `falsification_worker.py` — Full 10-vector `FalsificationWorker` with AST-based circular-dependency analysis
- `actuation_gate.py` — Protocol-based `ActuationGate` with pheromone pressure queries
- `pheromone_store.py` — Standalone `PheromoneStore` with per-key evaporation rates
- `replay.py` — Fixed-input paired-locality replay and machine-readable artifact writer
- `attestation.py` — Versioned hash-chained execution ledger with explicit validation states
- `reference.py` — Pure reference gate/state semantics for differential replay
- `formal.py` — Runtime obligations and optional solver-neutral/Z3 result bridge
- `research/` — Offline adversarial, calibration, persistence, and probabilistic adapters
- `README.md` — Module overview, quick-start, and architecture diagram (Mermaid)
- `AGENTS.md` — This document
- `SPEC.md` — Formal specification with API contracts and invariants (Mermaid)
- `MCP_TOOL_SPECIFICATION.md` — Full JSON schema for each MCP tool (Mermaid)

## Key Symbols

| Symbol | Module | Role |
|--------|--------|------|
| `ColonyKernel` | `kernel.py` | Top-level integration class; primary entrypoint |
| `ColonyKernelConfig` | `kernel.py` | Configuration dataclass (db_path, budget, pheromone_config) |
| `ResourceBudget` | `resource_ledger.py` | Period-scoped ceiling for seven cost dimensions |
| `PheromoneStore` | `pheromone_store.py` | Wraps `TraceField`; deposit, reinforce, sense, tick |
| `ResourceLedger` | `resource_ledger.py` | Accumulates and checks multi-dimensional resource cost |
| `ActuationGate` | `actuation_gate.py` | Computes weighted additive gate score; routes EXECUTE / HOLD / REFUSE with hard overrides |
| `ConsequenceMemory` | `consequence_memory.py` | SQLite persistence for consequence records and trust profiles |
| `RoleAdapter` | `role_adapter.py` | Deterministic role inference from trust score and proposal count |
| `PruningDaemon` | `pruning_daemon.py` | Identifies stale/duplicate module locations via pheromone field |
| `FalsificationWorker` | `falsification_worker.py` | Ten deterministic adversarial checks against a proposal |
| `ActionProposal` | `models.py` | Atomic unit submitted to the gate |
| `GateResult` | `models.py` | Gate verdict: decision, score, reason, required_evidence |
| `ConsequenceRecord` | `models.py` | Full lifecycle record: proposal → action → result |
| `AgentTrustProfile` | `models.py` | Per-agent trust state; role, trust_score, history |
| `ColonySignal` | `models.py` | Enriched pheromone trace with source trust multipliers |
| `ResourceCost` | `models.py` | Seven-dimensional cost estimate or actual cost |
| `PruningCandidate` | `models.py` | A module location flagged as stale with confidence score |
| `FalsificationFinding` | `models.py` | A single adversarial finding with severity and remediation |
| `run_paired_locality_replay` | `replay.py` | Repeats the caller-reported locality fixture and returns semantic/file-digest inputs |
| `AttestationLedger` | `attestation.py` | Authenticated lifecycle evidence; required-attestation mode is explicit opt-in |
| `ReferenceGate` | `reference.py` | Independent deterministic semantics used for differential checks |
| `run_paired_benchmark` | `research/benchmark.py` | Deterministic synthetic baseline/mediated comparison; not an external benchmark |

## Dependencies

### External to colony_kernel

- `codomyrmex.agentic_memory.stigmergy.field.TraceField` — pheromone backing store; `PheromoneStore` wraps this
- `codomyrmex.agentic_memory.stigmergy.models.StigmergyConfig` — evaporation and floor configuration passed to `TraceField`
- `codomyrmex.model_context_protocol.decorators.mcp_tool` — decorator used in `mcp_tools.py`

### Standard library only

- `sqlite3` — ConsequenceMemory persistence (WAL mode)
- `dataclasses`, `uuid`, `time`, `json`, `pathlib` — models and utility

### Expected external codomyrmex imports

The listed external dependencies are the expected cross-package imports for colony_kernel. Keep any new dependency explicit and documented here.

## MCP Tools

All eight tools delegate to a module-level `ColonyKernel` singleton (`_kernel` in `mcp_tools.py`), which is an instance of the integration class re-exported from `kernel.py`. State is therefore persistent for the lifetime of the MCP server process and benefits from the canonical subsystem implementations (ActuationGate, PheromoneStore, ConsequenceMemory, RoleAdapter, PruningDaemon).

| Tool | Category | Description |
|------|----------|-------------|
| `colony_propose_action` | `colony_kernel` | Submit an action proposal; runs falsification → budget → trust → gate; returns `GateResult` |
| `colony_record_outcome` | `colony_kernel` | Record a caller-reported consequence; updates trust, deposits SUCCESS/FAILURE + DEPENDENCY pheromones |
| `colony_agent_profile` | `colony_kernel` | Read an agent's current `AgentTrustProfile` (role, trust_score, history length) |
| `colony_status` | `colony_kernel` | Dashboard snapshot: pheromone_summary, budget_usage, role_distribution, recent_consequences, pruning_candidates_count |
| `colony_pheromone_query` | `colony_kernel` | Sense pheromone strength at a given location and signal type |
| `colony_falsify_plan` | `colony_kernel` | Adversarial plan evaluation (10 attack vectors) without running the full gate; returns findings + recommendation |
| `colony_pruning_report` | `colony_kernel` | Stale or broken module locations identified by `PruningDaemon.scan()` |
| `colony_tick` | `colony_kernel` | Advance one colony time-step; evaporates pheromone traces; returns post-tick status |

## Operational Notes

### Witness state

`ConsequenceMemory` stores what callers report; it is not an authoritative witness of execution. SQLite WAL mode supports concurrent readers for file-backed databases. The `db_path=":memory:"` default is process-local; a file path persists consequence rows and profiles across restarts, but not the pheromone field, budget accumulator, or complete kernel state.

### Consequence loop

`propose_action` does not consume budget — it only checks whether the estimate would exceed the ceiling. Budget consumption happens inside `record_outcome` via `ResourceLedger.consume`. If `record_outcome` is never called for an executed action, the ledger's accumulated cost for that period will be understated. Callers are responsible for always pairing a successful EXECUTE verdict with a downstream `record_outcome` call.

### Role ladder

A brand-new agent starts as SANDBOX until it accumulates at least three proposals (`_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3`). SANDBOX is hard-refused. Promotion changes a label; non-sandbox labels do not currently grant or restrict action types. The ladder is:

```
SANDBOX (< 3 proposals or trust < 0.20)
  → REPAIR_ANT  (trust ≥ 0.20)
  → MEMORY_ANT  (trust ≥ 0.35)
  → DISPATCHER  (trust ≥ 0.50)
  → GUARD_ANT   (trust ≥ 0.70)
```

SANDBOX agents receive an unconditional REFUSE from `ActuationGate`.

### Pheromone compound keys

The pheromone field uses compound keys of the form `"{location}:{signal_type.value}"` (e.g. `"codomyrmex.git_operations.core:failure"`). Callers that interact with the raw `TraceField` must follow this convention; otherwise `PruningDaemon` and `ActuationGate` will not find the signals they expect.

### Falsification severity threshold

`ActuationGate` issues an unconditional REFUSE for any CRITICAL falsification finding (severity weight 1.0). Non-critical findings are reported in the result and can cause the kernel to deposit RISK pressure after evaluation, but they do not directly enter the current additive score. Elevated effective hazard, computed as `max(RISK, FAILURE)` at the target, lowers the risk component of later proposals.

### Pruning report versus archive

The MCP pruning-report path only produces `PruningCandidate` lists for human or GUARD_ANT review. Candidates with confidence < 0.50 are suppressed, and modules protected by a HUMAN_PRIORITY signal are not flagged by the registry scan. The separate `archive(candidate, dry_run=False)` API can move a reviewed path into `docs/plans/archived/`; its default is a non-mutating dry run.

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- **Zero-Mock Policy**: all tests use real `ColonyKernel` instances; no `unittest.mock`.

## Test Commands

```bash
# Full colony_kernel suite
uv run pytest tests/unit/colony_kernel/ -v

# Coverage report
HYPOTHESIS_NO_NPY=1 uv run pytest tests/unit/colony_kernel/ \
  --cov=src/codomyrmex/colony_kernel --cov-report=term-missing

# Single test file
uv run pytest tests/unit/colony_kernel/test_kernel.py -v

# MCP tools smoke-test
uv run pytest tests/unit/colony_kernel/test_mcp_tools.py -v
```

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
- **Module Overview**: [README.md](README.md)
- **Formal Specification**: [SPEC.md](SPEC.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Stigmergy Dependency**: [agentic_memory/AGENTS.md](../agentic_memory/AGENTS.md)
