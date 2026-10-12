# server

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module implementation, resources, and local coordination for Server.

## Directory Contents

- `AddTask.ts` – File
- `CompleteProject.ts` – File
- `CreateMission.ts` – File
- `CreateProject.ts` – File
- `DataModels.ts` – File
- `DeleteMission.ts` – File
- `DeleteProject.ts` – File
- `GitHubSync.ts` – File
- `ListMissions.ts` – File
- `ListProjects.ts` – File
- `ListTasks.ts` – File
- `MissionDashboard.ts` – File
- `PAI.md` – File
- `PMDashboard.ts` – File
- `ProjectDashboard.ts` – File
- `README.md` – File
- `SPEC.md` – File
- `TaskSummary.ts` – File
- `UpdateMission.ts` – File
- `UpdateProject.ts` – File
- `UpdateTask.ts` – File
- `YamlUtils.ts` – File
- `bun.lock` – File
- `config.ts` – File
- `helpers.ts` – File
- `package.json` – File
- `routes/` – Subdirectory
- `server.ts` – File
- `services/` – Subdirectory
- `spa/` – Subdirectory

## Navigation

- **Parent Directory**: [pai_pm](../README.md)
- **Project Root**: ../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## SPA accessible form names

`spa/index.html` gives form controls stable accessible names across data search, inline editing, task creation, GitHub operations, interviews, calendar events, email, and voice replies. Visible labels use explicit `for`/`id` associations; `field()` retains its visible label rather than overriding it with placeholder text. Unlabelled controls use descriptive `aria-label` values.

```bash
uv run --locked pytest -q tests/unit/pai_pm/test_spa_accessibility.py
```

The suite parses production form markup and executes the real `field()` renderer through Node.js. It also checks all inline JavaScript syntax. These checks establish markup and renderer contracts. Local Chromium verification additionally confirms Tab/Shift+Tab containment, Escape dismissal, background inertness and restoration of the originating focus and prior inert states. Screen-reader-specific acceptance remains separate.
