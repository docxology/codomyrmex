# On Ramp — Graded Flexibility for PAI-Codomyrmex

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

> **Codomyrmex** is the orchestration, testing, and training environment for agentic functions. Smaller repositories — directly derived or constructed from its patterns — are where modular functions get built. This document maps the rapid curriculum of a tutoring session: five levels of increasing flexibility, each unlocking new capabilities.

## How to Read This Document

Think of Codomyrmex as a **training gym** for agentic code. You don't ship the gym — you ship what you trained. Each level below adds capability and responsibility:

```text
Level 1: Observer      → Watch, read, understand
Level 2: Explorer      → Run safe tools, verify, query
Level 3: Builder       → Write code, run tests, modify
Level 4: Module Dev    → Create derived repos, build modular functions
Level 5: Orchestrator  → Multi-repo, multi-agent, full PAI Algorithm
```

---

## Level 1 — Observer 👁

**Trust**: UNTRUSTED | **Risk**: None | **Time**: 5 minutes

You can browse everything without changing anything.

### What You Can Do

- **Browse the PAI Dashboard** at `http://localhost:8888/` — all 15 tabs are read-only
- **Read documentation** — this folder (`docs/pai/`), module READMEs, SPEC files
- **Understand the architecture** — see [architecture.md](architecture.md) for component diagrams
- **View the 7-phase Algorithm** — OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN

### Key Concepts

| Concept | What It Means |
|---------|--------------|
| **Codomyrmex** | 128-module Python toolbox — orchestration, testing, discovery |
| **PAI** | Personal AI Infrastructure — runs The Algorithm on every prompt |
| **MCP** | Model Context Protocol — how PAI talks to Codomyrmex |
| **Derived repo** | A smaller repository built using Codomyrmex patterns and tools |

### Your First Steps

```bash
# Start the dashboards
uv run python scripts/pai/dashboard.py
# Open http://localhost:8888/ and click through each tab
```

---

## Level 2 — Explorer 🔍

**Trust**: VERIFIED | **Risk**: Low (read-only operations) | **Time**: 15 minutes

**Unlock**: Run `/codomyrmexVerify` in Claude Code to promote ~469 safe tools.

### Explorer Capabilities

- **Query the system** — `codomyrmex.list_modules`, `codomyrmex.module_info`, `codomyrmex.pai_status`
- **Search code** — `codomyrmex.search_codebase` with regex patterns
- **Analyze structure** — `codomyrmex.analyze_python` on any `.py` file
- **Read files** — `codomyrmex.read_file`, `codomyrmex.json_query`
- **Check git** — `codomyrmex.git_status`, `codomyrmex.git_diff`
- **Use workflows** — `/codomyrmexAnalyze`, `/codomyrmexSearch`, `/codomyrmexDocs`, `/codomyrmexStatus`

### Degrees of Flexibility

At this level you can **ask questions** but not **change answers**:

- Browse all 129 modules, read their READMEs and SPECs
- Search across the codebase for patterns, imports, dependencies
- Analyze any Python file for classes, functions, metrics
- Query PAI state — missions, projects, tasks, TELOS identity
- Generate diagrams with `/generate-web-diagram` (external skill, no MCP)

### Practice Activities

```bash
# In Claude Code:
/codomyrmexVerify                    # Audit and promote safe tools
/codomyrmexAnalyze src/codomyrmex/agents/pai/pai_bridge.py
/codomyrmexSearch "async def.*mcp"   # Find async MCP functions
/codomyrmexDocs encryption           # Get encryption module docs
```

---

## Level 3 — Builder 🔨

**Trust**: TRUSTED | **Risk**: Medium (file writes, command execution) | **Time**: 30 minutes

**Unlock**: Run `/codomyrmexTrust` after `/codomyrmexVerify`.

### Builder Capabilities

Everything from Levels 1–2, plus:

- **Write files** — `codomyrmex.write_file` (create and modify source files)
- **Run commands** — `codomyrmex.run_command` (shell execution)
- **Run tests** — `codomyrmex.run_tests` (pytest with real assertions, zero mocks)
- **Call module functions** — `codomyrmex.call_module_function` (arbitrary function calls)
- **Sync with GitHub** — Push/Pull/Sync via the Git tab or `/api/github/*`
- **Send emails** — Compose and send via Gmail or AgentMail
- **Manage calendar** — Create/update/delete events on Google Calendar

### Builder Flexibility

At this level you can **modify the orchestration** — Codomyrmex itself:

| Capability | What It Means |
|-----------|--------------|
| Add a module | Create `src/codomyrmex/<name>/` with `__init__.py`, `mcp_tools.py`, README, SPEC |
| Add a tool | Decorate a function with `@mcp_tool` — auto-discovered at startup |
| Add a test | Write to `tests/unit/` or `tests/integration/` — zero-mock policy |
| Add a workflow | Create `.agents/workflows/<name>.md` with YAML frontmatter |
| Edit a route | Modify `routes/*.ts` to add PAI Dashboard API endpoints |
| Add a doc | Write to `docs/pai/` — follow RASP pattern (README/AGENTS/SPEC/PAI) |

### Builder Practice

```bash
# In Claude Code:
/codomyrmexTrust                     # Enable destructive tools
# Then:
# - Add a task to a project via the Board tab
# - Push project issues to GitHub via the Git tab
# - Run the test suite: codomyrmex.run_tests(module="email")
# - Compose a draft email with Ollama summarization in the Bike Ride tab
```

---

## Level 4 — Module Developer 📦

**Trust**: Full | **Risk**: Medium-High | **Time**: 1–2 hours

