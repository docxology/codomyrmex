# Agent Module Functions Analysis

**Generated**: January 2026  
**Purpose**: Comprehensive analysis of all agent module functions and their CLI exposure status

## Summary

This document provides a complete inventory of all functions, classes, and methods available in the `src/codomyrmex/agents/` module and compares them with what's currently exposed in `scripts/agents/orchestrate.py`.

## Core Module Functions

### Configuration (`config.py`)
- ✅ `get_config()` - Exposed via `info` command
- ❌ `set_config(config)` - **NOT EXPOSED** - Should add `config set` command
- ❌ `reset_config()` - **NOT EXPOSED** - Should add `config reset` command
- ✅ `AgentConfig` - Used internally, config shown via `info`

### Core Interfaces (`core.py`)
- ✅ `AgentRequest` - Used internally for all execute/stream commands
- ✅ `AgentResponse` - Used internally, returned by all commands
- ✅ `AgentInterface` - Base class, used internally
- ✅ `AgentCapabilities` - Enum, used internally
- ❌ `AgentIntegrationAdapter` - **NOT EXPOSED** - Integration adapters not exposed via CLI

## Agent Client Functions

### Jules (`jules/jules_client.py`)
- ✅ `execute()` - Exposed via `jules execute`
- ✅ `stream()` - Exposed via `jules stream`
- ✅ `_check_jules_available()` - Exposed via `jules check`
- ✅ `get_jules_help()` - Exposed via `jules help`
- ✅ `execute_jules_command()` - Exposed via `jules command`
- ✅ `get_capabilities()` - Used internally
- ✅ `supports_capability()` - Used internally
- ✅ `validate_request()` - Used internally

### Claude (`claude/claude_client.py`)
- ✅ `execute()` - Exposed via `claude execute`
- ✅ `stream()` - Exposed via `claude stream`
- ✅ `get_capabilities()` - Used internally
- ✅ `supports_capability()` - Used internally
- ✅ `validate_request()` - Used internally
- ❌ Configuration check - Exposed via `claude check` (checks config, not client method)

### Codex (`codex/codex_client.py`)
- ✅ `execute()` - Exposed via `codex execute`
- ✅ `stream()` - Exposed via `codex stream`
- ✅ `get_capabilities()` - Used internally
- ✅ `supports_capability()` - Used internally
- ✅ `validate_request()` - Used internally
- ❌ Configuration check - Exposed via `codex check` (checks config, not client method)

### OpenCode (`opencode/opencode_client.py`)
- ✅ `execute()` - Exposed via `opencode execute`
- ✅ `stream()` - Exposed via `opencode stream`
- ✅ `_check_opencode_available()` - Exposed via `opencode check`
- ✅ `initialize_project()` - Exposed via `opencode init`
- ✅ `get_opencode_version()` - Exposed via `opencode version`
- ✅ `get_capabilities()` - Used internally
- ✅ `supports_capability()` - Used internally
- ✅ `validate_request()` - Used internally

### Gemini (`gemini/gemini_client.py`)
- ✅ `execute()` - Exposed via `gemini execute`
- ✅ `stream()` - Exposed via `gemini stream`
- ✅ `_check_gemini_available()` - Exposed via `gemini check`
- ✅ `save_chat()` - Exposed via `gemini chat save`
- ✅ `resume_chat()` - Exposed via `gemini chat resume`
- ✅ `list_chats()` - Exposed via `gemini chat list`
- ✅ `execute_gemini_command()` - Available but not directly exposed
- ✅ `get_capabilities()` - Used internally
- ✅ `supports_capability()` - Used internally
- ✅ `validate_request()` - Used internally

## Droid Module Functions

