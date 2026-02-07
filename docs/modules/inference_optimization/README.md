# Inference Optimization Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Inference Optimization module provides model optimization techniques including quantization configuration, request batching, result caching, and a unified inference optimization engine for Codomyrmex. It enables cost-effective and low-latency inference by combining LRU caching, configurable request batching with timeout-based collection, and performance statistics tracking. The module supports both synchronous and asynchronous request submission.

## Key Features

- **Quantization Configuration**: Define quantization levels (FP32, FP16, INT8, INT4) for model optimization
- **Request Batching**: Configurable batching with fixed, dynamic, and adaptive strategies, timeout-based batch collection, and background processing
- **LRU Inference Cache**: Thread-safe Least Recently Used cache with configurable size for deduplicating repeated inference calls
- **Unified Optimizer**: `InferenceOptimizer` combining caching, batching, and direct inference with automatic statistics collection
- **Batch Inference**: Process multiple inputs in a single call with per-item latency tracking
- **Performance Statistics**: Track total requests, batches, average batch size, average latency, and cache hit rate
- **Sync and Async Submission**: `RequestBatcher` supports both `submit_sync` (blocking) and `submit_async` (Future-based) patterns

## Key Components

| Component | Description |
|-----------|-------------|
| `QuantizationType` | Enum of quantization levels: FP32, FP16, INT8, INT4 |
| `BatchingStrategy` | Enum of batching strategies: FIXED, DYNAMIC, ADAPTIVE |
| `OptimizationConfig` | Configuration dataclass for quantization, batch size, timeout, caching, and worker count |
| `InferenceStats` | Statistics dataclass tracking requests, batches, latency, and cache hit rate |
| `InferenceRequest` | Generic dataclass representing a single inference request with ID, data, priority, and age tracking |
| `InferenceResult` | Generic dataclass for inference output with latency, cache status, and batch size metadata |
| `InferenceCache` | Thread-safe LRU cache with configurable max size, get/put/contains/clear operations |
| `RequestBatcher` | Batches inference requests with timeout-based collection, background processing thread, and sync/async submission |
| `InferenceOptimizer` | Main optimization engine combining cache, batcher, and model function with single and batch inference methods |

## Quick Start

```python
from codomyrmex.inference_optimization import (
    InferenceOptimizer, OptimizationConfig, QuantizationType,
)

# Define a model function
def model_fn(inputs):
    return [f"result for {x}" for x in inputs]

# Create optimizer with caching enabled
optimizer = InferenceOptimizer(
    model_fn=model_fn,
    config=OptimizationConfig(
        quantization=QuantizationType.FP16,
        max_batch_size=16,
        enable_caching=True,
        cache_max_size=500,
    ),
)

# Single inference (uses cache automatically)
result = optimizer.infer("Hello, world!")
print(result.output)       # "result for Hello, world!"
print(result.from_cache)   # False (first call)

# Second call hits cache
result2 = optimizer.infer("Hello, world!")
print(result2.from_cache)  # True

# Batch inference
results = optimizer.infer_batch(["input1", "input2", "input3"])
print(optimizer.stats.cache_hit_rate)
```

### Using the Request Batcher Directly

```python
from codomyrmex.inference_optimization import RequestBatcher

batcher = RequestBatcher(
    max_batch_size=16,
    timeout_ms=50,
    processor=model_fn,
)
batcher.start()

# Async submission
future = batcher.submit_async("some input")
result = future.result()

batcher.stop()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k inference_optimization -v
```

## Related Modules

- [llm](../llm/) - LLM infrastructure that benefits from inference optimization
- [feature_store](../feature_store/) - Feature retrieval that feeds optimized inference pipelines

## Navigation

- **Source**: [src/codomyrmex/inference_optimization/](../../../src/codomyrmex/inference_optimization/)
- **API Specification**: [src/codomyrmex/inference_optimization/API_SPECIFICATION.md](../../../src/codomyrmex/inference_optimization/API_SPECIFICATION.md)
- **Parent**: [docs/modules/](../README.md)
