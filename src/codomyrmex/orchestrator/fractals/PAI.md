# orchestrator/fractals PAI Capability Map

## Module Overview
Fractal task orchestration — recursively decomposes complex tasks into subtasks and coordinates multi-agent execution via the orchestrator layer.

## MCP Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `orchestrate_fractal_task` | Decompose and execute a task via recursive fractal orchestration | `task_description: str`, `max_depth: int = 3`, `provider: str = "claude"` |

## PAI Algorithm Phase Map

| Phase | Tool / Capability |
|-------|-------------------|
| PLAN  | `orchestrate_fractal_task` — recursive task decomposition |
| EXECUTE | `orchestrate_fractal_task` — multi-agent coordination |

## Usage Notes
- Requires a PAI-compatible LLM provider (default: `claude`)
- `max_depth` controls recursion depth; keep ≤5 to avoid token budget overruns
- Results returned as structured dict with `task_tree`, `results`, and `metadata` keys
