# AGENTS.md — PAI PM Tools

## Purpose

This module provides a complete **Mission → Project → Task** management system for PAI (Personal AI Infrastructure). Agents can use these TypeScript CLI tools to create, update, query, and sync project management state.

## Quick Reference for Agents

### Creating work items

```bash
bun src/codomyrmex/agents/pai/pm/CreateMission.ts --slug <slug> --title "<title>" --description "<desc>"
bun src/codomyrmex/agents/pai/pm/CreateProject.ts --slug <slug> --title "<title>" --goal "<goal>" --mission <mission-slug>
bun src/codomyrmex/agents/pai/pm/AddTask.ts <project-slug> "<task text>" --priority HIGH
```

### Querying state

```bash
bun src/codomyrmex/agents/pai/pm/ListMissions.ts --verbose --json
bun src/codomyrmex/agents/pai/pm/ListProjects.ts --status IN_PROGRESS --json
bun src/codomyrmex/agents/pai/pm/ListTasks.ts --project <slug> --json
bun src/codomyrmex/agents/pai/pm/PMDashboard.ts --json
```

### Updating state

```bash
bun src/codomyrmex/agents/pai/pm/UpdateTask.ts <project-slug> "<task text>" --move-to completed
bun src/codomyrmex/agents/pai/pm/UpdateProject.ts <slug> --status IN_PROGRESS
bun src/codomyrmex/agents/pai/pm/UpdateMission.ts <slug> --link-project <project-slug>
```

### GitHub sync

```bash
bun src/codomyrmex/agents/pai/pm/GitHubSync.ts link --project <slug> --repo owner/repo
bun src/codomyrmex/agents/pai/pm/GitHubSync.ts push --project <slug>
bun src/codomyrmex/agents/pai/pm/GitHubSync.ts pull --project <slug>
bun src/codomyrmex/agents/pai/pm/GitHubSync.ts sync --all
```

## Output Format

All tools output structured JSON by default, making them ideal for programmatic consumption by agents. Example:

```json
{"created": true, "path": "/path/to/mission", "mission": {"id": "my-mission", ...}}
```

## State Location

All state lives in `$PAI_DIR/MEMORY/STATE/` (default `~/.claude/MEMORY/STATE/`):

- `missions/<slug>/MISSION.yaml` + `progress.json`
- `projects/<slug>/PROJECT.yaml` + `TASKS.md` + `progress.json`
- `sync/<slug>.json` (GitHub sync mappings)

## Coordination

These tools are the **single source of truth** for PAI project state. The modular server (`server.ts`) reads from the same YAML files and exposes a REST API + WebSocket + 15-tab SPA dashboard. Multiple agents can safely call these tools concurrently — each tool performs atomic file writes.

### HTTP Server API

```bash
# Start the modular server
bun src/codomyrmex/agents/pai/pm/server.ts --port=8888

# Available endpoints
curl http://localhost:8888/api/health
curl http://localhost:8888/api/missions
curl http://localhost:8888/api/projects
curl http://localhost:8888/api/awareness
```

### LLM Configuration

The bikeride/email features use LLM backends configurable via environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `PAI_PM_LLM_BACKEND` | `ollama` | Backend: `ollama`, `gemini`, `claude` |
| `PAI_PM_LLM_MODEL` | `gemma3:4b` | Model name (gemma3 preferred — no thinking artifacts) |
| `PAI_PM_LLM_TIMEOUT` | `60000` | Subprocess timeout (ms) |

### Mission Status Values

Missions support: `ACTIVE`, `PLANNING`, `IN_PROGRESS`, `PAUSED`, `COMPLETED`, `ARCHIVED`.

### Bike Ride (Email Briefing)

The Bike Ride feature loads Gmail threads awaiting reply, summarizes them via LLM, and generates A/B/C draft responses:

```bash
# Load unanswered threads + generate summaries/drafts
curl -X POST http://localhost:8888/api/bikeride/load -H 'Content-Type: application/json' -d '{"backend":"ollama","model":"gemma3:4b"}'

# Text-to-speech for audio briefing
curl -X POST http://localhost:8888/api/bikeride/tts -H 'Content-Type: application/json' -d '{"text":"Your summary here"}'

# Improve a draft
curl -X POST http://localhost:8888/api/bikeride/improve -H 'Content-Type: application/json' -d '{"draft":"Draft text","backend":"ollama"}'
```

All LLM output is post-processed by `stripThinking()` to remove chain-of-thought artifacts.
