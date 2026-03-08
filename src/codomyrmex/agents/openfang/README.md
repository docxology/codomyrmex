# agents/openfang

Codomyrmex integration for [openfang](https://github.com/RightNow-AI/openfang) — a Rust-based Agent Operating System with autonomous Hands scheduling, 40-channel messaging, WebSocket gateway, and multi-agent orchestration.

## Overview

openfang wraps the openfang Rust binary via subprocess. The vendor submodule tracks upstream so `git submodule update --remote` always fetches the latest release. A built-in deploy pipeline handles `cargo build --release` and binary installation.

## Installation

### Option 1 — Prebuilt binary (recommended)

```bash
curl -fsSL https://openfang.sh/install.sh | sh
```

### Option 2 — Cargo install

```bash
cargo install openfang
```

### Option 3 — Build from vendor submodule

```bash
# 1. Initialize the submodule
git submodule update --init src/codomyrmex/agents/openfang/vendor/openfang

# 2. Build and install
uv run python -c "
from codomyrmex.agents.openfang.update import build_and_install
result = build_and_install()
print(result)
"
```

## Quick Start

### Python API

```python
from codomyrmex.agents.openfang import HAS_OPENFANG, OpenFangRunner

if HAS_OPENFANG:
    runner = OpenFangRunner()
    result = runner.execute("Analyze the git log and summarize recent activity")
    print(result["stdout"])
```

### MCP Tools

```python
from codomyrmex.agents.openfang.mcp_tools import openfang_execute, openfang_check

# Check installation status
status = openfang_check()
print(status)  # {"status": "success", "installed": True, "version": "...", ...}

# Run an agent query
result = openfang_execute(prompt="List all Python files modified in the last 7 days")
print(result["stdout"])
```

## Core Capabilities

| Capability | Description |
|-----------|-------------|
| Agent execution | Run natural-language queries via `openfang agent --message` |
| Hands scheduling | Autonomous cron-style agent packages |
| Channel messaging | Send messages via 40+ adapters (telegram, slack, discord, etc.) |
| WebSocket gateway | Real-time bidirectional agent communication |
| Doctor checks | Health verification for all openfang components |

## MCP Tools (7)

| Tool | Description |
|------|-------------|
| `openfang_check` | Installation status, version, submodule state |
| `openfang_execute` | Run agent query, return response |
| `openfang_hands_list` | List autonomous Hands with metadata |
| `openfang_send_message` | Send via channel adapter |
| `openfang_gateway` | Start/stop/status WebSocket gateway |
| `openfang_config` | Show current configuration |
| `openfang_update` | Pull upstream + optionally rebuild/install |

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENFANG_COMMAND` | `openfang` | Binary name or path |
| `OPENFANG_TIMEOUT` | `120` | Subprocess timeout (seconds) |
| `OPENFANG_GATEWAY_URL` | `ws://localhost:3000` | WebSocket gateway URL |
| `OPENFANG_INSTALL_DIR` | `/usr/local/bin` | Binary install destination |

## Update Workflow

```python
from codomyrmex.agents.openfang.mcp_tools import openfang_update

# Pull latest source only
openfang_update(rebuild=False)

# Pull + rebuild from Rust source
openfang_update(rebuild=True)

# Pull + rebuild + install binary
openfang_update(rebuild=True, install=True)
```

## License

openfang upstream: Apache 2.0. This integration wrapper: same as codomyrmex project license.
