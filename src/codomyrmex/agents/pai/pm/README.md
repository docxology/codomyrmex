# PAI Project Manager (PM) Tools

> Mission → Project → Task management CLI and sync engine for the [Personal AI Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure).

## Overview

This directory contains the **complete PAI PM toolchain** — a set of TypeScript CLI tools powered by [Bun](https://bun.sh) that implement a three-tier project management hierarchy:

```text
Mission (strategic goal)
  └── Project (deliverable)
       └── Task (actionable work item)
```

All state is stored as YAML files under `~/.claude/MEMORY/STATE/` (configurable via `PAI_DIR` env var).

## Quick Start

```bash
# Install dependencies
cd scripts/pai/pm && bun install

# Create a mission
bun CreateMission.ts --slug my-mission --title "My Mission" --description "What we're doing"

# Create a project under it
bun CreateProject.ts --slug my-project --title "My Project" --goal "Ship it" --mission my-mission

# Add tasks
bun AddTask.ts my-project "Design the API" --priority HIGH
bun AddTask.ts my-project "Write tests" --depends-on "Design the API"

# View everything
bun PMDashboard.ts
bun ListMissions.ts --verbose
bun ListProjects.ts --verbose
bun ListTasks.ts --project my-project
```

## Tools Reference

### Mission Tools

| Tool | Description | Key Flags |
|------|-------------|-----------|
| `CreateMission.ts` | Create a new mission | `--slug`, `--title`, `--description`, `--priority` |
| `UpdateMission.ts` | Update mission metadata or link projects | `--status`, `--link-project`, `--log` |
| `ListMissions.ts` | List all missions | `--status`, `--sort`, `--verbose` |
| `MissionDashboard.ts` | Rich mission detail view | `--mission` |
| `DeleteMission.ts` | Delete a mission | `--confirm`, `--cascade` |

### Project Tools

| Tool | Description | Key Flags |
|------|-------------|-----------|
| `CreateProject.ts` | Create a new project | `--slug`, `--title`, `--goal`, `--mission` |
| `UpdateProject.ts` | Update project metadata | `--status`, `--add-task`, `--log` |
| `ListProjects.ts` | List all projects | `--status`, `--sort`, `--verbose` |
| `CompleteProject.ts` | Mark project complete | `--force`, `--summary` |
| `ProjectDashboard.ts` | Rich project detail view | `--project` |
| `DeleteProject.ts` | Delete a project | `--confirm` |

### Task Tools

| Tool | Description | Key Flags |
|------|-------------|-----------|
| `AddTask.ts` | Add a task to a project | `--priority`, `--due`, `--assignee`, `--depends-on` |
| `UpdateTask.ts` | Update task status/metadata | `--move-to`, `--priority`, `--rename` |
| `ListTasks.ts` | List tasks for a project | `--project`, `--section`, `--overdue` |
| `TaskSummary.ts` | Task completion summary | `--mission`, `--project` |

### Dashboard & Sync

| Tool | Description |
|------|-------------|
| `PMDashboard.ts` | Aggregate dashboard across all missions/projects |
| `GitHubSync.ts` | Bidirectional PAI ↔ GitHub Issues sync via `gh` CLI |

## Configuration

All paths are configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PAI_DIR` | `~/.claude` | Root PAI installation directory |
| `PAI_STATE_DIR` | `$PAI_DIR/MEMORY/STATE` | Mission/project/task state |
| `PAI_SYNC_DIR` | `$PAI_STATE_DIR/sync` | GitHub sync mappings |
| `GITHUB_DEFAULT_OWNER` | `""` | Default GitHub org for repo listing |
| `GITHUB_TOKEN` | — | Required for `GitHubSync.ts` (or use `gh auth login`) |
| `PAI_PM_LLM_BACKEND` | `ollama` | Default LLM backend for bikeride/email |
| `PAI_PM_LLM_MODEL` | `qwen3:4b` | Default LLM model |
| `PAI_PM_LLM_TIMEOUT` | `60000` | LLM subprocess timeout (ms) |
| `GOOGLE_CLIENT_ID` | — | Google Calendar/Gmail OAuth |
| `GOOGLE_CLIENT_SECRET` | — | Google Calendar/Gmail OAuth |
| `AGENTMAIL_API_KEY` | — | AgentMail API key |

## Data Model

See [DataModels.ts](DataModels.ts) for the full type definitions:

- **Mission**: `id`, `title`, `description`, `status` (ACTIVE/PLANNING/IN_PROGRESS/PAUSED/COMPLETED/ARCHIVED), `priority`, `linked_projects[]`
- **Project**: `id`, `title`, `goal`, `status` (PLANNING/IN_PROGRESS/COMPLETED/PAUSED/BLOCKED), `parent_mission`
- **Task**: `text`, `section` (completed/in_progress/remaining/blocked/optional), `priority`, `due`, `depends_on[]`

## Architecture

```text
scripts/pai/pm/
├── config.ts           # Externalized path configuration
├── DataModels.ts       # Shared type definitions
├── YamlUtils.ts        # YAML parsing/writing utilities
├── Create*.ts          # CRUD creation tools
├── Update*.ts          # CRUD update tools
├── List*.ts            # Listing/query tools
├── Delete*.ts          # Deletion tools
├── Complete*.ts        # Completion workflows
├── *Dashboard.ts       # Dashboard aggregation
├── TaskSummary.ts      # Task metrics
├── GitHubSync.ts       # GitHub ↔ PAI bidirectional sync
├── server.ts           # Modular HTTP server (v2.1.0)
├── helpers.ts          # Shared HTTP/WebSocket utilities
├── services/
│   └── oauth.ts        # Google Calendar, Gmail, AgentMail OAuth
├── routes/
│   ├── missions.ts     # /api/missions/* CRUD
│   ├── projects.ts     # /api/projects/* + /api/gantt/*
│   ├── tasks.ts        # /api/tasks/* CRUD
│   ├── github.ts       # /api/github/* (sync engine)
│   ├── dispatch.ts     # /api/dispatch/* (LLM dispatch)
│   ├── interview.ts    # /api/interview/* (AI interviews)
│   ├── awareness.ts    # /api/awareness (ecosystem state)
│   ├── calendar.ts     # /api/calendar/* (Google Calendar)
│   └── email.ts        # /api/email/* + /api/bikeride/*
├── spa/
│   └── index.html      # 15-tab single-page application
└── package.json        # Bun package manifest
```

## Dependencies

- **Runtime**: [Bun](https://bun.sh) ≥ 1.0.0
- **npm**: `js-yaml` (for YAML parsing in GitHubSync)
- **External**: `gh` CLI (for GitHub sync — install from [cli.github.com](https://cli.github.com))

## License

MIT — part of the [Codomyrmex](https://github.com/docxology/codomyrmex) ecosystem.
