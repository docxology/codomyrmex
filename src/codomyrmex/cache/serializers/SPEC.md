# Cache Serializers — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pluggable serialization framework for cache values with composable wrappers for compression and encoding.

## Architecture

Strategy pattern: `CacheSerializer` ABC defines the `serialize`/`deserialize` contract. Four leaf serializers and two composable wrappers can be combined. The `create_serializer` factory simplifies construction.

## Key Classes

### `CacheSerializer` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `serialize` | `value: Any` | `bytes` | Encode value to bytes |
| `deserialize` | `data: bytes` | `Any` | Decode bytes to value |

### Leaf Serializers

| Class | Constructor | Behavior |
|-------|-----------|----------|
| `JSONSerializer` | `indent: int \| None = None` | `json.dumps` with `default=str` fallback |
| `PickleSerializer` | `protocol: int = HIGHEST_PROTOCOL` | `pickle.dumps`/`pickle.loads` (trusted data only) |
| `StringSerializer` | `encoding: str = "utf-8"` | `str(value).encode()` / `data.decode()` |
| `TypedSerializer` | `base_serializer: CacheSerializer \| None` | Wraps value in `{"_type": ..., "_value": ...}`; restores primitives |

### Composable Wrappers

| Class | Constructor | Behavior |
|-------|-----------|----------|
| `CompressedSerializer` | `base_serializer, compression_level: int = 6` | `zlib.compress` / `zlib.decompress` around base |
| `Base64Serializer` | `base_serializer` | `base64.b64encode` / `base64.b64decode` around base |

### `create_serializer` (factory)

```python
create_serializer(serializer_type: str = "json", compress: bool = False, **kwargs) -> CacheSerializer
```

Accepted types: `"json"`, `"pickle"`, `"string"`, `"typed"`. Raises `ValueError` for unknown types. If `compress=True`, wraps in `CompressedSerializer`.

## Dependencies

- **Internal**: None
- **External**: Standard library (`json`, `pickle`, `zlib`, `base64`, `logging`)

## Constraints

- `PickleSerializer` is inherently unsafe for untrusted data (arbitrary code execution).
- `TypedSerializer` only restores `int`, `float`, `bool`, `str`, `list`, `dict`; other types returned as-is.
- `JSONSerializer` uses `default=str` to handle non-serializable types (lossy).
- Zero-mock: real serialization only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `json.JSONDecodeError` on malformed JSON in `JSONSerializer.deserialize`.
- `zlib.error` on corrupt compressed data in `CompressedSerializer.deserialize`.
- `TypedSerializer._is_json_serializable` logs debug on non-serializable values.
