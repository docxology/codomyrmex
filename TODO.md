# Codomyrmex TODO — Post-v1.3.0 Engineering & Research Backlog

**Version**: v1.3.1+ (Development)
**Scope**: Advanced research adapters, formal bridge extensions, adversarial robustness, concurrency & durability guarantees, type safety, and test suite performance.

This file tracks open research items, formal gaps, and architectural improvements following the published v1.3.0 technical report (concept DOI `10.5281/zenodo.21750800`, version DOI `10.5281/zenodo.21750801`). Completed publication blockers (P1–P7) are archived in [CHANGELOG.md](CHANGELOG.md).

---

## Evidence Program (Implemented Substrate, Open Studies)

| ID | Title | Scope & Artifacts | Acceptance Criteria |
| :--- | :------ | :------------------ | :-------------------- |
| **R2** | **External actuation study** | Adapter and deterministic verification tests are implemented. | Run a declared deployment adapter against independently sourced execution evidence; retain replay, forgery, linkage, and overhead results. |
| **R3** | **Adversarial workload study** | Synthetic evaluator and external benchmark protocols are implemented. | Execute preregistered external workloads with unique cases, paired assignments, complete traces, failure stratification, and independent rerun. |
| **R4** | **Trust calibration study** | Calibration harness is implemented. | Acquire held-out independently observed outcomes; report missingness, Brier score, ECE, log loss, selective risk, utility, and uncertainty. |
| **R5** | **Persistence and concurrency study** | SQLite WAL and crash/concurrency harnesses are implemented. | Run the declared multi-worker deployment matrix with restart, ordering, isolation, throughput, latency, and retained failure evidence. |
| **F5 / R6** | **Probabilistic and Active Inference comparison** | Declared generative-model and decision-loop prototypes are implemented. | Complete held-out calibration and paired policy comparisons without relabeling deterministic scores as probabilities or expected free energy. |
| **R7** | **Independent replication and promotion** | Dependency-aware orchestration is implemented; the independent study is not run. | Reproduce or reject each candidate result in a separate environment and issue a discrepancy ledger plus signed promotion decision. |

---

## Maintenance

| ID | Title | Scope & Artifacts | Acceptance Criteria |
| :--- | :------ | :------------------ | :-------------------- |
| **M3** | **Test Speed & Suite Optimization** | `pyproject.toml`, test runner configs | Benchmark/xdist isolation, deterministic execution without timeout stalls across unit test suites. |

---

## Working Constraints

- Preserve all v1.3.0 release receipts and Zenodo metadata bindings in historical logs.
- Preserve the dirty `src/codomyrmex/agents/open_gauss` submodule as a separate ownership boundary; no cleanup or edits are authorized.
- Preserve failed gates, negative controls, `not_estimated` calibration status, and conditional or `not_run` claims.
- Zero-Mock Policy: All test suites must exercise authentic functional implementations.

## Documentation contract completeness

The specification validators report unresolved API signatures and undocumented
MCP tools explicitly. Resolve these inventories and extend resolution/annotation
coverage before claiming complete public API/MCP documentation parity. A gate
with zero broken resolved references does not establish that stronger claim.

Completed F3/M1/M2 engineering and inventory work is recorded in CHANGELOG.md
and REVIEW_LOG_2026-10-12.md. Completed agent ergonomics entries remain in
historical review logs and git history rather than this open backlog.
