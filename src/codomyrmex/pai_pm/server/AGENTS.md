# AGENTS.md — PAI PM Tools

## Purpose

This module provides a complete **Mission → Project → Task** management system for PAI (Personal AI Infrastructure). Agents can use these TypeScript CLI tools to create, update, query, and sync project management state.

## Quick Reference for Agents

### Creating work items

```bash
bun scripts/pai/pm/CreateMission.ts --slug <slug> --title "<title>" --description "<desc>"
bun scripts/pai/pm/CreateProject.ts --slug <slug> --title "<title>" --goal "<goal>" --mission <mission-slug>
bun scripts/pai/pm/AddTask.ts <project-slug> "<task text>" --priority HIGH
```

### Querying state

```bash
bun scripts/pai/pm/ListMissions.ts --verbose --json
bun scripts/pai/pm/ListProjects.ts --status IN_PROGRESS --json
bun scripts/pai/pm/ListTasks.ts --project <slug> --json
bun scripts/pai/pm/PMDashboard.ts --json
```

### Updating state

```bash
bun scripts/pai/pm/UpdateTask.ts <project-slug> "<task text>" --move-to completed
bun scripts/pai/pm/UpdateProject.ts <slug> --status IN_PROGRESS
bun scripts/pai/pm/UpdateMission.ts <slug> --link-project <project-slug>
```

### GitHub sync

```bash
bun scripts/pai/pm/GitHubSync.ts link --project <slug> --repo owner/repo
bun scripts/pai/pm/GitHubSync.ts push --project <slug>
bun scripts/pai/pm/GitHubSync.ts pull --project <slug>
bun scripts/pai/pm/GitHubSync.ts sync --all
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

These tools are the **single source of truth** for PAI project state. The PMServer.ts web dashboard reads from the same YAML files. Multiple agents can safely call these tools concurrently — each tool performs atomic file writes.
