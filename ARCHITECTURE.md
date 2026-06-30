# Codomyrmex Architecture Overview

Codomyrmex is a modular, AI-first coding workspace enabling robust multi-agent development workflows across **128** top-level functional modules under `src/codomyrmex/` ([docs/reference/inventory.md](docs/reference/inventory.md) — collected test count, workflow count, and related metrics refresh there).

This top-level document serves as a high-level orientation for the system's structural design. For the exhaustive deep-dive, see the [Comprehensive Architecture Document](docs/project/architecture.md).

## Core Architectural Principles

1. **Modularity First**: Every capability is encapsulated in a self-contained module (mostly in `src/codomyrmex/`). Modules possess their own dependencies, tests, and documentation bridges.
2. **Zero-Mock Verification**: The ecosystem strictly enforces real functional verification. The architecture forbids the mock pattern; integrations are tested using authentic connections and implementations.
3. **Model Context Protocol (MCP)**: System capabilities are exposed uniformly via MCP tool decorators (`@mcp_tool`) for standardized consumption by AI agents.
4. **Polyglot & Pluggable**: Language-agnostic interfaces built on top of robust foundations (like `uv` for Python environments).
5. **Separation of Tool vs. Content**: Codomyrmex operates on projects without permanently altering their intrinsic structural integrity unless explicitly directed.

## System Layers

The codebase is stratified into four distinct operational layers:

- **Foundation Layer**: Core infrastructure (logging, environment setup, database management, terminal UI).
- **Core Functional Modules**: Primary agent operations (code execution, Git automation, static analysis, data visualization, security).
- **Service Modules**: High-level orchestrators (CI/CD pipelines, documentation generation, containerization).
- **Specialized / Secure Cognitive Modules**: Niche capabilities (spatial modeling, identity verification, multi-agent swarm dispatch).

## Directory Structure Strategy

- `src/codomyrmex/`: The primary source space housing all **128** top-level core modules.
- `docs/`: Comprehensive project documentation, mirroring the source structure (e.g., `docs/agents/`).
- `scripts/`: Automation utilities and maintenance scripts.
- `tests/`: Unified and modular integration/unit tests validating the Zero-Mock policy.

## Documentation maintenance

- **Repo metrics** (modules, `@mcp_tool`, workflows, optional pytest collect): `uv run python scripts/doc_inventory.py` — [docs/reference/inventory.md](docs/reference/inventory.md).
- **RASP folder coverage** (`AGENTS.md` / `README.md` gaps under scoped roots): `uv run python scripts/rasp_gap_report.py` — [docs/plans/agents-readme-gap-report.md](docs/plans/agents-readme-gap-report.md); progress notes [docs/plans/rasp-audit-progress.md](docs/plans/rasp-audit-progress.md).

## Colony Kernel — The Living Spine (v1.3.0)

The `colony_kernel` module introduces an **artificial ecology control plane** modeled after the homeostatic regulation found in superorganism colonies. Rather than treating agent behavior as a sequence of discrete tool calls, the kernel maintains a continuous pressure landscape — pheromone gradients that rise and decay based on system events — and uses that landscape to govern every consequential action.

The kernel is built around a closed pressure loop: the **pheromone store** accumulates intensity signals from any module in the system; the **resource ledger** tracks the double-entry accounting of colony resources (compute, budget, attention, trust); the **actuation gate** consults both stores and the consequence memory before issuing a `+1` (approve), `0` (defer), or `-1` (veto) decision on any proposed action; and the **consequence memory** records each action's real outcome so the gate's policy chain improves over time. This loop — pressure → proposal → gate → action → consequence → memory → role → pressure — runs continuously and is the spine around which all higher-level agent behavior is organized.

Three supporting subsystems complete the ecology. The **role adapter** dynamically assigns and revokes capability roles (clearance bitmasks) so the gate can enforce least-privilege at runtime without hardcoding permissions. The **pruning daemon** runs as a background `asyncio.Task`, evicting stale pheromone signals according to configurable per-class TTLs and preventing gradient saturation. The **falsification worker** stress-tests proposals before they reach the gate: it pulls candidate signals from the pheromone store, runs them through a registered chain of `Falsifier` callables, and writes `FalsificationResult` records to consequence memory — ensuring that only conjectures that survive adversarial scrutiny accumulate pressure.

The eight subsystems of the Colony Kernel are: `pheromone_store`, `resource_ledger`, `actuation_gate`, `consequence_memory`, `role_adapter`, `pruning_daemon`, `falsification_worker`, and the top-level `ColonyKernel` assembler with its eight MCP tools (`colony_propose_action`, `colony_record_outcome`, `colony_agent_profile`, `colony_status`, `colony_pheromone_query`, `colony_falsify_plan`, `colony_pruning_report`, `colony_tick`). All subsystems follow the Zero-Mock policy — real SQLite persistence, real asyncio tasks, real callable chains — and are exposed uniformly via `@mcp_tool` decorators for standardized consumption by AI agents.

## Navigation

- **Deep Architecture**: [docs/project/architecture.md](docs/project/architecture.md)
- **Module Overview**: [docs/modules/overview.md](docs/modules/overview.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Personal AI Infrastructure**: [PAI.md](PAI.md)
