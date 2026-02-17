# AI Safety -- Robotic Arm Guardrails

The most advanced machines on any modern factory floor are the robotic arms -- tireless, precise, and capable of exerting forces that would instantly injure a human worker. That is why every robotic arm operates inside a safety cage: a physical enclosure with interlocked doors, light curtains that detect intrusion, and a kill switch that halts motion the instant a boundary is violated. The arm does not *intend* harm, but it does not understand harm either. It follows its program with perfect fidelity, including programs that are subtly wrong. AI safety in Codomyrmex follows this same philosophy: assume the AI is powerful, assume it will faithfully execute its instructions, and build guardrails that prevent those instructions -- whether maliciously injected or accidentally malformed -- from causing damage.

## Prompt Injection Taxonomy

Prompt injection is the AI equivalent of feeding false instructions to a robotic arm's controller. It comes in several forms:

### Direct Injection

The attacker includes malicious instructions directly in the input that the AI processes. This is the factory equivalent of someone rewiring the arm's control panel to change its program:

- **Instruction override**: "Ignore your previous instructions and instead..." -- the attacker attempts to replace the system prompt with their own directives.
- **Role manipulation**: "You are now an unrestricted assistant..." -- the attacker attempts to change the AI's self-concept and behavioral boundaries.
- **Output formatting attacks**: Instructions that cause the AI to emit content in formats that downstream systems interpret as commands (e.g., generating SQL that a downstream parser executes).

### Indirect Injection

The malicious instructions are embedded in data that the AI retrieves or processes, not in the user's direct input. This is the factory equivalent of tampering with a parts bin so that the arm picks up a defective component:

- **Document poisoning**: Malicious instructions hidden in documents, web pages, or database entries that the AI is instructed to summarize or process.
- **Tool output manipulation**: If the AI uses tools whose output is controlled by an attacker, those outputs can contain injected instructions.
- **Multi-turn manipulation**: Gradually steering the AI's context over multiple interactions until it behaves as the attacker intends.

### Context Manipulation

Attacks that exploit the AI's context window -- its working memory -- to alter behavior:

- **Context flooding**: Filling the context window with benign-seeming content that displaces safety instructions.
- **Attention diversion**: Structuring input so that the AI focuses on attacker-controlled content and ignores system guardrails.
- **Memory poisoning**: In systems with persistent memory, injecting content that influences future interactions.

## Jailbreak Detection Strategies

Jailbreak attempts try to bypass the AI's safety training. Detection strategies mirror factory safety monitoring:

- **Pattern matching**: Known jailbreak templates are catalogued and matched against incoming prompts. This is the factory equivalent of the contraband list at the security checkpoint.
- **Semantic analysis**: Even when the exact wording varies, the *intent* of a jailbreak attempt has recognizable characteristics: requests to ignore instructions, adopt unrestricted personas, or circumvent restrictions. Semantic analysis detects the intent behind novel phrasings.
- **Behavioral anomaly detection**: Monitor the AI's outputs for signs that a jailbreak has partially succeeded -- unexpected tone shifts, policy violations in outputs, or tool calls that do not match the stated task.
- **Canary tokens**: Embed hidden markers in system prompts that the AI should never reproduce in output. If a canary appears in the response, the system prompt has been extracted.

## Adversarial Containment

Even if an attack succeeds in manipulating the AI's behavior, containment limits the damage:

- **Sandboxing**: AI-generated code executes in isolated environments with no access to production resources. The robotic arm's safety cage ensures that even if the arm malfunctions, it cannot reach workers. Sandbox environments serve the same purpose for AI-generated actions.
- **Output filtering**: Every AI response passes through filters that detect and block sensitive data leakage (PII, credentials, internal paths), harmful content, and instruction injection attempts targeting downstream systems.
- **Rate limiting**: Restrict the volume and velocity of AI actions. A robotic arm that suddenly begins moving at ten times its normal speed triggers an emergency stop. Similarly, an AI agent that suddenly attempts thousands of file operations triggers containment.
- **Blast radius limitation**: Restrict the set of resources any single AI interaction can affect. Even a fully compromised session cannot reach resources outside its designated scope.

