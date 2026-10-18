# llm

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Automation and utility scripts.

## Directory Contents

- `mlx_profile.py` – Portable Python 3.15 configuration-only profiling CLI
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `cost_tracking/` – Subdirectory
- `embeddings/` – Subdirectory
- `examples/` – Subdirectory
- `guardrails/` – Subdirectory
- `orchestrate.py` – File
- `prompt_template_demo.py` – File
- `prompts/` – Subdirectory
- `rag/` – Subdirectory
- `streaming/` – Subdirectory
- `test_ollama.py` – File

## Portable MLX Configuration Profile

From the repository root, use the script's PEP 723 environment rather than
requesting native MLX packages for Python 3.15:

```bash
uv run --python 3.15 --script scripts/llm/mlx_profile.py \
    --output-dir output/mlx-profile-study --iterations 2000 --repeats 7
```

Equivalent default-workload recipes require an explicit new output location:

```bash
make mlx-profile MLX_PROFILE_OUTPUT=output/mlx-profile-make
just mlx-profile output/mlx-profile-just
```

Unset `MLX_MAX_KV_SIZE`, `MLX_KV_BITS`, and `MLX_PREFILL_STEP_SIZE` first. The output
location must contain none of the named artifacts: `profile.json`, `timings.svg`,
`report.html`, `manuscript.md`, or `manifest.json`. The manifest is written last;
retain partial failures and retry at a fresh location. The CLI prints artifact
paths as JSON. Missing required `--output-dir` or invalid input exits with an error;
`--help` is read-only. Timing, cProfile, and tracemalloc are separate config-only
passes, not model inference or Metal measurements. No results are published here.
See the [study protocol](../../docs/modules/llm/mlx-profiling-study.md).

## Navigation

- **Parent Directory**: [scripts](../README.md)
- **Project Root**: ../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
