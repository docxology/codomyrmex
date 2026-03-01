# Codomyrmex Agents — src/codomyrmex/orchestrator

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Script orchestration engine for discovering, configuring, executing, and reporting on Python scripts. Provides workflow DAG execution with dependency resolution, parallel runners, retry logic, and CI/CD integration bridges.

## Active Components

- **`core.py`** — Main entry point (`run_orchestrator`): CLI-driven script discovery, execution, and summary reporting
- **`discovery.py`** — `discover_scripts()`: finds Python scripts by directory traversal with depth, pattern, and skip-list filtering
- **`runner.py`** — `run_script()`, `run_function()`: execute individual scripts/functions with timeout and config support
- **`parallel_runner.py`** — `ParallelRunner`, `BatchRunner`, `run_parallel()`: concurrent script execution with resource management
- **`workflow.py`** — `Workflow`, `Task`, `RetryPolicy`: DAG-based workflow engine with `chain()`, `parallel()`, `fan_out_fan_in()` helpers
- **`thin.py`** — Lightweight orchestration DSL: `step()`, `pipe()`, `batch()`, `shell()`, `python_func()`, `retry()`, `timeout()`, `condition()`
- **`config.py`** — `load_config()`, `get_script_config()`: YAML/JSON configuration loading for script execution
- **`reporting.py`** — `generate_report()`, `save_log()`, `generate_script_documentation()`: execution logs and Markdown doc generation
- **`integration.py`** — `OrchestratorBridge`, `CICDBridge`, `AgentOrchestrator`: bridges to CI/CD pipelines and agent task runners
- **`exceptions.py`** — `StepError`, `OrchestratorTimeoutError`, `StateError`, `DependencyResolutionError`, `ConcurrencyError`
- **`engines/`** — Pluggable execution engines
- **`monitors/`** — Execution monitoring and health checks
- **`schedulers/`** — Task scheduling strategies
- **`workflows/`** — Pre-built workflow definitions

## Operating Contracts

- Use `discover_scripts()` before execution to respect skip-lists and depth limits.
- Prefer `Workflow` with `RetryPolicy` for multi-step pipelines; use `thin` DSL for quick one-off chains.
- Always pass `timeout` to `run_script()` — the default is 60 seconds.
- Use `ParallelRunner` for independent scripts; `Workflow` DAG for scripts with dependencies.
- Integration bridges (`CICDBridge`, `AgentOrchestrator`) require corresponding external services to be available.

## Common Patterns

```python
from codomyrmex.orchestrator import (
    discover_scripts, run_script, Workflow, Task, RetryPolicy,
    chain, parallel, ParallelRunner, run_parallel,
    step, pipe, shell, python_func, retry, timeout
)

# Discover and run scripts
scripts = discover_scripts(Path("./scripts"), max_depth=2)
for script in scripts:
    result = run_script(script, timeout=30)

# DAG workflow with retry
wf = Workflow("deploy")
wf.add_task(Task("build", fn=build_app))
wf.add_task(Task("test", fn=run_tests, depends_on=["build"]))
wf.add_task(Task("deploy", fn=deploy, depends_on=["test"],
                  retry_policy=RetryPolicy(max_retries=3)))
wf.run()

# Thin DSL for quick chains
pipe(
    shell("echo 'start'"),
    python_func(my_function),
    retry(flaky_task, max_retries=2),
    timeout(slow_task, seconds=10)
)
```

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `get_scheduler_metrics` | Retrieve the current metrics of the Orchestrator AsyncScheduler | Safe |
| `analyze_workflow_dependencies` | Analyze a proposed workflow DAG for cyclic dependencies | Safe |

## Navigation Links

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- **Parent**: [codomyrmex](../README.md)
