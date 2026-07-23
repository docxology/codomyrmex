# Abstract {#sec:abstract .unnumbered}

Agentic software systems can preserve task state while still forgetting the consequences
of prior actions. Codomyrmex addresses that gap with a testable control-plane claim:
after a failed action, a materially similar proposal at the affected location should
become measurably harder to pass through the proposal-evaluation gate. The framework records
reported outcomes in consequence memory and converts them into changes in local
pheromone pressure, agent trust, role labels, and resource accounting. This environmental
feedback is stigmergic within a running kernel process: later agents encounter the
shared field even when the model or agent identity changes. Consequence records can be
made restart-persistent with file-backed SQLite; the default MCP kernel and pheromone
field are process-local.

The Colony Control Plane comprises {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} cooperating
subsystems for pheromone storage, resource accounting, actuation gating, consequence
memory, role adaptation, pruning nomination, adversarial falsification, and lifecycle
coordination. A weighted gate combines budget headroom, local hazard pressure, earned
trust, and proposal completeness, subject to hard overrides; EXECUTE begins at
{{CONFIG_GATE_EXECUTE_THRESHOLD}}, while new agents remain confined to the `SANDBOX`
role until their recorded history satisfies the configured promotion contract. The
pruning daemon nominates stale or duplicate module locations for review but does not
remove them autonomously.
{{CONFIG_MCP_TOOL_COUNT}} Model Context Protocol tools expose this control plane to
external orchestrators without collapsing governance into execution.

Evaluation is deliberately bounded to implementation contracts and controlled fixtures.
At composition time, the colony-kernel surface contains {{RESULT_TEST_COUNT}} passing
tests with {{RESULT_COVERAGE_PCT}}% branch coverage, {{RESULT_RUFF_ERRORS}} Ruff errors,
and {{RESULT_TY_ERRORS}} ty diagnostics. A paired deterministic contract test shows
that a failed outcome lowers the next complete proposal at the same target from
EXECUTE to HOLD while leaving an unrelated target unchanged; a separate all-success
fixture reaches its first non-sandbox role after {{RESULT_PROPOSALS_TO_PROMOTION}} recorded outcomes. These results validate internal
mechanics, not production safety or ecological optimality. The paper therefore pairs
the implementation evidence with explicit falsification criteria, a fixed-input replay
artifact, and deployment limitations. Within that bounded surface, process-local
failure memory raises friction for repeated same-location proposals; external workloads,
outcome attestation, and restart-persistent field storage remain necessary to establish
generality. Numeric claims are injected from generated
artifacts so the rendered manuscript remains tied to the evaluated code and
configuration.

**Keywords:** {{CONFIG_KEYWORDS}}

*Corresponding author: {{CONFIG_FIRST_AUTHOR}}*
