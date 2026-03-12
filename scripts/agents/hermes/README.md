# Hermes Thin Orchestrators

**Version**: v3.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

A suite of lightweight script orchestrators for setup, execution, and observability of the Hermes agent in your local environment. Each `main()` is a clean 5-step orchestrator delegating all meaningful work to named helper functions.

Aligned with **Hermes Agent v0.2.0** (v2026.3.12) — supports provider router, named sessions, `hermes doctor`, quiet mode, and MCP client detection.

## Execution Suite

### 1. Pre-flight Setup

Validates `config/agents/hermes.yaml`, binary availability (`hermes` CLI or `ollama`), SQLite storage writability, CLI version detection, and `hermes doctor` health check:

```bash
uv run python scripts/agents/hermes/setup_hermes.py
```

### 2. Execution Runbook

Submits a prompt to the Hermes agent, logging stateful sessions to SQLite (`~/.codomyrmex/hermes_sessions.db`):

```bash
uv run python scripts/agents/hermes/run_hermes.py --prompt "Explain agent swarms."
uv run python scripts/agents/hermes/run_hermes.py --prompt "Follow-up question" --session my-session-1

# Named sessions (v0.2.0) — create or resume by human-friendly name
uv run python scripts/agents/hermes/run_hermes.py --prompt "Continue task" --name "refactoring-payments"

# Quiet mode — raw response only, for CI/CD pipelines
uv run python scripts/agents/hermes/run_hermes.py --prompt "What is 2+2?" --quiet
```

### 3. Session Interpretability

Interrogates recent conversational states from the local SQLite store:

```bash
uv run python scripts/agents/hermes/observe_hermes.py --limit 3
uv run python scripts/agents/hermes/observe_hermes.py --limit 10 --db-path /path/to/sessions.db

# Search named sessions (v0.2.0)
uv run python scripts/agents/hermes/observe_hermes.py --search "refactoring"
```

### 4. AI-Powered Script Review

Dynamically scans a `scripts/` sub-directory, executes each orchestrator, and pipes source+output to Hermes to assess architectural thinness. Results saved as JSON + overall Markdown report:

```bash
uv run python scripts/agents/hermes/evaluate_orchestrators.py --target agents/hermes

# Dry run — discover scripts, execute them, but skip Hermes assessment
uv run python scripts/agents/hermes/evaluate_orchestrators.py --target agents/hermes --dry-run

# Save to a timestamped directory
uv run python scripts/agents/hermes/evaluate_orchestrators.py --target agents/hermes --output-dir evaluations/run_$(date +%Y%m%d)
```

### 5. Sweep-and-Dispatch Improvements

Reads the evaluation JSON files and dispatches targeted improvement prompts to a configurable agent (Hermes, Jules, or Claude Code):

```bash
# Dispatch via Hermes (default) — saves implementation guidance markdown
uv run python scripts/agents/hermes/dispatch_hermes.py --target agents/hermes

# Dispatch only NON-COMPLIANT scripts via Jules shell scripts
uv run python scripts/agents/hermes/dispatch_hermes.py \
  --dispatch-agent jules \
  --filter-failing

# Full sweep with Claude Code, custom output dir
uv run python scripts/agents/hermes/dispatch_hermes.py \
  --target agents/hermes \
  --eval-dir evaluations \
  --dispatch-agent claude \
  --output-dir dispatches/$(date +%Y%m%d)

# Dry run — plan what would be dispatched without executing
uv run python scripts/agents/hermes/dispatch_hermes.py --dry-run
```

## Configuration

See `config/agents/hermes.yaml` for all defaults including:

- `version_minimum` — minimum expected Hermes CLI version (default: `0.2.0`)
- `provider` — default inference provider (default: `openrouter`)
- `default_prompt` — default prompt for `run_hermes.py`
- `session_db` — SQLite path (overridable with `--db-path`)
- `observability.log_level` — log verbosity
- `evaluator.output_dir`, `evaluator.script_timeout`, `evaluator.excluded_dirs`
- `dispatch.agent`, `dispatch.mode`, `dispatch.filter_failing`, `dispatch.output_dir`

## v0.2.0 Features

| Feature | Script | Flag |
| :--- | :--- | :--- |
| Named Sessions | `run_hermes.py` | `--name "my-task"` |
| Quiet Mode | `run_hermes.py` | `--quiet` / `-Q` |
| Session Search | `observe_hermes.py` | `--search "query"` |
| Version Detection | `setup_hermes.py` | Automatic |
| Doctor Health Check | `setup_hermes.py` | Automatic |
| MCP Config Detection | `setup_hermes.py` | Automatic |

## Navigation

- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
- **Tests**: [test_hermes_orchestrators.py](../../../../src/codomyrmex/tests/unit/agents/test_hermes_orchestrators.py)
