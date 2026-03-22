# OpenGauss Agent — Documentation

**Module**: `src/codomyrmex/agents/open_gauss/` | **Upstream**: [math-inc/OpenGauss](https://github.com/math-inc/OpenGauss) v0.2.0 | **Status**: Active

## Overview

OpenGauss is a project-scoped **Lean4 workflow orchestrator** developed by Math, Inc. It provides a multi-agent frontend for the `lean4-skills` formal mathematics workflows:

| Workflow | Command | Description |
| --- | --- | --- |
| Guided proving | `/prove` | Interactive theorem proving agent |
| Autonomous proving | `/autoprove` | Runs without user interaction |
| Declaration drafting | `/draft` | Skeleton Lean4 declarations |
| Interactive formalization | `/formalize` | NL → Lean4, step by step |
| Autonomous formalization | `/autoformalize` | NL → Lean4, fully automatic |

Codomyrmex integrates this as a **Git submodule** with a configurable client wrapper, structured JSONL logging, JSON artifact exports, and a 111-test zero-mock suite.

---

## 1. Configure

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `GAUSS_HOME` | `~/.gauss` | Root for all Gauss state (DB, logs, artifacts) |
| `OPENROUTER_API_KEY` | *(required for LLM)* | OpenRouter API key |
| `GAUSS_DEFAULT_MODEL` | `openrouter/anthropic/claude-sonnet-4` | Default LLM model |
| `GAUSS_LOG_LEVEL` | `INFO` | Python log level: DEBUG/INFO/WARNING |
| `GAUSS_TIMEZONE` | *(server local)* | IANA timezone, e.g. `America/Los_Angeles` |

```bash
export GAUSS_HOME=~/.gauss
export OPENROUTER_API_KEY=sk-or-...
export GAUSS_DEFAULT_MODEL=openrouter/anthropic/claude-sonnet-4
export GAUSS_LOG_LEVEL=INFO
```

### Config file

Copy `config.example.yaml` to `~/.gauss/config.yaml` (optional — env vars take precedence):

```bash
cp src/codomyrmex/agents/open_gauss/config.example.yaml ~/.gauss/config.yaml
```

### Python config object

```python
from open_gauss_client import OpenGaussConfig

# From environment (preferred)
config = OpenGaussConfig.from_env()

# Or explicit
config = OpenGaussConfig(
    gauss_home=Path("~/.gauss"),
    default_model="openrouter/anthropic/claude-sonnet-4",
    log_level="INFO",
)
config.validate()        # raises ValueError on hard errors; returns list of warnings
print(config.to_dict())  # JSON-safe dict of all config values
```

---

## 2. Validate Environment

Before running, validate that all directories, the DB schema, timezone, and optional packages are healthy:

```bash
# CLI
uv run python src/codomyrmex/agents/open_gauss/open_gauss_client.py --validate
```

```python
from open_gauss_client import OpenGaussConfig, validate_environment

config = OpenGaussConfig.from_env()
result = validate_environment(config)
# result["status"] == "ok" | "warnings" | "error"
# result["checks"] — list of {"check": str, "result": "pass"|"warn"|"fail", "detail": str}
# result["warnings"] — list of warning strings
# Written automatically to: {artifact_dir}/validation_report.json
```

**11 checks performed:**
`gauss_home_exists`, `gauss_home_writable`, `log_dir_exists`, `artifact_dir_exists`, `session_db_schema` (v4), `gauss_time_tz_aware`, `import_yaml`, `import_pydantic`, `import_httpx`, `import_rich`, `import_tenacity`

---

## 3. Run

### CLI demo (no Lean4 required)

```bash
# Full 10-step demo — session management, FTS5, artifact exports, JSONL logging
uv run python src/codomyrmex/agents/open_gauss/open_gauss_client.py --demo

# With custom GAUSS_HOME
uv run python src/codomyrmex/agents/open_gauss/open_gauss_client.py \
  --demo --gauss-home /tmp/my-gauss-demo
```

### Python API

```python
from open_gauss_client import OpenGaussConfig, OpenGaussClient

config = OpenGaussConfig.from_env()
client = OpenGaussClient(config)

# Validate first
result = client.validate_environment()   # writes validation_report.json
print(result["status"])                   # "ok" or "warnings"

# Create a session (like a conversation thread)
sid = client.create_session(
    "proof-session-001",
    source="codomyrmex",
    model="openrouter/anthropic/claude-sonnet-4",
    system_prompt="You are a Lean4 expert.",
    user_id="mini",
)

# Append messages
client.append_message(sid, "user", "Prove: ∀ n : ℕ, n + 0 = n")
client.append_message(sid, "assistant", "Use `simp [Nat.add_zero]`.")

# FTS5 full-text search across all sessions
hits = client.search_sessions("theorem", limit=10)

# Stats
stats = client.get_stats()
print(stats["total_sessions"], stats["total_messages"])

client.close()
```

### Gauss CLI (requires Lean4 + gauss installed)

```bash
cd src/codomyrmex/agents/open_gauss && ./scripts/install.sh
source ~/.zshrc

cd ~/my-lean-project
gauss /project init
gauss /prove "theorem foo : 1 + 1 = 2"
gauss /swarm
```

---

## 4. Logging

Every `OpenGaussClient` operation is logged atomically to:

```text
{GAUSS_HOME}/codomyrmex_logs/operations.jsonl
```

Each line is a JSON object:

```json
{"ts": "2026-03-20T20:03:24Z", "event": "client_init", "config": {...}}
{"ts": "2026-03-20T20:03:24Z", "event": "create_session", "session_id": "...", "source": "..."}
{"ts": "2026-03-20T20:03:24Z", "event": "append_message", "session_id": "...", "msg_id": 1, "len": 42}
{"ts": "2026-03-20T20:03:24Z", "event": "search_messages", "query": "theorem", "hits": 3}
{"ts": "2026-03-20T20:03:24Z", "event": "export_session_artifact", "session_id": "...", "path": "..."}
```

**Event types**: `client_init`, `validate_environment`, `create_session`, `append_message`, `search_messages`, `get_stats`, `export_session_artifact`, `export_all_artifacts`, `client_close`

**Read logs:**

```bash
# Stream last 20 log entries
tail -20 ~/.gauss/codomyrmex_logs/operations.jsonl | python3 -m json.tool

# Filter by event
grep '"event": "create_session"' ~/.gauss/codomyrmex_logs/operations.jsonl

# Count events
cat ~/.gauss/codomyrmex_logs/operations.jsonl | python3 -c \
  "import sys,json; c={}; [c.update({d['event']:c.get(d['event'],0)+1}) \
   for d in map(json.loads,sys.stdin)]; print(c)"
```

---

## 5. Reporting & Artifacts

All exports are written atomically (tmp + fsync + os.replace) to:

```text
{GAUSS_HOME}/codomyrmex_artifacts/
├── validation_report.json        ← written by validate_environment()
├── session_<id>_<ts>.json        ← written by export_session_artifact()
├── all_sessions_<ts>.jsonl       ← written by export_all_artifacts()
├── sessions_<source>_<ts>.jsonl  ← when source-filtered
└── demo_summary.json             ← written by --demo run
```

```python
# Export a single session
path = client.export_session_artifact("proof-session-001")
# → {artifact_dir}/session_proof-session-001_20260320_200324.json

# Bulk export all sessions
path = client.export_all_artifacts()
# → {artifact_dir}/all_sessions_20260320_200324.jsonl

# Source-filtered bulk export
path = client.export_all_artifacts(source="codomyrmex")

# Read a session artifact
import json
data = json.loads(path.read_text())
print(data["id"], len(data["messages"]))
```

**Session artifact format:**

```json
{
  "id": "proof-session-001",
  "source": "codomyrmex",
  "model": "openrouter/anthropic/claude-sonnet-4",
  "started_at": "...",
  "messages": [
    {"role": "user", "content": "...", "ts": "..."},
    {"role": "assistant", "content": "...", "ts": "..."}
  ]
}
```

---

## 6. Tests

**111 tests, 0.39s, zero mocks.** All real I/O, SQLite, file system, datetime.

```bash
# Run both test suites
uv run pytest src/codomyrmex/tests/agents/test_open_gauss.py \
              src/codomyrmex/tests/agents/test_open_gauss_client.py \
              -v --no-cov

# Run with coverage
uv run pytest src/codomyrmex/tests/agents/test_open_gauss*.py --cov=. --cov-report=term-missing
```

| Test File | Tests | Coverage Area |
| --- | --- | --- |
| `test_open_gauss.py` | 77 | Upstream API: SessionDB, gauss_time, constants, utils, project |
| `test_open_gauss_client.py` | 34 | OpenGaussConfig, validate_environment, OpenGaussClient |
| **Total** | **111** | |

---

## 7. Architecture

```text
open_gauss/                         ← Git submodule (math-inc/OpenGauss)
├── gauss_state.py                  ← SessionDB: SQLite WAL + FTS5
├── gauss_cli/
│   ├── project.py                  ← GaussProject: manifest + discovery
│   ├── config.py                   ← Configuration management
│   ├── models.py                   ← Model definitions
│   ├── gateway.py                  ← Multi-platform gateway
│   └── autoformalize.py            ← Autoformalization workflow
├── swarm_manager.py                ← Multi-agent tracking
├── gauss_time.py                   ← Timezone-aware clock
├── gauss_constants.py              ← OpenRouter + Nous API endpoints
├── utils.py                        ← atomic_json/yaml_write
├── open_gauss_client.py            ← [CODOMYRMEX] Configurable wrapper + demo
├── config.example.yaml             ← [CODOMYRMEX] Canonical config template
├── CODOMYRMEX_AGENTS.md            ← [CODOMYRMEX] Agent coordination
├── CODOMYRMEX_SPEC.md              ← [CODOMYRMEX] Functional specification
├── CODOMYRMEX_PAI.md               ← [CODOMYRMEX] PAI integration strategy
└── CODOMYRMEX_SKILL.md             ← [CODOMYRMEX] Skill definition
```

---

## 8. Submodule Maintenance

```bash
# Update to latest upstream
git submodule update --remote src/codomyrmex/agents/open_gauss
git add src/codomyrmex/agents/open_gauss
git commit -m "chore: update open_gauss submodule to latest"

# Re-initialize after clone
git submodule update --init src/codomyrmex/agents/open_gauss
```

---

## Navigation

- **Client wrapper**: [open_gauss_client.py](../../src/codomyrmex/agents/open_gauss/open_gauss_client.py)
- **Config template**: [config.example.yaml](../../src/codomyrmex/agents/open_gauss/config.example.yaml)
- **Test suite (upstream)**: [test_open_gauss.py](../../src/codomyrmex/tests/agents/test_open_gauss.py)
- **Test suite (client)**: [test_open_gauss_client.py](../../src/codomyrmex/tests/agents/test_open_gauss_client.py)
- **Spec**: [CODOMYRMEX_SPEC.md](../../src/codomyrmex/agents/open_gauss/CODOMYRMEX_SPEC.md)
- **PAI**: [CODOMYRMEX_PAI.md](../../src/codomyrmex/agents/open_gauss/CODOMYRMEX_PAI.md)
- **Skill**: [CODOMYRMEX_SKILL.md](../../src/codomyrmex/agents/open_gauss/CODOMYRMEX_SKILL.md)
- **Upstream**: [github.com/math-inc/OpenGauss](https://github.com/math-inc/OpenGauss)
