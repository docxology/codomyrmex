# Codomyrmex Architecture Overview

Codomyrmex is a modular, AI-first coding workspace enabling robust multi-agent development workflows across 129+ specialized functional modules.

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

- `src/codomyrmex/`: The primary source space housing all 129+ core modules.
- `docs/`: Comprehensive project documentation, mirroring the source structure (e.g., `docs/agents/`).
- `scripts/`: Automation utilities and maintenance scripts.
- `tests/`: Unified and modular integration/unit tests validating the Zero-Mock policy.

## Navigation

- **Deep Architecture**: [docs/project/architecture.md](docs/project/architecture.md)
- **Module Overview**: [docs/modules/overview.md](docs/modules/overview.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Personal AI Infrastructure**: [PAI.md](PAI.md)
