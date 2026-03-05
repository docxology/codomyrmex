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
    handle_rules_check,
    handle_rules_list,
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

        script = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "scripts"
            / "website"
            / "launch_dashboard.py"
        )
        if not script.exists():
            print(f"❌ Dashboard script not found: {script}")
            return 1

        cmd = [sys.executable, str(script), f"--port={port}", f"--host={host}"]
        if open:
            cmd.append("--open")
        try:
            print(f"🚀 Launching dashboard on http://{host}:{port}...")
            subprocess.run(cmd, check=False, timeout=300)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
        return 0

    def shell(self):
        """Launch the interactive codomyrmex> REPL shell"""
        return run_interactive_shell()

    def doctor(
        self,
        pai=False,
        mcp=False,
        rasp=False,
        workflows=False,
        imports=False,
        all_checks=False,
        output_json=False,
    ):
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

    class workflow:
        """Workflow management subcommands"""

        def list(self):
            """List all available workflows"""
            return list_workflows()

        def run(self, name: str, params: str = ""):
            """Run a named workflow (params as JSON string)"""
            run_params: dict = {}
            if params:
                try:
                    run_params = json.loads(params)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON in params")
                    return False
            return run_workflow(name, **run_params)

        def create(self, name: str, template: str = ""):
            """Create a new workflow from an optional template"""
            return handle_workflow_create(name, template or None)

    class project:
        """Project management subcommands"""

        def list(self):
            """List all projects"""
            return handle_project_list()

        def create(
            self,
            name: str,
            template: str = "ai_analysis",
            description: str = "",
            path: str = "",
        ):
            """Create a new project"""
            kwargs = {}
            if description:
                kwargs["description"] = description
            if path:
                kwargs["path"] = path
            return handle_project_create(name, template, **kwargs)

    class orchestration:
        """Orchestration system management"""

        def status(self):
            """Show orchestration system status"""
            return handle_orchestration_status()

        def health(self):
            """Check orchestration system health"""
            return handle_orchestration_health()

    class ai:
        """AI-powered operations"""

        def generate(
            self, prompt: str, language: str = "python", provider: str = "openai"
        ):
            """Generate code from a prompt"""
            return handle_ai_generate(prompt, language, provider)

        def refactor(self, file: str, instruction: str):
            """Refactor a file given an instruction"""
            return handle_ai_refactor(file, instruction)

    class analyze:
        """Code and git analysis operations"""

        def code(self, path: str = ".", output: str = ""):
            """Analyze code quality at path"""
            return handle_code_analysis(path, output or None)

        def git(self, repo: str = "."):
            """Analyze git history for a repository"""
            return handle_git_analysis(repo)

    class build:
        """Build and synthesis operations"""

        def project(self, config: str = ""):
            """Build the project using an optional config file"""
            return handle_project_build(config or None)

    class fpf:
        """First Principles Framework operations"""

        def fetch(
            self, repo: str = "ailev/FPF", branch: str = "main", output: str = ""
        ):
            """Fetch the FPF repository"""
            return handle_fpf_fetch(repo, branch, output or None)

        def parse(self, file: str, output: str = ""):
            """Parse an FPF file"""
            return handle_fpf_parse(file, output or None)

        def export(self, file: str, output: str, format: str = "json"):
            """Export an FPF file to a given format"""
            return handle_fpf_export(file, output, format)

        def search(self, query: str, file: str = "", status: str = "", part: str = ""):
            """Search within an FPF file"""
            filters: dict = {}
            if status:
                filters["status"] = status
            if part:
                filters["part"] = part
            return handle_fpf_search(query, file or None, filters)

        def visualize(
            self,
            file: str,
            output: str,
            type: str = "hierarchy",
            format: str = "json",
            layout: str = "hierarchical",
            chart_type: str = "bar",
        ):
            """Visualize an FPF file"""
            return handle_fpf_visualize(file, type, output, format, layout, chart_type)

        def context(
            self, file: str, output: str = "", pattern: str = "", depth: int = 1
        ):
            """Show context for an FPF file"""
            return handle_fpf_context(file, pattern or None, output or None, depth)

        def export_section(
            self,
            file: str,
            output: str,
            part: str = "",
            pattern: str = "",
            include_dependencies: bool = False,
        ):
            """Export a section of an FPF file"""
            return handle_fpf_export_section(
                file, part or None, pattern or None, output, include_dependencies
            )

        def analyze(self, file: str, output: str = ""):
            """Analyze an FPF file"""
            return handle_fpf_analyze(file, output or None)

        def report(self, file: str, output: str, include_analysis: bool = True):
            """Generate a report from an FPF file"""
            return handle_fpf_report(file, output, include_analysis)

    class skills:
        """Skills management operations"""

        def sync(self, force: bool = False):
            """Sync available skills"""
            return handle_skills_sync(force)

        def list(self, category: str = ""):
            """List available skills, optionally filtered by category"""
            return handle_skills_list(category or None)

        def get(self, category: str, name: str, output: str = ""):
            """Get a specific skill by category and name"""
            return handle_skills_get(category, name, output or None)

        def search(self, query: str):
            """Search skills by query"""
            return handle_skills_search(query)

    class rules:
        """Rules management — query .cursorrules governance hierarchy"""

        def list(self):
            """List all rules with their priority and file path"""
            return handle_rules_list()

        def check(self, file: str):
            """Check applicable rules for a given file path"""
            return handle_rules_check(file)

    def test(self, module_name):
        """Run tests for a specific module"""
        return handle_module_test(module_name)

    def demo(self, module_name):
        """Run demonstration for a specific module"""
        return handle_module_demo(module_name)

    def run(self, target, args=None, timeout=60, parallel=False, verbose=False):
        """Quick run script, module, or directory"""
        if args is None:
            args = []
        return handle_quick_run(
            target, args=args, timeout=timeout, parallel=parallel, verbose=verbose
        )

    def pipe(self, commands, continue_on_error=False):
        """Pipe commands together sequentially"""
        return handle_quick_pipe(commands, stop_on_error=not continue_on_error)

    def batch(self, targets, workers=4, timeout=60, verbose=False):
        """Run multiple targets in parallel"""
        return handle_quick_batch(
            targets, workers=workers, timeout=timeout, verbose=verbose
        )

    def chain(self, scripts, timeout=60, continue_on_error=False):
        """Chain scripts sequentially with result passing"""
        return handle_quick_chain(
            scripts, timeout=timeout, continue_on_error=continue_on_error
        )

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


if __name__ == "__main__":
    main()
