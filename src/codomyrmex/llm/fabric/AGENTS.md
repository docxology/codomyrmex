# Codomyrmex Agents — src/codomyrmex/llm/fabric

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Integration bridge between Codomyrmex and the [Fabric](https://github.com/danielmiessler/fabric)
AI pattern framework (danielmiessler/fabric). Provides pattern execution via subprocess,
configuration management, and high-level orchestration workflows combining Fabric
patterns with Codomyrmex capabilities.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `fabric_manager.py` | `FabricManager` | Core integration: list patterns, run patterns, track history |
| `fabric_manager.py` | `FabricManager.list_patterns()` | Invoke `fabric --listpatterns`, parse stdout into list |
| `fabric_manager.py` | `FabricManager.run_pattern()` | Write input to tmpfile, pipe to `fabric --pattern {name}`; 120s timeout |
| `fabric_manager.py` | `FabricManager.get_results_history()` | Return copy of all prior `run_pattern` results |
| `fabric_config_manager.py` | `FabricConfigManager` | Load/save `~/.config/fabric/config.json`; register custom patterns |
| `fabric_config_manager.py` | `FabricConfig` | Dataclass: `api_key`, `default_model`, `patterns_dir`, `custom_patterns` |
| `fabric_config_manager.py` | `FabricPattern` | Dataclass: `name`, `description`, `system_prompt`, `user_prompt_template`, `model`, `temperature`, `max_tokens` |
| `fabric_orchestrator.py` | `FabricOrchestrator` | High-level workflows: `analyze_code()` dispatches pattern sets by analysis type |
| `fabric_orchestrator.py` | `FabricOrchestrator.analyze_code()` | Maps `analysis_type` (comprehensive/security/quality/documentation/optimization) to pattern lists |

## Operating Contracts

- `FabricManager.run_pattern()` returns a result dict with `success: False` (not an exception) when Fabric binary is unavailable or subprocess times out (120s).
- `FabricManager.list_patterns()` returns `[]` when fabric is unavailable; raises on timeout.
- Pattern execution writes input to a named tempfile — safe for large inputs, no shell injection.
- All results are appended to `results_history` regardless of success or failure.
- Config loads from `~/.config/fabric/config.json`; missing file returns default `FabricConfig()` silently.
- Errors during config load are logged with `logger.warning` and swallowed — defaults used instead.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (`get_logger`)
- **External**: `fabric` binary (optional, installed separately at `~/.local/bin/fabric` or in PATH)
- **Used by**: `codomyrmex.llm` package exports, `codomyrmex.llm.mcp` (`query_fabric_metadata` tool), the `/Fabric` PAI skill

## Navigation

- **📁 Parent**: [llm](../README.md)
- **🏠 Root**: ../../../../README.md
