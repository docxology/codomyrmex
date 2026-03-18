# Agent Documentation — Specification

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Defines the structure and behavioral standards for agent coordination documentation within the Codomyrmex ecosystem. This directory documents **38 agent frameworks** organized into 5 categories.

## Documentation Structure

Each agent documentation subfolder follows this convention:

```
docs/agents/<agent_name>/
├── README.md          # Overview, key files, usage, navigation
├── (optional files)   # Deep-dive docs for complex agents like Hermes
```

The `README.md` for each agent provides:
- Module identifier and category
- Purpose and description
- Key source files with links
- Quick start usage example
- Links to source documentation (README, SPEC, AGENTS, PAI)

## Architectural Constraints

- **Mirror Rule**: `docs/agents/` mirrors `src/codomyrmex/agents/` — every source agent directory has a corresponding docs subfolder
- **Modularity**: Agent rules must maintain strict modular boundaries — each rule file addresses a specific concern
- **Real Execution**: Rules must guarantee executable, verifiable behavior without reliance on stubbed or mocked data
- **Hierarchy**: Agent directives follow: root `AGENTS.md` → `docs/AGENTS.md` → `docs/agents/AGENTS.md` → per-agent `AGENTS.md`
- **Category Organization**: Agents are grouped into CLI-based, API-based, Core Infrastructure, Infrastructure, and Specialized

## Agent Categories

| Category | Count | Examples |
|:---|---:|:---|
| CLI-based | 10 | Jules, Gemini, Hermes, Every Code |
| API-based | 6 | Claude, Codex, O1, DeepSeek, Qwen, Perplexity |
| Core Infrastructure | 8 | Core, Droid, Planner, Memory, Meta, Learning |
| Infrastructure | 9 | Agent Setup, CLI, Context, Pooling, Transport |
| Specialized | 5 | Git Agent, Mission Control, Specialized, Theory |

## Verification Criteria

- [ ] Every `src/codomyrmex/agents/*/` has a corresponding `docs/agents/*/`
- [ ] Every agent doc README links back to its source module
- [ ] Navigation links are valid and bidirectional
- [ ] Version headers are current

## Navigation

- **README**: [README.md](README.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **PAI**: [PAI.md](PAI.md)
- **Parent**: [docs/](../README.md)
- **Source**: [src/codomyrmex/agents/](../../src/codomyrmex/agents/)
