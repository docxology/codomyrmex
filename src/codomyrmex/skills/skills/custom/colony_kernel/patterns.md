# Colony Kernel Patterns
# Proven patterns for using the colony control plane effectively

patterns:
  - name: Propose-Record-Tick Lifecycle
    description: The canonical agent action lifecycle — propose, execute, record, tick
    when: Any agent wants to perform an action on the codebase
    example: |
      # 1. Propose the action
      result = colony_propose_action(
          agent_id="engineer-1",
          action_type="patch_file",
          target="codomyrmex.git_operations.core",
          rationale="Fix off-by-one error in branch name parser",
          rollback_plan="git revert HEAD~1",
          evidence={"test_ids": ["test_slash_in_name"]}
      )

      # 2. If EXECUTE, perform the action, then record outcome
      if result["decision"] == "execute":
          # ... perform the action ...
          colony_record_outcome(
              agent_id="engineer-1",
              action_type="patch_file",
              target="codomyrmex.git_operations.core",
              actual_outcome="Patch applied; all 42 tests pass",
              tests_passed=True
          )

      # 3. Periodically advance the colony clock
      colony_tick()

  - name: Pre-flight Plan Validation
    description: Use colony_falsify_plan to validate a plan before formal gate submission
    when: Agent wants to check a plan without consuming gate resources or affecting trust
    example: |
      plan = {
          "action_type": "patch_file",
          "target": "codomyrmex.core.parser",
          "rationale": "Fix recursive descent parser for empty token streams",
          "rollback_plan": "git revert HEAD --no-edit",
          "evidence": {"test_id": "T-042", "error": "IndexError on line 87"},
          "budget_estimate": {"llm_calls": 2, "runtime_seconds": 30.0}
      }
      result = colony_falsify_plan(json.dumps(plan))
      # result["recommendation"] → "execute" / "hold" / "refuse"
      # result["findings"] → list of adversarial findings with remediation

  - name: Trust-Aware Dispatch
    description: Check agent profile before dispatching sensitive operations
    when: Dispatching tasks that require elevated trust (security, deployment, merge)
    example: |
      ```mermaid
      flowchart LR
          P["colony_agent_profile(id)"] --> R{"role ≥ DISPATCHER?"}
          R -->|"Yes, trust ≥ 0.50"| DISPATCH["Dispatch sensitive task"]
          R -->|"No, trust < 0.50"| QUEUE["Queue for review<br/>or escalate to human"]
          QUEUE -->|"Trust builds over time"| P
      ```

      profile = colony_agent_profile("repair-agent-42")
      if profile["trust_score"] >= 0.50 and profile["role"] in ("dispatcher", "guard_ant"):
          # Agent has sufficient trust for sensitive operations
          dispatch_task(agent_id="repair-agent-42", task=task)
      else:
          # Route to lower-priority queue or escalate to human
          queue_for_review(agent_id="repair-agent-42", task=task)

  - name: Pheromone-Guided Target Selection
    description: Query the pheromone field to avoid locations with high failure pressure
    when: Choosing which module to work on, or investigating why a location is hard to pass
    example: |
      failures = colony_pheromone_query("codomyrmex.git_operations.core", "failure")
      if failures and failures[0]["strength"] > 3.0:
          # This location has accumulated failure signals — proceed with caution
          # Consider: is this a genuinely risky module, or are signals stale?
          check_age = time.time() - failures[0]["last_reinforced"]
          if check_age > 7 * 86400:
              # Signals are >7 days old — may be stale, try with extra evidence
              pass

  - name: Budget-Aware Proposal
    description: Include realistic budget estimates to avoid HOLD
    when: Proposing actions that consume significant resources (LLM calls, runtime)
    example: |
      result = colony_propose_action(
          agent_id="researcher-1",
          action_type="exec_code",
          target="codomyrmex.research.loop",
          rationale="Run literature search for active inference papers",
          rollback_plan="Kill the process if it exceeds time limit",
          budget_estimate={"llm_calls": 10, "runtime_seconds": 300.0, "risk_level": 0.2}
      )
      # If HOLD due to budget, check required_evidence for which dimension was violated

  - name: Multi-Agent Coordination via Pheromone
    description: Use pheromone field as shared state for multi-agent coordination
    when: Multiple agents need to coordinate without direct communication
    example: |
      # Agent A deposits a NEED signal
      colony_pheromone_query("codomyrmex.module_x", "need")  # sense existing need

      # Agent B senses the NEED and responds
      needs = colony_pheromone_query("codomyrmex.module_x", "need")
      if needs and needs[0]["strength"] > 1.0:
          # Someone needs help here — propose work at this location
          colony_propose_action(agent_id="agent-b", target="codomyrmex.module_x", ...)

  - name: Pruning-Guided Refactoring
    description: Use pruning_report to identify stale modules for cleanup
    when: Planning refactoring or deprecation work
    example: |
      report = colony_pruning_report()
      for candidate in report["candidates"]:
          if candidate["confidence"] >= 0.7:
              # High-confidence stale module — flag for review
              print(f"Stale: {candidate['module_path']} — {candidate['reason']}")
