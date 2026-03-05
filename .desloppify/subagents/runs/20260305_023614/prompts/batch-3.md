You are a focused subagent reviewer for a single holistic investigation batch.

Repository root: /Users/mini/Documents/GitHub/codomyrmex
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Batch index: 3
Batch name: Abstractions & Dependencies
Batch dimensions: abstraction_fitness, dependency_health, mid_level_elegance, low_level_elegance
Batch rationale: abstraction hotspots (wrappers/interfaces/param bags), dep cycles

Files assigned:
- src/codomyrmex/data_visualization/utils.py
- src/codomyrmex/wallet/contracts/utils.py
- src/codomyrmex/tests/unit/agents/helpers.py
- src/codomyrmex/quantization/utils.py
- src/codomyrmex/cerebrum/core/utils.py
- src/codomyrmex/agents/ai_code_editing/ai_code_helpers/utils.py
- src/codomyrmex/cloud/coda_io/mixins/utils.py
- src/codomyrmex/cli/utils.py
- src/codomyrmex/website/accessibility/utils.py
- src/codomyrmex/agents/cli/handlers.py
- src/codomyrmex/tests/unit/encryption/test_encryption.py
- src/codomyrmex/tests/unit/edge_computing/test_edge_computing.py
- src/codomyrmex/testing/mcp_tools.py
- src/codomyrmex/tests/unit/agents/cli/test_handlers.py
- src/codomyrmex/tests/unit/smart_contracts/test_smart_contracts.py
- src/codomyrmex/tests/performance/test_benchmarking.py
- src/codomyrmex/tests/unit/agents/test_claude_client.py
- src/codomyrmex/tests/unit/api/mocking/test_mocking.py
- src/codomyrmex/tests/unit/documents/test_documents_chunking.py
- src/codomyrmex/tests/unit/agentic_memory/obsidian/test_commands.py
- src/codomyrmex/tests/unit/agentic_memory/obsidian/test_plugins.py
- src/codomyrmex/tests/unit/agentic_memory/obsidian/test_workspace.py
- src/codomyrmex/tests/unit/cloud/_stubs.py
- src/codomyrmex/tests/unit/email/test_email.py
- src/codomyrmex/tests/integration/data_visualization/test_visualization_performance.py
- src/codomyrmex/tests/integration/git_operations/verify_git_methods.py
- src/codomyrmex/tests/unit/agentic_memory/obsidian/test_daily_notes.py
- src/codomyrmex/tests/unit/api/webhooks/test_webhooks_direct.py
- src/codomyrmex/tests/unit/deployment/test_deployment_manager_core.py
- src/codomyrmex/tests/unit/agents/claude/test_claude_mixins.py
- src/codomyrmex/tests/unit/coding/test_metrics_mixin.py
- src/codomyrmex/security/digital/security_analyzer.py
- src/codomyrmex/agents/droid/generators/physical_generators/tasks.py
- src/codomyrmex/tests/performance/test_benchmarks.py
- src/codomyrmex/tests/unit/examples/conftest.py
- src/codomyrmex/telemetry/exporters/otlp_exporter.py
- src/codomyrmex/tests/unit/cloud/test_infomaniak_dns.py
- src/codomyrmex/tests/unit/cloud/test_infomaniak_network.py
- src/codomyrmex/tests/unit/logistics/test_orchestration_engine.py
- src/codomyrmex/cerebrum/fpf/orchestration.py
- src/codomyrmex/tests/unit/cloud/test_infomaniak_object_storage.py
- src/codomyrmex/llm/providers/__init__.py
- src/codomyrmex/tests/unit/events/test_events_comprehensive.py
- src/codomyrmex/tests/unit/cloud/test_infomaniak_orchestration.py
- src/codomyrmex/tests/unit/agents/test_mcp_discovery.py
- src/codomyrmex/tests/unit/cloud/test_infomaniak_metering.py
- src/codomyrmex/tests/unit/cloud/test_infomaniak_identity.py
- src/codomyrmex/ide/antigravity/live_bridge.py
- src/codomyrmex/utils/process/script_base.py
- src/codomyrmex/data_visualization/git/git_visualizer.py
- src/codomyrmex/agentic_memory/obsidian/tasks.py
- src/codomyrmex/events/emitters/event_emitter.py
- src/codomyrmex/data_visualization/engines/_line_bar.py
- src/codomyrmex/cloud/infomaniak/network/client.py
- src/codomyrmex/agentic_memory/obsidian/properties.py
- src/codomyrmex/ci_cd_automation/pipeline/async_manager.py
- src/codomyrmex/utils/process/subprocess.py
- src/codomyrmex/agents/ai_code_editing/ai_code_helpers/generation.py
- src/codomyrmex/agentic_memory/obsidian/cli_search.py
- scripts/llm/examples/openrouter_chat.py
- src/codomyrmex/agents/orchestrator.py
- src/codomyrmex/utils/retry.py
- src/codomyrmex/agents/ai_code_editing/ai_code_helpers/analysis.py
- src/codomyrmex/agentic_memory/obsidian/daily_notes.py
- src/codomyrmex/orchestrator/execution/parallel_runner.py
- src/codomyrmex/git_operations/api/github/issues.py
- src/codomyrmex/cloud/coda_io/mixins/pages.py
- src/codomyrmex/git_operations/api/github/pull_requests.py
- src/codomyrmex/logistics/orchestration/project/documentation_generator.py
- src/codomyrmex/tests/unit/website/unit/test_api_handler.py
- src/codomyrmex/tests/unit/website/unit/test_health_handler.py
- src/codomyrmex/collaboration/protocols/__init__.py
- src/codomyrmex/tests/unit/collaboration/test_collaboration_comprehensive.py
- src/codomyrmex/plugin_system/validation/__init__.py
- src/codomyrmex/plugin_system/validation/enforcer.py
- src/codomyrmex/tests/unit/ci_cd_automation/test_ci_cd_enhancements.py
- src/codomyrmex/tests/unit/utils/test_cli_helpers.py
- src/codomyrmex/api/openapi_generator.py
- src/codomyrmex/api/openapi_standardization_generator.
- src/codomyrmex/dependency_injection/container.py

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
  "batch": "Abstractions & Dependencies",
  "batch_index": 3,
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
