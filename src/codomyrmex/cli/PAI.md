# Personal AI Infrastructure — CLI Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The CLI module is the unified command-line interface for all codomyrmex operations.
It aggregates subcommands from every module into a single `codomyrmex` entry point,
providing a consistent, richly-formatted terminal experience for both human operators
and PAI agents invoking codomyrmex as a subprocess.

The CLI is organized into command groups:

| Command Group | Purpose |
|---------------|---------|
| `codomyrmex check` | Verify environment setup and dependencies |
| `codomyrmex modules` | List and inspect available modules |
| `codomyrmex status` | System status dashboard |
| `codomyrmex shell` | Interactive shell (REPL) |
| `codomyrmex workflow` | List and execute workflows |
| `codomyrmex project` | Project management |
| `codomyrmex ai` | AI code generation and analysis |
| `codomyrmex analyze <path>` | Code analysis |
| `codomyrmex build <path>` | Project build |
| `codomyrmex test <module>` | Run module tests |
| `codomyrmex fpf fetch <url>` | FPF fetch/parse/export |
| `codomyrmex skills` | Skill management |
| `codomyrmex quick run` | Quick script/workflow execution |
| `codomyrmex quick pipe` | Chain commands in a pipeline |
| `codomyrmex quick batch` | Parallel batch execution |
| `codomyrmex quick chain` | Sequential script chaining |

## PAI Capabilities

### No MCP Tools — CLI is Terminal-Only

The CLI module does not expose MCP tools. PAI agents interact with it via subprocess
invocation (Bash tool) rather than MCP calls. This is intentional: the CLI is the
human-facing interface layer; MCP is the agent-facing interface.

### Quick Run (PAI Agent Subprocess Pattern)

PAI agents in the EXECUTE phase can invoke codomyrmex operations as subprocesses:

```bash
# Run a module verification script
codomyrmex quick run scripts/verify_integration.py

# Run all scripts in a directory in parallel
codomyrmex quick run src/codomyrmex/tests/integration/ --parallel

# Chain scripts sequentially, passing results
codomyrmex quick chain scripts/build.py scripts/test.py scripts/deploy.py

# Pipe CLI commands together
codomyrmex quick pipe "codomyrmex check" "codomyrmex test agents"
```

### System Status Inspection (PAI OBSERVE Phase)

```bash
# See which modules are loaded and healthy
codomyrmex status

# List all 88 modules with their availability
codomyrmex modules

# Run environment validation before work begins
codomyrmex check
```

### Test Execution (PAI VERIFY Phase)

```bash
# Run tests for a specific module
codomyrmex test search
codomyrmex test events
codomyrmex test validation

# Run all tests
uv run pytest
```

### Workflow Execution (PAI EXECUTE Phase)

```bash
# List registered workflows
codomyrmex workflow list

# Execute a named workflow
codomyrmex workflow run <workflow-name>
```

## Architecture Role

**Application Layer (Interface)** — Top-level user interaction. Aggregates `cli_commands()`
from all modules via auto-discovery. No MCP tools. The CLI operates through direct
terminal I/O and subprocess invocation.

The `quick` command group (`handlers/quick.py`) enables PAI EXECUTE phase automation:
- `quick run`: executes scripts, modules, or directories of scripts (parallel or sequential)
- `quick pipe`: chains commands via the orchestrator Workflow engine
- `quick batch`: parallel batch execution with configurable worker count
- `quick chain`: sequential script chaining with result passing via environment variables
- `quick workflow`: executes structured workflow definitions from YAML/JSON files

## PAI Algorithm Phase Mapping

| Phase | CLI Contribution | Key Commands |
|-------|------------------|-------------|
| **OBSERVE** (1/7) | Inspect system state and module health before beginning work | `codomyrmex status`, `codomyrmex check`, `codomyrmex modules` |
| **PLAN** (3/7) | List available workflows and projects | `codomyrmex workflow list`, `codomyrmex project list` |
| **EXECUTE** (5/7) | Run scripts, pipelines, workflows, and tests | `codomyrmex quick run/pipe/batch/chain`, `codomyrmex workflow run` |
| **VERIFY** (6/7) | Execute module tests and verify environment | `codomyrmex test <module>`, `codomyrmex check` |

### Concrete PAI Usage Patterns

**OBSERVE — Check system is healthy before starting work:**
```bash
codomyrmex check && codomyrmex status
# Confirm: all required modules load, environment variables present
```

**EXECUTE — Run a workflow from PAI EXECUTE phase:**
```bash
codomyrmex workflow run release-pipeline
# Or directly:
codomyrmex quick run scripts/build_and_test.py --timeout 120
```

**VERIFY — Run targeted tests after changes:**
```bash
codomyrmex test validation  # After changing validation module
codomyrmex test events       # After changing events module
```

## PAI Configuration

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `CODOMYRMEX_CLI_COLOR` | `auto` | Force color output: `always`, `never`, `auto` |
| `CODOMYRMEX_CLI_VERBOSE` | `false` | Default verbose mode for all commands |
| `CODOMYRMEX_CLI_TIMEOUT` | `60` | Default timeout in seconds for `quick` commands |

## PAI Best Practices

1. **Use `codomyrmex check` at the start of every OBSERVE phase**: This validates the
   environment before investing time in analysis. Catch missing API keys and broken
   imports early.

2. **Use `quick batch` for parallel EXECUTE phase work**: When BUILD phase creates
   multiple independent scripts, use `quick batch` to run them concurrently rather
   than sequentially — respects the PAI parallelization principle.

3. **Use `quick chain` for dependent pipelines**: When scripts must run in order and
   each depends on the previous result, `quick chain` passes results via environment
   variables, preserving the dependency contract.

4. **Subprocess invocation from PAI agents**: PAI agents should invoke `codomyrmex`
   subcommands via the Bash tool rather than direct Python import — this ensures
   proper environment isolation and captures rich terminal output for VERIFY evidence.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.cli import ...`
- CLI: `codomyrmex <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
