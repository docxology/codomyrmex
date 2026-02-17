# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 2026 | **Strategic Target**: v0.2.0+

This document outlines the intelligent, phased roadmap for the Codomyrmex ecosystem, detailing the progression through intermediate stability releases (v0.1.x) to the major functional milestone v0.2.0 (The "Ant Colony" Orchestration Release).

---

## � Release Schedule & Objectives

### v0.1.3: Immediate Stability & Cleanup (Current Sprint)

**Theme**: "Foundation Hardening"

- [ ] **RASP Standardization**: Enforce stringent RASP (README, AGENTS, SPEC, PAI) documentation pattern across all 78 modules.
  - [ ] Run `scripts/audit_rasp.py` (to be created) to flag missing files.
- [ ] **Dependency Pruning**: Audit and cleanse `pyproject.toml` dependencies with `uv` to minimize bloat.
- [ ] **Pre-Release Checks**: Verify all existing tests pass for immediate bugfixes impacting `network` and `logging`.

---

### v0.1.4: The "Descaffold" & "Zero-Mock" Certification

**Theme**: "Real-World Reliability"
*Objective: Eliminate theoretical implementations and replace them with verified, functional code.*

#### 1. Zero-Mock Implementation

- [ ] **LLM Module**: Verify `src/codomyrmex/llm` uses strictly real API calls (OpenRouter/Ollama) in all tests marked `integration`.
  - [ ] Deprecate `MockLLMClient`.
- [ ] **Networking**: Replace verify-only mocks with `ephemeral_server` based tests for `src/codomyrmex/networking`.
- [ ] **Filesystem**: Ensure all file operations in tests use real temporary directories, not `unittest.mock.patch`.

#### 2. Test Suite Expansion

- [ ] **Coverage Targets**:
  - [ ] Core (`agents`, `coding`, `security`): >95%
  - [ ] Specialized (`cerebrum`, `meme`): >85%
- [ ] **Performance Benchmarks**: Introduce `pytest-benchmark` baselines for:
  - [ ] Module import time via `system_discovery`.
  - [ ] AST parsing speed in `coding/parsers`.

---

### v0.1.5: Cognitive Capabilities & Agentic Tools

**Theme**: "Tool Use & Memory"
*Objective: Expand the agent's ability to act autonomously and remember context.*

#### 1. MCP Expansion (Tool Explosion)

- [ ] **Git Operations**: Register `git_operations` as diverse MCP tools:
  - [ ] `git_create_branch`, `git_checkout`, `git_commit`, `git_merge_strategy`.
- [ ] **Docker Control**: Expose `containerization` tools:
  - [ ] `docker_list_containers`, `docker_logs_fetch`, `docker_compose_up`.
- [ ] **Filesystem Intelligence**: Add `smart_grep` and `semantic_search` tools to MCP.

#### 2. Agent Memory Integration

- [ ] **Context Persistence**: Integrate `agentic_memory` with `llm` calls.
  - [ ] Implement `ShortTermMemory` (session-based) via Redis/Dict.
  - [ ] Implement `LongTermMemory` (vector-based) via `vector_store`.
- [ ] **Profile Management**: Allow agents to read/write to `user_profile.json` (preferences, active context).

---

### v0.1.6: Observability & Interaction

**Theme**: "The Hive View"
*Objective: Make the system visible, interactive, and controllable via Web and CLI.*

#### 1. Web Dashboard (Interactive)

- [ ] **Live Graph**: Render the module dependency graph (`relationships.md`) interactively using D3.js or Cytoscape.
- [ ] **Workflow Control**: Add "Stop/Resume" buttons for running agent tasks.
- [ ] **Log Stream**: WebSocket-based real-time log streaming from `logging_monitoring`.

#### 2. CLI Refinements

- [ ] **Interactive Mode**: `codomyrmex interactive` shell with auto-completion for module commands.
- [ ] **Doctor**: `codomyrmex doctor` - Unified diagnostic tool.
  - [ ] Checks: Python version, `uv` status, Docker connectivity, API key validity.

---

### v0.1.7: Cognitive Architecture & Learning

**Theme**: "Active Inference"
*Objective: Enable the system to reason about its goals and improve over time.*

#### 1. Cerebrum Integration

- [ ] **Bayesian Reasoning**: Activate `cerebrum` module for decision making in `orchestrator`.
  - [ ] Use `CaseBase` for retrieving past successful code generation patterns.
- [ ] **Active Inference Loops**: Implement "Goal -> Action -> Observation -> Update" loops for autonomous agents.

#### 2. Memetic Defense

- [ ] **Pattern Recognition**: Use `meme` module to identify repetitive failure patterns in codebase (anti-patterns) and suggest refactors.
- [ ] **Information Dynamics**: Track "concept drift" in documentation vs code.

---

### v0.1.8 and v0.1.9: Security, Scale & Optimization

**Theme**: "Fortress & Velocity"

#### 1. Security (v0.1.8)

- [ ] **Wallet & Identity**: Harden `wallet` module for secure key management.
- [ ] **Defense**: Activate `active_defense` patterns (e.g., honeytokens in test envs).
- [ ] **Governance**: Implement rigorous dependency scanning in CI/CD.

#### 2. Performance (v0.1.9)

- [ ] **Parallel Execution**: Optimize `orchestrator` for `asyncio` efficient task parallelization.
- [ ] **Startup Time**: Reduce CLI startup time to <500ms via lazy loading optimization in `__init__.py`.

---

## 🎯 v0.2.0: The "Ant Colony" Release

**Theme**: "Swarm Orchestration"
*Objective: Fully autonomous multi-agent collaboration.*

### Key Deliverables

- [ ] **Swarm Protocol**: Standardized communication protocol between specialized agents (e.g., "Coder" asks "Reviewer" for checking).
- [ ] **Self-Healing Workflows**: If a build fails, the "DevOps Agent" automatically diagnoses logs, fixes the config, and retries.
- [ ] **Project-Level Context**: Agents understand the entire repository context, not just single files.

---

## � Technical Debt & Maintenance (Ongoing)

- [ ] **Refactoring**: Continuous removal of "magic numbers" and hardcoded paths.
- [ ] **Documentation**: Keep `SPEC.md` and `AGENTS.md` strictly synchronized with code changes.
- [ ] **Type Safety**: Enforce `mypy --strict` compliance gradually across the codebase.
