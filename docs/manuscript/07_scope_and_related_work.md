# Scope, Related Work, and Claim Boundaries {#sec:scope}

{{CONFIG_PARAMETER_STATUS_NOTE}} This distinction is central to the scholarship: the
paper contributes an inspectable implementation and a falsifiable evaluation agenda,
not a claim that a hand-specified policy has already been calibrated or shown superior.

## Unit of Analysis

The unit of analysis in this paper is the Colony Kernel, not every subsystem distributed
with Codomyrmex. The broader repository includes agent, orchestration, model-integration,
identity, and other facilities. The claims made here concern the kernel path that combines
proposal data, budget state, pheromone readings, consequence-derived trust, role inference,
falsification findings, and a ternary gate decision.

This distinction matters for both novelty and evaluation. The Colony Kernel can be used as
a control-plane component, but the present artifact does not show that every Codomyrmex
action is mediated by it, that external clients cannot bypass it, or that a gate decision
is enforced by an operating-system or cloud authorization layer.

## Agentic Software Engineering {#sec:agentic-se}

SWE-bench evaluates model-generated patches against real repository issues, while
SWE-agent shows that the agent-computer interface materially shapes software-engineering
performance [@yang2024swebench; @yang2024sweagent]. These projects motivate evaluating a
control plane in the same environments where agents inspect files, run tools, and modify
persistent state. They do not provide evidence for the Colony Kernel until the kernel is
actually evaluated as part of such a workflow.

LangGraph, AutoGen, and CrewAI provide stateful graphs, conversational multi-agent
composition, and role-oriented orchestration, respectively [@langgraph2024;
@wu2023autogen; @crewai2024]. Their current designs include state or memory facilities,
so the Colony Kernel's positioning does not depend on claiming that other frameworks are
stateless or lack cross-session mechanisms. The narrower distinction is architectural:
the kernel exposes a deterministic proposal-evaluation path over explicit budget,
effective local hazard, trust, and completeness inputs. Whether that path improves outcomes when integrated with
another runtime is an empirical question, not a property established by juxtaposing
feature lists.

The Model Context Protocol supplies a standard tool-exposure interface
[@anthropic2024mcp]. The kernel's MCP tools make its operations callable by compatible
clients, but protocol exposure is not enforcement: a client or tool path that does not
invoke the gate is outside the protection claimed here.

## What the Colony Kernel Is—and Is Not {#sec:scope-not}

**A deterministic governance prototype.** The gate converts a specified kernel state and
proposal into EXECUTE, HOLD, or REFUSE. This makes the decision path inspectable and
testable.

**Not a complete agent runtime.** The kernel itself does not generate proposals, choose
models, execute arbitrary tools, or guarantee that a downstream runtime obeys its verdict.
Other Codomyrmex packages may provide adjacent capabilities, but they are not evidence for
the kernel claims in this paper.

**Process-lifetime by default.** The MCP module owns a single kernel instance within one
process. Consequence memory defaults to SQLite in-memory mode, and the pheromone field is
in memory. A caller can choose a file-backed database for consequence records; the default
does not provide cross-session persistence, and file-backed consequence records do not
by themselves persist the whole kernel or pheromone field.

**Not a per-role authorization system.** RoleAdapter infers labels from trust and proposal
count, and SANDBOX is a hard gate condition. The other role labels do not currently
define or enforce an action-by-role permission matrix.

**Not a security boundary.** Trust scores are mutable state associated with caller-supplied
agent identifiers, not unforgeable capability tokens. The default compatibility outcome
path remains caller-reported. An opt-in `AttestationLedger` can authenticate lifecycle
linkage and required-attestation mode can reject outcomes without a prior authorization
and receipt, but the ledger does not prove that an external observer saw a safe or useful
action and is not automatically enabled for every interface.

**Not production- or scale-validated.** The checked-in tests exercise internal contracts.
The manuscript does not release the repeated-trial traces, production replays, concurrent
load results, or external benchmark runs needed for effectiveness or scaling claims.

