You are a focused subagent reviewer for a single holistic investigation batch.

Repository root: /Users/mini/Documents/GitHub/codomyrmex
Blind packet: /Users/mini/Documents/GitHub/codomyrmex/.desloppify/review_packet_blind.json
Batch index: 1
Batch name: Architecture & Coupling
Batch dimensions: cross_module_architecture, high_level_elegance
Batch rationale: god modules, import-time side effects

Files assigned:
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/src/codomyrmex/data_visualization/plots/_base.py
- .claude/worktrees/agent-a2169dc4/src/codomyrmex/data_visualization/plots/_base.py
- .claude/worktrees/agent-a7acc629/src/codomyrmex/data_visualization/plots/_base.py
- .claude/worktrees/agent-a8fb956a/src/codomyrmex/data_visualization/plots/_base.py
- .claude/worktrees/agent-ac1aa160/src/codomyrmex/data_visualization/plots/_base.py
- src/codomyrmex/data_visualization/plots/_base.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/src/codomyrmex/exceptions/base.py
- .claude/worktrees/agent-a2169dc4/src/codomyrmex/exceptions/base.py
- .claude/worktrees/agent-a7acc629/src/codomyrmex/exceptions/base.py
- .claude/worktrees/agent-a8fb956a/src/codomyrmex/exceptions/base.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agentic_memory/agentic_memory_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/advanced_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/agent_diagnostics.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/agent_status.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/basic_usage.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/claude_code_workflow.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/claude_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/code_editor_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/codex_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/deepseek/deepseek_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/droid_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/evaluation/evaluation_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/gemini_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/history/history_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/jules_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/mega_swarm_harvester.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/o1/o1_demo.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/opencode_example.py
- .claude/worktrees/agent-a2169dc4/.claude/worktrees/agent-a81fc169/scripts/agents/orchestrate.py

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
  "batch": "Architecture & Coupling",
  "batch_index": 1,
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
