# Colony Kernel Anti-Patterns
# Common mistakes that corrupt the colony's trust model or stigmergic integrity

anti_patterns:
  - name: Trust Laundering
    description: Calling record_outcome with tests_passed=True to artificially inflate trust
    impact: Corrupts the trust model — agent appears reliable but produces bad code
    why_it_happens: Pressure to get agents past the gate; trust score is the only metric visible to dispatch
    correct_approach: Record honest outcomes. If tests failed, set tests_passed=False. The colony's value is in truthful signals, not high scores.
    detection: Agent with high trust_score but frequent repair cycles at targets it touched
    visualization: |
      ```mermaid
      flowchart TD
          A["Agent wants high trust"] --> B{"Tests actually passed?"}
          B -->|"No"| C["Agent sets tests_passed=True<br/> anyway"]
          B -->|"Yes"| D["Agent sets tests_passed=True"]
          C --> E["Trust inflates artificially"]
          E --> F["Agent gets DISPATCHER role"]
          F --> G["Agent causes repair cycles"]
          G --> H["FAILURE signals deposited<br/>by other agents"]
          H --> I["Location becomes 'toxic'<br/>but agent's trust stays high"]
          I --> J["COLONY LOSES TRUST<br/>IN THE AGENT"]
          D --> K["Trust earned honestly"]
          K --> L["Agent gets role on merit"]
          L --> M["Clean outcomes reinforce trust"]
          M --> N["COLONY GETS BETTER"]

          style C fill:#dc2626,color:#fff
          style E fill:#dc2626,color:#fff
          style F fill:#dc2626,color:#fff
          style I fill:#dc2626,color:#fff
          style D fill:#0f766e,color:#fff
          style K fill:#0f766e,color:#fff
          style M fill:#0f766e,color:#fff
      ```

  - name: Pheromone Spam
    description: Depositing excessive signals at the same location to manipulate gate scores
    impact: Drowns out legitimate signals; makes the field uninformative
    why_it_happens: Agent wants to "claim" a location or suppress competition
    correct_approach: Each action deposits at most one SUCCESS and one FAILURE signal. The field is append-only but decay handles stale signals naturally.
    detection: Single agent responsible for >50% of signals at a location

  - name: Gate Score Gaming
    description: Crafting proposals specifically to pass the gate rather than to solve real problems
    impact: Gate becomes meaningless; agents optimize for score, not value
    why_it_happens: Gate score is the only visible metric; agents are evaluated on pass rate
    correct_approach: The gate is a safety mechanism, not a performance metric. A REFUSE with good reason is better than an EXECUTE with a bad action.
    detection: High gate pass rate but low code quality in executed actions

  - name: Ignoring HOLD Verdicts
    description: Treating HOLD as a temporary inconvenience and resubmitting unchanged
    impact: Wastes gate cycles; budget violations accumulate; trust doesn't improve
    why_it_happens: HOLD feels like a bug (the proposal looks correct); budget constraints seem arbitrary
    correct_approach: Read required_evidence in the HOLD response — it tells you exactly what to fix (budget dimension, missing evidence, trust deficit).
    detection: Same proposal submitted 3+ times in a row with HOLD each time

  - name: Orphan Proposals
    description: Proposing actions without ever recording outcomes
    impact: Trust scores become stale; budget ledger understates real consumption; pheromone field loses accuracy
    why_it_happens: Agent crashes or context window expires between propose and record
    correct_approach: Use a wrapper that guarantees record_outcome is called. If the agent crashes, the next agent at the same target should notice the stale state via pheromone query.
    detection: Propose count > record count for same agent over time window

  - name: Bypassing the Gate
    description: Calling record_outcome directly without going through propose_action
    impact: Completely bypasses trust, budget, and falsification checks
    why_it_happens: "I know what I'm doing" — experienced agent assumes it doesn't need gate approval
    correct_approach: Always go through propose_action. Even GUARD_ANT agents must propose. The gate is the colony's only mechanism for collective learning.
    detection: ConsequenceRecord with no corresponding gate evaluation in the pheromone field

  - name: Over-Reliance on SANDBOX
    description: Keeping agents in SANDBOX indefinitely by never letting them build trust
    impact: Agents can never contribute write actions; colony wastes gate evaluations on SANDBOX REFUSE
    why_it_happens: Fear of bad outcomes; no mechanism to promote agents
    correct_approach: Let agents propose. Even SANDBOX agents can propose — they'll get REFUSE, but the proposal is recorded. After 3 proposals with clean outcomes, they auto-promote.
    detection: Agent stuck in SANDBOX after 10+ proposals
