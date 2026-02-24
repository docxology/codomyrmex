import fire
import json
import sys
from pathlib import Path

import codomyrmex.performance
from .commands import Command

# Import all handlers
from .handlers import (
    check_environment,
    handle_ai_generate,
    handle_ai_refactor,
    handle_chat_session,
    handle_code_analysis,
    handle_fpf_analyze,
    handle_fpf_context,
    handle_fpf_export,
    handle_fpf_export_section,
    handle_fpf_fetch,
    handle_fpf_parse,
    handle_fpf_report,
    handle_fpf_search,
    handle_fpf_visualize,
    handle_git_analysis,
    handle_module_demo,
    handle_module_test,
    handle_orchestration_health,
    handle_orchestration_status,
    handle_project_build,
    handle_project_create,
    handle_project_list,
    handle_quick_batch,
    handle_quick_chain,
    handle_quick_pipe,
    handle_quick_run,
    handle_quick_workflow,
    handle_skills_get,
    handle_skills_list,
    handle_skills_search,
    handle_skills_sync,
    handle_workflow_create,
    list_workflows,
    run_interactive_shell,
    run_workflow,
    show_info,
    show_modules,
    show_system_status,
)
from .utils import (
    PERFORMANCE_MONITORING_AVAILABLE,
    TERMINAL_INTERFACE_AVAILABLE,
    TerminalFormatter,
    get_logger,
)

logger = get_logger(__name__)


class Cli:
    """Codomyrmex CLI"""

    def __init__(self, verbose=False, performance=False):
        """Execute   Init   operations natively."""
        if verbose:
            logger.setLevel(10)  # DEBUG level
            logger.debug("Verbose mode enabled")
        if performance and PERFORMANCE_MONITORING_AVAILABLE:
            from codomyrmex.performance.monitoring.performance_monitor import PerformanceMonitor
            monitor = PerformanceMonitor()
            logger.info("Performance monitoring enabled")
            codomyrmex.performance._performance_monitor = monitor

    def check(self):
        """Check environment setup"""
        return check_environment()

    def info(self):
        """Show project information"""
        return show_info()

    def modules(self):
        """List available modules"""
        return show_modules()

    def status(self):
        """Show comprehensive system status"""
        return show_system_status()

    def shell(self):
        """Launch interactive shell"""
        return run_interactive_shell()

    def doctor(self, pai=False, mcp=False, rasp=False, workflows=False, imports=False, all_checks=False, output_json=False):
        """Run self-diagnostics on the Codomyrmex ecosystem"""
        from .doctor import run_doctor
        return run_doctor(
            pai=pai,
            mcp=mcp,
            rasp=rasp,
            workflows=workflows,
            imports=imports,
            all_checks=all_checks,
            output_json=output_json,
        )

    def chat(self, todo="TO-DO.md", rounds=0, context=[], stream=False, resume=None):
        """Launch infinite conversation and dev_loop"""
        return handle_chat_session(
            todo_path=todo,
            rounds=rounds,
            context=context,
            stream=stream,
            resume=resume,
        )

    def workflow(self, action, name=None, template=None, params=None, async_run=False):
        """Workflow management"""
        if action == "list":
            return list_workflows()
        elif action == "run":
            run_params = {}
            if params:
                try:
                    run_params = json.loads(params)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON in --params")
                    sys.exit(1)
            return run_workflow(name, **run_params)
        elif action == "create":
            return handle_workflow_create(name, template)

    def project(self, action, name=None, template=None, description=None, path=None):
        """Project management"""
        if action == "list":
            return handle_project_list()
        elif action == "create":
            kwargs = {}
            if description:
                kwargs["description"] = description
            if path:
                kwargs["path"] = path
            return handle_project_create(name, template, **kwargs)

    def orchestration(self, action):
        """Orchestration system management"""
        if action == "status":
            return handle_orchestration_status()
        elif action == "health":
            return handle_orchestration_health()

    def ai(self, action, prompt=None, language="python", provider="openai", file=None, instruction=None):
        """AI-powered operations"""
        if action == "generate":
            return handle_ai_generate(prompt, language, provider)
        elif action == "refactor":
            return handle_ai_refactor(file, instruction)

    def analyze(self, action, path=None, output=None, repo="."):
        """Code analysis operations"""
        if action == "code":
            return handle_code_analysis(path, output)
        elif action == "git":
            return handle_git_analysis(repo)

    def build(self, action, config=None):
        """Build and synthesis operations"""
        if action == "project":
            return handle_project_build(config)

    def module(self, action, name):
        """Module-specific operations"""
        if action == "test":
            return handle_module_test(name)
        elif action == "demo":
            return handle_module_demo(name)

    def fpf(self, action, file=None, repo="ailev/FPF", branch="main", output=None, format="json", query=None, status=None, part=None, type="hierarchy", layout="hierarchical", chart_type="bar", pattern=None, depth=1, include_dependencies=False, include_analysis=True):
        """First Principles Framework operations"""
        if action == "fetch":
            return handle_fpf_fetch(repo, branch, output)
        elif action == "parse":
            return handle_fpf_parse(file, output)
        elif action == "export":
            return handle_fpf_export(file, output, format)
        elif action == "search":
            filters = {}
            if status:
                filters["status"] = status
            if part:
                filters["part"] = part
            return handle_fpf_search(query, file, filters)
        elif action == "visualize":
            return handle_fpf_visualize(file, type, output, format, layout, chart_type)
        elif action == "context":
            return handle_fpf_context(file, pattern, output, depth)
        elif action == "export-section":
            return handle_fpf_export_section(file, part, pattern, output, include_dependencies)
        elif action == "analyze":
            return handle_fpf_analyze(file, output)
        elif action == "report":
            return handle_fpf_report(file, output, include_analysis)

    def skills(self, action, force=False, category=None, name=None, output=None, query=None):
        """Skills management operations"""
        if action == "sync":
            return handle_skills_sync(force)
        elif action == "list":
            return handle_skills_list(category)
        elif action == "get":
            return handle_skills_get(category, name, output)
        elif action == "search":
            return handle_skills_search(query)

    def run(self, target, args=[], timeout=60, parallel=False, verbose=False):
        """Quick run script, module, or directory"""
        return handle_quick_run(target, args=args, timeout=timeout, parallel=parallel, verbose=verbose)

    def pipe(self, commands, continue_on_error=False):
        """Pipe commands together sequentially"""
        return handle_quick_pipe(commands, stop_on_error=not continue_on_error)

    def batch(self, targets, workers=4, timeout=60, verbose=False):
        """Run multiple targets in parallel"""
        return handle_quick_batch(targets, workers=workers, timeout=timeout, verbose=verbose)

    def chain(self, scripts, timeout=60, continue_on_error=False):
        """Chain scripts sequentially with result passing"""
        return handle_quick_chain(scripts, timeout=timeout, continue_on_error=continue_on_error)

    def exec(self, definition, params=None, verbose=False):
        """Execute workflow from definition file"""
        return handle_quick_workflow(definition, params=params, verbose=verbose)


def main():
    """Execute Main operations natively."""
    try:
        fire.Fire(Cli)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()