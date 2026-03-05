FILES=(
  projects/test_project/tests/test_analyzer.py
  projects/test_project/tests/conftest.py
  scripts/utils/verify_structure_parity.py
  scripts/validation/dependency_analyzer.py
  scripts/validation/examples/advanced_workflow.py
  scripts/validation/examples/basic_usage.py
  scripts/validation/orchestrate.py
  scripts/validation/rules/rules_demo.py
  scripts/validation/sanitizers/sanitizers_demo.py
  scripts/validation/schemas/schemas_demo.py
  scripts/validation/validate_data.py
  scripts/validation/validate_dependencies.py
  scripts/verification/verify_phase1.py
  scripts/verification/verify_phase2.py
  scripts/verification/verify_phase3.py
  scripts/verification/verify_secure_agent_system.py
  scripts/video/examples/basic_usage.py
  scripts/video/orchestrate.py
  scripts/website/examples/advanced_workflow.py
  scripts/website/examples/basic_usage.py
  scripts/website/launch_dashboard.py
  scripts/website/orchestrate.py
  scripts/website/website_utils.py
  scripts/workflow_execution/workflow_runner.py
  scripts/workflow_testing/workflow_testing_demo.py
  src/codomyrmex/environment_setup/__init__.py
  src/codomyrmex/logistics/orchestration/project/mcp_tools.py
  src/codomyrmex/module_template/scaffold.py
  src/codomyrmex/tests/integration/calendar_integration/test_mcp_tools.py
  src/codomyrmex/tests/integration/cli/test_cli_commands.py
  src/codomyrmex/tests/integration/git_operations/test_github_functionality_demo.py
  src/codomyrmex/tests/integration/git_operations/test_github_operations_demo.py
  src/codomyrmex/tests/integration/git_operations/test_real_github_repos.py
  src/codomyrmex/tests/integration/security/test_security_integration.py
  src/codomyrmex/tests/unit/agentic_memory/test_consolidation.py
  src/codomyrmex/tests/unit/agentic_memory/test_rule_content_validation.py
  src/codomyrmex/tests/unit/graph_rag/test_mcp_tools.py
  src/codomyrmex/tests/unit/p3_remediation/test_p3_file_permissions.py
  src/codomyrmex/tests/unit/p3_remediation/test_p3_illegal_raise_guards.py
)

for f in "${FILES[@]}"; do
  if [ -f "$f" ]; then
    uv run ruff check --fix "$f" || true
    uv run ruff format "$f" || true
  fi
done
