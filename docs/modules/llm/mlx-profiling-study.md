# Portable MLX Configuration Profiling Study

**Version**: 1.0 | **Status**: Protocol; local exploratory collection verified | **Date**: 2026-10-17

## Scope and claim boundaries

This protocol measures Python configuration setup only: constructing `MLXConfig`,
serializing it with `to_dict()`, and validating/resolving generation kwargs with
`get_generation_kwargs()`. It does not instantiate a native cache or load a model.
Scenario names describe requested configuration, not demonstrated backend support.
Local exploratory collection and bundle integrity have been verified. No numerical
performance results are published here; independent reruns and production-model
benchmarking remain open.

Native inference is `not_run` and Metal memory is `not_measured`. This study cannot
establish token throughput, prefill/decode latency, attention correctness,
long-context recall, device-memory savings, or native MLX support on Python 3.15.
It does not compare Python versions causally. Portable configuration tests and
opt-in tiny-model cache regressions are separate evidence, not production-model
benchmark replications.

## Reproduction

### Local exploratory baseline

The locally reviewed Python 3.15.0 bundle is
`output/mlx-profile-20261017-reviewed`, collected with 50,000 iterations and
21 repeats. Its manifest hashes were verified. It records HEAD
`6fedfa54334e7575f7fcfe6c25ac7e24b6ac3572`, `source_dirty=true`, and hashes of
the measured source files. This is a local exploratory baseline, not an
independently reproduced or production inference benchmark. The uncommitted
source hashes, not HEAD alone, identify the measured implementation.

### Collection command

Run from the repository root, selecting a new output location for each run:

```bash
uv run --python 3.15 --script scripts/llm/mlx_profile.py \
    --output-dir output/mlx-profile-study --iterations 2000 --repeats 7
```

The script requires Python 3.15 or newer. Its PEP 723 inline dependency metadata
selects portable Python dependencies without requesting `mlx` or `mlx-lm`.
This avoids the native MLX `cp315` packaging constraint for this config-only
workflow; it does not solve or test native packaging compatibility. Dependency
resolution may require network access; the resulting report is offline.

Unset `MLX_MAX_KV_SIZE`, `MLX_KV_BITS`, and `MLX_PREFILL_STEP_SIZE` before running;
the collector rejects their presence, even if empty. It also rejects an already
active `tracemalloc` session or CPU profiler rather than taking ownership of
caller instrumentation.
Active trace functions and monitoring tools are also rejected. Under coverage,
collect in an uninstrumented subprocess so tracing does not contaminate timing.
Explicit synthetic model/cache paths prevent user model selection and do not
load weights or write a model cache. `RUN_LIVE_MLX=1` is not required.

## Methodology

| Scenario | Requested cache settings | Resolved automatic prefill |
| --- | --- | --- |
| `unbounded` | No cap or KV quantization | 2048 tokens |
| `bounded_4096` | `max_kv_size=4096` | 1 token |
| `quantized_4bit` | `kv_bits=4` | 512 tokens |
| `quantized_8bit` | `kv_bits=8` | 512 tokens |

All scenarios use the same explicit non-sensitive settings, including seed 0,
`kv_group_size=64`, and `quantized_kv_start=0`. Bounded and quantized settings
are not combined. Prefill values are resolved configuration, not executed work.

1. Warm each scenario with `min(iterations, 100)` operations.
2. Collect uninstrumented `perf_counter_ns()` batch timings, dividing elapsed
   nanoseconds by the iteration count. Rotate the starting scenario cyclically
   per repeat to reduce fixed-order effects, without claiming randomization.
3. Run one separate `cProfile` batch per scenario; retain the top 30 entries by
   cumulative time, with self/cumulative seconds and call counts. These seconds
   include profiler overhead and are not the uninstrumented timing samples.
4. Run another separate batch under `tracemalloc`, recording retained and peak
   traced Python bytes. These are batch measurements, not bytes per operation,
   RSS, model-weight memory, or Metal/GPU allocations.
5. Report raw timing samples, their median, and median absolute deviation (MAD).
   MAD and the chart whiskers describe dispersion, not confidence intervals or
   statistical significance. Exceptions propagate rather than becoming timings.

The default workload is 2000 iterations and 7 repeats. Accepted bounds are
1–1,000,000 iterations and 3–100 repeats, with integer values only. Imports,
tokenization, model loading, prefill, and decode are outside the timed operation.
Host load, thermal state, and interpreter/build differences can affect timings;
record comparable conditions and independent reruns before interpreting changes.

## Artifacts and provenance

The collector schema is `codomyrmex.mlx.configuration-profile.v1`. The bundle is:

| File | Evidence |
| --- | --- |
| `profile.json` | Raw samples, effective settings, profiler entries, environment, and provenance |
| `timings.svg` | Accessible median timing chart with MAD whiskers |
| `report.html` | Escaped offline dashboard without scripts or remote assets |
| `manuscript.md` | Generated companion narrative for this run, not the central manuscript |
| `manifest.json` | SHA-256 hashes of the other four files |

Provenance records UTC creation time, Python version/build/implementation,
platform/machine, selected dependency versions, and clock resolution. The CLI
records Git HEAD and dirty status; source SHA-256 hashes cover `config.py`,
`profiling.py`, and `profile_report.py`. HEAD alone does not identify dirty source;
retain the exact source snapshot as well as hashes. The manifest detects changed
artifact bytes but is not a signature or independent scientific validation.

The writer rejects existing named artifacts and symlinks and uses exclusive file
creation. It writes the manifest last; its absence marks an incomplete bundle.
This is not an atomic directory transaction: preserve partial failures and retry
in a fresh directory instead of overwriting evidence. Verify manifest hashes and
source provenance before comparing or distributing bundles.

The writer checks consistency of raw samples with median/MAD and requires integer
allocation counts with retained bytes no greater than peak. HTML/SVG text is
escaped and Markdown metadata is encoded as literal text. These checks are not
independent evidence of scientific validity or a substitute for reviewing
identifying environment metadata before sharing.

## Related work and evidence boundaries

- **StreamingLLM**: Xiao et al., [*Efficient Streaming Language Models with
  Attention Sinks*](https://arxiv.org/abs/2309.17453v4), arXiv **2309.17453v4**
  (2024 revision). Background for why initial-token attention sinks matter to
  streaming cache design, not validation of Codomyrmex's bounded-prefill workaround
  or this Python microbenchmark.
- **KIVI**: Liu et al., [*KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV
  Cache*](https://arxiv.org/abs/2402.02750v2), arXiv **2402.02750v2** (2024).
  Background on KV-cache quantization only. Requesting MLX 4-bit or 8-bit cache
  settings does not implement or reproduce KIVI's asymmetric 2-bit method, nor
  establish equivalent quality or savings.

The versioned scholarly sources are intentionally distinct from the
[upstream rotating-mask PR](https://github.com/ml-explore/mlx-lm/pull/1978) and
[external workload report](https://gist.github.com/robertcprice/88f542f29ec8b97f2a8b1edde3fdc903).
Those are implementation evidence and motivation, not independent peer-reviewed
replications or local measurements. Production-model memory, throughput, and
recall studies remain pending; do not import external numbers into this study.

## Navigation

- **Parent**: [LLM documentation](README.md)
- **Source**: [MLX module](../../../src/codomyrmex/llm/mlx/README.md)
- **API**: [Profiling functions](../../../src/codomyrmex/llm/API_SPECIFICATION.md#25-portable-mlx-configuration-profiling)
- **Root**: [Repository overview](../../../README.md)
