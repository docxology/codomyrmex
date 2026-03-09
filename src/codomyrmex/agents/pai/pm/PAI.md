# PAI.md — PAI Integration Reference

**Module**: `src/codomyrmex/agents/pai/pm/`
**PAI Version Compatibility**: v4.0.x+

## How This Module Connects to PAI

This module **is** the PAI Project Manager — the complete Mission/Project/Task management engine extracted from the private `~/.claude/skills/PAI/Tools/` into the shareable codomyrmex repository.

## Integration Points

### 1. PAI State Directory

Reads/writes to `$PAI_DIR/MEMORY/STATE/` (default `~/.claude/MEMORY/STATE/`):

- `missions/<slug>/MISSION.yaml` — mission definitions
- `projects/<slug>/PROJECT.yaml` — project definitions
- `projects/<slug>/TASKS.md` — task lists
- `sync/<slug>.json` — GitHub sync mappings

### 2. PAI Credentials

Uses credentials stored in `~/.codomyrmex/`:

- `gcal_token.json` — Google Calendar OAuth token
- `gcal_links.json` — Calendar ↔ PAI project links
- `gmail_token.json` — Gmail OAuth token

### 3. PAI Dashboard (`dashboard.py`)

The `scripts/pai/dashboard.py` orchestrator launches both:

- This module's PMServer (`:8888`) — primary TypeScript server
- The Python WebsiteServer (`:8787`) — admin module dashboard

### 4. PAIMixin (Python-side awareness)

`src/codomyrmex/website/pai_mixin.py` delegates to this module's `/api/awareness` endpoint when the server is running, falling back to direct YAML reads when it's not.

### 5. Upstream PAI

The upstream [danielmiessler/Personal_AI_Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure) provides the PAI framework (skills, memory, hooks, TELOS). This module extends it with a complete PM system that is entirely missing from upstream.

## Agent Usage

Agents should use the CLI tools for atomic operations:

```bash
bun src/codomyrmex/agents/pai/pm/CreateMission.ts --slug <slug> --title "<title>"
bun src/codomyrmex/agents/pai/pm/ListProjects.ts --json
bun src/codomyrmex/agents/pai/pm/AddTask.ts <project> "<task text>" --priority HIGH
```

For bulk operations or real-time awareness, agents should use the HTTP API:

```bash
curl http://localhost:8888/api/awareness
curl http://localhost:8888/api/missions
curl http://localhost:8888/api/health
```

## Configuration

LLM defaults for bikeride/email features are configurable via environment variables:

| Variable | Default | Description |
|---|---|---|
| `PAI_PM_LLM_BACKEND` | `ollama` | LLM backend (`ollama`, `gemini`, `claude`) |
| `PAI_PM_LLM_MODEL` | `gemma3:4b` | Model name (gemma3 preferred — no thinking artifacts) |
| `PAI_PM_LLM_TIMEOUT` | `60000` | Subprocess timeout (ms) |
