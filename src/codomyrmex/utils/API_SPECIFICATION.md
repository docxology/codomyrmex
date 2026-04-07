# Utils Module API Specification

**Version**: v1.2.8 | **Status**: Stable | **Last Updated**: April 2026

## 1. Overview
The `utils` module is a collection of common helpers for file operations, JSON handling, hashing, and execution timing.

## 2. Core Components

### 2.1 File System
- **`ensure_directory(path: Union[str, Path]) -> Path`**: Creates directories recursively.

### 2.2 Serialization
- **`safe_json_loads(text: str, default: Any = None) -> Any`**: Parses JSON without raising exceptions.
- **`safe_json_dumps(obj: Any, indent: int = 2) -> str`**: Serializes object to JSON safely.

### 2.3 Security & Hashing
- **`hash_content(content: Union[str, bytes], algorithm: str = "sha256") -> str`**: Hashes string or bytes.
- **`hash_file(path: Union[str, Path], algorithm: str = "sha256") -> Optional[str]`**: Hashes file content.

### 2.4 Decorators
- **`timing_decorator`**: Measures wall time; adds `execution_time_ms` when the return value is a `dict`.
- **`retry`** (import from `codomyrmex.utils`): Synchronous decorator with `max_attempts`, `delay`, `backoff`, and `exceptions`. Defined on the package so it is not shadowed by a submodule name collision.
- **`retry_sync` module** (`codomyrmex.utils.retry_sync`): `RetryConfig`, synchronous `retry`, and `async_retry` with jitter, capped delay, and `retryable_exceptions`. Use this surface for async code or richer backoff than the package `retry`.

### 2.5 Misc
- **`get_timestamp`**: Returns formatted current time.
- **`truncate_string`**: Shortens string with suffix.
- **`get_env`**: Safe environment variable retrieval.
- **`flatten_dict`**: Flattens nested dictionaries.
- **`deep_merge`**: Recursively merges dictionaries.

## 3. Usage examples

### Package-level `retry`

```python
from codomyrmex.utils import safe_json_loads, retry

@retry(max_attempts=3, delay=0.1, backoff=2.0, exceptions=(ConnectionError,))
def fetch_data():
    ...

data = safe_json_loads('{"key": "value"}')
```

### `retry_sync` (jitter, async)

```python
from codomyrmex.utils.retry_sync import async_retry, retry as retry_jitter

@retry_jitter(max_attempts=3, base_delay=0.5, jitter=True)
def call_upstream():
    ...

@async_retry(max_attempts=3, base_delay=0.1)
async def call_upstream_async():
    ...
```
