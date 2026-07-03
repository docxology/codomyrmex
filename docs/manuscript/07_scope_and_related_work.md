# Scope, Related Work, and Positioning {#sec:scope}

## Agentic Software Engineering {#sec:agentic-se}

The emergence of LLM-based software agents has produced a wave of frameworks and benchmarks for orchestrating tool-using models in engineering contexts. SWE-bench [@yang2024swebench] established the first systematic evaluation of agent-generated patches against real GitHub issues, revealing that even strong models fail on the majority of tasks when operating without structured oversight. SWE-agent [@yang2024sweagent] showed that agent-computer interface design can substantially change autonomous software-engineering performance, making the interface itself part of the agent system under evaluation. LangGraph [@langgraph2024] provides a graph-based state machine for multi-step agent pipelines, and AutoGen [@wu2023autogen] enables conversational multi-agent workflows where agents negotiate task decomposition through natural language. CrewAI [@crewai2024] extends this model with role-based agent teams, pre-defined workflows, and hierarchical task delegation. These frameworks excel at composing individual agent turns but lack a persistent, inspectable control plane: there is no first-class concept of trust accumulation, no cross-session consequence memory, and no signal-based coordination between concurrent agents.

Crucially, none of LangGraph, AutoGen, or CrewAI implement a pre-actuation falsification gate. In all three systems, an agent that has been granted a tool invocation right may exercise it on any proposal that passes syntactic validation — there is no mechanism for asking "has this agent's consequence history justified this class of action?" before execution proceeds. The ActuationGate addresses exactly this gap: every destructive proposal is evaluated against four measurable dimensions (budget, risk, trust, completeness) weighted 0.30 / 0.30 / 0.25 / 0.15, and only proposals that clear the composite threshold — calibrated against the agent's accumulated trust trajectory — proceed to execution. This falsification-before-actuation discipline is structurally absent from runtime-centric frameworks because those frameworks have no persistent consequence memory from which to compute a justified threshold.

Codomyrmex occupies precisely this gap. It is not a competing agent runtime — it is the missing control plane layer that sits above runtimes such as LangGraph and AutoGen. Where those frameworks answer "how do I route messages between agents?", Codomyrmex answers "which agents have earned the right to execute destructive actions, what have previous actuations cost, and where in the codebase is failure pheromone currently elevated?" The ActuationGate, TraceField, and consequence memory together constitute a governance substrate that any MCP-compatible runtime can query and respect.

## What Codomyrmex Is Not {#sec:scope-not}

Explicit scope statements prevent mischaracterization of the contribution. The following are deliberate exclusions, not implementation gaps.

**Not a general-purpose agent framework.** Codomyrmex does not implement agent execution, message routing, tool dispatch, or task decomposition. It is a governance and coordination layer. Researchers seeking a full agent runtime should use LangGraph [@langgraph2024], AutoGen [@wu2023autogen], or CrewAI [@crewai2024] and optionally layer Codomyrmex above them for trust-gated actuation control.

**Not a replacement for LLM APIs.** Codomyrmex does not wrap or abstract LLM inference. It has no opinion on which model generates proposals — only on whether those proposals, once generated, meet the evidentiary standard required for destructive actuation. Model selection, prompt engineering, and inference costs remain entirely outside the system boundary.

**Not evaluated on production workloads.** The results in [@sec:results] are derived from deterministic contract tests and a configured experimental protocol with 5 agents, 10 adversarial falsification vectors, and a fixed scenario corpus. No claims are made about behavior under real-world traffic patterns, adversarial users with persistent access, or multi-tenant deployments. The actuation gate has been validated against the checked-in contract surface; extrapolation to production workloads requires independent evaluation and is an identified future direction.

**Not a security boundary.** The ActuationGate is a governance mechanism grounded in consequence history, not a cryptographic access-control system. A sufficiently persistent agent that accumulates enough positive interactions can eventually earn destructive access. The system is designed to make this process transparent and auditable, not to prevent it. Readers seeking cryptographic capability confinement should treat the ActuationGate as complementary to, not a replacement for, OS-level sandboxing, network egress controls, capability-based security substrates, and threat-informed controls such as those discussed in [@sec:capability-security; @sec:advanced-threat-security].

**Not a distributed system.** The current implementation uses a single-process SQLite backend. Multi-repository colony state, shared pheromone fields across machines, and distributed consensus for trust scores are all out of scope for this paper.

## Stigmergy and Self-Organizing Systems

Grassé's original term [@grasse1959reconstruction] described how ants coordinate without central control — work done by one individual modifies the environment in a way that stimulates further work. Parunak's foundational work on digital pheromones [@parunak1997pheromones] showed that synthetic stigmergy could govern distributed software agents without central coordination, and Dorigo & Stützle's comprehensive treatment of Ant Colony Optimization [@dorigo2004aco] established the computational theory underlying pheromone-guided search: decay rates, evaporation schedules, and reinforcement dynamics that balance exploitation of known-good paths against exploration of alternatives. These are the direct computational ancestors of the TraceField and ColonySignal design.

The Colony Kernel implements digital stigmergy via TraceField pheromone deposits keyed by (location, signal_type). Unlike biological systems where signals are continuous diffusion fields, the Colony Kernel uses discrete strength values with configurable exponential decay — more predictable, less emergent, but verifiable. The decay schedule borrows directly from Dorigo's evaporation parameter: deposits weaken each tick, preventing stale success signals from permanently masking accumulated failure signals.

## Multi-Agent Systems and Trust

Classical MAS literature (Wooldridge & Jennings [@wooldridge1995intelligent]) distinguished between architectures but seldom addressed how trust accumulates over time in an operative sense. The foundational conceptual work comes from Marsh's formalization of computational trust [@marsh1994trust], which decomposed trust into competence, benevolence, and integrity dimensions — a tripartite structure that maps directly onto the Colony Kernel's consequence memory: competence is approximated by the action success rate, integrity by the human_feedback multiplier, and benevolence by the pattern of proactive vs. reactive failure responses.

