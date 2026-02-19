"""CLI command handlers."""

from .ai import handle_ai_generate, handle_ai_refactor
from .analysis import handle_code_analysis, handle_git_analysis, handle_module_test
from .chat import handle_chat_session
from .demos import (
    demo_ai_code_editing,
    demo_code_execution,
    demo_data_visualization,
    demo_git_operations,
    handle_module_demo,
)
from .fpf import (
    handle_fpf_analyze,
    handle_fpf_context,
    handle_fpf_export,
    handle_fpf_export_section,
    handle_fpf_fetch,
    handle_fpf_parse,
    handle_fpf_report,
    handle_fpf_search,
    handle_fpf_visualize,
)
from .orchestration import (
    handle_orchestration_health,
    handle_orchestration_status,
    handle_project_build,
    handle_project_create,
    handle_project_list,
    handle_workflow_create,
    list_workflows,
    run_workflow,
)
from .quick import (
    handle_quick_batch,
    handle_quick_chain,
    handle_quick_pipe,
    handle_quick_run,
    handle_quick_workflow,
)
from .skills import (
    handle_skills_get,
    handle_skills_list,
    handle_skills_search,
    handle_skills_sync,
)
from .system import (
    check_environment,
    run_interactive_shell,
    show_info,
    show_modules,
    show_system_status,
)
