# Codomyrmex Scripts

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `scripts/` directory contains operational scripts, automation utilities, demos, and orchestrators organized by codomyrmex module domain. Each subdirectory corresponds to a module's operational scripts, separate from the source Python implementation in `src/codomyrmex/`.

## Directory Structure

| Directory | Scripts | Purpose |
|-----------|:-------:|---------|
| `agentic_memory/` | 1 | Agent memory storage, retrieval, and semantic search demos |
| `agents/` | 31 | Agent subsystem examples, provider demos, and pooling utilities |
| `api/` | 2 | API orchestration, circuit breaker, pagination, and webhook examples |
| `audio/` | 1 | Audio processing example scripts |
| `audits/` | 4 | Codebase audits: documentation, exports, imports, RASP compliance |
| `auth/` | 2 | Authentication and authorization example scripts |
| `bio_simulation/` | 1 | Biological simulation runner scripts |
| `build_synthesis/` | 2 | Build synthesis and compilation orchestration |
| `cache/` | 3 | Cache management, async ops, replication, and warmers |
| `cerebrum/` | 3 | Case-based reasoning and knowledge retrieval demos |
| `ci_cd_automation/` | 3 | CI/CD pipeline management and build automation |
| `cli/` | 2 | CLI utilities and interactive shell examples |
| `cloud/` | 3 | Cloud instance management and S3 operations |
| `coding/` | 2 | Code execution sandbox and review demos |
| `collaboration/` | 3 | Multi-user session and collaborative editing demos |
| `compression/` | 2 | Data compression and decompression utilities |
| `concurrency/` | 2 | Concurrent execution and task management demos |
| `config_audits/` | 1 | Configuration audit and compliance checking |
| `config_management/` | 2 | Configuration get/set/validate operations |
| `config_monitoring/` | 1 | Configuration change monitoring and snapshots |
| `container_optimization/` | 1 | Container image optimization and layer analysis |
| `containerization/` | 2 | Docker build, scan, and runtime management |
| `cost_management/` | 1 | Cloud cost tracking, budget management, and spend analysis |
| `dark/` | 1 | PDF dark mode processing with filter presets |
| `data_lineage/` | 1 | Data flow tracking and impact analysis for pipelines |
| `data_visualization/` | 3 | Chart generation and dashboard HTML export |
| `database_management/` | 2 | Database operations, backup, replication, and sharding |
| `defense/` | 1 | Defense module demonstration scripts |
| `demos/` | 6 | Module demos: defense, identity, market, privacy, wallet |
| `dependency_injection/` | 1 | DI container and service registration demos |
| `deployment/` | 2 | Deployment automation and environment management |
| `docs/` | 5 | Documentation tooling: docstring fixes, architecture diagrams |
| `docs_gen/` | 1 | Documentation generation automation |
| `documentation/` | 21 | Documentation generation, linting, and publishing workflows |
| `documents/` | 2 | Document processing and transformation utilities |
| `edge_computing/` | 1 | Edge computing deployment and management scripts |
| `email/` | 1 | AgentMail and Gmail integration demos |
| `embodiment/` | 2 | Physical embodiment and robotics interface demos |
| `encryption/` | 2 | Encryption operations and key management examples |
| `environment_setup/` | 2 | Environment validation and dependency checking |
| `events/` | 2 | Event bus emit, history, and type registry demos |
| `evolutionary_ai/` | 2 | Evolutionary AI algorithm examples |
| `examples/` | 2 | Cross-module example scripts and output |
| `exceptions/` | 1 | Exception handling patterns and error hierarchy demos |
| `feature_flags/` | 2 | Feature flag strategies and evaluation examples |
| `feature_store/` | 1 | Feature store management and retrieval |
| `file_system/` | 1 | Cross-platform file system operations CLI |
| `finance/` | 1 | Financial calculation and analysis scripts |
| `formal_verification/` | 1 | Z3 constraint solving, ISC verification, and optimization |
| `fpf/` | 2 | Fetch-Parse-Format pipeline demos |
| `git_operations/` | 3 | Git automation and version control utilities |
| `graph_rag/` | 1 | Graph-based retrieval-augmented generation demos |
| `ide/` | 1 | IDE integration and antigravity module demos |
| `identity/` | 1 | Identity management demonstration scripts |
| `inference_optimization/` | 1 | Inference optimization (placeholder -- not yet implemented) |
| `llm/` | 3 | LLM provider examples: OpenRouter, Ollama, streaming, RAG |
| `logging_monitoring/` | 2 | Structured logging and monitoring integration |
| `logistics/` | 2 | Logistics orchestration and task management |
| `maintenance/` | 8 | Stub auditing, dependency checks, RASP fixers, doc sync |
| `metrics/` | 2 | Metrics collection and reporting examples |
| `migration/` | 1 | Database migration (placeholder -- not yet implemented) |
| `model_context_protocol/` | 7 | MCP server management, tool inspection, and debugging |
| `model_ops/` | 2 | Model operations and lifecycle management |
| `model_registry/` | 1 | Model registry (placeholder -- not yet implemented) |
| `module_template/` | 1 | Template for creating new module script directories |
| `multimodal/` | 2 | Image generation via Google AI (Imagen 3) with config |
| `networking/` | 2 | Network operations and connectivity utilities |
| `notification/` | 1 | Notification delivery (placeholder -- not yet implemented) |
| `observability_dashboard/` | 1 | Observability dashboard (placeholder -- not yet implemented) |
| `orchestrator/` | 4 | Workflow execution, pipelines, state, triggers, templates |
| `pai/` | 6 | PAI integration: docs, skill updates, validation |
| `pattern_matching/` | 2 | Code pattern recognition and matching demos |
| `performance/` | 5 | Benchmarks, mutation testing, and regression detection |
| `physical_management/` | 1 | Physical infrastructure management scripts |
| `plugin_system/` | 2 | Plugin discovery and dependency resolution demos |
| `prompt_testing/` | 1 | Prompt testing (placeholder -- not yet implemented) |
| `reports/` | 1 | Coverage report generation from pytest JSON output |
| `rna/` | 1 | RNA-seq pipeline utilities (Amalgkit missing sample finder) |
| `scrape/` | 2 | HTML content extraction and text similarity |
| `security/` | 3 | Vulnerability scanning, secret detection, compliance audits |
| `serialization/` | 2 | Data serialization and format conversion demos |
| `skills/` | 2 | Skill discovery, marketplace, permissions, versioning |
| `spatial/` | 2 | Spatial data processing and 3D operations |
| `static_analysis/` | 2 | Code quality, linting, and security scanning |
| `system_discovery/` | 2 | Module discovery and health monitoring |
| `telemetry/` | 2 | Telemetry collection, alerting, sampling, and tracing |
| `templating/` | 2 | Template engine operations (Jinja2, Mako) |
| `terminal_interface/` | 2 | Rich terminal output and formatting demos |
| `tools/` | 2 | Tool management and invocation utilities |
| `tree_sitter/` | 2 | Tree-sitter AST parsing and code analysis |
| `utils/` | 7 | Shared utility functions and helper scripts |
| `validation/` | 4 | Schema validation, rules, sanitizers, and config checks |
| `verification/` | 4 | Phase verification scripts (phase 1-3, secure agent system) |
| `video/` | 1 | Video processing example scripts |
| `website/` | 3 | Dashboard and website utilities |
| `workflow_execution/` | 1 | CLI workflow runner with dry-run support |
| `workflow_testing/` | 1 | Workflow testing (placeholder -- not yet implemented) |