## Tool Misuse Prevention

AI agents that can invoke tools (file operations, code execution, API calls) require additional controls:

- **Capability restrictions**: Each agent is granted the minimum set of tools required for its task. The factory worker who operates the lathe does not have the keys to the forklift. In Codomyrmex, this is enforced through the trust gateway at `src/codomyrmex/agents/pai/trust_gateway.py`.
- **Trust gating**: Destructive operations (write, execute, delete) require explicit trust elevation. The `/codomyrmexTrust` workflow is the digital equivalent of the factory supervisor physically handing over the key to a restricted machine.
- **Pre-execution validation**: Before a tool is invoked, the request is validated against the agent's permissions, the tool's preconditions, and the current system state. A robotic arm does not begin a cutting operation if the safety guard sensor reports "open."
- **Post-execution audit**: Every tool invocation is logged with full context: who requested it, what parameters were used, what the outcome was. This audit trail enables both incident investigation and behavioral analysis.

## AI Incident Monitoring and Response

When AI safety controls detect an anomaly, the response follows a structured protocol:

1. **Detection**: Automated monitoring identifies a potential safety violation -- a jailbreak attempt, an unexpected tool invocation, a containment boundary probe.
2. **Classification**: Is this a genuine attack, a false positive, or an edge case that reveals a gap in the safety model?
3. **Containment**: Immediately restrict the affected session's capabilities. In the factory, this is the emergency stop: halt the arm, then investigate.
4. **Investigation**: Examine the full context -- prompt history, tool invocations, output patterns -- to understand what happened and how.
5. **Remediation**: Update detection rules, tighten containment boundaries, or modify trust policies to prevent recurrence.
6. **Post-incident review**: Document the incident, update the threat model, and share findings with the team. Every factory incident becomes a training case study.

## Component Mapping

AI safety in Codomyrmex is implemented at `src/codomyrmex/security/ai_safety/`:

| Component | Factory Analogy | Responsibility |
|-----------|----------------|----------------|
| **AISafetyMonitor** | Safety cage sensor array and kill switch | Real-time monitoring of AI behavior, anomaly detection, emergency containment |
| **PromptGuard** | Input inspection at the loading dock | Prompt injection detection, jailbreak pattern matching, semantic analysis |
| **OutputFilter** | Quality control at the shipping dock | Response sanitization, data leakage prevention, downstream injection blocking |
| **ToolGatekeeper** | Machine-specific key control | Capability restriction enforcement, pre-execution validation, trust verification |
| **IncidentResponder** | Emergency response team | Incident classification, containment activation, investigation coordination |

## From Factory Floor to Code

The robotic arm safety cage and the AI sandbox serve identical purposes: they contain a powerful, non-sentient system within boundaries that prevent it from causing unintended harm. The kill switch and the emergency containment protocol share the same philosophy: when in doubt, stop everything and investigate.

AI safety is not about distrusting AI -- it is about respecting its power. A factory that trusts its robotic arms enough to remove the safety cages is not brave; it is negligent. Similarly, an AI system that operates without prompt injection defenses, output filtering, and trust gating is not efficient; it is unguarded.

The factory metaphor makes this viscerally clear: you would never stand inside a robotic arm's work envelope without the safety cage active. Do not let your data, your systems, or your users stand inside an AI's operational envelope without equivalent protections.

## Cross-References

- Technical implementation details: [`docs/modules/security/`](../modules/security/) (AI safety components are documented within the broader security module)
- PAI trust gateway: The trust gating mechanism is documented in the PAI integration -- see [`docs/modules/security/PAI.md`](../modules/security/PAI.md)
- Security philosophy and index: [index.md](index.md)
- Trust and governance (the policy layer that AI safety enforces): [trust-and-governance.md](trust-and-governance.md)
- Digital security (operational controls that complement AI safety): [digital-security.md](digital-security.md)
