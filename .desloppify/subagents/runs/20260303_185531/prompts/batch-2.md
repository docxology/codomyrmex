You are a focused subagent reviewer for a single holistic investigation batch.

Repository root: /Users/mini/Documents/GitHub/codomyrmex
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Batch index: 2
Batch name: Conventions & Errors
Batch dimensions: convention_outlier, error_consistency, mid_level_elegance
Batch rationale: naming drift, behavioral outliers, mixed error strategies

Files assigned:
- projects/test_project/src/__init__.py
- projects/test_project/tests/__init__.py
- projects/test_project/tests/test_codomyrmex_integration.py
- scripts/__init__.py
- scripts/agents/agent_utils.py
- scripts/agents/discursive_debate.py
- scripts/agents/mega_swarm_harvester.py
- scripts/agents/recursive_task.py
- scripts/bio_simulation/run_colony.py
- scripts/config_monitoring/orchestrate.py
- scripts/defense/demo_orchestrator.py
- scripts/docs_gen/orchestrate_docs.py
- scripts/documentation/enrich_thin_readmes.py
- scripts/documentation/fix_install_sections.py
- scripts/edge_computing/orchestrator.py
- scripts/finance/orchestrator.py
- scripts/maintenance/update_overview.py
- scripts/maintenance/verify_index.py
- scripts/orchestrator/__init__.py
- scripts/rna/find_missing_samples.py
- scripts/verification/verify_phase1.py
- scripts/verification/verify_phase2.py
- scripts/agents/mega_swarm_dispatcher.py
- scripts/config_audits/run_audit.py
- scripts/container_optimization/orchestrator.py
- scripts/dependency_injection/orchestrator.py
- scripts/docs/remediate_documentation.py
- scripts/documentation/deepen_src_docs.py
- scripts/documentation/enrich_docs_layer.py
- scripts/documentation/enrich_module_docs.py
- scripts/documentation/enrich_spec_and_submodules.py
- scripts/documentation/enrich_src_docs.py
- scripts/documentation/fix_docs_readmes.py
- scripts/documentation/fix_formatting.py
- scripts/documentation/fix_readme_quality.py
- scripts/documentation/improve_crossrefs.py
- scripts/email/orchestrator.py
- scripts/ide/antigravity/gui_chat.py
- scripts/identity/orchestrator.py
- scripts/maintenance/audit_stubs.py
- scripts/maintenance/fix_llm_rasp.py
- scripts/maintenance/fix_nested_rasp.py
- scripts/maintenance/generate_configs.py
- scripts/maintenance/sync_docs.py
- scripts/model_context_protocol/verify_dynamic_mcp.py
- scripts/orchestrator/workflows/__init__.py
- scripts/performance/benchmark_startup.py
- scripts/verification/verify_phase3.py
- scripts/run_all_scripts.py

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
3. Return 0-10 high-quality findings for this batch (empty array allowed).
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
11. Ignore prior chat context and any target-threshold assumptions.
12. Do not edit repository files.
13. Return ONLY valid JSON, no markdown fences.

Scope enums:
- impact_scope: "local" | "module" | "subsystem" | "codebase"
- fix_scope: "single_edit" | "multi_file_refactor" | "architectural_change"

Output schema:
{
  "batch": "Conventions & Errors",
  "batch_index": 2,
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
