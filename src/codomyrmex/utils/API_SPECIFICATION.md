# Utils Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

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
- **`timing_decorator`**: Logs execution time of decorated function.
- **`retry`**: Retries operations with exponential backoff.

### 2.5 Misc
- **`get_timestamp`**: Returns formatted current time.
- **`truncate_string`**: Shortens string with suffix.
- **`get_env`**: Safe environment variable retrieval.
- **`flatten_dict`**: Flattens nested dictionaries.
- **`deep_merge`**: Recursively merges dictionaries.

## 3. Usage Example

```python
from codomyrmex.utils import safe_json_loads, retry

@retry(max_attempts=3)
def fetch_data():
    # ... implementation
    pass

data = safe_json_loads('{"key": "value"}')
```
