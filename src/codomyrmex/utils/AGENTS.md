# Codomyrmex Agents - Utils Module

**Context**: Low-level foundational utilities.
**Status**: Critical Infrastructure.

## Purpose

This directory contains the bedrock utilities for the repository. Agents modifying this folder must be extremely careful as changes here propagate to **every other module**.

## Operating Contracts

### 1. Script Creation

When creating **ANY** new script or CLI tool in this repository, you **MUST** inherit from `ScriptBase`.

- **DO NOT** use raw `argparse` boilerplate.
- **DO NOT** use raw `logging.basicConfig`.
- **ALWAYS** use `ScriptBase` to ensure standardized logging, config loading, and telemetry.

### 2. Subprocess Execution

When executing system commands:

- **NEVER** use `os.system`.
- **AVOID** raw `subprocess.run` or `subprocess.Popen` if possible.
- **ALWAYS** use `utils.run_command` or `utils.stream_command`.
  - Reasoning: These wrappers handle edge cases, logging, timeouts, and error formatting consistently.

### 3. Path Handling

- **ALWAYS** use `pathlib.Path` objects, never string paths.
- **ALWAYS** use `utils.ensure_directory()` before writing files.

## Common Patterns

**Async Command Execution**:

```python
from codomyrmex.utils import run_command_async

async def main():
    result = await run_command_async(["echo", "hello"])
```

**Retry Logic**:

```python
from codomyrmex.utils import retry

@retry(max_attempts=3)
def unstable_network_call():
    ...
```
