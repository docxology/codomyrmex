# Codomyrmex Scripts

This directory contains orchestration, maintenance, and utility scripts for the Codomyrmex ecosystem.

## Quick Start

```bash
# Run all scripts (141 total)
python run_all_scripts.py

# Run with verbose output
python run_all_scripts.py --verbose

# Run specific modules only
python run_all_scripts.py --subdirs agents llm api

# Dry run - show what would execute
python run_all_scripts.py --dry-run

# Generate documentation
python run_all_scripts.py --generate-docs docs/scripts.md
```

## Module Index

| Module | Description |
|--------|-------------|
| `agents/` | Agent orchestration and LLM interactions |
| `api/` | API endpoint management |
| `auth/` | Authentication and authorization |
| `build_synthesis/` | Build artifact generation |
| `cache/` | Caching subsystem |
| `cerebrum/` | Reasoning engine and FPF integration |
| `ci_cd_automation/` | CI/CD pipeline automation |
| `cloud/` | Cloud provider integrations |
| `coding/` | Code generation and transformation |
| `compression/` | Data compression utilities |
| `config_management/` | Configuration management |
| `containerization/` | Docker and container operations |
| `data_visualization/` | Chart and visualization generation |
| `database_management/` | Database operations |
| `documentation/` | Documentation generation |
| `documents/` | Document processing |
| `encryption/` | Encryption operations |
| `environment_setup/` | Environment configuration |
| `events/` | Event-driven architecture |
| `fpf/` | First Principles Framework |
| `git_operations/` | Git workflow automation |
| `ide/` | IDE integrations |
| `llm/` | LLM provider clients |
| `logging_monitoring/` | Structured logging |
| `logistics/` | Workflow logistics |
| `metrics/` | Metrics collection |
| `model_context_protocol/` | MCP integrations |
| `module_template/` | Module scaffolding |
| `networking/` | Network operations |
| `orchestrator/` | Script orchestration core |
| `pattern_matching/` | Pattern matching utilities |
| `performance/` | Performance monitoring |
| `physical_management/` | Physical systems |
| `plugin_system/` | Plugin architecture |
| `scrape/` | Web scraping |
| `security/` | Security operations |
| `serialization/` | Data serialization |
| `skills/` | Skill definitions |
| `spatial/` | Spatial/3D operations |
| `static_analysis/` | Static code analysis |
| `system_discovery/` | System introspection |
| `templating/` | Template rendering |
| `terminal_interface/` | Terminal UI |
| `tools/` | Development tools |
| `utils/` | Shared utilities |
| `validation/` | Data validation |
| `website/` | Website generation |

## Structure

Each module directory contains:
- `orchestrate.py` - Thin wrapper that delegates to `codomyrmex.orchestrator.core`
- `examples/` - Usage examples (`basic_usage.py`, `advanced_workflow.py`)

See [SPEC.md](SPEC.md) for detailed architecture and [AGENTS.md](AGENTS.md) for AI agent guidance.