### Controller (`droid/controller.py`)
- ✅ `DroidController.start()` - Exposed via `droid start`
- ✅ `DroidController.stop()` - Exposed via `droid stop`
- ✅ `DroidController.status` - Exposed via `droid status`
- ✅ `DroidController.metrics` - Exposed via `droid metrics`
- ✅ `DroidController.config` - Exposed via `droid config show`
- ✅ `DroidController.update_config()` - Exposed via `droid config set`
- ✅ `DroidController.reset_metrics()` - Exposed via `droid metrics reset`
- ✅ `DroidController.execute_task()` - **NOT EXPOSED** - Could add `droid execute-task`
- ✅ `DroidController.record_heartbeat()` - **NOT EXPOSED** - Internal function
- ✅ `create_default_controller()` - Used internally
- ✅ `save_config_to_file()` - **NOT EXPOSED** - Could add `droid config save`
- ✅ `load_config_from_file()` - **NOT EXPOSED** - Could add `droid config load`
- ✅ `DroidConfig.from_dict()` - Used internally
- ✅ `DroidConfig.from_file()` - Used internally
- ✅ `DroidConfig.from_env()` - Used internally
- ✅ `DroidConfig.validate()` - Used internally

### Todo Manager (`droid/todo.py`)
- ❌ `TodoManager.load()` - **NOT EXPOSED** - Could add `droid todo load`
- ❌ `TodoManager.save()` - **NOT EXPOSED** - Could add `droid todo save`
- ❌ `TodoManager.validate()` - **NOT EXPOSED** - Could add `droid todo validate`
- ❌ `TodoManager.migrate_to_three_columns()` - **NOT EXPOSED** - Could add `droid todo migrate`
- ❌ `TodoItem.parse()` - Used internally
- ❌ `TodoItem.serialise()` - Used internally

### Droid Runner (`droid/run_todo_droid.py`)
- ❌ `main()` - **NOT EXPOSED** - This is a separate CLI entry point
- ❌ `run_todos()` - **NOT EXPOSED** - Could add `droid run-todos`
- ❌ `build_controller()` - Used internally
- ❌ `resolve_handler()` - Used internally

## Generic Module Functions

### Agent Orchestrator (`generic/agent_orchestrator.py`)
- ✅ `execute_parallel()` - Exposed via `orchestrate parallel`
- ✅ `execute_sequential()` - Exposed via `orchestrate sequential`
- ✅ `execute_with_fallback()` - Exposed via `orchestrate fallback`
- ❌ `select_agent_by_capability()` - **NOT EXPOSED** - Could add `orchestrate select --capability <cap>`
- ✅ `AgentOrchestrator.__init__()` - Used internally

### Task Planner (`generic/task_planner.py`)
- ❌ `TaskPlanner.create_task()` - **NOT EXPOSED** - Could add `task create`
- ❌ `TaskPlanner.decompose_task()` - **NOT EXPOSED** - Could add `task decompose`
- ❌ `TaskPlanner.get_task()` - **NOT EXPOSED** - Could add `task get`
- ❌ `TaskPlanner.update_task_status()` - **NOT EXPOSED** - Could add `task update`
- ❌ `TaskPlanner.get_ready_tasks()` - **NOT EXPOSED** - Could add `task ready`
- ❌ `TaskPlanner.get_task_execution_order()` - **NOT EXPOSED** - Could add `task order`
- ❌ `TaskPlanner.get_all_tasks()` - **NOT EXPOSED** - Could add `task list`

### Message Bus (`generic/message_bus.py`)
- ❌ `MessageBus.subscribe()` - **NOT EXPOSED** - Could add `message subscribe`
- ❌ `MessageBus.unsubscribe()` - **NOT EXPOSED** - Could add `message unsubscribe`
- ❌ `MessageBus.publish()` - **NOT EXPOSED** - Could add `message publish`
- ❌ `MessageBus.send()` - **NOT EXPOSED** - Could add `message send`
- ❌ `MessageBus.broadcast()` - **NOT EXPOSED** - Could add `message broadcast`
- ❌ `MessageBus.get_message_history()` - **NOT EXPOSED** - Could add `message history`

## Integration Adapters

