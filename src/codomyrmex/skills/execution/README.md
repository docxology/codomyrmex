# Execution

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill runtime execution with error handling, timeouts, and chaining. Provides a unified executor that wraps skill invocations with parameter validation, timing, structured logging, and an execution audit trail.

## Key Exports

- **`SkillExecutor`** -- Executes skills with error handling, logging, and execution history tracking. Key methods:
  - `execute(skill, **kwargs)` -- Run a skill with parameter validation and structured logging
  - `execute_with_timeout(skill, timeout, **kwargs)` -- Run a skill with a timeout guard (uses ThreadPoolExecutor)
  - `execute_chain(skills, **kwargs)` -- Run a sequence of skills where each receives the previous result as `input`
  - `get_execution_log()` -- Retrieve the audit trail of all executions
  - `clear_log()` -- Reset the execution log
- **`SkillExecutionError`** -- Exception raised when skill execution fails, including timeout and validation failures

## Directory Contents

- `__init__.py` - SkillExecutor and SkillExecutionError (146 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.skills.execution import SkillExecutor, SkillExecutionError

executor = SkillExecutor(max_workers=4)

# Simple execution
result = executor.execute(my_skill, text="hello")

# With timeout
result = executor.execute_with_timeout(slow_skill, timeout=10.0, data="input")

# Chain: output of each skill feeds into the next
result = executor.execute_chain([parse_skill, transform_skill, output_skill], raw="data")
```

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