For agents with unknown histories — which is the common case for newly provisioned LLM agents — bootstrapping trust is a distinct problem from updating trust given evidence. The FIRE model [@huynh2006fire] addresses this through interaction, witness, role-based, and certified trust components, providing mechanisms to derive initial trust estimates from indirect evidence when direct interaction history is sparse. Burnett et al. [@burnett2013bootstrapping] extend this to agents operating across heterogeneous environments, showing that referral networks can seed trust scores before any direct observation. In the Colony Kernel, this bootstrapping problem is currently handled conservatively: new agents begin below the actuation threshold and must accumulate direct consequence history before the gate opens. Integrating FIRE-style indirect evidence propagation is an identified future extension.

Sabater & Sierra's survey [@sabater2005review] of trust and reputation systems provides the conceptual grounding for trust_score computation from consequence history, situating the Colony Kernel's approach within the broader trajectory from purely social reputation systems toward hybrid models that combine direct experience with structural context.

## Model Context Protocol
The MCP specification [@anthropic2024mcp] defines a JSON-RPC protocol for tool exposure. Codomyrmex exposes all Colony Kernel subsystems as MCP tools, meaning the gate can be queried and the pheromone field inspected from any MCP-compatible LLM client. This integration is in-scope; MCP server deployment and transport configuration are out of scope.

## Reinforcement Learning, Constitutional AI, and Consequence Memory

Sutton & Barto [@sutton2018reinforcement] formalize the reward-feedback loop that consequence memory approximates. The Colony Kernel does not implement policy gradients — trust_delta is a hand-crafted heuristic (success → +{{CONFIG_TRUST_DELTA_PASS}}, failure → {{CONFIG_TRUST_DELTA_FAIL}}, human_feedback multiplier) rather than a learned policy. Connecting consequence memory to a proper RL policy optimizer is explicitly deferred.

Two more recent lines of work sharpen the relationship between consequence memory and learned alignment mechanisms. Constitutional AI (CAI) [@bai2022constitutional] and RLHF [@christiano2017deep] train models to internalize normative constraints through a reward signal derived from human preference feedback. The Colony Kernel's trust score dynamics are structurally analogous: the human_feedback multiplier in the trust update formula plays the role of a preference signal, and the accumulation of consequence records over time resembles the dataset that reward modeling optimizes against. The key difference is that CAI/RLHF modify the underlying model weights — their alignment signal is baked into the parameters. The Colony Kernel leaves model weights unchanged and instead maintains an external, auditable consequence ledger that gates actuation at inference time. This makes the governance layer model-agnostic and revocable: a trust score can be reset, audited, or overridden by a human operator without touching the model. Whether external consequence memory or internalized reward modeling produces more robust alignment under adversarial conditions is an open empirical question.

**The actuation gate as a process reward model.** Process reward models (PRMs) [@lightman2023let; @uesato2022solving] assign scalar scores to intermediate reasoning steps rather than only to final outputs, enabling fine-grained feedback during multi-step problem solving. The ActuationGate is functionally a process reward model applied to agent action proposals: it scores proposals along four dimensions (budget, risk, trust, completeness) weighted 0.30 / 0.30 / 0.25 / 0.15, producing a composite score that determines whether execution proceeds. Unlike learned PRMs trained on human annotations, the ActuationGate's scoring function is hand-crafted and deterministic. But the architectural pattern is the same — a step-level evaluator interposed between proposal generation and execution. This connection suggests a concrete upgrade path: replacing the hand-crafted scoring function with a learned PRM trained on accumulated consequence logs, inheriting the PRM literature's training and calibration methodology while retaining the Colony Kernel's external, auditable governance structure. This integration is an identified future direction.

## Capability-Based Security and Least Authority {#sec:capability-security}

The ActuationGate instantiates a well-established security architecture that deserves explicit acknowledgment. Miller's capability-based security model [@miller2003capabilities] argues that access rights should be unforgeable tokens carried by callers, not checked against ambient authority tables — a shift from identity-based ("who are you?") to capability-based ("what do you hold?") authorization. Saltzer and Schroeder's Principle of Least Authority (POLA) [@saltzer1975protection] states that every component should operate with the minimum set of privileges needed to accomplish its task, and authority should be granted incrementally as need is demonstrated.

The ActuationGate enforces both principles. Trust tokens are earned through consequence history rather than conferred by identity: an agent's trust_score is an unforgeable capability accumulated from verifiable past interactions, not a static credential that can be spoofed. Destructive tools require a trust_score above a configurable threshold — authority is granted incrementally as the agent's consequence record justifies it. This is POLA applied to the agentic context: LLM agents begin with read-only access and graduate toward write and execute authority only as their consequence memory warrants. Security venues reviewing this work should recognize the ActuationGate as a concrete instantiation of least-authority principles, extended to cover the distinct challenge of agents whose competence distribution is unknown at provisioning time.

## Advanced Threat Models, Zero Trust, and Supply-Chain Integrity {#sec:advanced-threat-security}

A RedTeam and nation-state reading sharpens rather than weakens the scope boundary. NIST Zero Trust Architecture defines a resource-centric posture in which no network location, caller identity, or previous interaction is sufficient for implicit trust [@nist2020zerotrust]. Codomyrmex is compatible with that posture because every proposed destructive action is re-evaluated against budget, risk, trust, and completeness before actuation. It is not, however, a complete zero-trust architecture: it does not supply enterprise identity proofing, device posture, network segmentation, policy decision points for every resource, or continuous detection across an operating environment.

