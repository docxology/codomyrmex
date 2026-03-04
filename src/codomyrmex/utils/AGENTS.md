# Agent Guidelines - Utils

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Common utility functions: subprocess, JSON, file handling, retry, hashing.

## Key Functions

- **run_command(cmd)** — Execute shell command
- **safe_json_loads/dumps** — Safe JSON parsing
- **ensure_directory(path)** — Create directory if needed
- **hash_file(path)** — Hash file contents
- **retry(max_attempts)** — Retry decorator

## Agent Instructions

1. **Use safe JSON** — Always use `safe_json_loads` for untrusted input
2. **Retry transients** — Use `@retry()` for network calls
3. **Hash for verification** — Use `hash_file` for integrity
4. **Get env safely** — Use `get_env(key, required=True)`
5. **Time operations** — Use `@timing_decorator` for monitoring

## Common Patterns

```python
from codomyrmex.utils import (
    run_command, safe_json_loads, ensure_directory,
    hash_file, retry, get_env, deep_merge
)

# Execute command safely
result = run_command(["git", "status"])
if result.success:
    print(result.stdout)

# Parse JSON with fallback
data = safe_json_loads(response.text, default={})

# Ensure output directory
output_dir = ensure_directory("./output/reports")

# Retry with exponential backoff
@retry(max_attempts=3, delay=1.0, backoff=2.0)
def call_api():
    return requests.get(url)

# Merge configs
config = deep_merge(defaults, user_overrides)
```

## Testing Patterns

```python
# Verify safe JSON
result = safe_json_loads("invalid", default=None)
assert result is None

# Verify retry
attempts = []
@retry(max_attempts=3)
def flaky():
    attempts.append(1)
    if len(attempts) < 3:
        raise ValueError()
    return "ok"
assert flaky() == "ok"
```

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `utils_hash_content` | Hash text content using sha256/sha512/md5. Returns hex digest string. | SAFE |
| `utils_json_loads` | Safely parse a JSON string with a fallback default value. | SAFE |
| `utils_flatten_dict` | Flatten a nested dictionary into single-level with dot-separated keys. | SAFE |

## Operating Contracts

**DO:**
- Use `safe_json_loads(text, default={})` instead of `json.loads()` for untrusted input
- Use `@retry(max_attempts=3, delay=1.0, backoff=2.0)` for all network/external calls
- Use `ensure_directory(path)` before writing files — it creates parents automatically
- Use `get_env(key, required=True)` for all environment variable access

**DO NOT:**
- Use `json.loads()` directly — it raises on invalid input; `safe_json_loads` handles this gracefully
- Hard-code file paths — always use `ensure_directory()` + `Path` objects
- Retry non-transient errors (e.g., `FileNotFoundError`) — `@retry` should filter by exception type

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import; `utils_hash_content`, `utils_json_loads`, `utils_flatten_dict` MCP tools | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Utility function correctness, retry backoff behavior, JSON parsing edge cases | OBSERVED |
| **Researcher** | Read-only | `utils_hash_content` for content integrity verification; `utils_json_loads` for parsing results | SAFE |

### Engineer Agent
**Use Cases**: Use utility functions (`safe_json_loads`, `run_command`, `retry`, `hash_file`) during all BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Review utility API design, evaluate `deep_merge` behavior, plan retry and error handling strategies.

### QATester Agent
**Use Cases**: Validate utility function correctness, verify retry backoff behavior, test JSON parsing edge cases during VERIFY.

### Researcher Agent
**Use Cases**: Hash content for integrity verification, parse JSON responses from external sources safely.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/utils.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/utils.cursorrules)
