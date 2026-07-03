# Abstract {#sec:abstract .unnumbered}

The central claim of this paper is bounded and testable: after a failed action,
matching future proposals should become measurably harder to pass under the
colony gate. Each rejected tool call, failed gate, or contradicted consequence
is written into a shared consequence memory that reshapes trust weights, role
assignments, and resource budgets for subsequent proposals. The mechanism that
produces this pressure is stigmergy: rather than maintaining ephemeral,
per-session agent state, the framework encodes learned caution directly into a
persistent pheromone field that survives model swaps, session boundaries, and
agent population changes. The colony does not converge toward a fixed policy;
it adapts its recorded pressure profile to the problem surface.

This paper presents **Codomyrmex** (v{{CONFIG_VERSION}}), an agentic software-development framework that instantiates this insight as a closed feedback loop governed by the Colony Control Plane. Agents accumulate consequence histories, receive deterministic role reassignment, and are constrained by recorded consequence; stale or duplicate module locations may be flagged for human-reviewed pruning under configured pressure signals.

The architectural centerpiece is the **Colony Control Plane**, comprising {{CONFIG_COLONY_KERNEL_SUBSYSTEMS}} subsystems: (1) *pheromone gradients* — ephemeral stigmergic signals implementing stigmergy (indirect coordination through environment-mediated signals, Grassé 1959) that bias agent attention toward high-yield paths without explicit coordination; (2) *resource budget* — per-agent and per-colony token, tool-call, and wall-time envelopes enforced before dispatch; (3) *actuation gate* — a weighted additive score with hard overrides ($\tau_{\text{gate}} = {{CONFIG_GATE_EXECUTE_THRESHOLD}}$) that blocks proposals lacking sufficient evidence mass; (4) *consequence memory* — a persistent, append-only ledger of action outcomes indexed by agent, role, and context hash; (5) *role adaptation* — deterministic reassignment of the {{CONFIG_ROLE_COUNT}} canonical roles (`SANDBOX`, `REPAIR_ANT`, `MEMORY_ANT`, `DISPATCHER`, `GUARD_ANT`) based on trust and proposal count; (6) *pruning daemon* — read-only nomination of stale, dormant, or duplicate module locations for human or `GUARD_ANT` review; (7) *falsification worker* — deterministic adversarial checks that attempt to invalidate a proposal before any gate decision is finalised; and (8) *ColonyKernel* — the hub class coordinating the other subsystems as a single re-entrant transaction.

These subsystems implement a closed feedback loop: environmental pressure
generates proposals; proposals pass (or are blocked by) the actuation gate;
surviving actions produce consequences; consequences are written to memory;
memory drives role reassignment; roles reshape the pressure distribution. The
loop repeats with a colony that is less vulnerable to repeated context-reset
and local-failure deception patterns because memory is retained and gate
thresholds tighten on repeated failure patterns. {{CONFIG_MCP_TOOL_COUNT}} MCP
tools expose the Control Plane to external orchestrators, and
{{CONFIG_SIGNAL_TYPES_COUNT}} typed inter-agent signal channels — `FAILURE`,
`SUCCESS`, `RISK`, `NEED`, `DEPENDENCY`, and `HUMAN_PRIORITY` — propagate state
changes without shared mutable state.

The framework ships {{CONFIG_MODULE_COUNT}} top-level submodules covering the colony kernel, MCP surface, agent lifecycle, signal bus, role engine, gate logic, consequence ledger, and CLI harness. The colony-kernel manuscript surface enforces the no-mock contract throughout: **{{RESULT_TEST_COUNT}} tests**, **{{RESULT_COVERAGE_PCT}}% branch coverage**, **{{RESULT_RUFF_ERRORS}} ruff errors**, and **{{RESULT_TY_ERRORS}} ty type errors** — all figures drawn from a single authoritative `pytest --cov --cov-branch` invocation at compose time. Behaviorally, deterministic contract tests confirm that the actuation gate rejects {{RESULT_GATE_REFUSAL_RATE}}% of low-evidence proposals in the controlled gate fixture, and the trust trajectory reaches its first non-sandbox role after {{RESULT_TRUST_CONVERGENCE_STEPS}} clean feedback cycles under the configured role ladder. Numeric claims in this manuscript are hydrated from generated artifacts at compose time so reviewer-sensitive figures remain tied to the artifact that produced them.

**Keywords:** {{CONFIG_KEYWORDS}}

*Corresponding author: {{CONFIG_FIRST_AUTHOR}}*