**Key insight**: Codomyrmex is the **testing and orchestration plane**. Modular functions live in **smaller, derived repositories**.

### The Codomyrmex ↔ Derived Repo Pattern

```text
Codomyrmex (this repo)                    Derived Repo (e.g., QuadCraft)
┌─────────────────────────┐              ┌──────────────────────┐
│ 129 modules             │              │ Focused codebase     │
│ Testing infrastructure  │──creates──→  │ Single responsibility│
│ MCP tool discovery      │              │ Own CI/CD            │
│ PAI Dashboard           │──manages──→  │ Linked via GitHub    │
│ Documentation standards │──templates──→│ RASP docs            │
│ Security scanning       │──audits───→  │ Validated            │
└─────────────────────────┘              └──────────────────────┘
```

### Module Developer Capabilities

- **Create a derived repo** — Start from Codomyrmex patterns, build a focused project
- **Link to PAI** — `POST /api/github/link` to connect the repo to PAI project tracking
- **Sync bidirectionally** — Issues, tasks, and status flow between PAI and GitHub
- **Test from Codomyrmex** — Run integration tests against the derived repo
- **Share tools** — Export `@mcp_tool` functions back into Codomyrmex discovery

### Module Developer Flexibility

| Flexibility Level | Description |
|------------------|-------------|
| **Tight coupling** | Module lives inside `src/codomyrmex/<name>/` — full tool discovery |
| **Linked repo** | Separate GitHub repo, linked via PAI project — issue sync, no tool sharing |
| **Loose federation** | Independent repo using Codomyrmex doc standards (RASP) but no runtime dependency |
| **Fully independent** | No Codomyrmex dependency — just follows the patterns learned here |

### Creating a Derived Repository

```bash
# 1. Create a new GitHub repo (can be done via PAI Dashboard Git tab)
gh repo create docxology/my-module --public

# 2. Set up with Codomyrmex patterns
mkdir my-module && cd my-module
# Copy RASP doc templates: README.md, AGENTS.md, SPEC.md, PAI.md
# Set up pyproject.toml with uv
# Add tests/ with zero-mock policy

# 3. Link to PAI project
curl -X POST http://localhost:8888/api/github/link \
  -H 'Content-Type: application/json' \
  -d '{"project":"my-module","repo":"docxology/my-module"}'

# 4. Sync issues and track progress from the Dashboard
```

### Module Developer Practice

- Create a small utility repo (e.g., a data parser, a CLI tool)
- Link it to PAI as a project under a mission
- Write tests for it using Codomyrmex's zero-mock patterns
- Push/pull issues between GitHub and the PAI Dashboard

---

## Level 5 — Orchestrator 🎭

**Trust**: Full | **Risk**: High | **Time**: Ongoing

**The whole point**: You can now orchestrate across multiple repos, agents, and Algorithm phases.

### Orchestrator Capabilities

- **Run The Algorithm** across a portfolio of projects (Dispatch tab)
- **Coordinate agents** — Engineer, Architect, QATester, Researcher each use different tool sets
- **Multi-repo orchestration** — Summarize, Scope & Plan, Review, Enact across linked repos
- **Email briefing** — Bike Ride loads Gmail, summarizes with LLM (`gemma3:4b`), drafts A/B/C responses
- **Calendar scheduling** — Integrate Algorithm execution windows with Google Calendar
- **Awareness synthesis** — `/api/awareness` aggregates TELOS, missions, projects, tasks, memory

### Full Flexibility Map

```text
┌──────────────────────────────────────────────────────────┐
│                    PAI Algorithm                          │
│  OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN │
└─────────────────────────┬────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ Codomyrmex│   │ Derived   │   │ Derived   │
    │ (testing) │   │ Repo A    │   │ Repo B    │
    │ 128 module│   │ (focused) │   │ (focused) │
    └───────────┘   └───────────┘   └───────────┘
```

### Configurable Parameters

| Parameter | Location | Purpose |
|-----------|----------|---------|
| `PAI_PM_LLM_MODEL` | `.env` or `config.ts` | LLM for Bike Ride/Dispatch (`gemma3:4b` default) |
| `PAI_PM_LLM_BACKEND` | `.env` or `config.ts` | Backend: `ollama`, `gemini`, `claude` |
| `GITHUB_DEFAULT_OWNER` | `.env` | Default GitHub org for repo linking |
| Trust ledger | `~/.codomyrmex/trust_ledger.json` | Persistent tool trust across sessions |
| PAI state | `~/.claude/MEMORY/STATE/` | Missions, projects, tasks (YAML) |

### The Tutoring Session Metaphor

Think of progressing through these levels as a tutoring session:

1. **Watch me do it** (Observer) — See the dashboard, read the docs
2. **Ask questions** (Explorer) — Query the system, search, analyze
3. **Try it yourself** (Builder) — Write code, run tests, modify the system
4. **Build something new** (Module Dev) — Create your own repo from patterns
5. **Teach others** (Orchestrator) — Run the full Algorithm, coordinate agents, manage a portfolio

The transition from Level 3 → 4 is the critical shift: **from modifying Codomyrmex to using it as a launchpad** for your own modular, tested, documented code.

---

## Navigation

- **Index**: [README.md](README.md)
- **Architecture**: [architecture.md](architecture.md)
- **Dashboard Setup**: [dashboard-setup.md](dashboard-setup.md)
- **Workflows**: [workflows.md](workflows.md)
- **Tools**: [tools-reference.md](tools-reference.md)
- **Root PAI Bridge**: [../../PAI.md](../../PAI.md)