The same distinction applies to secure development and supply-chain integrity. NIST SSDF describes practices for reducing software-vulnerability risk throughout development [@nist2022ssdf]. SLSA v1.2 defines levels and tracks for software supply-chain integrity and provenance [@slsa2026], while Sigstore provides a public-good signing and transparency-log system for verifying software artifacts [@newman2022sigstore]. The Codomyrmex manuscript pipeline records configuration hashes, generated variables, rendered artifacts, and quality gates, so it can participate in a provenance-aware workflow. That evidence does not claim SLSA certification, complete SBOM coverage, or resistance to a compromised builder, dependency, package registry, signing key, or continuous-integration identity.

Threat-informed defense frameworks make the remaining gap explicit. MITRE ATT&CK is a knowledge base of adversary tactics and techniques based on real-world observations [@mitre2026attack], and MITRE ATLAS extends this style of knowledge base to adversarial activity against AI-enabled systems [@mitre2026atlas]. OWASP's LLM and agentic-AI guidance names prompt injection, insecure output handling, supply-chain vulnerabilities, excessive agency, tool misuse, identity and privilege abuse, memory or context poisoning, insecure inter-agent communication, cascading failures, and rogue-agent behavior as relevant risk classes [@owasp2025llm; @owasp2026agentic; @owasp2026agentsecurity]. Codomyrmex directly addresses only part of that space: it can make destructive actuation depend on earned consequence history, falsification pressure, and auditable gate decisions. It does not solve prompt injection, exfiltration, sandbox escape, model poisoning, compromised credentials, malicious dependencies, or post-compromise lateral movement by itself.

[@tbl:threat-informed-security] summarizes the threat-informed security framing used in this paper.

| Threat lens | Primary sources | Codomyrmex relevance | Boundary |
|:---|:---|:---|:---|
| Zero-trust authorization | NIST SP 800-207 [@nist2020zerotrust] and NIST agent identity work [@nist2026agentidentity] | Treats each destructive proposal as a fresh authorization question | Not an enterprise zero-trust architecture or identity system |
| Secure development | NIST SSDF [@nist2022ssdf] | Keeps verifier-first manuscript, code, and artifact checks auditable | Not a formal SSDF compliance assessment |
| Supply-chain provenance | SLSA [@slsa2026] and Sigstore [@newman2022sigstore] | Makes manuscript and package claims easier to bind to generated evidence | Does not claim SLSA certification, SBOM completeness, or signed-release enforcement |
| AI risk management | NIST AI RMF [@tabassi2023airmf] and the NIST Generative AI Profile [@autio2024genairmf] | Treats the gate ledger as evidence for Govern, Map, Measure, and Manage activities | Not an AI risk-management framework implementation or organizational governance program |
| AI and agentic threats | MITRE ATT&CK [@mitre2026attack], MITRE ATLAS [@mitre2026atlas], and OWASP LLM/Agentic guidance [@owasp2025llm; @owasp2026agentic; @owasp2026agentsecurity] | Gives RedTeam vectors for prompt, tool, memory, identity, and supply-chain abuse | Does not claim exhaustive ATT&CK/ATLAS coverage or production adversarial validation |

