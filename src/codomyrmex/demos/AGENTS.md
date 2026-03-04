# Demos -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The demos module provides a centralized registration and execution framework for system demonstrations. It enables AI agents to register callable functions or script-file paths as named demos, discover demo scripts by filesystem scanning, and run demos with timing, success/failure tracking, and structured result reporting. The singleton `DemoRegistry` is the hub; the `@demo` decorator provides ergonomic registration.

## Key Files

| File | Class/Function | Role |
|------|----------------|------|
| `__init__.py` | Exports `DemoRegistry`, `demo`, `get_registry` | Module entry point |
| `registry.py` | `DemoRegistry` | Central registry: `register()`, `get_demo()`, `list_demos()`, `discover_scripts()`, `run_demo()`, `run_all()` |
| `registry.py` | `DemoInfo` (dataclass) | Metadata for a registered demo: name, description, target (callable or Path), module, category |
| `registry.py` | `DemoResult` (dataclass) | Execution result: name, success (bool), output, error, execution_time, metadata |
| `registry.py` | `demo` (decorator) | Registers a function as a demo in the global registry with optional name, description, module, category |
| `registry.py` | `get_registry()` | Returns the global singleton `DemoRegistry` instance |

## MCP Tools Available

This module exposes no MCP tools. Agents interact with it by importing from `codomyrmex.demos` directly.

## Agent Instructions

1. **Use the global registry** -- Always call `get_registry()` to access the singleton `DemoRegistry`. Do not instantiate `DemoRegistry` directly unless creating an isolated test context.
2. **Register demos with the decorator** -- Use `@demo(name="my_demo", description="...", module="my_module")` on functions. The decorator auto-detects the source module if `module` is not provided.
3. **Register script-based demos** -- Call `registry.register(name, description, target=Path("script.py"))`. Script demos are executed via `codomyrmex.orchestrator.thin.run()`.
4. **Discover demos from directories** -- Call `registry.discover_scripts("/path/to/demos", pattern="demo_*.py")` to auto-register all matching scripts. It extracts descriptions from the first docstring line.
5. **Run demos and check results** -- `run_demo(name)` returns a `DemoResult` with `success`, `output`, `error`, and `execution_time`. Always check `result.success` before proceeding.
6. **Filter demos by module or category** -- `list_demos(module="my_module")` or `list_demos(category="integration")` returns filtered `DemoInfo` lists.
7. **Run all demos** -- `run_all()` executes every registered demo sequentially and returns a list of `DemoResult` objects.
8. **Async support** -- If a demo target is an `async` function, `run_demo()` will execute it via `asyncio.run()` automatically.

## Operating Contracts

- The global registry is a module-level singleton (`_registry`). It persists for the process lifetime. Use `get_registry()` exclusively.
- `register()` warns via logger if overwriting an existing demo name but does not raise.
- `run_demo()` never raises exceptions. Failures are captured in `DemoResult.error` with `success=False`.
- Script-based demos are executed via `orchestrator.thin.run()`. The script must be a valid Python file.
- `discover_scripts()` silently skips files that cannot be read. It does not raise on permission errors.
- Callable demos: if the function returns `None`, it is treated as success. Any truthy return is success; falsy return is failure.
- `execution_time` is measured in seconds using `time.time()`.
- **Zero-Mock Policy**: Tests must use real callables or real script files. Do not mock `subprocess`, `Path`, or the orchestrator.
- **Isolation**: Each demo should be self-contained and clean up any resources it creates (temp files, state changes).

## Common Patterns

```python
from codomyrmex.demos import demo, get_registry

# Register a demo via decorator
@demo(name="hello_world", description="Simple hello demo", category="example")
def hello_world():
    print("Hello from demo!")
    return True

# Run it
registry = get_registry()
result = registry.run_demo("hello_world")
print(f"Success: {result.success}, Time: {result.execution_time:.2f}s")
```

```python
from pathlib import Path
from codomyrmex.demos import get_registry

# Discover and run script-based demos
registry = get_registry()
registry.discover_scripts(Path("scripts/demos"), pattern="demo_*.py")

# List all discovered demos
for info in registry.list_demos():
    print(f"  {info.name}: {info.description} [{info.category}]")

# Run all demos
results = registry.run_all()
passed = sum(1 for r in results if r.success)
print(f"Passed: {passed}/{len(results)}")
```

## Testing Patterns

```python
from codomyrmex.demos import DemoRegistry

class TestDemoRegistry:
    def test_register_and_run(self):
        reg = DemoRegistry()
        reg.register("test_demo", "A test", target=lambda: True)
        result = reg.run_demo("test_demo")
        assert result.success is True
        assert result.execution_time >= 0

    def test_missing_demo(self):
        reg = DemoRegistry()
        result = reg.run_demo("nonexistent")
        assert result.success is False
        assert "not found" in result.error

    def test_failing_demo(self):
        def bad_demo():
            raise ValueError("intentional failure")
        reg = DemoRegistry()
        reg.register("bad", "fails", target=bad_demo)
        result = reg.run_demo("bad")
        assert result.success is False
        assert "intentional failure" in result.error
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Use |
|-----------|-------------|-------------|
| **Engineer** | Full | Register demos, discover scripts, run demos during BUILD/EXECUTE |
| **Architect** | Design | Review demo catalog structure and categorization during PLAN |
| **QATester** | Validation | Run all demos and verify pass/fail results during VERIFY |
| **Researcher** | Read-only | List available demos and inspect results during OBSERVE |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
