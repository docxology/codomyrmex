# Codomyrmex Functional Specification

**Version**: v1.0.3 | **Status**: Active | **Last Updated**: February 2026

## System Concept

Codomyrmex is an idealized modular workspace designed to facilitate interaction between (pairwise) and among (multiple) humans, people, agents, synthetic systems, embodiments, tools, and things most broadly.

It functions as a cohesive "colony" of specialized modules where each component has a single responsibility, clear boundaries, and standardized interfaces. The system abstracts complexity through layering, ensuring that high-level workflows can be orchestrated without tight coupling to low-level implementations.

## Functional Requirements

- **Modularity**: The system must allow individual modules to be added, removed, or upgraded without breaking the larger system.
- **Agent-Readability**: All components must be self-documenting in a way that is parseable and understandable by AI agents (via `AGENTS.md` and `SPEC.md`).
- **Deep Signposting**: Every directory must provide clear navigation to its parent, children, and related modules to enable distinct context retrieval.
- **Polyglot Support**: The architecture must support tools and code in multiple languages, unified by standard protocols (like MCP and shared config).
- **Safe Execution**: Code execution must be sandboxed and observable.
- **Discoverability**: All modules must be discoverable via the `system_discovery` mechanism and registered in the module index.
- **Instrumentation**: Every module must integrate with `logging_monitoring` for structured telemetry and observability.

## Design Principles

### Modularity

- Each module is a self-contained unit under `src/codomyrmex/` with its own implementation, tests, and **RASP documentation pattern** — four standard files that make every module self-describing:
  - **R**EADME.md — Module overview, exports, and quick start
  - **A**GENTS.md — AI agent coordination and operating contracts
  - **S**PEC.md — Functional specification and design rationale
  - **P**AI.md — PAI system integration and algorithm phase mapping
- Modules expose only public APIs; internal implementation details remain encapsulated.
- Adding, removing, or upgrading a module must not require changes to unrelated modules.

### Internal Coherence

- Consistent directory structure and naming conventions across all 88 modules.
- Unified documentation patterns: every module carries the same set of specification files.
- Shared configuration idioms via standardized `Config` objects and `pyproject.toml` extras.

### Parsimony

- Include only essential elements; avoid speculative abstractions.
- Minimize the public API surface area of each module to reduce coupling.
- Lazy module loading ensures startup cost scales with usage, not with total module count.

### Functionality

- Prioritize working solutions over theoretical completeness.
- Forward-looking design that accommodates future modules without requiring rewrites.
- Each module must deliver demonstrable value through its defined interfaces.

### Testing

- Comprehensive test coverage enforced through `pytest` with structured markers (`unit`, `integration`, `slow`, `network`, `external`).
- Test-driven development practices encouraged; tests live alongside source in `src/codomyrmex/tests/unit/<module>/`.
- Real data analysis required over mocked approximations. Tests use skip-when-unavailable guards for external dependencies.

### Documentation

- Self-documenting code with clear docstrings and type annotations.
- Complete API specifications (`API_SPECIFICATION.md`) and MCP tool definitions (`MCP_TOOL_SPECIFICATION.md`) for applicable modules with AI-callable tools.
- Living documentation that stays synchronized with implementation through scaffolding tools.

## Architecture

The system is organized into four hierarchical layers. Dependencies flow strictly upward: higher layers may depend on lower layers, but never the reverse.

```mermaid
graph TB
    subgraph Application["Application Layer"]
        CLI[cli]
        SD[system_discovery]
    end

    subgraph Service["Service Layer"]
        DOC[documentation]
        API[api]
        CICD[ci_cd_automation]
        CONT[containerization]
        DB[database_management]
        CFG[config_management]
        LOG2[logistics]
        ORCH[orchestrator]
    end

    subgraph Core["Core Layer"]
        AGT[agents]
        COD[coding]
        LLM[llm]
        GIT[git_operations]
        SEC[security]
        PERF[performance]
        DV[data_visualization]
    end

    subgraph Foundation["Foundation Layer"]
        LM[logging_monitoring]
        ES[environment_setup]
        MCP[model_context_protocol]
        TI[terminal_interface]
    end

    Application --> Service
    Service --> Core
    Core --> Foundation
```

- **Foundation Layer**: Core infrastructure consumed by every other layer. Provides logging, environment validation, MCP interfaces, and terminal formatting.
- **Core Layer**: Primary capabilities including agent frameworks, code analysis (within `coding/`), LLM integration, version control, security scanning, performance profiling, and data visualization.
- **Service Layer**: Higher-level orchestration that composes core capabilities into documentation generation, API management, CI/CD pipelines (includes build automation), container management, database operations, configuration, logistics workflows, and workflow orchestration.
- **Application Layer**: User-facing entry points. The CLI provides the primary human interface; `system_discovery` provides module health monitoring and dynamic registration.

## API Specifications

### Simulation Module (`codomyrmex.simulation`)

#### `Simulator`

- `__init__(config: SimulationConfig = None, agents: List[Agent] = None)`: Initialize simulation.
- `run() -> SimulationResult`: Execute simulation loop.
- `add_agent(agent: Agent)`: Add agent to environment.
- `remove_agent(agent_id: str)`: Remove agent from environment.

#### `Agent` (Abstract Base Class)

- `act(observation: dict) -> Action`: logic for agent decision making.
- `learn(reward: float)`: logic for agent learning.

### Networks Module (`codomyrmex.networks`)

#### `NetworkGraph`