### All Integration Adapters
- ❌ `JulesIntegrationAdapter.adapt_for_ai_code_editing()` - **NOT EXPOSED** - Integration adapters are programmatic
- ❌ `JulesIntegrationAdapter.adapt_for_llm()` - **NOT EXPOSED** - Integration adapters are programmatic
- ❌ `JulesIntegrationAdapter.adapt_for_code_execution()` - **NOT EXPOSED** - Integration adapters are programmatic
- ❌ Similar for Claude, Codex, OpenCode, Gemini adapters - **NOT EXPOSED**

**Note**: Integration adapters are designed for programmatic use, not CLI. They adapt agents for use with other Codomyrmex modules.

## Theory Module

### Architectures (`theory/agent_architectures.py`)
- ✅ `ReactiveArchitecture` - Listed via `theory architectures`
- ✅ `DeliberativeArchitecture` - Listed via `theory architectures`
- ✅ `HybridArchitecture` - Listed via `theory architectures`
- ❌ Architecture instantiation/usage - **NOT EXPOSED** - These are classes, not CLI commands

### Reasoning Models (`theory/reasoning_models.py`)
- ✅ `SymbolicReasoningModel` - Listed via `theory reasoning`
- ✅ `NeuralReasoningModel` - Listed via `theory reasoning`
- ✅ `HybridReasoningModel` - Listed via `theory reasoning`
- ❌ Model instantiation/usage - **NOT EXPOSED** - These are classes, not CLI commands

## Missing CLI Commands (Recommended Additions)

### High Priority
1. **Config Management**
   - `config set <key=value>` - Set configuration values
   - `config reset` - Reset to defaults
   - `config validate` - Validate current configuration

2. **Orchestrator Enhancements**
   - `orchestrate select --capability <cap>` - Select agents by capability

3. **Droid Enhancements**
   - `droid config save <file>` - Save configuration to file
   - `droid config load <file>` - Load configuration from file
   - `droid execute-task <operation_id>` - Execute a specific task
   - `droid todo load` - Load TODO list
   - `droid todo save` - Save TODO list
   - `droid todo validate` - Validate TODO file format

### Medium Priority
4. **Task Planner**
   - `task create <description>` - Create a new task
   - `task list` - List all tasks
   - `task get <id>` - Get task details
   - `task update <id> --status <status>` - Update task status
   - `task ready` - Get ready tasks
   - `task order` - Get execution order

5. **Message Bus**
   - `message subscribe <type> <handler>` - Subscribe to messages
   - `message publish <type> <content>` - Publish a message
   - `message history [--type <type>] [--limit <n>]` - Get message history

### Low Priority
6. **Droid Runner**
   - `droid run-todos [--count <n>]` - Run TODO items (separate from main runner)

## Functions Intentionally Not Exposed

1. **Integration Adapters** - Designed for programmatic use with other modules
2. **Internal Methods** - Methods prefixed with `_` are internal implementation details
3. **Base Classes** - Abstract base classes are not directly usable via CLI
4. **Theory Classes** - Architecture and reasoning model classes are for programmatic use

## Coverage Statistics

- **Total Agent Client Methods**: ~35
- **Exposed via CLI**: ~25 (71%)
- **Not Exposed (but could be)**: ~10 (29%)
- **Not Exposed (intentionally)**: ~15 (integration adapters, internal methods)

## Recommendations

1. **Add config management commands** - High value, low effort
2. **Add orchestrator capability selection** - Useful for advanced users
3. **Add droid TODO management** - Useful for task management workflows
4. **Consider task planner commands** - Useful for complex task decomposition
5. **Message bus commands** - Lower priority, more advanced use case

## Conclusion

The current CLI implementation covers **71% of directly usable functions**. The remaining functions are either:
- Internal implementation details (should not be exposed)
- Integration adapters (designed for programmatic use)
- Utility classes that could benefit from CLI exposure (recommended additions)

The core agent operations (execute, stream, check) are fully covered for all agent types.

