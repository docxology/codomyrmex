# PAI Dashboard Screenshots

**15 interface tabs** + 1 animated tour recording.

## Tab Screenshots

| File | Tab | Content |
|------|-----|---------|
| `pai_analytics.png` | Analytics | Mission/project KPIs, status/priority charts, completion bars |
| `pai_awareness.png` | Awareness | PAI awareness data, mission/project context |
| `pai_bikeride.png` | 🚴 Bike Ride | Unanswered Gmail threads + LLM-generated A/B/C drafts + TTS |
| `pai_blockers.png` | Blockers | Blocked items and dependency tracking |
| `pai_board.png` | Board | Kanban (ACTIVE, PLANNING, IN PROGRESS, BLOCKED, PAUSED, COMPLETED) |
| `pai_calendar.png` | Calendar | Google Calendar OAuth, month view, event creation |
| `pai_data.png` | Data | Full CRUD tables — Missions, Projects, Tasks |
| `pai_dispatch.png` | Dispatch | Algorithm actions: Summarize, Scope & Plan, Review, Enact |
| `pai_email.png` | Email | AgentMail + Gmail dual-provider, AI-assisted compose |
| `pai_git.png` | Git | Repository sync — Push, Pull, Sync, Unlink |
| `pai_integration.png` | Integration | GitHub bridge, issue tracking, JSON/CSV export |
| `pai_interview.png` | Interview | Task requirement gathering through structured interviews |
| `pai_network.png` | Network | Force-directed mission→project→task graph |
| `pai_projects.png` | Projects | Per-project drill-down with task breakdown |
| `pai_timeline.png` | Timeline | Gantt-style temporal project visualization |

## Animated Tour

| File | Description |
|------|-------------|
| `pai_interface_tour.webp` | Full interface tour through all tabs |

## Server Location

All tabs are served from the modular SPA at `src/codomyrmex/agents/pai/pm/spa/index.html` via the Bun server at `src/codomyrmex/agents/pai/pm/server.ts` on port **8888**.