- `add_node(node_id: str, data: Any = None) -> Node`: Add node to graph.
- `add_edge(source_id: str, target_id: str, weight: float = 1.0) -> Edge`: Add edge between nodes.
- `get_neighbors(node_id: str) -> List[Node]`: Get adjacent nodes.
- `shortest_path(start_id: str, end_id: str) -> List[Node]`: Find shortest path (Dijkstra).

## Quality Standards

- **Coupling**: Aim for loose coupling between modules and high cohesion within each module.
- **Modularity Gate**: New modules must pass structure validation (RASP documentation — README, AGENTS, SPEC, PAI — plus `__init__.py` and test file scaffolding) before being committed.
- **Documentation Coverage**: 100% of module directories must contain a non-skeletal `README.md` with accurate content.
- **Interface Stability**: Public API changes require a semantic version bump and updated specification documents.
- **Test Coverage**: All modules must maintain unit test coverage; integration tests are required for cross-module interactions.

## Interface Contracts

- **Entry Points**: `__init__.py` serves as the primary entry point for every module, exporting the public API.
- **Configuration**: Modules receive configuration through standardized `Config` objects and environment variables validated by `environment_setup`.
- **Output Standards**: Consistent return types (e.g., `Result` objects for operations, structured dicts for data) across all module APIs.
- **MCP Protocol**: Modules that expose AI-callable tools must define them in `MCP_TOOL_SPECIFICATION.md` following the Model Context Protocol schema.
- **Error Handling**: Modules must raise domain-specific exceptions and log errors through `logging_monitoring` rather than silently failing.

## Modularity & Interfaces

- **Inputs**:
  - User commands (CLI, Shell).
  - AI Agent requests (MCP, Function Calls).
  - Event triggers (File changes, Webhooks).
- **Outputs**:
  - Synthesized code and artifacts.
  - Structured logs and telemetry.
  - Visualizations and reports.
  - Executable processes.
- **Boundaries**:
  - Modules interact primarily through public APIs defined in `src/codomyrmex/`.
  - Cross-module dependencies are strictly hierarchical (Foundation -> Core -> Service -> Application).

## Implementation Guidelines

- **Scaffolding**: Use `doc_scaffolder.py` to initialize new modules with the correct directory structure and documentation templates.
- **Signposting**: Maintain current parent/child navigation links in all markdown files to support agent traversal.
- **Dependency Management**: All dependencies are declared in `pyproject.toml`; module-specific `requirements.txt` files are deprecated.
- **Refactoring**: Regularly audit modules for TODO cleanup, placeholder replacement, and adherence to current conventions.
- **Versioning**: All modules follow semantic versioning starting at `v0.1.0`; version bumps are coordinated at the repository level.

## Coherence

This root directory serves as the nexus of the colony. It does not contain business logic itself but defines the structure (skeleton) and rules (membrane) that hold the organism together. The `src/` directory contains the organs, `docs/` the memory, and `scripts/` the reflexive behaviors.

## Known Architecture Debt

Tracked items by sprint target. Resolved items are kept for historical reference.

| Item | Status | Sprint Target | Notes |
|------|--------|---------------|-------|
| Circular imports: ~35 pairs across modules | Open | Sprint 3 | Use `isort --check` + dependency graph to surface |
| Oversized files: 1 non-test file >1K LOC | Open | Sprint 3 | `server.py` (1,052 lines); `reviewer.py` modularized to 388 LOC in v1.0.2 |
| EventBus trust events wrong signature | **Resolved v1.0.2** | — | `EventType.TRUST_LEVEL_CHANGED` added; `publish_event` call fixed in `trust_gateway.py` |
| PAI.md thin files (5 modules at <52 lines) | **Resolved v1.0.2** | — | All 5 expanded to ≥100 lines with MCP tool docs and phase mapping |
| Tool versioning: no deprecation scheme | **Resolved v1.0.2** | — | `version` + `deprecated_in` params added to `@mcp_tool` decorator |
| Stale module/tool counts in docs | **Resolved v1.0.3** | — | Updated: 88 modules, 171 tools (167 safe + 4 destructive), 3 resources |
| 6 optional modules fail import | Expected | — | Cloud (AWS/Azure/GCP), performance.monitoring, lazy_loader, security cert validator — require optional SDKs |
| Shutdown logging on closed streams | **Resolved v1.0.3** | — | `OrchestrationEngine.__del__` and `shutdown()` guarded against `ValueError` on closed file handles |
| Session status enum misuse | **Resolved v1.0.3** | — | `close_session()` now uses `SessionStatus.COMPLETED` instead of raw `"closed"` string |
| Telemetry DRY violation in server.py | **Resolved v1.0.3** | — | Extracted `_ensure_telemetry()` classmethod; eliminated ~60 lines of duplicated init code |
| Bidirectional PAI↔codomyrmex comms | Open | Sprint 4 | Codomyrmex cannot initiate calls to PAI; filesystem back-channel only |
| Tool versioning: no deprecation timeline UI | Open | Sprint 4 | `deprecated_in` metadata added but not surfaced in MCP tool list |

## Navigation Links

- **Documentation**: [Reference Guides](docs/README.md)
- **All Agents**: [AGENTS.md](AGENTS.md)
- **Functional Spec**: [SPEC.md](SPEC.md)
- **Source Index**: [src/README.md](src/README.md)
- **Module Docs**: [docs/modules/](docs/modules/README.md)
- **Repository Root**: [README.md](README.md)
