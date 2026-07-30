# Abstract {#sec:abstract .unnumbered}

Agentic software can preserve task state while still forgetting the consequences of
prior actions. Codomyrmex studies a narrow control-plane question: after a caller reports
a failed action at one software location, can the system deterministically increase
friction for a materially similar proposal at that location without changing an
unrelated target? Its Colony Control Plane records consequence reports and couples them
to target-indexed signal pressure, agent trust, role labels, resource accounting,
adversarial checks, and an explicit EXECUTE/HOLD/REFUSE gate.

The implementation comprises {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} cooperating subsystems.
The ordinary Model Context Protocol path remains caller-reported and unattested.
Optional and required `ColonyKernel` attestation modes instead bind proposal, verdict,
authorization, execution receipt, and outcome in a signed, hash-linked local ledger.
That ledger protects lifecycle linkage but does not independently observe external
actuation or establish deployment safety. Consequence records can use file-backed
SQLite; the default MCP kernel and signal field remain process-local.

Evaluation is limited to implementation properties and controlled fixtures. At
composition time, the scoped Colony Kernel surface contains {{RESULT_TEST_COUNT}}
passing tests with {{RESULT_COVERAGE_PCT}}% branch coverage,
{{RESULT_RUFF_ERRORS}} Ruff errors, and {{RESULT_TY_ERRORS}} ty diagnostics. A paired
deterministic replay moves the same-target proposal from
{{RESULT_PAIRED_CLEAR_SCORE}}/EXECUTE to
{{RESULT_PAIRED_FAILURE_SCORE}}/HOLD after a reported failure while leaving an unrelated
target unchanged. Separate fixtures exercise trust promotion, bounded arithmetic,
linear signal decay, local attestation integrity, and interface behavior. These results
support reproducible software contracts, not ecological optimality, calibrated risk,
production harm reduction, or generalization to external workloads.

The report contributes the typed control plane, transparent gate, coupled local
feedback, authenticated local lifecycle option, and source-bound publication workflow.
Generated variables, figures, citations, claim boundaries, and release receipts tie the
rendered report to the evaluated checkout. End-to-end external-actuation attestation,
restart-persistent field storage, representative benchmarks, and independent deployment
validation remain open.

**Keywords:** {{CONFIG_KEYWORDS}}

*Corresponding author: {{CONFIG_FIRST_AUTHOR}}*
