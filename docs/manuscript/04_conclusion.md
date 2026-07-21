# Conclusion {#sec:conclusion}

This paper presents the Colony Kernel as a deterministic, inspectable prototype for
placing a control decision between an agent's proposal and software actuation. Within
the kernel evaluation path, a proposal is considered alongside budget headroom, local
hazard pressure, consequence-derived trust, proposal completeness, the agent's inferred
role label, recent failures, and falsification findings. The result is an explicit
EXECUTE, HOLD, or REFUSE decision rather than an implicit assumption that possession of
a tool implies permission to use it.

The implementation evidence supports a bounded claim. The checked-in tests exercise the
kernel's data models, gate arithmetic, consequence updates, pheromone operations, role
inference, and MCP-facing tools. These tests establish deterministic software contracts
for the cases they cover. They do not establish production safety, robustness at scale,
resistance to a strategic adversary, or improved task performance relative to another
agent runtime.

{{CONFIG_PARAMETER_STATUS_NOTE}} The current figures and fixtures should therefore be
changed only through a declared tuning or calibration protocol with regenerated tests,
tables, figures, and provenance—not silently treated as universal constants.

Several boundaries are especially important. The default MCP server owns one kernel
instance for the lifetime of its process. Its consequence database defaults to SQLite
in-memory mode, and its pheromone field is also in memory. A caller may configure a
file-backed SQLite path for consequence records, but that does not persist the complete
kernel state or the pheromone field. The present artifact therefore does not support a
claim that local pressure, trust, or gate state automatically survives process restarts,
model swaps, or deployment across machines.

The role ladder is similarly narrower than an authorization hierarchy. RoleAdapter
deterministically maps trust and proposal-count state to labels, and SANDBOX receives a
hard gate override. The remaining role names do not currently carry an action-specific
permission matrix. They describe inferred operating status; they are not cryptographic
capabilities or independently enforced privilege scopes.

The FAILURE and RISK channels remain distinct in storage, but they are now coupled at
the gate: local hazard is the maximum of the two sensed pressures. The paired contract
test records a failed outcome, observes the resulting FAILURE pressure, and changes a
complete same-target proposal from EXECUTE to HOLD while leaving an unrelated target
unchanged. Passive tick decay later restores the original decision. This verifies a
process-local locality invariant. It does not verify the truth of the outcome report:
the MCP outcome endpoint still accepts caller-supplied data without binding it to a
prior EXECUTE authorization or independently observed actuation.

## Falsification Criteria and Evaluation Agenda {#sec:falsification-criteria}

The architecture should be judged by tests that can fail, not by the biological metaphor.
The following criteria separate contracts already exercised by the repository from
claims that still require implementation or empirical evaluation.

### F1: Failure-to-gate coupling

The checked-in paired test submits identical proposals under identical agent, budget,
completeness, and falsification state, varying only whether the target location has a
reported failed outcome. The failed-location proposal receives a strictly lower score
and a stricter decision; an unrelated location does not. The remaining falsification
criterion is end-to-end attestation: the same result must hold when FAILURE can only be
created from a prior authorized action and an independently observed adverse outcome.

### F2: Deterministic gate evaluation

Two evaluations with the same complete kernel state and proposal must produce the same
score, decision, and stated reasons. Complete state includes the inferred role, budget,
effective local hazard, trust tier, completeness tier, recent-failure count, and any CRITICAL
finding. This is a software determinism criterion; it is not a claim that the resulting
decision is calibrated to real-world harm.

### F3: Bounded trust updates

For clean outcomes and zero human feedback, trust should increase by the configured pass
delta while the score remains below its upper clamp. At the boundary, the clamp must be
included in the expected result. The analogous checks apply to failed tests, repair
requirements, and negative feedback. Passing these checks establishes arithmetic
consistency, not that the heuristic deltas are statistically optimal.

### F4: Role-label determinism and authorization separation

At each documented trust and proposal-count boundary, RoleAdapter should return the
specified label. A separate negative test should confirm the current limit: beyond the
SANDBOX override and other gate conditions, non-sandbox role labels alone do not enforce
which action types an agent may perform. Any future per-role permission claim requires a
policy matrix and action-level enforcement tests.

### F5: Adversarial and restart behavior

An external evaluation should test unlinked outcome submission, agent-identifier reuse,
semantically empty completeness fields, process restart, concurrent clients, budget-window
timing, and poisoning of shared state. These cases probe assumptions that deterministic
unit tests cannot settle.

| Question | Evidence in this artifact | Publication-honest status |
|:---|:---|:---|
| Is gate arithmetic deterministic for covered fixtures? | Checked-in unit and contract tests | Supported within the tested state space |
| Does reported FAILURE tighten same-target local gating? | Paired contract test over `max(RISK, FAILURE)` | Supported within one kernel process |
| Do role labels enforce per-action permissions? | SANDBOX override; no general role/action matrix | Not implemented |
| Does colony state survive a default MCP process restart? | In-memory default database and field | No |
| Does the kernel reduce unsafe actuation on external workloads? | Proposed protocol; no released trial traces | Not yet evaluated |
| Does the kernel remain correct under production concurrency or scale? | Single-process implementation and local tests | Unverified |

: Evidence boundary and falsification agenda; external benchmark rows are future work, not reported experiments. {#tbl:falsification-benchmarks}

[@tbl:falsification-benchmarks] keeps implemented contracts separate from open external
claims.

## Limitations and Next Work

The experimental protocol in [@sec:experimental_setup] is a specification for future
evaluation. The repository does not currently provide the raw repeated-trial traces,
baseline runs, or external workload results needed to estimate refusal rates, repair
rates, latency, or safety benefit. Consequently, configured scenario counts and expected
rates should not be read as measured outcomes.

The gate weights, trust deltas, decay amounts, role thresholds, and falsification checks
are fixed engineering heuristics. They have not been calibrated against downstream harm
or production repair cost. The falsification worker is also a deterministic proposal
checker, not a proof of semantic safety: only CRITICAL findings independently force a
gate refusal, and syntactically complete but misleading evidence may evade its checks.

Four implementation priorities follow directly from these limits. First, bind outcome
records to prior EXECUTE authorizations, observed effects, and authenticated agent
identities. Second, persist and reconcile the entire field and budget state when
cross-session behavior is required. Third, define and enforce
an action-by-role authorization policy if role names are to carry security meaning.
Fourth, run the proposed paired and external benchmarks with released traces, explicit
baselines, and predeclared outcome measures before making effectiveness or scale claims.

The Colony Kernel's present contribution is thus a testable control-plane scaffold. It
makes selected state transitions and decision rules visible enough to inspect, replay
within a process, and challenge. That is useful groundwork, but it is not yet evidence
that the colony becomes safer merely by accumulating history. In this version, the
record is evidence for a control decision—not a guarantee that the decision is correct.
