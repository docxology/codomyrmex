# Colony Kernel Decisions
# Key design decisions and their rationale

decisions:
  - id: stigmergy-over-central-coordination
    decision: Use stigmergic pheromone field instead of central coordinator
    context: Need to coordinate multiple agents without a single point of failure
    alternatives:
      - Central orchestrator (bottleneck, single point of failure)
      - Direct agent-to-agent communication (complex protocol, tight coupling)
      - Shared database (not real-time, requires polling)
    rationale: |
      Ants do not negotiate with each other. They deposit chemical traces in
      the environment, and other ants sense those traces and modulate their
      behavior. The colony's collective intelligence emerges from the accumulated
      pattern of signals, not from any central authority. For software agents,
      this means:
      - No single point of failure
      - Memory persists across session boundaries, model swaps, and agent churn
      - Agents can coordinate without knowing about each other
      - The system degrades gracefully as agents join and leave
    consequences:
      - Gate scores depend on accumulated history, not just current state
      - Pheromone decay rates must be tuned to balance recency vs. stability
      - Debugging requires inspecting the pheromone field, not just agent logs
    diagram: |
      ```mermaid
      graph TD
          subgraph warehouse["Warehouse Model (rejected)"]
              CO["Central Orchestrator"] --> A1["Agent 1"]
              CO --> A2["Agent 2"]
              CO --> A3["Agent 3"]
          end

          subgraph ecology["Ecology Model (chosen)"]
              PF["Pheromone Field<br/>shared environment"]
              A4["Agent 4"] -->|"deposits"| PF
              A5["Agent 5"] -->|"senses"| PF
              A6["Agent 6"] -->|"deposits"| PF
              PF -->|"evolves"| PF
          end

          style ecology fill:#0f766e,color:#fff
          style warehouse fill:#f3f4f6,color:#6b7280
      ```

  - id: trust-based-gate-not-rbac
    decision: Use earned trust scores instead of role-based access control
    context: Need to gate agent actions based on reliability
    alternatives:
      - Static RBAC (roles assigned at startup, never change)
      - Capability tokens (require external authority)
      - Reputation systems (complex, gameable)
    rationale: |
      Static roles don't adapt to agent behavior. An agent that caused a 5-hour
      repair cycle last Tuesday should have less access today. Trust scoring creates
      a self-correcting system: clean outcomes earn access, failures restrict it.
      The role ladder (SANDBOX → REPAIR_ANT → MEMORY_ANT → DISPATCHER → GUARD_ANT)
      makes the trust-to-permission mapping deterministic and auditable.
    consequences:
      - New agents start with no write access (SANDBOX)
      - Trust deltas must be carefully tuned (+0.04 pass, -0.08 fail)
      - Human override possible via HUMAN_PRIORITY pheromone signal

  - id: sqlite-over-orm
    decision: Use stdlib sqlite3 directly for consequence persistence
    context: Need persistent storage for trust profiles and consequence records
    alternatives:
      - SQLAlchemy ORM (heavy dependency, async complexity)
      - Redis (in-memory, no durability)
      - File-based JSON (no concurrent access safety)
    rationale: |
      SQLite with WAL mode gives us concurrent readers without blocking writers,
      zero external dependencies (stdlib), and file-based persistence that survives
      process restarts. The schema is simple (two tables: consequences, profiles).
      No ORM needed — direct SQL is clearer for this use case.
    consequences:
      - Trust survives process restarts
      - Concurrent agents can read profiles simultaneously
      - WAL mode prevents read-write contention

  - id: falsification-before-gate
    decision: Run adversarial falsification before the gate evaluation
    context: Need to catch bad proposals before they consume gate resources
    alternatives:
      - Falsification inside the gate (couples scoring with validation)
      - Falsification after the gate (wastes gate cycles on bad proposals)
      - No falsification (trust all proposals)
    rationale: |
      Falsification is cheap (deterministic checks, no LLM calls). Running it
      before the gate means bad proposals never reach the scoring stage. The
      FalsificationWorker applies 10 attack vectors, including rollback,
      test-value, scope, metric, circular-architecture, dependency, security,
      module breadth, maintenance-cost, and abstraction checks. Each finding
      carries a severity and concrete remediation.
    consequences:
      - Bad proposals are caught early
      - Gate score incorporates falsification penalty
      - Agents receive actionable feedback (findings[].remediation)

  - id: read-only-pruning
    decision: PruningDaemon only reports candidates, never auto-deletes
    context: Need to identify stale modules without risking accidental data loss
    alternatives:
      - Auto-archive stale modules (risky, irreversible)
      - Manual pruning only (slow, requires human attention)
      - Time-based auto-delete (may remove modules that are rarely used but critical)
    rationale: |
      The colony should be cautious about self-contraction. A module that hasn't
      been touched in 7 days might still be critical for edge cases. The
      PruningDaemon produces PruningCandidate reports with confidence scores.
      Only candidates with confidence ≥ 0.70 should be considered, and the final
      decision should involve a human or GUARD_ANT review.
    consequences:
      - Stale modules are identified but never auto-removed
      - Human review required for actual pruning
      - Confidence scoring allows prioritization
