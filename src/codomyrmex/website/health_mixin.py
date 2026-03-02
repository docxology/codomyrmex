"""Health, pipeline, and LLM config mixin for DataProvider.

Extracted from data_provider.py for modularity. This mixin provides:
- get_pipeline_status(): CI/CD workflow scanning
- get_health_status(): comprehensive system health
- get_llm_config(): LLM configuration
- run_tests(): pytest runner with JUnit XML parsing
"""

from __future__ import annotations

import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL
from codomyrmex.llm.ollama.config_manager import ConfigManager
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class HealthProviderMixin:
    """Mixin providing health, pipeline, and LLM config methods."""

    def get_pipeline_status(self) -> list[dict[str, Any]]:
        """Scan .github/workflows/ for real CI/CD workflow definitions."""
        workflows_dir = self.root_dir / ".github" / "workflows"
        if not workflows_dir.exists():
            return []

        pipelines = []
        counter = 0
        for wf_file in sorted(workflows_dir.glob("*.yml")):
            try:
                content = wf_file.read_text(encoding="utf-8")
                try:
                    data = yaml.safe_load(content)
                except Exception:
                    data = None

                if not isinstance(data, dict):
                    # Fallback for files with heredocs or other constructs
                    # that break yaml.safe_load()
                    fallback = self._parse_workflow_fallback(content, wf_file.stem)
                    if fallback is None:
                        continue
                    name = fallback["name"]
                    trigger_list = fallback["triggers"]
                    stages = fallback["stages"]
                else:
                    name = data.get("name", wf_file.stem)
                    # YAML parses bare 'on' key as boolean True
                    triggers = data.get("on") or data.get(True) or {}
                    if isinstance(triggers, str):
                        trigger_list = [triggers]
                    elif isinstance(triggers, list):
                        trigger_list = triggers
                    elif isinstance(triggers, dict):
                        trigger_list = list(triggers.keys())
                    else:
                        trigger_list = []

                    jobs = data.get("jobs", {})
                    stages = [
                        {"name": job_name, "status": "defined"}
                        for job_name in jobs
                    ] if isinstance(jobs, dict) else []

                counter += 1
                pipelines.append({
                    "id": f"wf-{counter:04d}",
                    "name": name,
                    "status": "defined",
                    "file": str(wf_file.relative_to(self.root_dir)),
                    "triggers": trigger_list,
                    "stages": stages,
                })
            except Exception:
                continue

        return pipelines

    def _parse_workflow_fallback(self, content: str, filename: str) -> dict | None:
        """Fallback parser for workflows with embedded heredocs that break yaml.safe_load()."""

        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        name = name_match.group(1).strip().strip("'\"") if name_match else filename

        # Extract top-level trigger keys from 'on:' section (2-space indent only)
        triggers = []
        in_on = False
        for line in content.splitlines():
            if re.match(r'^on:\s*$', line):
                in_on = True
                continue
            if in_on:
                # A new top-level key exits the on: section
                if re.match(r'^[a-zA-Z_][\w-]*:', line):
                    break
                # Only capture trigger names at exactly 2-space indent
                m = re.match(r'^  ([a-zA-Z_][\w-]*):', line)
                if m:
                    triggers.append(m.group(1))

        # Extract job names: scan all lines after 'jobs:' for 2-space-indented keys.
        # Skip heredoc blocks (content between << 'EOF' and EOF) which may contain
        # unindented text that looks like top-level YAML keys.
        stages = []
        in_jobs = False
        heredoc_terminator = None
        for line in content.splitlines():
            # Skip lines inside heredoc blocks
            if heredoc_terminator is not None:
                if line.strip() == heredoc_terminator:
                    heredoc_terminator = None
                continue

            # Detect heredoc start: << 'EOF', << "EOF", or << EOF
            heredoc_match = re.search(r"<<\s*['\"]?(\w+)['\"]?\s*$", line)
            if heredoc_match:
                heredoc_terminator = heredoc_match.group(1)
                continue

            if re.match(r'^jobs:\s*$', line):
                in_jobs = True
                continue
            if in_jobs:
                # Job definitions are at exactly 2-space indent under jobs:
                if re.match(r'^  [a-zA-Z_][\w-]*:', line):
                    job_name = line.strip().split(':')[0].strip()
                    if job_name and not job_name.startswith('#'):
                        stages.append({"name": job_name, "status": "defined"})

        return {"name": name, "triggers": triggers, "stages": stages}

    def _compute_overall_status(self, modules: list[dict[str, Any]], git_info: dict[str, str]) -> tuple[str, str]:
        """Compute overall system status from module health and git availability.

        Returns (status_text, status_class) where status_class is 'ok', 'warn', or 'err'.
        """
        error_statuses = {"SyntaxError", "ImportError", "Error", "Unknown"}
        error_count = sum(1 for m in modules if m.get("status") in error_statuses)
        total = len(modules)
        git_available = "error" not in git_info

        if total == 0:
            return "No Modules", "warn"
        if error_count == 0 and git_available:
            return "Operational", "ok"
        if error_count > total * 0.5:
            return "Error", "err"
        if error_count > 0 or not git_available:
            return "Degraded", "warn"
        return "Operational", "ok"

    def get_health_status(self) -> dict[str, Any]:
        """Returns comprehensive system health for the Health tab."""
        uptime_seconds = int(time.time() - self._start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        git_info = self._get_git_info()
        python_info = {
            "version": platform.python_version(),
            "executable": sys.executable,
            "platform": platform.platform(),
        }

        modules = self.get_modules()
        modules_with_tests = 0
        modules_with_api_spec = 0
        modules_with_mcp_spec = 0
        modules_needing_api_spec = 0
        src_path = self.root_dir / "src" / "codomyrmex"

        for mod in modules:
            mod_path = src_path / mod["name"]
            test_path = src_path / "tests" / "unit" / mod["name"]
            if test_path.exists():
                modules_with_tests += 1
            if (mod_path / "API_SPECIFICATION.md").exists():
                modules_with_api_spec += 1
            if (mod_path / "MCP_TOOL_SPECIFICATION.md").exists():
                modules_with_mcp_spec += 1
            if mod["name"] not in self._UTILITY_MODULES:
                modules_needing_api_spec += 1

        status_text, status_class = self._compute_overall_status(modules, git_info)

        return {
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "uptime_seconds": uptime_seconds,
            "status_text": status_text,
            "status_class": status_class,
            "python": python_info,
            "git": git_info,
            "modules": {
                "total": len(modules),
                "with_tests": modules_with_tests,
                "with_api_spec": modules_with_api_spec,
                "with_mcp_spec": modules_with_mcp_spec,
                "needing_api_spec": modules_needing_api_spec,
                "test_coverage_pct": round(modules_with_tests / max(len(modules), 1) * 100, 1),
                "api_spec_pct": round(modules_with_api_spec / max(len(modules), 1) * 100, 1),
                "api_spec_contextual_pct": round(modules_with_api_spec / max(modules_needing_api_spec, 1) * 100, 1),
                "mcp_spec_pct": round(modules_with_mcp_spec / max(len(modules), 1) * 100, 1),
            },
            "architecture_layers": self._get_architecture_layers(),
            "llm_config": self.get_llm_config(),
        }

    def get_llm_config(self) -> dict[str, Any]:
        """
        Get the current LLM configuration.
        """
        try:
            config_manager = ConfigManager()
            if config_manager.config:
                return {
                    "default_model": config_manager.config.default_model,
                    "preferred_models": config_manager.config.preferred_models,
                    "available_models": config_manager.get_available_models(),
                    "ollama_host": f"{config_manager.config.server_host}:{config_manager.config.server_port}"
                }
        except Exception as e:
            logger.warning(f"Failed to load LLM config: {e}")

        # Fallback defaults
        return {
            "default_model": "llama3.1:latest",
            "preferred_models": ["llama3.1:latest", "codellama:latest"],
            "available_models": ["llama3.1:latest"],
            "ollama_host": os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL).replace("http://", "")
        }

    def _get_git_info(self) -> dict[str, str]:
        """Get current git repository information."""
        try:
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, cwd=self.root_dir, timeout=5
            ).stdout.strip()

            last_commit = subprocess.run(
                ["git", "log", "-1", "--format=%h %s (%ar)"],
                capture_output=True, text=True, cwd=self.root_dir, timeout=5
            ).stdout.strip()

            commit_count = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, cwd=self.root_dir, timeout=5
            ).stdout.strip()

            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=self.root_dir, timeout=5
            )
            dirty_count = len([line for line in status_result.stdout.strip().split("\n") if line.strip()])

            return {
                "branch": branch,
                "last_commit": last_commit,
                "commit_count": commit_count,
                "dirty_files": dirty_count,
                "status": "clean" if dirty_count == 0 else f"{dirty_count} changed",
            }
        except Exception as e:
            return {"branch": "unknown", "last_commit": "unknown", "error": str(e)}

    def _get_architecture_layers(self) -> list[dict[str, Any]]:
        """Return architecture layer breakdown for module classification.

        Loads layer definitions from architecture_layers.yaml if available,
        falls back to hardcoded defaults otherwise.
        """
        layers_file = Path(__file__).parent / "architecture_layers.yaml"
        try:
            data = yaml.safe_load(layers_file.read_text(encoding="utf-8"))
            layer_defs = data.get("layers", [])
        except Exception:
            layer_defs = [
                {"name": "Foundation", "color": "#10b981",
                 "modules": ["logging_monitoring", "environment_setup", "model_context_protocol", "terminal_interface"]},
                {"name": "Core", "color": "#3b82f6",
                 "modules": ["agents", "static_analysis", "coding", "llm", "pattern_matching", "git_operations"]},
                {"name": "Service", "color": "#8b5cf6",
                 "modules": ["build_synthesis", "documentation", "ci_cd_automation", "containerization", "orchestrator"]},
                {"name": "Application", "color": "#f59e0b",
                 "modules": ["cli", "system_discovery", "website"]},
            ]

        existing_modules = {m["name"] for m in self.get_modules()}
        classified = set()
        result = []

        for layer in layer_defs:
            present = [m for m in layer.get("modules", []) if m in existing_modules]
            classified.update(layer.get("modules", []))
            result.append({
                "name": layer["name"],
                "modules": present,
                "color": layer.get("color", "#94a3b8"),
            })

        other = sorted(existing_modules - classified)
        if other:
            result.append({"name": "Extended", "modules": other, "color": "#94a3b8"})

        return result

    def run_tests(self, module: str | None = None) -> dict[str, Any]:
        """Run pytest and return structured results via JUnit XML."""
        import tempfile
        import xml.etree.ElementTree as ET

        # Create a temporary file for JUnit XML output
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tf:
            xml_path = tf.name

        try:
            cmd = [sys.executable, "-m", "pytest", f"--junitxml={xml_path}", "-q", "--no-header"]

            if module and module != "all":
                test_path = self.root_dir / "src" / "codomyrmex" / "tests" / "unit" / module
                if test_path.exists():
                    cmd.append(str(test_path))
                else:
                    os.unlink(xml_path)
                    return {"error": f"No tests found for module: {module}"}

            # Inject PYTHONPATH to include src/
            env = os.environ.copy()
            src_path = self.root_dir / "src"
            env["PYTHONPATH"] = str(src_path) + os.pathsep + env.get("PYTHONPATH", "")

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=self.root_dir, env=env, timeout=600
            )

            # Parse XML
            passed = failed = skipped = errors = 0

            if os.path.exists(xml_path) and os.path.getsize(xml_path) > 0:
                try:
                    tree = ET.parse(xml_path)
                    root = tree.getroot()

                    # JUnit XML format: <testsuites> or <testsuite>
                    # Attributes: tests, failures, errors, skipped
                    # But individual test cases are more reliable to iterate

                    for testcase in root.iter("testcase"):
                        # Check for failure, error, skipped elements inside testcase
                        if testcase.find("failure") is not None:
                            failed += 1
                        elif testcase.find("error") is not None:
                            errors += 1
                        elif testcase.find("skipped") is not None:
                            skipped += 1
                        else:
                            passed += 1

                except ET.ParseError:
                    # XML might be malformed if pytest crashed early
                    errors += 1
            else:
                # No XML generated usually means severe collection error or crash
                if result.returncode != 0:
                    errors += 1

            return {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "errors": errors,
                "warnings": 0, # XML doesn't strictly track warnings easily without plugins
                "total": passed + failed + skipped + errors,
                "success": failed == 0 and errors == 0 and result.returncode == 0,
                "returncode": result.returncode,
                "output": (result.stdout + result.stderr)[-5000:], # Cap output
                "module": module or "all",
            }

        except subprocess.TimeoutExpired:
            return {"error": "Test run timed out after 600 seconds"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            if os.path.exists(xml_path):
                try:
                    os.unlink(xml_path)
                except OSError as e:
                    logger.debug("Failed to remove temp xml_path %s: %s", xml_path, e)
                    pass
