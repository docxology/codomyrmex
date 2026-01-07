# Codomyrmex Agents — scripts/fabric

## Signposting
- **Parent**: [scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Automation and utility scripts for Fabric AI integration with Codomyrmex. Provides CLI access to Fabric functionality and workflow orchestration.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `AGENTS.md` – Project file
- `QUICKSTART.md` – Quick start guide
- `orchestrate.py` – Main orchestration script
- `fabric_orchestrator.py` – Fabric + Codomyrmex orchestrator
- `fabric_config_manager.py` – Configuration management script
- `setup_fabric_env.py` – Interactive environment setup
- `setup_demo.sh` – Setup demonstration script
- `fabric_env_template` – Environment template
- `code_improvement_workflow.py` – Code improvement workflow
- `content_analysis_workflow.py` – Content analysis workflow
- `demo_env_setup.py` – Demo environment setup
- `examples/` – Example implementations

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Scripts delegate to core module in `src/codomyrmex/llm/fabric/`.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../README.md) - Main project documentation
- **Core Module**: [src/codomyrmex/llm/fabric](../../../src/codomyrmex/llm/fabric/README.md)

