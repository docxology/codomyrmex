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

- [x] **Delegated URL admission:** Video transcription and AgentMail webhook MCP
  wrappers now deny backend delegation by default, including raw MCP registration.
  Strict per-tool operator grants and stable denial codes complete the admission
  control. Enabling a tool still requires separately enforced and tested downloader
  or delivery-service destination/DNS/redirect/proxy controls; keep it disabled when
  those controls are unavailable. Follow the
  [delegated URL deployment guide](src/codomyrmex/model_context_protocol/SECURITY.md#delegated-url-tools).
  The opt-in HTTP client policy does not certify external engines.

- **Portable MLX configuration study:** Two fresh-process Python 3.15 runs now
  retain raw samples, exact source archive/import hashes, full dependency freeze,
  revision/dirty state, and bundle manifests; see the
  [replication record](docs/modules/llm/mlx-profiling-study.md#2026-10-19-fresh-process-replication).
  These are same-host configuration observations, not causal improvements or
  independent-host replication. Repeat on an independently controlled host;
  production inference and Metal-memory/recall studies remain open work.

- **MLX upstream follow-up:** Verify ml-explore/mlx-lm PR #1978 after release,
  compare bounded chunked-prefill logits/recall against token-by-token prefill,
  and only then relax the temporary one-token bounded-cache policy. Reproduce
  long-context peak-memory/throughput/recall measurements on declared hardware
  before making performance claims; existing tiny-model regressions are not
  that benchmark study.

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

## Workflowz review — 2026-11-10

- [ ] **C1 (P1) — Make rollback outcomes reflect an actual restore.** `DeploymentOrchestrator._rollback_deployment` returns normally when `previous_version` is missing, performs no default rollback, and dispatches to `_rollback_rolling` / `_rollback_blue_green` bodies containing successful no-op branches; `deploy()` then unconditionally assigns `ROLLED_BACK`. Implement the supported backend restores, or explicitly reject unsupported/missing rollback state and leave the deployment failed rather than claiming restoration. **Evidence:** `src/codomyrmex/ci_cd_automation/deployment_orchestrator.py:309-334`, `src/codomyrmex/ci_cd_automation/deployment_orchestrator.py:680-740`; current tests explicitly accept the no-ops at `tests/unit/ci_cd_automation/test_deployment_orchestrator.py:697-715`. **Acceptance probe:** from the repository root run `uv run --locked pytest -q tests/unit/ci_cd_automation/test_deployment_orchestrator.py`; new real-subprocess/temporary-environment cases must show that every `ROLLED_BACK` result follows a completed restore and absent backends, absent previous versions, and canary/default paths cannot produce that status. **Constraints:** no mock Docker/Kubernetes clients; preserve real `kubectl rollout undo` behavior and keep unsupported providers explicit rather than inventing success.

- [ ] **C2 (P1) — Remove Hermes's fabricated successful delegation.** `hermes_spawn_agent` catches every client-construction failure, installs a delegate returning only `"Hermes agent delegated (stub)"`, and `_dispatch.spawn_agent` wraps it as top-level success; execution also returns model content without checking `AgentResponse.is_success()`. Propagate unavailable-provider and unsuccessful-response errors without a canned result, and replace the permissive mocked test with behavioral coverage of success and failure. **Evidence:** `src/codomyrmex/agents/hermes/mcp_tools_pkg/execution.py:306-355`, `src/codomyrmex/agents/hermes/_dispatch.py:17-59`, `tests/unit/agents/hermes/test_mcp_tools.py:242-264`. **Acceptance probe:** run `uv run --locked pytest -q tests/unit/agents/hermes/test_mcp_tools.py tests/unit/agents/hermes/test_dispatch_boundary.py`; with no Hermes/Ollama backend the tool must return `status="error"` and never the stub note, while a real controlled local backend success still returns its content and a real unsuccessful response returns `status="error"`. **Constraints:** follow the zero-mock policy (use a real local CLI/server fixture or environment-gated integration case, not monkeypatched fake responses); preserve `_dispatch.spawn_agent`'s public result shape.

- [ ] **C3 (P1) — Stop generating a fake Ollama integration.** The public `ollama_module` task writes a client whose `generate()` merely formats the prompt back with `[ollama:...]`, generates an import from a different package than the one it writes, and resolves `project_root` to the package directory (creating a nested `src/codomyrmex/src/codomyrmex/...` path). Replace this generator with the existing real HTTP-client path and genuine response assertions, or remove/refuse the task until it can be implemented. **Evidence:** `src/codomyrmex/agents/droid/generators/physical_generators/tasks.py:189-230`; `run_todos` treats any non-exception handler return as completed at `src/codomyrmex/agents/droid/run_todo_droid.py:235-264`; the existing real implementation is `src/codomyrmex/agents/llm_client.py:47-116`. **Acceptance probe:** run `uv run --locked pytest -q tests/unit/agents/droid`; generator coverage must execute its generated integration against a real temporary local Ollama-compatible HTTP server, assert returned server content (not a prompt echo), and prove all writes/imports resolve below the actual repository/package root with no fabricated client and no nested duplicate package tree. **Constraints:** no network dependence in the default suite and no mock transport; a localhost `http.server` fixture is acceptable. Small model choice is not constrained by this cleanup.

- [ ] **C4 (P2) — Eliminate acknowledgment-only droid task handlers.** `refactor_todo_processing` and `testing_and_docs` claim refactoring/testing outcomes although they only log fixed acknowledgment strings. Remove these reserved handlers and exports/documentation, or implement and verify their advertised effects so unsupported work cannot be treated as completed. **Evidence:** `src/codomyrmex/agents/droid/generators/physical_generators/tasks.py:125-144`, exports at `src/codomyrmex/agents/droid/generators/physical_generators/__init__.py:18-43`, contract at `src/codomyrmex/agents/droid/generators/physical_generators/SPEC.md:26-30`; generic success rotation at `src/codomyrmex/agents/droid/run_todo_droid.py:235-264` and `src/codomyrmex/agents/droid/run_todo_droid.py:315-317`. **Acceptance probe:** run `uv run --locked pytest -q tests/unit/agents/droid`; each remaining handler must have an observable filesystem/process/test outcome, while attempting to resolve either removed acknowledgment-only handler must fail and leave its TODO unrotated rather than report completion. **Constraints:** do not rewrite historical completed-task receipts; this is a live-handler/contract cleanup, not a generic refactor of `TodoManager`.

- [ ] **C5 (P2) — Prevent generated test scaffolds from passing without exercising code.** `TestGenerator` emits `assert True` for every function/class body, so its rendered suite passes while testing nothing, contradicting the documented Red-phase expectation. Make the scaffold fail explicitly with actionable `pytest.fail(...)`/`NotImplementedError` markers until an agent supplies assertions, and update dependent review-loop behavior and documentation; do not guess behavior-specific assertions without evidence. **Evidence:** unconditional bodies at `src/codomyrmex/coding/test_generator.py:104-153`; consumer at `src/codomyrmex/agents/specialized/review_loop.py:12-15`; documented Red-phase contract at `src/codomyrmex/testing/PAI.md:143-145`, while `docs/modules/testing/PAI.md:28` explicitly describes temporary stubs. **Acceptance probe:** run `uv run --locked pytest -q tests/unit/observability/test_observability_codegen.py tests/unit/coding/test_generator_module.py` plus a new test that writes one generated suite to `tmp_path` and invokes `uv run --locked pytest -q <generated-file>`; the subprocess must be nonzero with one clear unimplemented-test failure per generated case, and suite/rendered test-count behavior must remain intact. **Constraints:** preserve syntax-error handling and the existing `TestSuite`/`GeneratedTest` interfaces; do not claim these generated placeholders are valid verification.

- [ ] **C6 (P2) — Separate sample Git charts from repository data.** The PNG Git tree/activity methods silently manufacture branches/commits whenever inputs are absent or an explicitly supplied list is empty, then return success as for a repository-backed chart. Require an explicit `sample=True` path (or separate sample-only helper) and make empty repository/explicit data return an empty-input failure rather than fabricated activity. **Evidence:** fallback branches at `src/codomyrmex/data_visualization/git/_charts.py:79-93` and `src/codomyrmex/data_visualization/git/_charts.py:244-252`; tests currently bless both behaviors at `tests/unit/data_visualization/test_git_visualizer.py:240-248` and `tests/unit/data_visualization/test_git_visualizer.py:370-395`. **Acceptance probe:** run `uv run --locked pytest -q tests/unit/data_visualization/test_git_visualizer.py tests/unit/data_visualization/test_dataviz_advanced.py`; absent/empty real inputs must not emit sample charts, `sample=True` must produce a clearly sample-labelled chart, and a real temporary Git repository or supplied commits must still render unchanged actual data. **Constraints:** preserve the explicit `_generate_sample_commits` utility for examples; satisfy CI's real-temporary-Git approach without mocks.
