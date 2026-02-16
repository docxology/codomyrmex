> **Not a bug.** An epistemic offering — sharing how one downstream project uses PAI, in the spirit of open source, active inference, and alignment.

---

## The Analogy That Clicked

While building [Codomyrmex](https://github.com/docxology/codomyrmex), an open-source modular toolkit for AI-assisted development, we found ourselves reaching for PAI repeatedly — not because we had to, but because the architecture *made sense of* what we were already doing.

**PAI is the cognitive augmentation of the agent.** It gives an AI system *identity* (TELOS), *method* (The Algorithm), *memory* (three-tier STATE/LEARNING/HISTORY), and *judgment* (the Security System). Without PAI, an agent is a stateless tool-caller. With PAI, it knows *who it's working for*, *what matters*, and *what it learned last time*.

**Codomyrmex is a Swiss Army knife of tools.** 100+ modules for code analysis, testing, documentation, security, LLM orchestration, git operations, and infrastructure — all exposed via the [Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/). It doesn't know *why* it's being asked to do something. It just does the thing well.

The two are complementary the way a mind is complementary to hands. Neither is sufficient alone. Neither claims to be the best or only solution in its space. But together, they illustrate a pattern that we think is worth sharing.

---

## What We Built

We created a **bidirectional bridge** ([v0.1.1 release](https://github.com/docxology/codomyrmex/releases/tag/v0.1.1)) with three layers:

### Layer 1: Discovery — PAIBridge reads PAI's filesystem

[`pai_bridge.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/pai_bridge.py) treats `~/.claude/` as the source of truth:

```python
from codomyrmex.agents.pai import PAIBridge

bridge = PAIBridge()
bridge.get_telos_files()      # → ['BELIEFS.md', 'CHALLENGES.md', 'GOALS.md', ...]
bridge.list_skills()          # → [PAISkillInfo(name='PAI', has_skill_md=True, ...)]
bridge.list_hooks()           # → [PAIHookInfo(name='FormatReminder', ...)]
bridge.list_memory_stores()   # → [PAIMemoryStore(name='STATE', ...), ...]
bridge.get_algorithm_phases() # → ['OBSERVE', 'THINK', 'PLAN', 'BUILD', 'EXECUTE', 'VERIFY', 'LEARN']
```

No network calls. Pure filesystem inspection. The bridge encodes all 16 PAI Principles and The Algorithm v0.2.25 as constants, so downstream code can reason about PAI's structure programmatically.

### Layer 2: Communication — MCP exposes 100+ tools to PAI agents

[`mcp_bridge.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/mcp_bridge.py) maps every module to Algorithm phases:

```
OBSERVE  →  list_modules, module_info, list_directory
THINK    →  analyze_python, search_codebase
PLAN     →  read_file, json_query
BUILD    →  write_file
EXECUTE  →  run_command, run_tests
VERIFY   →  git_status, git_diff, checksum_file
LEARN    →  pai_awareness, pai_status
```

This mapping isn't prescriptive — it's descriptive. It helps a PAI-aware agent understand *when* a tool is most naturally useful within the Algorithm's flow.

### Layer 3: Security — TrustGateway enforces PAI's security principle

[`trust_gateway.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/trust_gateway.py) implements a three-tier trust model (UNTRUSTED → VERIFIED → TRUSTED) that mirrors PAI's own security philosophy: **validate before you execute**.

---

## Why We Think This Pattern Matters

We're not claiming Codomyrmex is the right toolbox for every PAI user. We're observing that the **separation PAI creates** — between *purpose* (TELOS), *method* (Algorithm), *memory* (three tiers), and *execution* (Skills/Tools) — naturally invites modular toolkits to plug into the execution layer.

This is essentially the [Active Inference](https://en.wikipedia.org/wiki/Active_inference) pattern applied to AI agents:

```
┌─────────────────────────────────┐
│  Generative Model (PAI)         │
│                                 │
│  "Who am I? What do I want?     │
│   What have I learned?          │
│   What should I do next?"       │
│                                 │
│  TELOS → Algorithm → Memory     │
└────────────┬────────────────────┘
             │ action selection
             ▼
┌─────────────────────────────────┐
│  Action Repertoire (Toolkits)   │
│                                 │
│  "Here are 100+ things I can    │
│   actually do in the world."    │
│                                 │
│  Codomyrmex, or any MCP server  │
└────────────┬────────────────────┘
             │ observations
             ▼
┌─────────────────────────────────┐
│  World (Codebase, APIs, Infra)  │
└─────────────────────────────────┘
```

PAI handles the **belief updating** (TELOS + Memory). The toolkit handles the **action execution**. The world provides **observations** that feed back into PAI's learning phases. This is the perception-action loop, and PAI's architecture is already shaped for it.

---

## Documentation

We wrote a [10-document guide](https://github.com/docxology/codomyrmex/tree/main/docs/modules/agents/PAI) for the integration:

| Document | What It Covers |
|:---|:---|
| [README](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/README.md) | Bidirectional architecture overview |
| [ARCHITECTURE](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/ARCHITECTURE.md) | Three-layer technical deep dive |
| [ALGORITHM](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/ALGORITHM.md) | Algorithm v0.2.25 phase integration |
| [SKILLS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/SKILLS.md) | Skill system architecture |
| [TELOS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/TELOS.md) | Deep goal understanding |
| [HOOKS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/HOOKS.md) | Hook system lifecycle events |
| [WORKFLOWS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/WORKFLOWS.md) | Workflows and dispatch |
| [FLOWS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/FLOWS.md) | Mermaid sequence diagrams |
| [SIGNPOSTS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/SIGNPOSTS.md) | Line-level source code pointers |
| [AGENTS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/AGENTS.md) | Agent coordination guide |

---

## Questions for the Community

We're not proposing changes to PAI. We're curious:

1. **Are others building similar bridges?** We'd love to see how other tool ecosystems integrate with PAI's Algorithm and TELOS.
2. **Memory interoperability** — is there an emerging pattern for how external tools should read from / write to the three-tier memory system?
3. **Skill manifest conventions** — we generate a PAI-compatible skill manifest via `get_skill_manifest()`. Are there conventions forming around how external skill packs describe their capabilities?

---

**[Codomyrmex v0.1.1](https://github.com/docxology/codomyrmex/releases/tag/v0.1.1)** · [Repository](https://github.com/docxology/codomyrmex) · [PAI Integration Docs](https://github.com/docxology/codomyrmex/tree/main/docs/modules/agents/PAI) · MIT License


---

**Submitted**: [danielmiessler/Personal_AI_Infrastructure#710](https://github.com/danielmiessler/Personal_AI_Infrastructure/issues/710)
