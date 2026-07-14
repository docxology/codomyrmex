# Codomyrmex Agents — src/codomyrmex/colony_kernel

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Colony Kernel has two explicit profiles. Advisory mode runs adversarial checks,
budget evaluation, trust lookup, and a ternary gate while retaining
`caller_reported_unattested` audit evidence. Strict mode governs only the
declared action-scope map: an `EXECUTE` proposal receives an Ed25519-signed,
single-use authorization; a registered executor consumes it atomically and
returns a signed receipt; only that receipt-linked path updates enforced trust,
budget, and outcome state. Unregistered mutating paths fail closed in strict
mode. Neither profile is a truth oracle or a repository-wide enforcement claim.

## Active Components

- `models.py` — Shared value-object and enum contract for subsystem exchange
- `kernel.py` — `ColonyKernel` integration class plus compatibility re-exports for subsystem classes
- `authorization.py` — Ed25519 capability envelopes, key registry, and SQLite lifecycle ledger
- `executor.py` — registered real-component executor and signed receipt adapter
- `sqlite_signal_store.py` — durable WAL-backed signal field for strict deployments
- `mcp_tools.py` — advisory, authorization, receipt, and scope `@mcp_tool` wrappers over the kernel singleton
- `config_loader.py` — YAML config loading from `config/colony_kernel/` (kernel.yaml, roles.yaml, decay_rates.yaml)
- `resource_ledger.py` — Standalone `ResourceLedger` / `ResourceBudget` (used by kernel.py and independently)
- `falsification_worker.py` — Ten attack-vector categories implemented by eleven concrete checks, including AST-based circular-dependency analysis
- `actuation_gate.py` — Protocol-based `ActuationGate` with pheromone pressure queries
- `pheromone_store.py` — Standalone `PheromoneStore` with per-key evaporation rates
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

## Dependencies

### External to colony_kernel

- `codomyrmex.agentic_memory.stigmergy.field.TraceField` — pheromone backing store; `PheromoneStore` wraps this
- `codomyrmex.agentic_memory.stigmergy.models.StigmergyConfig` — evaporation and floor configuration passed to `TraceField`
- `codomyrmex.model_context_protocol.decorators.mcp_tool` — decorator used in `mcp_tools.py`

### Standard library only

- `sqlite3` — consequence, authorization, signal, and resource persistence (WAL mode)
- `cryptography` — Ed25519 authorization and executor signatures
- `dataclasses`, `uuid`, `time`, `json`, `pathlib` — models and utility

### Expected external codomyrmex imports

The listed external dependencies are the expected cross-package imports for colony_kernel. Keep any new dependency explicit and documented here.

## MCP Tools

The advisory MCP tools delegate to a module-level `ColonyKernel` singleton (`_kernel` in `mcp_tools.py`). Strict deployments additionally expose authorization, attested-outcome, and action-scope tools through an explicitly configured kernel. The advisory singleton is process-local; strict durable state uses the configured SQLite profile.

| Tool | Category | Description |
|------|----------|-------------|
| `colony_propose_action` | `colony_kernel` | Submit an action proposal; runs falsification → budget → trust → gate; returns `GateResult` |
| `colony_record_outcome` | `colony_kernel` | Advisory caller-reported evidence; strict mode quarantines it |
| `colony_execute_authorized` | `colony_kernel` | Consume a signed capability and return a signed executor receipt |
| `colony_record_attested_outcome` | `colony_kernel` | Accept one receipt-linked attested outcome |
| `colony_action_scope` | `colony_kernel` | Inspect declared scope and bypass semantics |
| `colony_agent_profile` | `colony_kernel` | Read an agent's current `AgentTrustProfile` (role, trust_score, history length) |
| `colony_status` | `colony_kernel` | Dashboard snapshot: pheromone_summary, budget_usage, role_distribution, recent_consequences, pruning_candidates_count |
| `colony_pheromone_query` | `colony_kernel` | Sense pheromone strength at a given location and signal type |
| `colony_falsify_plan` | `colony_kernel` | Adversarial plan evaluation (10 attack vectors) without running the full gate; returns findings + recommendation |
| `colony_pruning_report` | `colony_kernel` | Stale or broken module locations identified by `PruningDaemon.scan()` |
| `colony_tick` | `colony_kernel` | Advance one colony time-step; evaporates pheromone traces; returns post-tick status |

## Operational Notes

### Witness state

`ConsequenceMemory` stores typed consequence records; advisory reports remain
caller supplied and are not an authoritative witness of execution. Strict
file-backed profiles persist consequence, authorization, receipt, signal, and
resource state through SQLite WAL tables. The `db_path=":memory:"` default is
explicit isolated-test mode and is not durable.

### Consequence loop

`propose_action` does not consume budget — it only checks whether the estimate would exceed the ceiling. Budget consumption happens inside the outcome path via `ResourceLedger.consume`. Advisory callers pair a successful EXECUTE verdict with caller-reported `record_outcome`; strict declared actions pair a consumed authorization and signed receipt with `record_attested_outcome`. A missing outcome still leaves the ledger's accumulated cost understated, so service integrations must monitor uncompleted lifecycles.

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

`ActuationGate` issues an unconditional REFUSE for any CRITICAL falsification finding (severity weight 1.0). Prospective MEDIUM+ findings use the RISK channel; REFUSE uses a distinct POLICY_REJECTION audit signal. Non-critical findings do not become observed FAILURE. Elevated effective hazard, computed as `max(RISK, FAILURE)` at the target, lowers the risk component of later proposals.

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
