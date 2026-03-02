import json
import sys

import fire

import codomyrmex.performance

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
    get_logger,
)

logger = get_logger(__name__)


class Cli:
    """Codomyrmex CLI"""

    def __init__(self, verbose=False, performance=False):
        if verbose:
            logger.setLevel(10)  # DEBUG level
            logger.debug("Verbose mode enabled")
        if performance and PERFORMANCE_MONITORING_AVAILABLE:
            from codomyrmex.performance.monitoring.performance_monitor import (
                PerformanceMonitor,
            )
            monitor = PerformanceMonitor()
            logger.info("Performance monitoring enabled")
            codomyrmex.performance._performance_monitor = monitor

    def check(self):
        """Check environment setup and dependencies"""
        return check_environment()

    def info(self):
        """Show platform information and available tools"""
        return show_info()

    def modules(self):
        """List all available modules and their descriptions"""
        return show_modules()

    def status(self):
        """Show comprehensive system status dashboard"""
        return show_system_status()

    def dashboard(self, port=8787, host="0.0.0.0", open=True):
        """Launch the Codomyrmex web dashboard"""
        import subprocess
        from pathlib import Path

        script = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "website" / "launch_dashboard.py"
        if not script.exists():
            print(f"❌ Dashboard script not found: {script}")
            return 1

        cmd = [sys.executable, str(script), f"--port={port}", f"--host={host}"]
        if open:
            cmd.append("--open")
        try:
            print(f"🚀 Launching dashboard on http://{host}:{port}...")
            subprocess.run(cmd, check=False)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
        return 0

    def shell(self):
        """Launch the interactive codomyrmex> REPL shell"""
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

    def chat(self, todo="TODO.md", rounds=0, context=None, stream=False, resume=None):
        """Launch infinite conversation and dev_loop for AI agent interaction"""
        if context is None:
            context = []
        return handle_chat_session(
            todo_path=todo,
            rounds=rounds,
            context=context,
            stream=stream,
            resume=resume,
        )

    def workflow(self, action, name=None, template=None, params=None):
        """Workflow management (list, run, create)"""
        if action == "list":
            return list_workflows()
        elif action == "run":
            if not name:
                print("❌ Must specify a workflow name to run")
                return False
            run_params = {}
            if params:
                try:
                    run_params = json.loads(params)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON in --params")
                    return False
            return run_workflow(name, **run_params)
        elif action == "create":
            if not name:
                print("❌ Must specify a name for the new workflow")
                return False
            return handle_workflow_create(name, template)
        else:
            print(f"❌ Unknown workflow action: {action}")
            return False

    def project(self, action, name=None, template=None, description=None, path=None):
        """Project management (list, create)"""
        if action == "list":
            return handle_project_list()
        elif action == "create":
            if not name:
                print("❌ Must specify a project name")
                return False
            kwargs = {}
            if description:
                kwargs["description"] = description
            if path:
                kwargs["path"] = path
            return handle_project_create(name, template or "ai_analysis", **kwargs)
        else:
            print(f"❌ Unknown project action: {action}")
            return False

    def orchestration(self, action):
        """Orchestration system management (status, health)"""
        if action == "status":
            return handle_orchestration_status()
        elif action == "health":
            return handle_orchestration_health()
        else:
            print(f"❌ Unknown orchestration action: {action}")
            return False

    def ai(self, action, prompt=None, language="python", provider="openai", file=None, instruction=None):
        """AI-powered operations (generate, refactor)"""
        if action == "generate":
            if not prompt:
                print("❌ Must specify a prompt for generation")
                return False
            return handle_ai_generate(prompt, language, provider)
        elif action == "refactor":
            if not file or not instruction:
                print("❌ Must specify both --file and --instruction for refactoring")
                return False
            return handle_ai_refactor(file, instruction)
        else:
            print(f"❌ Unknown ai action: {action}")
            return False

    def analyze(self, action, path=".", output=None, repo="."):
        """Code and git analysis operations (code, git)"""
        if action == "code":
            return handle_code_analysis(path, output)
        elif action == "git":
            return handle_git_analysis(repo)
        else:
            print(f"❌ Unknown analyze action: {action}")
            return False

    def build(self, action="project", config=None):
        """Build and synthesis operations"""
        if action == "project":
            return handle_project_build(config)
        else:
            print(f"❌ Unknown build action: {action}")
            return False

    def test(self, module_name):
        """Run tests for a specific module"""
        return handle_module_test(module_name)

    def demo(self, module_name):
        """Run demonstration for a specific module"""
        return handle_module_demo(module_name)

    def fpf(self, action, file=None, repo="ailev/FPF", branch="main", output=None, format="json", query=None, status=None, part=None, type="hierarchy", layout="hierarchical", chart_type="bar", pattern=None, depth=1, include_dependencies=False, include_analysis=True):
        """First Principles Framework operations (fetch, parse, export, search, etc.)"""
        if action == "fetch":
            return handle_fpf_fetch(repo, branch, output)
        elif action == "parse":
            if not file:
                print("❌ Must specify --file to parse")
                return False
            return handle_fpf_parse(file, output)
        elif action == "export":
            if not file or not output:
                print("❌ Must specify --file and --output for export")
                return False
            return handle_fpf_export(file, output, format)
        elif action == "search":
            if not query:
                print("❌ Must specify --query to search")
                return False
            filters = {}
            if status:
                filters["status"] = status
            if part:
                filters["part"] = part
            return handle_fpf_search(query, file, filters)
        elif action == "visualize":
            if not file or not output:
                print("❌ Must specify --file and --output for visualization")
                return False
            return handle_fpf_visualize(file, type, output, format, layout, chart_type)
        elif action == "context":
            if not file:
                print("❌ Must specify --file for context")
                return False
            return handle_fpf_context(file, pattern, output, depth)
        elif action == "export-section":
            if not file or not output:
                print("❌ Must specify --file and --output for export-section")
                return False
            return handle_fpf_export_section(file, part, pattern, output, include_dependencies)
        elif action == "analyze":
            if not file:
                print("❌ Must specify --file for analysis")
                return False
            return handle_fpf_analyze(file, output)
        elif action == "report":
            if not file or not output:
                print("❌ Must specify --file and --output for report")
                return False
            return handle_fpf_report(file, output, include_analysis)
        else:
            print(f"❌ Unknown fpf action: {action}")
            return False

    def skills(self, action, force=False, category=None, name=None, output=None, query=None):
        """Skills management operations (sync, list, get, search)"""
        if action == "sync":
            return handle_skills_sync(force)
        elif action == "list":
            return handle_skills_list(category)
        elif action == "get":
            if not category or not name:
                print("❌ Must specify both --category and --name to get a skill")
                return False
            return handle_skills_get(category, name, output)
        elif action == "search":
            if not query:
                print("❌ Must specify --query to search skills")
                return False
            return handle_skills_search(query)
        else:
            print(f"❌ Unknown skills action: {action}")
            return False

    def run(self, target, args=None, timeout=60, parallel=False, verbose=False):
        """Quick run script, module, or directory"""
        if args is None:
            args = []
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
    """Run the Codomyrmex CLI entry point."""
    try:
        fire.Fire(Cli)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"💥 An unexpected error occurred: {e}", file=sys.stderr)
        if "--verbose" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
