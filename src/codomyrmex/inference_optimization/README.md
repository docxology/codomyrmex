# inference_optimization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model inference optimization techniques including request batching, LRU caching, and quantization configuration. Provides a `RequestBatcher` that collects inference requests into batches using configurable size and timeout parameters, an `InferenceCache` with thread-safe LRU eviction, and an `InferenceOptimizer` that wraps a model function with caching, batching, and performance statistics tracking.


## Installation

```bash
pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Enums

- **`QuantizationType`** -- Quantization precision levels: FP32, FP16, INT8, INT4
- **`BatchingStrategy`** -- Request batching strategies: FIXED, DYNAMIC, ADAPTIVE

### Data Classes

- **`OptimizationConfig`** -- Configuration for inference optimization including quantization type, max batch size, batch timeout, caching toggle, cache size limit, and worker count
- **`InferenceStats`** -- Performance statistics with total requests/batches, average batch size, average latency, cache hits/misses, and computed cache hit rate
- **`InferenceRequest`** -- A generic inference request with ID, input data, priority, and creation timestamp; includes `age_ms` property
- **`InferenceResult`** -- Result of an inference call with request ID, output, latency in milliseconds, cache-hit flag, and batch size

### Components

- **`InferenceCache`** -- Thread-safe LRU cache for inference results; supports get, put, contains, clear, and reports current size; evicts least-recently-used entries when capacity is exceeded
- **`RequestBatcher`** -- Generic request batcher that collects requests in a background thread, groups them by configurable max batch size and timeout, and dispatches to a batch processor function; supports both synchronous (`submit_sync`) and asynchronous (`submit_async` returning `Future`) submission

### Services

- **`InferenceOptimizer`** -- Main inference optimization engine; wraps any batch-capable model function with LRU caching, single and batch inference methods, performance statistics, and cache management

## Directory Contents

- `__init__.py` -- Module implementation with optimizer, batcher, cache, and data models
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Quick Start

```python
from codomyrmex.inference_optimization import QuantizationType, BatchingStrategy, OptimizationConfig

# Initialize QuantizationType
instance = QuantizationType()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k inference_optimization -v
```

## Navigation

- **Full Documentation**: [docs/modules/inference_optimization/](../../../docs/modules/inference_optimization/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
