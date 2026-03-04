You are a focused subagent reviewer for a single holistic investigation batch.

Repository root: /Users/mini/Documents/GitHub/codomyrmex
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Batch index: 10
Batch name: Full Codebase Sweep
Batch dimensions: cross_module_architecture, convention_outlier, error_consistency, abstraction_fitness, dependency_health, test_strategy, ai_generated_debt, package_organization, high_level_elegance, mid_level_elegance, low_level_elegance, design_coherence
Batch rationale: thorough default: evaluate cross-cutting quality across all production files

Files assigned:
- fix_docstrings_v2.py
- list_all_models.py
- list_models.py
- patch_basic_usage.py
- patch_docs.py
- projects/test_project/run_demo.py
- projects/test_project/src/__init__.py
- projects/test_project/src/analyzer.py
- projects/test_project/src/main.py
- projects/test_project/src/pipeline.py
- projects/test_project/src/reporter.py
- projects/test_project/src/visualizer.py
- scripts/__init__.py
- scripts/agentic_memory/agentic_memory_demo.py
- scripts/agents/advanced_workflow.py
- scripts/agents/agent_comparison.py
- scripts/agents/agent_diagnostics.py
- scripts/agents/agent_status.py
- scripts/agents/agent_utils.py
- scripts/agents/basic_usage.py
- scripts/agents/claude_code_demo.py
- scripts/agents/claude_code_workflow.py
- scripts/agents/claude_example.py
- scripts/agents/code_editor_example.py
- scripts/agents/codex_example.py
- scripts/agents/deepseek/deepseek_demo.py
- scripts/agents/discursive_debate.py
- scripts/agents/droid_example.py
- scripts/agents/evaluation/evaluation_demo.py
- scripts/agents/gemini_example.py
- scripts/agents/history/history_demo.py
- scripts/agents/jules_example.py
- scripts/agents/mega_swarm_dispatcher.py
- scripts/agents/mega_swarm_harvester.py
- scripts/agents/multi_agent_workflow.py
- scripts/agents/o1/o1_demo.py
- scripts/agents/opencode_example.py
- scripts/agents/orchestrate.py
- scripts/agents/orchestrate_with_ollama.py
- scripts/agents/pai/agent_personality.py
- scripts/agents/pai/algorithm_orchestrator.py
- scripts/agents/pai/claude_pai_bridge.py
- scripts/agents/pai/hook_lifecycle.py
- scripts/agents/pai/mcp_server_ops.py
- scripts/agents/pai/memory_explorer.py
- scripts/agents/pai/security_audit.py
- scripts/agents/pai/skill_manifest.py
- scripts/agents/pai/tool_invocation.py
- scripts/agents/pai/trust_lifecycle.py
- scripts/agents/pai_dashboard.py
- scripts/agents/pai_example.py
- scripts/agents/pooling/pooling_demo.py
- scripts/agents/qwen/qwen_demo.py
- scripts/agents/recursive_task.py
- scripts/agents/relay_chat_demo.py
- scripts/agents/run_all_agents.py
- scripts/agents/simulate_pai_chat.py
- scripts/agents/theory_example.py
- scripts/agents/verify_skill_structure.py
- scripts/agents/z3_pai_example.py
- scripts/api/api_tester.py
- scripts/api/circuit_breaker/circuit_breaker_demo.py
- scripts/api/examples/advanced_workflow.py
- scripts/api/examples/basic_usage.py
- scripts/api/mocking/mocking_demo.py
- scripts/api/orchestrate.py
- scripts/api/pagination/pagination_demo.py
- scripts/api/webhooks/webhooks_demo.py
- scripts/audio/examples/basic_usage.py
- scripts/audio/orchestrate.py
- scripts/audits/audit_documentation.py
- scripts/audits/audit_exports.py
- scripts/audits/audit_imports.py
- scripts/audits/audit_rasp.py
- scripts/auth/auth_utils.py
- scripts/auth/examples/advanced_workflow.py
- scripts/auth/examples/basic_usage.py
- scripts/auth/orchestrate.py
- scripts/bio_simulation/run_colony.py
- scripts/build_synthesis/build_utils.py

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