**Not an integrated Active Inference implementation.** The core kernel remains
deterministic and has no posterior or expected-free-energy policy optimizer. A separate,
explicit probabilistic adapter now declares states, observations, likelihoods, priors,
transitions, preferences, horizon, and seed for offline research; its presence does not
turn gate scores into probabilities or connect that model to production actuation. The
comparison in [@sec:active-inference] remains a design crosswalk.

## Stigmergy and Environmental Traces

Grassé introduced stigmergy to describe coordination mediated by changes to a shared
environment [@grasse1959reconstruction]. Digital-pheromone systems later adapted this
idea to software-agent coordination [@parunak1997pheromones], while ant-colony
optimization formalized reinforcement and evaporation for search
[@dorigo2004ant]. The Colony Kernel borrows the environmental-trace idea; it does not
implement an ant-colony optimization algorithm.

The TraceField stores strengths under compound location and signal-type keys. Evaporation
occurs only when the kernel is explicitly ticked, subtracting a configured amount and
deleting depleted markers. This is a deterministic, discrete-time store rather than a
continuous diffusion field. Its coordination scope is also bounded by process lifetime in
the default MCP configuration.

Signal types must not be conflated. A failed outcome deposits FAILURE and changes the
responsible agent's consequence history; prospective checks may deposit RISK. The gate
retains these raw readings for diagnosis and uses their maximum as effective local
hazard. Thus a reported failure can tighten a later same-target decision without being
silently relabeled as RISK. This coupling is process-local and only as trustworthy as the
unattested report that created the FAILURE signal.

## Computational Trust and Role Labels

Computational-trust research treats trust as contextual, evidence-dependent, and distinct
from simple identity [@marsh1994trust; @sabater2005review]. FIRE combines direct
interaction with witness, role-based, and certified evidence [@huynh2006fire]. These
sources provide comparison points, not validation of the Colony Kernel's scalar score.

The current kernel uses fixed outcome deltas and clamps the resulting score to a bounded
range. It does not estimate a calibrated probability of competence, benevolence,
integrity, or future safety. It also does not import witness reputation or certified
credentials into the trust update. Two agents with the same score but different sample
sizes can therefore receive the same trust tier, and an outcome record has meaning only
to the extent that the caller and record are trustworthy.

Role inference is deterministic categorization over this heuristic history. The labels
may be useful for routing, explanation, or future policy definition, but only implemented
gate conditions have authorization effect. Calling the labels a permission ladder would
overstate the artifact until each action class is checked against an explicit policy.

## Security Boundary {#sec:capability-security}

Capability security requires authority that cannot be obtained merely by naming another
principal, while least privilege requires each component to receive only the authority it
needs [@miller2003capabilities; @saltzer1975protection]. A scalar trust score indexed by
agent identifier is not such a capability. The gate may contribute evidence to a broader
authorization decision, but it must be paired with authenticated identities,
non-bypassable mediation, sandboxing, constrained credentials, and downstream policy
enforcement.

NIST Zero Trust Architecture likewise requires a broader resource-centric control system,
including policy decision and enforcement points, identity and device evidence, and
continuous evaluation [@nist2020zerotrust]. The Colony Kernel is compatible with the
general practice of reevaluating proposed actions, but it is not an implementation or
certification of NIST SP 800-207.

### Threat-informed evaluation {#sec:advanced-threat-security}

Tool-using agents can be redirected by untrusted content, can misuse available tools, and
can fail in high-impact simulated environments. AgentDojo and InjecAgent operationalize
prompt-injection attacks against tool-integrated agents, and ToolEmu evaluates risks in
high-stakes tool use [@debenedetti2024agentdojo; @zhan2024injecagent;
@ruan2023toolemu]. These are appropriate future falsification workloads. They have not
been run in this manuscript, so they should not be cited as evidence that the gate reduces
attack success.

