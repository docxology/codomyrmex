# Agent Guidelines - Utils

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
