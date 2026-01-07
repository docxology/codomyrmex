# Codomyrmex Agents — src/codomyrmex

## Signposting
- **Parent**: [src](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [agents](agents/AGENTS.md)
    - [api](api/AGENTS.md)
    - [auth](auth/AGENTS.md)
    - [build_synthesis](build_synthesis/AGENTS.md)
    - [cache](cache/AGENTS.md)
    - [cerebrum](cerebrum/AGENTS.md)
    - [ci_cd_automation](ci_cd_automation/AGENTS.md)
    - [coding](coding/AGENTS.md)
    - [compression](compression/AGENTS.md)
    - [config_management](config_management/AGENTS.md)
    - [containerization](containerization/AGENTS.md)
    - [data_visualization](data_visualization/AGENTS.md)
    - [database_management](database_management/AGENTS.md)
    - [documentation](documentation/AGENTS.md)
    - [documents](documents/AGENTS.md)
    - [encryption](encryption/AGENTS.md)
    - [environment_setup](environment_setup/AGENTS.md)
    - [events](events/AGENTS.md)
    - [fpf](fpf/AGENTS.md)
    - [git_operations](git_operations/AGENTS.md)
    - [llm](llm/AGENTS.md)
    - [logging_monitoring](logging_monitoring/AGENTS.md)
    - [metrics](metrics/AGENTS.md)
    - [model_context_protocol](model_context_protocol/AGENTS.md)
    - [module_template](module_template/AGENTS.md)
    - [networking](networking/AGENTS.md)
    - [pattern_matching](pattern_matching/AGENTS.md)
    - [performance](performance/AGENTS.md)
    - [physical_management](physical_management/AGENTS.md)
    - [plugin_system](plugin_system/AGENTS.md)
    - [logistics](logistics/AGENTS.md)
    - [scrape](scrape/AGENTS.md)
    - [security](security/AGENTS.md)
    - [serialization](serialization/AGENTS.md)
    - [spatial](spatial/AGENTS.md)
    - [static_analysis](static_analysis/AGENTS.md)
    - [system_discovery](system_discovery/AGENTS.md)
    - [template](template/AGENTS.md)
    - [templating](templating/AGENTS.md)
    - [terminal_interface](terminal_interface/AGENTS.md)
    - [tests](tests/AGENTS.md)
    - [tools](tools/AGENTS.md)
    - [utils](utils/AGENTS.md)
    - [validation](validation/AGENTS.md)
    - [website](website/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Core Codomyrmex package containing all functional modules. Provides modular coding workspace enabling AI development workflows with comprehensive capabilities including agents, code execution, security, LLM integration, spatial computing, and more. This is the root package that coordinates all submodules.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `agents/` – Directory containing agents components
- `api/` – Directory containing api components
- `auth/` – Directory containing auth components
- `build_synthesis/` – Directory containing build_synthesis components
- `cache/` – Directory containing cache components
- `cerebrum/` – Directory containing cerebrum components
- `ci_cd_automation/` – Directory containing ci_cd_automation components
- `cli.py` – Project file
- `coding/` – Directory containing coding components
- `compression/` – Directory containing compression components
- `config_management/` – Directory containing config_management components
- `conftest.py` – Project file
- `containerization/` – Directory containing containerization components
- `data_visualization/` – Directory containing data_visualization components
- `database_management/` – Directory containing database_management components
- `documentation/` – Directory containing documentation components
- `documents/` – Directory containing documents components
- `encryption/` – Directory containing encryption components
- `environment_setup/` – Directory containing environment_setup components
- `events/` – Directory containing events components
- `exceptions.py` – Project file
- `fpf/` – Directory containing fpf components
- `git_operations/` – Directory containing git_operations components
- `llm/` – Directory containing llm components
- `logging_monitoring/` – Directory containing logging_monitoring components
- `metrics/` – Directory containing metrics components
- `model_context_protocol/` – Directory containing model_context_protocol components
- `module_template/` – Directory containing module_template components
- `networking/` – Directory containing networking components
- `pattern_matching/` – Directory containing pattern_matching components
- `performance/` – Directory containing performance components
- `physical_management/` – Directory containing physical_management components
- `plugin_system/` – Directory containing plugin_system components
- `project_orchestration/` – Directory containing project_orchestration components
- `scrape/` – Directory containing scrape components
- `security/` – Directory containing security components
- `serialization/` – Directory containing serialization components
- `spatial/` – Directory containing spatial components
- `static_analysis/` – Directory containing static_analysis components
- `system_discovery/` – Directory containing system_discovery components
- `task_queue/` – Directory containing task_queue components
- `template/` – Directory containing template components
- `templating/` – Directory containing templating components
- `terminal_interface/` – Directory containing terminal_interface components
- `tests/` – Directory containing tests components
- `tools/` – Directory containing tools components
- `utils/` – Directory containing utils components
- `validation/` – Directory containing validation components
- `website/` – Directory containing website components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [src](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../README.md) - Main project documentation