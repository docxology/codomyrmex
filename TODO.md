<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.5.0 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 33

> v1.5.3 "Session Routing & Inference" delivered. Cross-platform identity resolution, tool sandboxing, and token streaming completed.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.5.4 — Multimodal Media Handlers

> **Theme**: Audio, Image, and Document processing pipelines over channels.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Voice/Audio Transcoding** | `agents/hermes/` | Integrate `audio/` primitives (e.g. Whisper STT) to transcribe voice notes received natively across messaging adapters before LLM routing. |
| D2 | **VLM Image Descriptions** | `agents/hermes/` | Route incoming media attachments through a local Ollama VLM (via `vision/`) to generate descriptive alt-text appended natively into the session prompt. |
| D3 | **Document Extraction** | `agents/hermes/` | Parse incoming PDF/TXT files utilizing `documents/` extracting the raw text and injecting it cleanly into the active session context window. |

---

## 🚀 v1.5.5 — Advanced Agent Automation

> **Theme**: Tool orchestration, memory retrieval, and sequential tasking.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Long-Term Memory Search** | `agents/hermes/` | Expose the `agentic_memory/` vector search as a native tool, allowing the agent to recall deeply archived session interactions. |
| D2 | **Automated Task Execution** | `agents/hermes/` | Enable the agent to formulate step-by-step checklists internally via a `task_manager` without requiring external prompts for multi-step goals over chat. |

---

## 🔭 v1.6.0+ — Horizon & Integration

> **Theme**: Cryptographic persistence, spatial world modeling, and omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | Fully integrate 4D time-series scene generation to render persistent simulation environments natively for agent embodied trials. |
| R2 | **Self-Custody Wallet** | `wallet/` | Expose zero-knowledge decentralized self-custody frameworks to allow agents to control their operational resources and perform autonomous transactions securely. |
| R3 | **Identity & Persona** | `identity/` | Establish bio-verified and multi-persona cognitive masking for defensive agentic operations across public networks. |

---

## Release Criteria

> [!IMPORTANT]
> **Strict Delivery Requirements**:
>
> - **Zero-Mock Policy**: All tests must use 100% real dependencies and functional components. No mock methods.
> - **Full Test Pass**: All 33,000+ unit and integration tests passing natively (`uv run pytest`) before final branch integration.
> - **Code Health**: No backwards or legacy methods, no technical debt, and 100% lint compliance. Clean repository state.
> - **Documentation**: Complete API documentation and signposting (`AGENTS.md`) for all new capabilities. Consistency with README.md and SPEC.md.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=75`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-13 — Sprint 33.*
