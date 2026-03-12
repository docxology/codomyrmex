# Mission Control Agent Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Mission Control Agent Module integrates builderz-labs' [Mission Control](https://github.com/builderz-labs/mission-control) — an open-source dashboard for AI agent orchestration — into the Codomyrmex ecosystem. The dashboard provides 32 panels for managing agent fleets, task boards, cost tracking, real-time monitoring, GitHub sync, skills hub, and memory knowledge graphs.

## Core Features

1. **REST API Client**:
   Communicates with the Mission Control Next.js dashboard via its 100+ REST endpoints. Manages agents, tasks, sessions, and cost tracking programmatically.

2. **Zero-Dependency HTTP**:
   Uses Python's stdlib `urllib.request` — no external HTTP libraries required.

3. **Server Lifecycle**:
   Can start and stop the Mission Control dev server from Python, enabling automated orchestration workflows.

4. **MCP Tool Suite**:
   Provides 6 Model Context Protocol tools for other swarm agents to interact with Mission Control (status, agents, tasks, server control).

## Directory Structure

- `mission_control_client.py`: The `MissionControlClient` wrapper class.
- `mcp_tools.py`: Model Context Protocol tool definitions.
- `app/`: Git submodule containing the upstream mission-control repository.

## Tech Stack (Dashboard)

| Layer | Technology |
|:---|:---|
| Framework | Next.js 16 (App Router) |
| UI | React 19, Tailwind CSS 3.4 |
| Language | TypeScript 5.7 (strict) |
| Database | SQLite via better-sqlite3 (WAL mode) |
| State | Zustand 5 |
| Real-time | WebSocket + SSE |
| Auth | scrypt hashing, session tokens, RBAC |

## Requirements

- **Node.js 22.x** (LTS) and **pnpm** for the dashboard app
- Python 3.11+ for the client wrapper

## Navigation
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
