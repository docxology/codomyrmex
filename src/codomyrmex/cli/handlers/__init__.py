from .ai import handle_ai_generate, handle_ai_refactor
from .analysis import handle_code_analysis, handle_git_analysis, handle_module_test
from .demos import handle_module_demo, demo_data_visualization, demo_ai_code_editing, demo_code_execution, demo_git_operations
from .fpf import (
    handle_fpf_fetch,
    handle_fpf_parse,
    handle_fpf_export,
    handle_fpf_search,
    handle_fpf_visualize,
    handle_fpf_context,
    handle_fpf_export_section,
    handle_fpf_analyze,
    handle_fpf_report,
)
from .orchestration import (
    handle_workflow_create,
    handle_project_create,
    handle_project_list,
    handle_orchestration_status,
    handle_orchestration_health,
    handle_project_build,
    list_workflows,
    run_workflow,
)
from .quick import (
    handle_quick_run,
    handle_quick_pipe,
    handle_quick_batch,
    handle_quick_chain,
    handle_quick_workflow,
)
from .skills import (
    handle_skills_sync,
    handle_skills_list,
    handle_skills_get,
    handle_skills_search,
)
from .system import (
    check_environment,
    show_info,
    show_modules,
    show_system_status,
    run_interactive_shell,
)