Runtime-assurance work provides another useful comparison. Simplex architectures
interpose a decision mechanism capable of switching from an advanced controller to a
verified-safe baseline [@seto1998simplex]. The Colony Kernel also interposes a decision,
but it has no verified fallback controller or formal safety invariant. The comparison
identifies an engineering direction rather than an inherited guarantee.

| Evaluation question | Suitable evidence | Status in this paper |
|:---|:---|:---|
| Does the gate improve repository-task outcomes? | Controlled SWE-bench or SWE-agent integration with a baseline | Not run |
| Does it reduce unsafe tool use under indirect injection? | AgentDojo or InjecAgent attack-success comparison | Not run |
| Does it reduce high-impact tool failures? | ToolEmu scenarios with linked proposal, verdict, and outcome traces | Not run |
| Can clients bypass or forge control state? | Authenticated end-to-end adversarial tests | Not run |
| Does state survive restart and concurrent access? | Persistence and concurrency tests under a declared deployment configuration | Not established for the default MCP service |
| Are HOLD and REFUSE calibrated to downstream harm? | Held-out outcomes with calibration and utility analysis | Not evaluated |

: External validation agenda; every row is future work rather than a reported benchmark. {#tbl:external-validation-agenda}

[@tbl:external-validation-agenda] states the minimum comparisons needed before making
effectiveness or deployment claims.

## Active Inference and Free Energy

Friston's Free Energy Principle [@friston2010free] frames intelligent behavior as
minimization of variational free energy—the gap between an agent's generative model and
its sensory observations. A full mapping of the Colony Kernel onto this framework would
require an explicit generative model over observations and hidden states, an implemented
posterior approximation, and policy selection under expected free energy
[@friston2017active].

[@sec:active-inference] develops this analogy explicitly by proposing a generative-model
interpretation of colony observations, hidden states, and policy selection. That treatment
is a conceptual reconstruction of the implemented heuristics, not evidence that the
current kernel performs variational Bayesian inference or minimizes canonical expected
free energy. High failure pheromone concentrations can be read as coarse, persistent
prediction-error signals, but the mapping remains an engineering interpretation rather
than a proof of formal equivalence.

## Explicit Limitations and Future Work

The benchmark protocol in [@sec:experimental_setup] remains unexecuted as a repeated
comparative study. Configured agent counts, scenarios, and expected rates are protocol
parameters or analytical fixtures, not observations. A publication-quality experiment
requires released traces, explicit baselines, linked proposal-to-outcome records,
predeclared outcomes, and an analysis appropriate to ternary gate decisions.

The current system is synchronous and single-process by default. It has no demonstrated
throughput envelope, distributed consistency model, or merge protocol for independent
pheromone fields and trust histories. File-backed consequence storage can be evaluated as
one deployment option, but it should not be described as persistence of the complete
control plane.

The gate weights, trust deltas, role thresholds, decay amounts, and falsification checks
are hand-authored heuristics. They are auditable, but auditability is not calibration.
Future learning or optimization should predict downstream repair, harm, or policy
violation on held-out data; fitting a model to reproduce the existing EXECUTE/HOLD/REFUSE
labels would merely imitate the current rule.

Adjacent wallet, HMAC challenge-response, physiological-signal, persona, and spatial
world-model modules are outside the evaluated gate path. This paper makes no
zero-knowledge, wallet-ownership, coercion-detection, physiological-authentication, or
trajectory-aware gating claim on their behalf.

The resulting position is deliberately modest. The Colony Kernel is an inspectable
software experiment in consequence-aware gating. Its deterministic contracts are
testable now. Persistence across sessions, enforceable role authority, resistance to
adversarial clients, and improved safety on realistic workloads remain implementation
and evaluation targets. The relevant comparison with prior work is therefore at the
level of control-plane decomposition and measurement design; it should not be read as
an empirical comparison with the cited systems.