: Threat-informed security framing for Codomyrmex. {#tbl:threat-informed-security}

AI risk-management standards add an organizational lens to the same boundary. NIST AI RMF organizes risk work around Govern, Map, Measure, and Manage functions, while the Generative AI Profile adapts those functions to generative-AI risks and lifecycle evidence [@tabassi2023airmf; @autio2024genairmf]. Codomyrmex can supply auditable Measure/Manage artifacts: gate decisions, trust deltas, local pressure, falsification outcomes, and rendered reproducibility records. It does not supply the surrounding governance system: policy ownership, risk tolerance, impact assessment, user redress, model lifecycle controls, vendor management, or enterprise accountability. The contribution is therefore evidence-producing infrastructure for a future AI risk-management process, not certification against one.

The agentic-security scholarship supplies a second, more empirical pressure test for the same boundary. Indirect prompt-injection work shows that untrusted retrieved content can steer LLM-integrated applications and tool calls [@greshake2023indirectprompt]. InjecAgent and AgentDojo turn that risk into benchmarkable tool-integrated scenarios where agents must preserve utility while resisting adversarial instructions embedded in external data [@zhan2024injecagent; @debenedetti2024agentdojo]. ToolEmu demonstrates that high-stakes tool interactions can fail even in sandboxed evaluation [@ruan2023toolemu], while Agent-SafetyBench, Agent Security Bench, RAS-Eval, and SafeToolBench broaden the evaluation surface across safety failures, attacks, defenses, tools, and real-world-style environments [@zhang2024agentsafetybench; @zhang2024asb; @fu2025raseval; @xia2025safetoolbench]. PrivacyLens adds an action-level privacy lens: models can answer privacy questions correctly yet still leak sensitive information when executing agent trajectories [@shao2024privacylens]. Memory-poisoning and AgentAuditor work sharpen the temporal part of the Codomyrmex thesis: memory can preserve adversarial influence, but structured experiential memory can also improve safety evaluation when it is audited and retrieved deliberately [@dash2026memorypoisoning; @luo2025agentauditor]. Finally, tool-permission attack studies warn that agents may treat tool availability as implied permission unless an external policy layer blocks that inference [@lupinacci2025darkside].

[@tbl:agent-security-scholarship] maps these papers to the part of the control-plane claim they support.

| Scholarship lens | Representative sources | Claim pressure on Codomyrmex | Boundary |
|:---|:---|:---|:---|
| Indirect prompt injection | Greshake et al. [@greshake2023indirectprompt], InjecAgent [@zhan2024injecagent], AgentDojo [@debenedetti2024agentdojo] | Tool calls must not inherit authority from retrieved or user-supplied text | The manuscript does not claim prompt-injection immunity |
| High-stakes tool failure | ToolEmu [@ruan2023toolemu] and tool-permission attacks [@lupinacci2025darkside] | Tool availability does not imply permission; destructive actions need external gating | The ActuationGate is not a sandbox or downstream authorization system |
| Security benchmark coverage | Agent-SafetyBench [@zhang2024agentsafetybench], ASB [@zhang2024asb], RAS-Eval [@fu2025raseval], SafeToolBench [@xia2025safetoolbench] | A credible control plane should be evaluated against safety, attack, defense, and tool-use benchmark suites | Codomyrmex has not yet been run against these external benchmarks |
| Privacy leakage through action | PrivacyLens [@shao2024privacylens] | Treat disclosure, forwarding, and cross-context sharing as actuation harms, not just text-generation harms | The current falsification vectors do not include privacy-norm trajectory benchmarks |
| Memory as attack surface and evaluator | Memory poisoning [@dash2026memorypoisoning] and AgentAuditor [@luo2025agentauditor] | Persistent history can both carry adversarial residue and improve future safety judgments | Consequence memory must itself be audited; persistence is not automatically trustworthy |

: Agentic-security scholarship that motivates future Codomyrmex evaluation. {#tbl:agent-security-scholarship}

This table is intentionally framed as a falsification agenda, not as validation already achieved. The current results show that Codomyrmex is internally contract-tested against its checked-in falsification vectors and manuscript invariants. They do not show that Codomyrmex reduces attack success on AgentDojo, InjecAgent, ToolEmu, Agent-SafetyBench, ASB, RAS-Eval, SafeToolBench, PrivacyLens, or memory-poisoning benchmarks. A future external evaluation should treat those benchmarks as adversarial workloads: the control plane succeeds only if failed tool proposals produce durable consequence records, lower future trust, raise local pressure, and measurably reduce later unsafe actuation attempts under comparable tasks.

The assurance and agent-evaluation literature adds a third pressure test: evidence must be useful enough to support a structured safety argument, and benchmark tasks must resemble the workflows in which agents will actually operate. Agentic-governance guidance names task suitability, constrained action spaces, approval, legibility, monitoring, attribution, interruptibility, and maintained human control as baseline practices for agentic systems [@shavit2023governing]. AI-control work studies programming-task protocols under intentionally subversive untrusted models, making explicit the difference between a helpful assistant and a model that may strategically evade monitoring [@greenblatt2023aicontrol]. Safety-case work for frontier AI and AMLAS both frame safety as a structured claim supported by explicit evidence in a defined operational context [@buhl2024safetycases; @hawkins2021amlas]. These sources support the manuscript's evidence discipline: consequence records, gate decisions, rendered variables, and reproducibility certificates should be treated as ingredients for an assurance case, not as a substitute for one.

Realistic agent benchmarks sharpen the same requirement from the evaluation side. AgentBench, WebArena, OSWorld, GAIA, AppWorld, TheAgentCompany, and benchmark-mutation work on SWE-bench all move evaluation away from isolated prompt-answer tasks and toward long-horizon, tool-rich, state-changing environments [@liu2023agentbench; @zhou2023webarena; @xie2024osworld; @mialon2023gaia; @trivedi2024appworld; @xu2024theagentcompany; @garg2025savingswebench]. Their lesson for Codomyrmex is conservative: internal contract tests can prove that the control plane enforces its own invariants, but they cannot prove that earned actuation lowers real-world unsafe action rates. [@tbl:assurance_benchmark_agenda] therefore extends the falsification agenda from security attacks to assurance and workflow realism.

| Scholarship lens | Representative sources | Claim pressure on Codomyrmex | Boundary |
|:---|:---|:---|:---|
| Agentic governance | Shavit et al. [@shavit2023governing] | Constrain action space, keep activity legible, monitor automatically, preserve interruptibility | Codomyrmex is not a full organizational AI-management system |
| AI control | Greenblatt et al. [@greenblatt2023aicontrol] | Treat powerful model assistance as potentially untrusted and evaluate oversight under strategic subversion | Current tests do not model collusion, sabotage, or deceptive alignment |
| Assurance cases | Buhl et al. [@buhl2024safetycases] and AMLAS [@hawkins2021amlas] | Bind safety claims to explicit evidence, operational context, and revision when evidence changes | The manuscript does not present a certified safety case |
| Software-agent interfaces | SWE-agent [@yang2024sweagent] and SWE-bench mutation [@garg2025savingswebench] | Evaluate coding agents through realistic repository interaction, interface design, and user-query distributions | Codomyrmex has not yet been evaluated as a SWE-agent or mutated SWE-bench policy layer |
| Long-horizon tool environments | AgentBench [@liu2023agentbench], WebArena [@zhou2023webarena], OSWorld [@xie2024osworld], GAIA [@mialon2023gaia], AppWorld [@trivedi2024appworld], and TheAgentCompany [@xu2024theagentcompany] | Require control-plane evaluation where actions change persistent external state across tools, apps, files, and workflows | Internal deterministic fixtures are not substitutes for external environment benchmarks |

: Assurance and benchmark scholarship that extends the Codomyrmex falsification agenda. {#tbl:assurance_benchmark_agenda}

Runtime-assurance, provenance, and visibility scholarship makes the engineering obligation sharper still. The Simplex line of work allows an advanced, high-performance controller to operate only while a decision module can switch to a verified-safe baseline when safety is threatened [@seto1998simplex; @phan2017componentbased; @mehmood2021blackboxsimplex]. Shielding work applies a similar idea to reinforcement learning by interposing a monitor that filters or corrects unsafe actions before they violate a temporal-logic specification [@alshiekh2018shielding]. Codomyrmex does not provide formal control-theoretic or temporal-logic guarantees, but the analogy is useful: the ActuationGate is a runtime assurance point for software actuation, and its future evaluation should ask whether the gate behaves like a conservative shield under pressure.

Software-supply-chain research points to a second hardening path. In-toto records a cryptographically verifiable chain of supply-chain steps from project inception through deployment [@torresarias2019intoto], while TUF designs software update systems to survive key compromise through role separation, delegation, thresholds, and rollback protection [@samuel2010tuf]. The current manuscript pipeline records hashes, generated variables, rendered artifacts, and quality gates; it does not yet bind those records into an in-toto layout, TUF repository, or signed release policy. Visibility and infrastructure work for AI agents adds the governance analogue: identifiers, real-time monitoring, activity logging, credentials, reputation, and action logs are treated as shared infrastructure for accountable agents rather than optional observability features [@chan2024visibility; @chan2025infrastructure; @kolt2025governing].

Finally, the evaluation surface should include explicitly harmful, cyber-capable, and collusive agent behavior. AgentHarm measures whether tool-using agents comply with malicious multi-step requests [@andriushchenko2024agentharm]. ST-WebAgentBench measures whether web agents complete tasks while respecting safety and trustworthiness policies [@levy2024stwebagentbench]. CyberSecEval 3, one-day vulnerability exploitation, zero-day multi-agent exploitation, and CVE-Bench test cybersecurity risk, offensive capability, and exploit behavior in settings closer to operational abuse than ordinary coding benchmarks [@wan2024cyberseceval3; @fang2024oneday; @zhu2024zerodayagents; @zhu2025cvebench]. Secret-collusion work shows that multiple agents can coordinate through steganographic channels to evade oversight [@motwani2024secretcollusion]. Codomyrmex has not yet been evaluated against AgentHarm, ST-WebAgentBench, CyberSecEval, one-day or zero-day exploitation scenarios, CVE-Bench, or secret-collusion scenarios; those are future falsification workloads, not evidence already achieved.

[@tbl:runtime_visibility_provenance_agenda] summarizes the added hardening agenda.

| Scholarship lens | Representative sources | Claim pressure on Codomyrmex | Boundary |
|:---|:---|:---|:---|
| Runtime assurance and shielding | Simplex [@seto1998simplex; @phan2017componentbased; @mehmood2021blackboxsimplex] and safe RL shielding [@alshiekh2018shielding] | Treat gate decisions as runtime safety checks interposed before action | The ActuationGate is not a formally verified controller, temporal-logic shield, or safe fallback policy |
| Verifiable provenance | In-toto [@torresarias2019intoto] and TUF [@samuel2010tuf] | Convert manuscript/package evidence from local hashes into verifiable supply-chain attestations | Current artifacts are not signed, thresholded, delegated, or TUF/in-toto enforced |
| Agent visibility and infrastructure | Visibility into AI Agents [@chan2024visibility], Infrastructure for AI Agents [@chan2025infrastructure], and Governing AI Agents [@kolt2025governing] | Make identifiers, monitoring, activity logging, credentials, reputation, and action records first-class governance surfaces | Codomyrmex is not a legal identity, liability, dispute-resolution, or cross-platform agent infrastructure system |
| Harmful and cyber agent benchmarks | AgentHarm [@andriushchenko2024agentharm], ST-WebAgentBench [@levy2024stwebagentbench], CyberSecEval 3 [@wan2024cyberseceval3], one-day exploitation [@fang2024oneday], zero-day multi-agent exploitation [@zhu2024zerodayagents], and CVE-Bench [@zhu2025cvebench] | Evaluate whether earned actuation reduces malicious multi-step tool use, policy violations, cyber abuse, and exploit behavior | These external harmful/cyber benchmark results are not reported in this paper |
| Multi-agent collusion | Secret Collusion among AI Agents [@motwani2024secretcollusion] | Test whether independent-looking agents can covertly coordinate to evade monitoring and gate pressure | Current deterministic fixtures do not model collusion, steganography, or deceptive multi-agent coordination |

: Runtime-assurance, provenance, visibility, and harmful-agent scholarship that extends the external validation agenda. {#tbl:runtime_visibility_provenance_agenda}

Under an advanced persistent threat model, the strongest safe claim is therefore architectural compatibility, not containment. Assume an adversary can compromise an agent process, poison a dependency, steal a CI token, replay a stale artifact, or use prompt injection to steer an otherwise trusted model. Codomyrmex can reduce blast radius by requiring consequence-backed authorization, preserving local failure history, and forcing high-risk proposals through auditable gate decisions. It still requires external controls: workload sandboxing, least-privilege credentials, network egress restrictions, signed artifacts, SBOM/provenance verification, protected secrets, independent monitoring, incident response, and human review for high-impact actions. Alignment with these frameworks is an evaluation agenda, not an achieved security certification.

## Active Inference and Free Energy

Friston's Free Energy Principle [@friston2010free] frames intelligent behavior as minimization of variational free energy — the gap between an agent's generative model of the world and its sensory observations. A full mapping of the Colony Kernel onto this framework requires identifying three components: (1) a generative model $p(o, s)$ over observations $o$ and hidden states $s$; (2) a variational posterior $q(s)$ that the agent maintains over those hidden states; and (3) a policy-selection mechanism that minimizes expected free energy over future states.

A rigorous active inference treatment of the Colony Kernel is beyond the scope of this paper and is deferred to future work. What can be noted structurally is that the pressure loop shares the phenomenology of free energy minimization — high failure pheromone concentrations correspond to regions of elevated prediction error, and agent routing toward those regions resembles the exploratory behavior that active inference predicts when epistemic value is high. We do not claim formal equivalence. Readers who find the analogy productive should treat it as a design intuition rather than a theoretical commitment; readers seeking formal guarantees should await the companion mathematical treatment.

## Explicit Scope Limitations

The following limitations are deliberate design decisions, not oversights. Each reflects a trade-off made to keep the initial system tractable and verifiable; each names a concrete future extension.

**Control plane only.** The Colony Kernel governs agent behavior but does not execute actions itself. This boundary is load-bearing: mixing governance and execution in a single component makes both harder to audit. LLM runtimes (LangGraph, AutoGen, or direct MCP clients) sit below the Colony Kernel and handle execution; the Colony Kernel sits above them and handles authority. A future integration layer could make this separation transparent to callers.

**No security certification or nation-state containment claim.** The system records consequence, gates action, and preserves evidence, but it does not claim SLSA certification, zero-trust architecture compliance, full ATT&CK/ATLAS coverage, or operational resistance to advanced persistent threats. Production deployments require external identity, isolation, provenance, monitoring, and response controls beyond the scope of the Colony Kernel.

**Discrete-tick time model.** Pheromone decay advances on `ColonyKernel.tick()` calls rather than on a wall-clock timer. This was chosen deliberately: a tick-driven model is deterministic, testable, and reproducible across environments without scheduling infrastructure. Real-time decay introduces non-determinism that complicates replay and debugging. Integration with a real-time clock daemon — mapping ticks to configurable wall-clock intervals — is a straightforward future extension once the tick semantics are proven stable.

**Heuristic trust deltas, no learned policy.** Trust scoring uses fixed deltas (success → +{{CONFIG_TRUST_DELTA_PASS}}, failure → {{CONFIG_TRUST_DELTA_FAIL}}, human_feedback multiplier) rather than a policy learned from data. This choice follows the principle Sutton & Barto [@sutton2018reinforcement] articulate for bootstrapping reinforcement learning systems: hand-crafted reward shaping provides stable initial signal while learned policies are still sample-starved. The heuristic deltas were calibrated to match the intuition that failures should cost more than successes gain — a risk-averse bias appropriate for irreversible actions. Replacing the heuristic with a proper policy gradient or Q-learning update is an identified future direction, contingent on accumulating sufficient consequence logs to train from.

**Human-confirmed pruning.** The pruning daemon identifies stale consequence records and low-activity code regions but never archives automatically. Automated pruning of operational memory raises correctness risks that are difficult to bound without extensive deployment experience. Human confirmation is required until a sufficient empirical record justifies a configurable auto-prune threshold.

**Synchronous MCP tools.** The current MCP surface is synchronous, which means concurrent proposals from multiple agents serialize at the gate. This is conservative and safe; it does not reflect a fundamental design constraint. Async concurrency across simultaneous proposals — with per-proposal trust evaluation and pheromone read isolation — is the primary scalability target for a future release.

**Single-process consequence memory.** The SQLite backend stores consequence history in a single-process database, making distributed colony state across multiple repositories or machines out of scope. Distributed consensus for pheromone fields and shared trust scores is a substantial engineering problem; the current design optimizes for correctness and debuggability in the single-repository case. Sharding or replication strategies will be addressed in a follow-on architecture document.

---

## Information-Theoretic Security and Differential Privacy Bounds on Trust {#sec:infosec-dp}

The trust score is, at its core, a statistic computed over a private ledger of agent
interactions. This observation connects the Colony Kernel to the differential privacy
literature [@dwork2014algorithmic], which provides rigorous tools for reasoning about
what an adversary can infer about the ledger from the published statistic.

### Trust as a Published Statistic

When the colony publishes trust scores via `colony_agent_profile` (the MCP tool), it
releases a function of the consequence memory. An adversary with access to the published
trust score $\tau_n$ and the update rule [@eq:trust-update] can potentially infer
individual interaction outcomes from changes in the score — particularly in sparse
interaction histories where the delta from a single outcome is relatively large compared
to the total accumulated score. This is the *inference attack* problem in differential
privacy terminology [@dwork2014algorithmic; @near2021programming].

### Sensitivity Analysis for Trust Publication

As established in [@sec:theory-privacy], the global $\ell_1$ sensitivity of the trust
score to any single interaction record is bounded by $\Delta_{\text{global}} = 0.16$.
This means that if two consequence histories differ in a single record, the published
trust scores differ by at most 0.16 — a non-trivial fraction of the $[0, 1]$ range.

An adversary observing the trust score before and after an interaction can infer:

- Whether the action passed or failed (if the delta is close to $\pm 0.04$ or $-0.08$)
- Whether repair was needed (if the delta is $-0.05$ below the pass/fail component)
- The sign of human feedback (if the total delta deviates from the pass/fail baseline)

The *privacy risk* is highest when:
1. The trust history is short (few interactions), so individual deltas are large relative to accumulated history
2. The score is queried both before and after a sensitive interaction
3. The observer has side information about the agent's normal behavioral patterns

### Practical Mitigations and Deployment Recommendations

The current implementation does not apply differential privacy noise: trust scores are
published in full. This is appropriate for the single-repository, internal deployment
model described in this paper, where the consequence ledger and the agent pool are both
under the operator's direct control. For deployments where:

- Multiple organizations share a colony (federated deployment)
- Agent identities map to real individuals whose failure rates could be sensitive
- The trust score is used for downstream decisions beyond gate gating

the Gaussian mechanism calibration in [@eq:dp-noise] specifies the noise level required.
At $\epsilon = 1.0$, $\delta = 10^{-5}$, the required noise is approximately $\sigma_{\text{DP}} \approx 0.76$
on a $[0, 1]$ trust scale — large enough to substantially obscure individual interactions.
This creates a fundamental tension: the trust score must be precise enough to gate actions
accurately, but revealing enough information that adding protective noise degrades gate
accuracy. Resolution requires calibrating the privacy budget against the gate's sensitivity
to trust-score uncertainty.

**Connection to Secure Aggregation.** Multi-party computation literature [@bonawitz2017practical]
offers an alternative: rather than adding noise to the published score, organizations can
compute trust aggregates over federated consequence histories using secure aggregation
protocols that reveal only the aggregate without exposing individual records. This is
compatible with the Colony Kernel's trust update rule because the trust score is a linear
function of outcome deltas, and linear functions are tractable under standard secure
aggregation frameworks [@mohassel2017secureml]. Federated colony trust computation is
an identified future direction.

### Shannon Entropy of Gate Decisions

A second information-theoretic property concerns the information content of gate decisions.
Define the entropy of the gate decision distribution at location $l$ under the stationary
failure process (Corollary 2 of [@sec:theory-field]) as:

$$H(\text{gate} \mid l) = -\sum_{d \in \{\text{EXECUTE, HOLD, REFUSE}\}} p_d^{(l)} \log p_d^{(l)}$$ {#eq:gate-entropy}

where $p_d^{(l)}$ is the stationary probability of decision $d$ at location $l$.

**Proposition 4 (Gate Entropy Decreases at High-Risk Locations).** At locations with
high failure rates $q \rightarrow 1$, the stationary gate decision distribution concentrates
on REFUSE, and $H(\text{gate} \mid l) \rightarrow 0$. At locations with low failure rates
$q \rightarrow 0$, the distribution concentrates on EXECUTE, and $H(\text{gate} \mid l) \rightarrow 0$.
Gate entropy is maximized at intermediate failure rates, where all three decisions have
non-trivial probability.

*Proof sketch.* High $q$ drives RISK pheromone to its steady-state maximum (bounded in
[@eq:field-bound]), causing `risk_ok = 0.0` and $g < 0.75$ with high probability under
reasonable trust distributions. Low $q$ drives RISK pheromone to zero, causing
`risk_ok = 1.0` and $g \geq 0.75$ with high probability. Both extremes minimize entropy.
At intermediate $q$, the pheromone dynamics create a distribution over all three decisions. $\square$

**Information Value of Sensing.** The mutual information $I(\text{RISK pressure}; \text{decision})$
measures how much information the pheromone field adds to the gate decision beyond what
trust score alone provides. Under the gate's additive structure, this is bounded by the
information in the `risk_ok` component, which itself depends on the three-tier mapping.
The mutual information is maximized when `risk_ok` is the decisive component — when
trust, budget, and completeness are all near their maximum values, and only risk pressure
distinguishes EXECUTE from HOLD. This suggests that the pheromone field is most
informative precisely when agents are competent (high trust) and well-organized (complete
proposals) — conditions under which a binary trust-only gate would wrongly pass dangerous
proposals, but the stigmergic risk signal correctly applies caution.

---

## Mechanism Design and Incentive Compatibility {#sec:mechanism-design}

The Colony Kernel can be analyzed as a *mechanism* in the sense of mechanism design
theory: it is a set of rules that maps agents' reports (proposals) and revealed actions
(outcomes) to decisions (gate verdicts and trust updates) that allocate valuable resources
(execution authority) [@roughgarden2016cs269i; @myerson1979incentivecompatibility].

### The Colony as a Direct Revelation Mechanism

In a direct revelation mechanism, agents are asked to report their types (in our case,
the true safety and completeness of their proposals) directly, and the mechanism is
designed so that truthful reporting is an equilibrium strategy [@myerson1979incentivecompatibility].
The Colony Kernel is *not* a direct revelation mechanism: agents submit structured proposals
(not type reports), and the gate independently evaluates completeness, risk, and trust.
However, the mechanism's incentive properties are still analyzable.

**Definition 5 (Proposal Game).** The proposal game $\Gamma$ is a sequential game where:
- Players are agents $\mathcal{A}$
- Each agent chooses a proposal strategy $\sigma_a : \text{task} \mapsto \text{ActionProposal}$
- The gate mechanism $M$ maps proposals to decisions $\{$EXECUTE, HOLD, REFUSE$\}$
- Agent payoffs: $+R$ for EXECUTE, $0$ for HOLD (with option to revise), $-C$ for REFUSE
  (where $R, C > 0$ represent the value of executing vs. the cost of a false rejection)

**Theorem 8 (Incentive Compatibility of Completeness Scoring).** In the proposal game
$\Gamma$, truthful proposal completion (submitting all three required fields when the
agent possesses the information) is a weakly dominant strategy.

*Proof.* For an agent with a safe proposal (true `risk_ok = 1.0`, true `budget_ok = 1.0`,
trust\_ok $\geq 0.5$), the gate score with full completeness is:
$g_{\text{full}} = 0.30 + 0.30 + \text{trust} + 0.15 \geq 0.875$, which is EXECUTE.
With one missing field: $g_{\text{partial}} = 0.30 + 0.30 + \text{trust} + 0.15 \times 0.65
= 0.30 + 0.30 + \text{trust} + 0.098$. For an agent with trust\_ok = 0.5:
$g_{\text{full}} = 0.875$, $g_{\text{partial}} = 0.823$. Both are EXECUTE.

The omission of a field can only reduce the gate score by $0.15 \times 0.35 = 0.0525$
per missing field. When the gate score with full completeness is in the EXECUTE band
$(g \geq 0.75)$, it may still pass with one missing field (as shown in the worked
example in [@sec:methodology]). However, an agent near the EXECUTE/HOLD boundary who
strategically omits evidence to save submission effort risks being pushed into HOLD —
a worse outcome than EXECUTE. Therefore, submitting complete proposals weakly dominates
incomplete proposals for all agents whose proposals are genuinely safe. $\square$

**Remark (Strategic Incompleteness as a Red Flag).** An agent that *deliberately* submits
incomplete proposals to game the HOLD threshold (preferring HOLD to EXECUTE for reasons
the mechanism does not see, e.g., to extend the HOLD window as cover while preparing
a second action) benefits from the partial score reduction. However, repeated HOLD
decisions with incomplete proposals do not increase trust — they generate no trust delta
at all until the action executes — and the agent accumulates `total_proposals` without
the matching trust accumulation, creating a detectable anomaly in its consequence history.
This side effect makes strategic incompleteness detectable as a behavioral pattern,
supporting the GUARD\_ANT role's audit function.

### Free-Rider Detection via Pheromone Imbalance

A free-rider problem in multi-agent systems occurs when agents benefit from collective
resources without contributing proportionally. In the Colony Kernel, the equivalent
free-rider is an agent that extracts value (EXECUTE decisions) by accumulating trust
cheaply — e.g., by submitting many low-risk proposals to build trust, then submitting
a high-risk proposal once trust is established.

**Proposition 5 (Free-Rider Resistance via Pheromone Separation).** The pheromone field
provides partial resistance to trust-laundering attacks because RISK pheromone is
deposited at the *target location* of the high-risk proposal, not at the agent's trust
record. An agent that successfully builds trust through low-risk proposals and then
submits a high-risk proposal to a location with existing RISK pressure faces two
independent barriers: the gate evaluates `risk_ok` for the target location (where RISK
pressure may already be elevated from prior failures) and `trust_ok` for the proposing
agent (accumulated from prior history). These are orthogonal: trust at the agent level
does not reduce RISK pressure at the target location.

*Proof.* By the compound-key addressing of the pheromone field, $(l, \text{RISK})$ and
agent trust are stored in independent data structures. The gate score formula
[@eq:gate_score_detail] adds their contributions independently. High agent trust does
not reduce `risk_ok`; elevated target RISK pressure does not reduce `trust_ok`.
Therefore, an agent cannot leverage accumulated agent-level trust to bypass location-level
risk barriers. $\square$

This orthogonality is a deliberate design property: it means that the two primary risk
signals in the gate (risk pheromone at the target and agent trust history) cannot be
traded against each other through strategic proposal sequencing.

### Mechanism Optimality and the Budget Constraint

Myerson's revenue-equivalence theorem [@myerson1979incentivecompatibility] and its
extensions characterize optimal mechanisms for resource allocation under private
information. In the Colony Kernel, the scarce resource is execution authority — a slot
in the colony's actuation envelope. The budget constraint (one of the four gate components)
implements a hard feasibility constraint: proposals that exceed the period budget are
ineligible regardless of other attributes.

From the mechanism design perspective, the budget constraint is a *participation
constraint*: the colony can only allocate what it has. The multi-dimensional nature of
the budget (seven independent cost dimensions) means that the feasibility region is a
hyperrectangle in $\mathbb{R}^7_{\geq 0}$, and the `can_afford` check is a test for
membership in this hyperrectangle. The mechanism is *ex-post individually rational*
— no agent is forced to incur costs it has not consented to — because REFUSE and HOLD
decisions do not consume budget, and EXECUTE decisions consume only the resources
explicitly estimated in the proposal.

**Future Direction: Optimal Threshold Calibration.** Mechanism design provides normative
tools for calibrating the gate thresholds (0.75 for EXECUTE, 0.50 for HOLD) to maximize
a colony-level objective (e.g., maximize expected colony output subject to a maximum
expected repair rate). This would require specifying a utility function over gate
decisions and fitting a model of the proposal quality distribution from production
consequence logs. Myerson's optimal mechanism framework [@myerson1979incentivecompatibility]
then provides the optimal threshold as a function of the proposal quality distribution
and the utility function. This calibration is an identified future direction, contingent
on accumulating sufficient production data.

---

## Crowdsourcing, Collective Intelligence, and Colony Wisdom {#sec:collective-intelligence}

The Colony Kernel draws on a research tradition that predates agentic AI: the study of
how collectives of agents — human or artificial — aggregate distributed information
into better decisions than any individual agent could make alone [@surowiecki2004wisdom;
@condorcet1785essai].

### The Condorcet Jury Theorem as a Design Template

Condorcet's Jury Theorem [@condorcet1785essai] states that if each member of a jury
independently makes the correct judgment with probability $p > 0.5$, then as the jury
size grows, the probability that the majority vote is correct approaches 1. The theorem
formalizes the intuition that independent, better-than-random agents collectively
converge on truth.

The FalsificationWorker implements a version of this principle: its 10 independent
attack vectors are orthogonal checks, each with different precision-recall trade-offs,
and the overall verdict is a majority-style aggregation (PASS if no HIGH findings,
CONDITIONAL if moderate findings, FAIL if any HIGH or CRITICAL). Under the assumption
that each attack vector is independently informative about proposal safety, the 10-vector
ensemble is more accurate than any single vector — a direct application of Condorcet's
principle.

**Quantitative Bound.** Let $p_v$ be the probability that attack vector $v$ correctly
identifies a dangerous proposal (sensitivity) and $1 - q_v$ the probability it flags a
safe proposal (false positive rate). Under independence, the probability that *at least
one* vector flags a dangerous proposal is:

$$\Pr[\text{at least one flag} \mid \text{dangerous}] = 1 - \prod_{v=1}^{10} (1 - p_v)$$ {#eq:ensemble-detection}

For $p_v = 0.5$ (each vector has 50% sensitivity), the ensemble sensitivity is
$1 - 0.5^{10} = 99.9\%$. This bound is highly favorable, but it depends critically on
the independence assumption. Correlated attack vectors — e.g., `NO_ROLLBACK` and
`NO_TEST_VALUE` both triggered by proposals that omit validation evidence — provide less
additional information than independent vectors. The current vector taxonomy was designed
to minimize correlation by targeting orthogonal aspects of proposal quality (rollback,
testing, architecture, dependencies, security, scope, metrics), but empirical correlation
analysis over production logs is needed to validate this design intent.

### Colony-Level Intelligence and Modularity

Research on organizational modularity [@simon1962architecture] and parallel distributed
processing [@rumelhart1986parallel] both suggest that decomposing complex tasks into
independent modules improves collective performance. The Colony Kernel's eight subsystems
are designed with strict independence: no subsystem imports from another, and all
communication goes through the shared `models.py` contract. This modularity provides
a precisely analogous benefit: each subsystem can be independently validated, replaced,
or upgraded without cascading effects on others — a property that supports the
"harder to fool" claim by ensuring that adversarial attacks on one subsystem cannot
trivially compromise the gate logic in another.


