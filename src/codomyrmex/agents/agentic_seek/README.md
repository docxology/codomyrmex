# agentic_seek

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Integration with [agenticSeek](https://github.com/Fosowl/agenticSeek)—a fully-local, privacy-first autonomous agent system (25k+ ★) that autonomously browses the web, writes and executes code in multiple languages, and plans complex multi-step tasks. All processing runs on local hardware via Ollama, LM Studio, or custom servers.

### Key Capabilities

| Capability | Description |
|---|---|
| **Multi-Agent Routing** | Automatic classification into Coder, Browser, Planner, File, or Casual agents |
| **Code Execution** | Python, C, Go, Java, Bash with iterative error correction |
| **Web Browsing** | Autonomous search (SearxNG) and navigation (Selenium) |
| **Task Planning** | JSON-based multi-step decomposition with dependency ordering |
| **100% Local** | No cloud APIs required; optional API providers supported |

## Directory Contents

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `agentic_seek_client.py` | Main CLI client (extends `CLIAgentBase`) |
| `agent_router.py` | Heuristic query-to-agent classifier |
| `agent_types.py` | Enums, dataclasses, language resolution |
| `code_execution.py` | Code block extraction and command building |
| `task_planner.py` | JSON plan parsing, validation, topological ordering |
| `browser_automation.py` | Link/form extraction, prompt builders |
| `AGENTS.md` | Agent integration specification |
| `SPEC.md` | Technical specification |
| `PAI.md` | PAI integration notes |

## Quick Start

```python
from codomyrmex.agents.agentic_seek import (
    AgenticSeekClient,
    AgenticSeekRouter,
    AgenticSeekCodeExecutor,
    AgenticSeekTaskPlanner,
)

# Route a query to the right agent type
router = AgenticSeekRouter()
agent_type = router.classify_query("Write a Python script to sort a list")
# → AgenticSeekAgentType.CODER

# Extract and classify code blocks
executor = AgenticSeekCodeExecutor(work_dir="/tmp")
blocks = executor.extract("Here is the code:\n```python\nprint('hello')\n```")
cmd = executor.command_for(blocks[0])
# → ['python3', '/tmp/agentic_seek_exec.py']

# Parse a multi-step plan
planner = AgenticSeekTaskPlanner()
steps = planner.parse('```json\n{"plan": [{"agent": "coder", "id": 1, "task": "Write script"}]}\n```')
```

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: ../../../../README.md
