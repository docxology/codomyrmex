You are a focused subagent reviewer for a single holistic investigation batch.

Repository root: /Users/mini/Documents/GitHub/codomyrmex
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Batch index: 10
Batch name: Full Codebase Sweep
Batch dimensions: cross_module_architecture, convention_outlier, error_consistency, abstraction_fitness, dependency_health, test_strategy, ai_generated_debt, package_organization, high_level_elegance, mid_level_elegance, low_level_elegance, design_coherence
Batch rationale: thorough default: evaluate cross-cutting quality across all production files

Files assigned:
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/run_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/src/__init__.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/src/analyzer.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/src/main.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/src/pipeline.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/src/reporter.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/projects/test_project/src/visualizer.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/__init__.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agentic_memory/agentic_memory_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/advanced_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/agent_comparison.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/agent_diagnostics.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/agent_status.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/agent_utils.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/basic_usage.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/claude_code_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/claude_code_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/claude_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/code_editor_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/codex_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/deepseek/deepseek_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/discursive_debate.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/droid_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/evaluation/evaluation_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/gemini_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/history/history_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/jules_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/mega_swarm_dispatcher.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/mega_swarm_harvester.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/multi_agent_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/o1/o1_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/opencode_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/orchestrate.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/orchestrate_with_ollama.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/agent_personality.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/algorithm_orchestrator.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/claude_pai_bridge.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/hook_lifecycle.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/mcp_server_ops.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/memory_explorer.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/security_audit.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/skill_manifest.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/tool_invocation.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai/trust_lifecycle.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai_dashboard.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pai_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/pooling/pooling_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/qwen/qwen_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/recursive_task.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/relay_chat_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/run_all_agents.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/simulate_pai_chat.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/theory_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/verify_skill_structure.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/z3_pai_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/api_tester.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/circuit_breaker/circuit_breaker_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/examples/advanced_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/examples/basic_usage.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/mocking/mocking_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/orchestrate.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/pagination/pagination_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/api/webhooks/webhooks_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/audio/examples/basic_usage.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/audio/orchestrate.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/audits/audit_documentation.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/audits/audit_exports.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/audits/audit_imports.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/audits/audit_rasp.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/auth/auth_utils.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/auth/examples/advanced_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/auth/examples/basic_usage.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/auth/orchestrate.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/bio_simulation/run_colony.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/build_synthesis/build_utils.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/build_synthesis/examples/advanced_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/build_synthesis/examples/basic_usage.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/build_synthesis/orchestrate.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/cache/async_ops/async_ops_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/cache/cache_stats.py

Task requirements:
1. Read the blind packet and follow `system_prompt` constraints exactly.
1a. If previously flagged issues are listed above, use them as context for your review.
    Verify whether each still applies to the current code. Do not re-report fixed or
    wontfix issues. Use them as starting points to look deeper — inspect adjacent code
    and related modules for defects the prior review may have missed.
1c. Think structurally: when you spot multiple individual issues that share a common
    root cause (missing abstraction, duplicated pattern, inconsistent convention),
    explain the deeper structural issue in the finding, not just the surface symptom.
    If the pattern is significant enough, report the structural issue as its own finding
    with appropriate fix_scope ('multi_file_refactor' or 'architectural_change') and
    use `root_cause_cluster` to connect related symptom findings together.
2. Evaluate ONLY listed files and ONLY listed dimensions for this batch.
3. Return 0-12 high-quality findings for this batch (empty array allowed).
3a. Do not suppress real defects to keep scores high; report every material issue you can support with evidence.
3b. Do not default to 100. Reserve 100 for genuinely exemplary evidence in this batch.
4. Score/finding consistency is required: broader or more severe findings MUST lower dimension scores.
4a. Any dimension scored below 85.0 MUST include explicit feedback: add at least one finding with the same `dimension` and a non-empty actionable `suggestion`.
5. Every finding must include `related_files` with at least 2 files when possible.
6. Every finding must include `dimension`, `identifier`, `summary`, `evidence`, `suggestion`, and `confidence`.
7. Every finding must include `impact_scope` and `fix_scope`.
8. Every scored dimension MUST include dimension_notes with concrete evidence.
9. If a dimension score is >85.0, include `issues_preventing_higher_score` in dimension_notes.
10. Use exactly one decimal place for every assessment and abstraction sub-axis score.
9a. For package_organization, ground scoring in objective structure signals from `holistic_context.structure` (root_files fan_in/fan_out roles, directory_profiles, coupling_matrix). Prefer thresholded evidence (for example: fan_in < 5 for root stragglers, import-affinity > 60%, directories > 10 files with mixed concerns).
9b. Suggestions must include a staged reorg plan (target folders, move order, and import-update/validation commands).
11. Ignore prior chat context and any target-threshold assumptions.
12. Do not edit repository files.
13. Return ONLY valid JSON, no markdown fences.

Scope enums:
- impact_scope: "local" | "module" | "subsystem" | "codebase"
- fix_scope: "single_edit" | "multi_file_refactor" | "architectural_change"

Output schema:
{
  "batch": "Full Codebase Sweep",
  "batch_index": 10,
  "assessments": {"<dimension>": <0-100 with one decimal place>},
  "dimension_notes": {
    "<dimension>": {
      "evidence": ["specific code observations"],
      "impact_scope": "local|module|subsystem|codebase",
      "fix_scope": "single_edit|multi_file_refactor|architectural_change",
      "confidence": "high|medium|low",
      "issues_preventing_higher_score": "required when score >85.0",
      "sub_axes": {"abstraction_leverage": 0-100 with one decimal place, "indirection_cost": 0-100 with one decimal place, "interface_honesty": 0-100 with one decimal place}  // required for abstraction_fitness when evidence supports it
    }
  },
  "findings": [{
    "dimension": "<dimension>",
    "identifier": "short_id",
    "summary": "one-line defect summary",
    "related_files": ["relative/path.py"],
    "evidence": ["specific code observation"],
    "suggestion": "concrete fix recommendation",
    "confidence": "high|medium|low",
    "impact_scope": "local|module|subsystem|codebase",
    "fix_scope": "single_edit|multi_file_refactor|architectural_change",
    "root_cause_cluster": "optional_cluster_name_when_supported_by_history"
  }],
  "retrospective": {
    "root_causes": ["optional: concise root-cause hypotheses"],
    "likely_symptoms": ["optional: identifiers that look symptom-level"],
    "possible_false_positives": ["optional: prior concept keys likely mis-scoped"]
  }
}
