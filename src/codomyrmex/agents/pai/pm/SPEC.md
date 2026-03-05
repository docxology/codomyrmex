# SPEC.md — PAI PM Module Specification

**Module**: `scripts/pai/pm/`
**Version**: 2.0.0 (modular decomposition)
**Runtime**: [Bun](https://bun.sh) ≥ 1.0.0
**Language**: TypeScript

## Purpose

Complete Mission → Project → Task management system for the Personal AI Infrastructure (PAI). Provides both standalone CLI tools and a modular HTTP server with REST API, WebSocket, and embedded SPA.

## Architecture

```
scripts/pai/pm/
├── config.ts              # Centralized env-overridable configuration
├── helpers.ts             # Shared HTTP/WebSocket utilities
├── DataModels.ts          # TypeScript type definitions
├── YamlUtils.ts           # YAML parsing/writing utilities
├── server.ts              # Modular HTTP server (v2.0.0)
├── services/
│   └── oauth.ts           # Google Calendar, Gmail, AgentMail OAuth
├── routes/
│   ├── missions.ts        # /api/missions/* CRUD
│   ├── projects.ts        # /api/projects/* + /api/gantt/*
│   ├── tasks.ts           # /api/tasks/* CRUD
│   ├── github.ts          # /api/github/* (sync engine)
│   ├── dispatch.ts        # /api/dispatch/* (LLM dispatch + queue)
│   ├── interview.ts       # /api/interview/* (AI-powered interviews)
│   ├── awareness.ts       # /api/awareness (ecosystem state + Mermaid)
│   ├── calendar.ts        # /api/calendar/* (Google Calendar)
│   └── email.ts           # /api/email/* + /api/gmail/* + /api/bikeride/*
├── [16 CLI tool .ts files]
├── package.json           # Bun dependencies (js-yaml)
├── .env.example           # All configurable environment variables
├── README.md              # User-facing documentation
├── AGENTS.md              # Agent-facing quick reference
└── SPEC.md                # This file
```

## Data Model

### Mission

| Field | Type | Description |
| --- | --- | --- |
| `id` | `string` | URL-safe slug |
| `title` | `string` | Display name |
| `status` | `ACTIVE \| PAUSED \| COMPLETED \| ARCHIVED` | Current state |
| `priority` | `HIGH \| MEDIUM \| LOW` | Priority level |
| `description` | `string` | Mission description |
| `linked_projects` | `string[]` | Linked project slugs |

### Project

| Field | Type | Description |
| --- | --- | --- |
| `id` | `string` | URL-safe slug |
| `title` | `string` | Display name |
| `status` | `PLANNING \| IN_PROGRESS \| COMPLETED \| PAUSED \| BLOCKED` | Current state |
| `goal` | `string` | Project goal |
| `parent_mission` | `string` | Parent mission slug |

### Task

| Field | Type | Description |
| --- | --- | --- |
| `text` | `string` | Task description |
| `section` | `completed \| in_progress \| remaining \| blocked \| optional` | Kanban section |
| `priority` | `HIGH \| MEDIUM \| LOW` | Priority |
| `due` | `string \| null` | Due date (ISO 8601) |
| `depends_on` | `string[]` | Dependency list |

## State Storage

All state is stored as YAML/JSON files under `$PAI_STATE_DIR` (default: `~/.claude/MEMORY/STATE/`):

```
~/.claude/MEMORY/STATE/
├── missions/
│   └── <slug>/
│       ├── MISSION.yaml      # Mission definition
│       └── progress.json     # Computed metrics
├── projects/
│   └── <slug>/
│       ├── PROJECT.yaml      # Project definition
│       ├── TASKS.md           # Task list (markdown format)
│       └── progress.json     # Computed metrics
└── sync/
    └── <slug>.json           # GitHub sync mappings
```

## API Endpoints (server.ts)

| Method | Path | Handler | Description |
| --- | --- | --- | --- |
| `GET` | `/api/health` | server.ts | Health check |
| `GET/POST/PUT/DELETE` | `/api/missions/*` | routes/missions.ts | Mission CRUD |
| `GET/POST/PUT/DELETE` | `/api/projects/*` | routes/projects.ts | Project CRUD + Gantt |
| `GET/POST/PUT` | `/api/tasks/*` | routes/tasks.ts | Task CRUD |
| `GET/POST` | `/api/github/*` | routes/github.ts | GitHub sync |
| `GET/POST/DELETE` | `/api/dispatch/*` | routes/dispatch.ts | LLM dispatch + queue |
| `GET/POST/DELETE` | `/api/interview/*` | routes/interview.ts | AI interviews |
| `GET` | `/api/awareness` | routes/awareness.ts | Ecosystem state |
| `GET/POST/PUT/DELETE` | `/api/calendar/*` | routes/calendar.ts | Google Calendar |
| `GET/POST` | `/api/email/*` | routes/email.ts | Email (AgentMail + Gmail) |
| `POST` | `/api/bikeride/*` | routes/email.ts | Bike ride email digest |

## Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Default | Used By |
| --- | --- | --- |
| `PAI_PM_PORT` | `8889` | `server.ts`, `config.ts` |
| `PAI_DIR` | `~/.claude` | `config.ts`, all CLI tools |
| `PAI_STATE_DIR` | `$PAI_DIR/MEMORY/STATE` | `config.ts` |
| `GOOGLE_CLIENT_ID/SECRET` | — | `services/oauth.ts` |
| `AGENTMAIL_API_KEY` | — | `services/oauth.ts` |
| `AGENTMAIL_DEFAULT_INBOX` | — | `services/oauth.ts` |
| `GITHUB_DEFAULT_OWNER` | — | `config.ts`, `routes/github.ts` |

## PAIMixin Integration

The Python `PAIProviderMixin` (in `src/codomyrmex/website/pai_mixin.py`) delegates to `GET /api/awareness` when the PM server is running, falling back to direct YAML reads when it's not. This ensures a single source of truth for awareness data.

## Dependencies

- **Runtime**: Bun ≥ 1.0.0
- **npm**: `js-yaml` ^4.1.0
- **External CLIs**: `gh` (GitHub sync), `ollama`/`claude`/`gemini` (dispatch), `say` (TTS)
