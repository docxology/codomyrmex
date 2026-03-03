# AGENTS.md — Video Generation Scripts

## Purpose
These scripts are the **runnable entry points** for video generation. AI agents should use these as the canonical way to trigger video generation workflows.

## Key Entry Points

| Script | When to Use |
|--------|-------------|
| `orchestrate.py` | Config-driven generation with all parameters from YAML |
| `examples/basic_usage.py` | Minimal API demonstration |

## Execution Contract

- **Safe to run without API key**: Both scripts print a warning and exit 0 (not a failure)
- **Requires `GEMINI_API_KEY`** for live generation via Veo 2.0
- **Configurable via**: `config/video/config.yaml` — change model, prompt, aspect ratio, duration
- **Output destination**: `outputs/videos/` (relative to repo root, auto-created)

## Invocation Pattern

```python
# Programmatic invocation from another script
import subprocess
result = subprocess.run(
    ["uv", "run", "python", "scripts/video/orchestrate.py", "--prompt", "A sunset"],
    capture_output=True,
    text=True,
)
```

## Agent Guidelines

1. **Never hardcode API keys** — always use `GEMINI_API_KEY` environment variable
2. **Check output dir** before assuming generation succeeded — bytes may be returned as URI
3. **Veo 2.0 is slow** — expect 30–120 seconds per generation; handle timeouts gracefully
4. **Model selection**: Use `veo-2.0-generate-001` (stable) — do not use `veo-latest` in production scripts