## Root Files

| File | Purpose |
|------|---------|
| `run_all_scripts.py` | Master orchestrator -- discovers and runs scripts across all subdirectories |
| `config.yaml` | Shared script configuration |
| `generate_config_docs.py` | Generates documentation from config directory structures |
| `__init__.py` | Package marker |
| `PAI.md` | PAI integration documentation for scripts |
| `AGENTS.md` | Agent context for the scripts directory |
| `SPEC.md` | Specification for the scripts directory |

## Usage

**Prerequisites:**
```bash
uv sync                          # Core dependencies
uv sync --extra <module>         # Module-specific optional deps
uv sync --all-extras             # All optional dependencies
```

**Run individual scripts:**
```bash
# Run a specific audit
uv run python scripts/audits/audit_rasp.py

# Run a demo
uv run python scripts/demos/demo_wallet.py

# Run maintenance tasks
uv run python scripts/maintenance/audit_stubs.py

# Run all scripts
uv run python scripts/run_all_scripts.py

# Launch the dashboard
uv run python scripts/website/launch_dashboard.py
```

## Conventions

- Each subdirectory has `README.md`, `AGENTS.md`, `SPEC.md`, and `PAI.md` (RASP pattern)
- Scripts import from `src/codomyrmex/` via sys.path manipulation or installed package
- Config-driven scripts read from `config/<module>/config.yaml`
- Placeholder demos raise `NotImplementedError` when the source module is not yet implemented
- Scripts use `codomyrmex.utils.cli_helpers` for consistent CLI output formatting

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Project Root](../README.md) | [Source Code](../src/codomyrmex/)
