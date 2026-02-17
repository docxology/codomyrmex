# Plan: Create PAI Discussion — Codomyrmex Show & Tell

## Context

Issue #710 on `danielmiessler/Personal_AI_Infrastructure` was closed as "not an issue." The content was solid but wrong venue. Daniel wants a fresh **Discussion** in the "Show and tell" category that demonstrates — through deep links and architecture, not abstract claims — how PAI and Codomyrmex form a synergistic system.

## Approach

1. Create a GitHub Discussion using `gh api graphql` with the "Show and tell" category (`DIC_kwDOPsEkG84Cvr4p`)
2. Repository ID: needs to be fetched (will use `gh api graphql`)
3. All links point to `https://github.com/docxology/codomyrmex/blob/main/` or tree

## Discussion Content (Full Draft)

**Title:** `Codomyrmex v0.1.2: 78-Module Python Toolbox Bridging PAI to Scientific Computing via MCP`

**Category:** Show and tell

**Body:**

---

We built [Codomyrmex](https://github.com/docxology/codomyrmex) (v0.1.2) as an open-source, modular Python development platform — 78 specialized modules that PAI agents consume via MCP. Here's what that looks like concretely.

## The Architecture

PAI is the cognitive layer (TypeScript/Bun, `~/.claude/`). Codomyrmex is the tool layer (Python, installable via `uv`). MCP connects them:

```
PAI (Algorithm v1.5.0 + 38 Skills + 20 Hooks + 13 Agents + 3-tier Memory)
  │
  │  MCP Protocol (stdio or HTTP)
  ▼
Codomyrmex (78 Python modules)
  ├── PAIBridge      → reads PAI's own filesystem to discover skills, hooks, agents, memory
  ├── MCP Bridge     → exposes 18 static tools + auto-discovered module tools
  └── Trust Gateway  → gates destructive ops behind explicit approval (UNTRUSTED → VERIFIED → TRUSTED)
```

**Source**: [`docs/pai/architecture.md`](https://github.com/docxology/codomyrmex/blob/main/docs/pai/architecture.md) — full component diagram and data flow

## What PAI Provides: Cognitive Augmentation

Without PAI, an agent is a stateless function caller. PAI provides the cognitive scaffold:

| PAI Component | What It Gives the Agent | Scale |
|---|---|---|
| **The Algorithm** (v1.5.0) | 7-phase method: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN | Every prompt |
| **Ideal State Criteria** | Binary-testable verification targets — the agent knows *when it's done* | 4-500+ per task |
| **Identity** (TELOS) | Who the user is, what matters, what the agent learned last time | Persistent |
| **Memory** (WORK/STATE/LEARNING) | Three-tier state that survives across sessions | Persistent |
| **Skills** (38) | Domain-specific sub-algorithms (Research, RedTeam, Council, Browser, etc.) | Composable |
| **Hooks** (20) | Event-driven behavioral gates (voice, capability recommendation, security) | Automatic |
| **Named Agents** (13+) | Typed personalities: Engineer, Architect, Researcher, QATester — each with tools and voice | Parallelizable |

This is the "nestmate" augmentation: PAI turns a generic LLM session into a situated agent with method, memory, and judgment.

## What Codomyrmex Provides: The Bridge from NL to Tools

Codomyrmex is the continuum from natural language intent to deterministic tool execution:

```
Natural Language (user prompt)
  → PAI Algorithm (capability selection, ISC creation)
    → MCP Bridge (tool routing, trust enforcement)
      → Codomyrmex Modules:
          coding/static_analysis/  → PyRefly, Ruff, security scanning
          git_operations/          → version control automation
          data_visualization/      → matplotlib charts, reports
          orchestrator/            → workflow DAG execution
          security/                → vulnerability scanning, governance
          llm/                     → multi-provider LLM infrastructure
          agentic_memory/          → persistent knowledge stores
          cerebrum/                → case-based reasoning
          ... (78 total)
```

Every module follows the [RASP pattern](https://github.com/docxology/codomyrmex/blob/main/PAI.md#rasp-documentation-pattern) — `README.md`, `AGENTS.md`, `SPEC.md`, `PAI.md` — so AI agents can discover what each module offers without parsing source code.

**Source**: [`PAI.md`](https://github.com/docxology/codomyrmex/blob/main/PAI.md) — the authoritative bridge document

## Algorithm Phase → Module Mapping

Each phase of PAI's Algorithm routes to specific Codomyrmex tools:

| Algorithm Phase | Codomyrmex Modules | Example Tool Calls |
|---|---|---|
| **OBSERVE** | `system_discovery`, `search`, `pattern_matching` | `list_modules`, `search_codebase` |
| **THINK** | `cerebrum`, `graph_rag`, `agents/theory/` | `analyze_python`, `module_info` |
| **PLAN** | `orchestrator`, `logistics` | `read_file`, `json_query` |
| **BUILD** | `coding`, `agents/ai_code_editing/` | `write_file` |
| **EXECUTE** | `agents` (all providers), `git_operations` | `run_command`, `run_tests` |
| **VERIFY** | `coding/static_analysis/`, `security` | `git_diff`, `checksum_file` |
| **LEARN** | `agentic_memory`, `logging_monitoring` | `pai_awareness`, `pai_status` |

**Source**: [`docs/pai/workflows.md`](https://github.com/docxology/codomyrmex/blob/main/docs/pai/workflows.md) — bidirectional data flow details

## Nesting, Recursion, and Self-Reference

The architecture is reflexive by design:

1. **PAIBridge introspects PAI itself.** The [`pai_bridge.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/pai_bridge.py) module reads `~/.claude/skills/PAI/SKILL.md`, enumerates all skills/hooks/agents/memory stores, and exposes them as structured data. PAI can query its own configuration through Codomyrmex.

2. **The MCP Bridge is self-discovering.** [`mcp_bridge.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/mcp_bridge.py) auto-discovers tools from every module at runtime via `discover_all_public_tools()`. Add a module, and its functions appear as MCP tools — no registration step.

3. **The Trust Gateway gates itself.** [`trust_gateway.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/trust_gateway.py) enforces a three-tier model (`UNTRUSTED → VERIFIED → TRUSTED`) where the `/codomyrmexVerify` and `/codomyrmexTrust` workflows — themselves exposed via the MCP bridge — control which tools are executable. The verification workflow audits the trust system using the trust system.

4. **Universal module proxy.** Three meta-tools ([`list_module_functions`](https://github.com/docxology/codomyrmex/blob/main/docs/pai/tools-reference.md#universal-module-proxy-3-tools), `call_module_function`, `get_module_readme`) let a PAI agent discover and invoke *any* public function from *any* of the 78 modules — without those modules knowing they're being called via MCP. The tool layer is transparent to itself.

This recursive structure means PAI agents can inspect, extend, and reason about the toolbox they're using — while using it.

## Concrete Numbers (v0.1.2)

| What | Count |
|---|---|
| Python modules | 78 |
| Static MCP tools | 18 (14 safe + 4 destructive) |
| MCP resources | 2 |
| MCP prompts | 10 |
| PAI bridge dataclasses | 7 |
| Bridge API methods | 22 |
| Test suite | 25 passing, 5 skipped |
| RASP docs per module | 4 (README, AGENTS, SPEC, PAI) |

## Get Started

```bash
git clone https://github.com/docxology/codomyrmex.git
cd codomyrmex && uv sync
```

Then [connect to PAI via MCP](https://github.com/docxology/codomyrmex/blob/main/docs/getting-started/tutorials/connecting-pai.md).

**Full integration docs**: [`docs/pai/`](https://github.com/docxology/codomyrmex/tree/main/docs/pai) — architecture, tools reference, API, workflows

---

## Verification

After posting, verify:
1. Discussion appears at `https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions`
2. All deep links resolve (spot-check 3-4)
3. Category is "Show and tell"

## Command

```bash
gh api graphql -f query='
mutation {
  createDiscussion(input: {
    repositoryId: "<REPO_ID>",
    categoryId: "DIC_kwDOPsEkG84Cvr4p",
    title: "Codomyrmex v0.1.2: 78-Module Python Toolbox Bridging PAI to Scientific Computing via MCP",
    body: "<BODY>"
  }) {
    discussion { url }
  }
}'
```

Repository ID will be fetched via `gh api graphql` before posting.
