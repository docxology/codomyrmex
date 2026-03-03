# PAI Integration — Website Scripts

**Module**: scripts/website
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `scripts/website/` directory provides the **launcher** for the Codomyrmex Web Dashboard — the browser interface for the PAI toolbox. It bridges the `src/codomyrmex/website/` module with your shell, handling server startup, static generation, and browser launching.

## Primary Script: `launch_dashboard.py`

```bash
# Recommended invocation
python scripts/website/launch_dashboard.py --port 8787 --open
```

**Startup sequence:**
1. Resolves project root (parent of `scripts/`)
2. Calls `WebsiteGenerator.generate()` → renders 14 Jinja2 pages to `output/website/`
3. Creates `index.html` root redirect
4. Instantiates `DataProvider(project_root)` — aggregates modules, git, PAI awareness
5. Binds `WebsiteServer` on the configured port
6. Optionally launches `webbrowser.open()`

## PAI Algorithm Phase Mapping

| Phase | Endpoint / Page | What It Provides |
|-------|----------------|-----------------|
| **OBSERVE** | `/api/status`, `/api/modules`, `/api/awareness` | System state, module inventory, PAI missions/projects |
| **OBSERVE** | `/api/health`, `/api/tools` | Vitals, git status, coverage, MCP tool count |
| **THINK** | `/api/awareness/summary` | Ollama-powered ecosystem analysis |
| **PLAN** | Dashboard coverage bars | Identifies documentation and test gaps |
| **BUILD** | `/api/config`, `/api/execute` | Edit configs, run scripts from browser |
| **EXECUTE** | `/api/agent/dispatch`, `/api/chat` | Agent orchestrator, LLM chat |
| **VERIFY** | `/api/tests`, `/api/health`, `/api/security/posture` | Run pytest, check system status, security risk score |
| **LEARN** | Awareness page | Mission/project progress over sessions |

## Key Files

| File | Role |
|------|------|
| `launch_dashboard.py` | Shell entry point: generation + server startup |
| `orchestrate.py` | Demo of ConversationOrchestrator multi-agent flow |
| `website_utils.py` | Helper utilities for website operations |

## Related PAI Dashboards

| Dashboard | Port | Purpose |
|-----------|------|---------|
| Codomyrmex (this) | **8787** | Module health, tools, awareness, security |
| PAI Observability | **5172** (UI) + **4000** (API) | Real-time agent monitoring, event streams, heat levels |
| PAI Project Manager | **8889** | Kanban, Gantt, Git sync, AI dispatch |
| MCP HTTP Server | **8080** | MCP tools REST API |

> **Port conflict note**: PAI VoiceServer (`~/.claude/VoiceServer/server.ts`) runs on port **8888**. PMServer now defaults to **8889** — run both simultaneously without conflict.

## Accessibility Features

The dashboard follows WCAG guidelines:
- Skip navigation link (`<a href="#main-content">Skip to main content</a>`)
- ARIA labels on nav groups and interactive regions
- Keyboard shortcuts Alt+1 through Alt+0 for page navigation
- `aria-live` regions for dynamic content updates
- Responsive breakpoints at 900px and 600px

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Module Source**: [src/codomyrmex/website/PAI.md](../../src/codomyrmex/website/PAI.md)
- **Root Bridge**: [../../PAI.md](../../PAI.md)
- **Siblings**: [README.md](README.md) | [SPEC.md](SPEC.md)
