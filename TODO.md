# Codomyrmex TODO — Post-v1.3.0 Engineering & Research Backlog

**Version**: v1.3.1+ (Development)
**Scope**: Advanced research adapters, formal bridge extensions, adversarial robustness, concurrency & durability guarantees, type safety, and test suite performance.

This file tracks open research items, formal gaps, and architectural improvements following the published v1.3.0 technical report (concept DOI `10.5281/zenodo.21750800`, version DOI `10.5281/zenodo.21750801`). Completed publication blockers (P1–P7) are archived in [CHANGELOG.md](CHANGELOG.md).

---

## Major Items (Foundational Adapters & Workload Harnesses)

| ID | Title | Scope & Artifacts | Acceptance Criteria |
|:---|:------|:------------------|:--------------------|
| **R2** | **External-Actuation Observation Adapter** | `src/codomyrmex/colony_kernel/research/actuation_adapter.py`, `tests/unit/colony_kernel/test_external_actuation.py` | Independent runtime observation harness distinguishing external actuation from caller-reported lifecycle events, with tamper-proof receipt verification, replay rejection, and execution verification. |
| **R3** | **Adversarial Workload Evaluation Adapter** | `src/codomyrmex/colony_kernel/research/adversarial_workload.py`, `tests/unit/colony_kernel/test_adversarial_workload.py` | Implementation of threat-stratified benchmark adapter (AgentDojo, InjecAgent, ToolEmu protocols) with paired assignments, attack success metrics, and safety-utility frontier analysis. |
| **F5 / R6** | **Active Inference Research Adapter & Formal Bridge** | `src/codomyrmex/colony_kernel/research/active_inference_adapter.py`, `src/codomyrmex/colony_kernel/research/probabilistic.py`, `tests/unit/colony_kernel/test_active_inference_adapter.py` | End-to-end active inference decision loop bridging `cerebrum` and `colony_kernel`, evaluating expected free energy against deterministic gates under declared generative model assumptions. |

---

## Medium Items (Empirical Studies & Formalism Crosswalk)

| ID | Title | Scope & Artifacts | Acceptance Criteria |
|:---|:------|:------------------|:--------------------|
| **R4** | **Trust Calibration Study Harness** | `src/codomyrmex/colony_kernel/research/calibration_study.py`, `tests/unit/colony_kernel/test_calibration_study.py` | Multi-method calibration analysis (Brier score, ECE, Platt scaling, reliability diagrams) on synthetic and attested traces with formal missingness handling. |
| **R5** | **Persistence and Concurrency Study Harness** | `src/codomyrmex/colony_kernel/research/concurrency_study.py`, `tests/unit/colony_kernel/test_concurrency_study.py` | Multi-worker concurrent load testing, crash injection across transaction boundaries, WAL persistence verification, and race condition auditing. |
| **F3** | **Formalism-to-Code Runtime Invariant Crosswalk** | `src/codomyrmex/colony_kernel/invariants.py`, `tests/unit/colony_kernel/test_invariants.py` | Extended runtime invariant predicates validating budget monotonicity, gate decision space closure, consequence trust bounds, and cross-subsystem invariant suites. |

---

## Minor Items (Typing, Documentation & Performance)

| ID | Title | Scope & Artifacts | Acceptance Criteria |
|:---|:------|:------------------|:--------------------|
| **M1** | **Type Safety & `py.typed` Markers** | `src/codomyrmex/colony_kernel/research/py.typed`, `src/codomyrmex/colony_kernel/falsification/py.typed`, strict type annotations | Package markers present, zero unsafe type ignores in core kernel packages, full stub parity. |
| **M2** | **Docs Crosswalk & Inventory Audit** | `docs/reference/inventory.md`, `docs/todo/COLONY_KERNEL.md` | Inventory counters, module links, and roadmap alignment fully verified with live code tree. |
| **M3** | **Test Speed & Suite Optimization** | `pyproject.toml`, test runner configs | Benchmark/xdist isolation, deterministic execution without timeout stalls across unit test suites. |

---

## Working Constraints

- Preserve all v1.3.0 release receipts and Zenodo metadata bindings in historical logs.
- Preserve the dirty `src/codomyrmex/agents/open_gauss` submodule as a separate ownership boundary; no cleanup or edits are authorized.
- Preserve failed gates, negative controls, `not_estimated` calibration status, and conditional or `not_run` claims.
- Zero-Mock Policy: All test suites must exercise authentic functional implementations.
