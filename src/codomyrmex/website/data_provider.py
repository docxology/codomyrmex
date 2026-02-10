"""Data aggregation layer for the Codomyrmex website.

Provides DataProvider, which scans the project directory to collect
module metadata, agent integrations, scripts, configuration files,
documentation trees, CI/CD pipeline status, and system health metrics.
"""

import importlib.util
import json as _json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class DataProvider:
    """
    Aggregates data from various system modules to populate the website.
    """

    # Utility modules that don't need API specs
    _UTILITY_MODULES = frozenset({
        "__pycache__", "tests", "utils", "exceptions", "skills",
        "module_template", "examples",
    })

    _PAI_ROOT: Path = Path.home() / ".claude"

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self._start_time = time.time()

    def get_system_summary(self) -> dict[str, Any]:
        """Returns high-level system metrics."""
        return {
            "status": "Operational",
            "version": "0.1.0",
            "environment": os.getenv("CODOMYRMEX_ENV", "Development"),
            "module_count": len(self.get_modules()),
            "agent_count": len(self.get_actual_agents()),
            "last_build": self._get_last_build_time()
        }

    def _compute_module_status(self, module_path: Path) -> str:
        """Compute module status by trying to find the module spec via importlib."""
        module_name = f"codomyrmex.{module_path.name}"
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                return "Active"
            # Fallback to syntax check if spec not found
            init = module_path / "__init__.py"
            if init.exists():
                content = init.read_text(encoding="utf-8")
                compile(content, str(init), "exec")
                return "Active"
            return "Unknown"
        except ModuleNotFoundError:
            return "ImportError"
        except SyntaxError:
            return "SyntaxError"
        except Exception:
            return "Unknown"

    def get_modules(self) -> list[dict[str, Any]]:
        """
        Scans the `src/codomyrmex` directory for all modules (packages).
        This returns all Codomyrmex packages, not agents.
        """
        modules = []
        src_path = self.root_dir / "src/codomyrmex"

        if not src_path.exists():
            return []

        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                description = self._get_description(item)
                if description == "No description available":
                    description = self._get_description_from_markdown(item)

                modules.append({
                    "name": item.name,
                    "status": self._compute_module_status(item),
                    "path": str(item.relative_to(self.root_dir)),
                    "description": description,
                    "submodules": self._get_submodules(item)
                })

        return sorted(modules, key=lambda x: x["name"])

    def _get_submodules(self, module_path: Path) -> list[dict[str, Any]]:
        """Get submodules of a module for hierarchical navigation."""
        submodules = []
        for item in module_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                submodules.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.root_dir)),
                    "description": self._get_description(item)
                })
        return sorted(submodules, key=lambda x: x["name"])

    def get_actual_agents(self) -> list[dict[str, Any]]:
        """
        Returns actual AI agent integrations from `src/codomyrmex/agents/`.
        These are the real agent frameworks (jules, claude, codex, etc.).
        """
        agents = []
        agents_path = self.root_dir / "src/codomyrmex/agents"

        if not agents_path.exists():
            return []

        # Known agent integration directories
        for item in agents_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                # Skip non-agent directories like 'tests'
                if item.name in ["tests", "__pycache__"]:
                    continue
                description = self._get_description(item)
                if description == "No description available":
                    description = self._get_description_from_markdown(item)

                agents.append({
                    "name": item.name,
                    "status": self._compute_module_status(item),
                    "path": str(item.relative_to(self.root_dir)),
                    "description": description,
                    "type": self._get_agent_type(item.name)
                })

        return sorted(agents, key=lambda x: x["name"])

    def _get_agent_type(self, agent_name: str) -> str:
        """Categorize agent by type."""
        cli_agents = ["jules", "opencode", "gemini", "mistral_vibe", "droid"]
        api_agents = ["claude", "codex"]
        framework_agents = ["generic", "theory", "every_code", "ai_code_editing"]

        if agent_name in cli_agents:
            return "CLI Integration"
        elif agent_name in api_agents:
            return "API Integration"
        elif agent_name in framework_agents:
            return "Framework"
        return "Agent"


    def get_available_scripts(self) -> list[dict[str, Any]]:
        """
        Scans the `scripts` directory for executable scripts.
        """
        scripts = []
        scripts_dir = self.root_dir / "scripts"

        if not scripts_dir.exists():
            return []

        # Recursive search for .py files
        for path in scripts_dir.rglob("*.py"):
            # Skip hidden files, __init__.py, and output directories
            if path.name.startswith(("_", ".")) or "output" in path.parts:
                continue

            rel_path = path.relative_to(scripts_dir)
            title, description = self._get_script_metadata(path)

            scripts.append({
                "name": str(rel_path),
                "title": title,
                "path": str(rel_path),
                "full_path": str(path),
                "description": description
            })

        return sorted(scripts, key=lambda x: x["name"])

    def _get_description(self, path: Path) -> str:
        """Extracts description from __init__.py docstring."""
        init_file = path / "__init__.py"
        if init_file.exists():
            try:
                content = init_file.read_text(encoding="utf-8")
                # Very basic parsing
                if '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end != -1:
                        return content[start:end].strip()
            except Exception:
                pass
        return "No description available"

    def _get_script_metadata(self, script_path: Path) -> tuple[str, str]:
        """Extracts title and description from script."""
        title = script_path.name
        description = "No description available"

        try:
            content = script_path.read_text(encoding="utf-8")

            # Extract docstring
            docstring = None
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end != -1:
                    docstring = content[start:end].strip()
            elif "'''" in content:
                start = content.find("'''") + 3
                end = content.find("'''", start)
                if end != -1:
                    docstring = content[start:end].strip()

            if docstring:
                lines = docstring.split('\n')
                # Try to find a title
                # 1. explicit "Title: ..."
                for line in lines:
                    if line.strip().lower().startswith("title:"):
                        title = line.split(":", 1)[1].strip()
                        break
                else:
                    # 2. First non-empty line
                    for line in lines:
                        if line.strip():
                            title = line.strip()
                            break

                description = docstring

        except Exception:
            pass

        return title, description

    def _get_description_from_markdown(self, agent_dir: Path) -> str:
        """Attempts to read the description from AGENTS.md or README.md."""
        for filename in ["AGENTS.md", "README.md"]:
            file_path = agent_dir / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    # Simple markdown extraction: find first non-empty line that isn't a header
                    lines = content.splitlines()
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            return line if len(line) < 100 else line[:97] + "..."
                    return "Documented"
                except Exception:
                    continue
        return "No description available"


    def get_config_files(self) -> list[dict[str, str]]:
        """Scans for configuration files."""
        configs = []
        # Look for typical config files in root
        patterns = ["*.toml", "*.yaml", "*.yml", "*.json", "requirements.txt"]

        for pattern in patterns:
            for path in self.root_dir.glob(pattern):
                if path.is_file():
                    configs.append({
                        "name": path.name,
                        "path": path.name, # Relative to root
                        "type": path.suffix.lstrip(".")
                    })

        # Also look in config/ dir if it exists
        config_dir = self.root_dir / "config"
        if config_dir.exists():
            for pattern in patterns:
                for path in config_dir.glob(pattern):
                    if path.is_file():
                        configs.append({
                            "name": f"config/{path.name}",
                            "path": str(path.relative_to(self.root_dir)),
                            "type": path.suffix.lstrip(".")
                        })

        return sorted(configs, key=lambda x: x["name"])

    _SAFE_CONFIG_EXTENSIONS = frozenset({
        ".toml", ".yaml", ".yml", ".json", ".txt", ".cfg", ".ini", ".conf",
    })

    def get_config_content(self, filename: str) -> str:
        """Reads content of a config file.

        Security: prevents traversal and restricts to safe file extensions.
        """
        # Security: prevent traversal
        if ".." in filename or filename.startswith("/"):
            raise ValueError("Invalid filename")

        file_path = (self.root_dir / filename).resolve()
        root_resolved = self.root_dir.resolve()

        if not str(file_path).startswith(str(root_resolved)):
            raise ValueError("Path escapes project root")

        # Restrict to safe extensions
        suffix = file_path.suffix.lower()
        if suffix not in self._SAFE_CONFIG_EXTENSIONS:
            raise ValueError(f"File type '{suffix}' is not allowed - only config files permitted")

        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")

        return file_path.read_text(encoding="utf-8")

    def save_config_content(self, filename: str, content: str) -> None:
        """Saves content to a config file."""
        # Security: prevent traversal
        if ".." in filename or filename.startswith("/"):
            raise ValueError("Invalid filename")

        file_path = (self.root_dir / filename).resolve()
        root_resolved = self.root_dir.resolve()

        # Verify path stays within root_dir
        if not str(file_path).startswith(str(root_resolved)):
            raise ValueError("Path escapes project root")

        # Only allow updating existing files - refuse to create new ones
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} does not exist - refusing to create new files")

        logger.info("Saving config file: %s", filename)
        file_path.write_text(content, encoding="utf-8")

    def get_doc_tree(self) -> dict[str, Any]:
        """Builds a tree of documentation files."""
        docs_root = self.root_dir / "docs"
        src_root = self.root_dir / "src"

        tree = {"name": "Documentation", "children": []}

        # Add docs/ folder
        if docs_root.exists():
            tree["children"].append(self._scan_directory_for_docs(docs_root))

        # Add src/ READMEs
        src_docs = {"name": "Modules", "children": []}
        if src_root.exists():
             for path in src_root.rglob("README.md"):
                  src_docs["children"].append({
                      "name": str(path.relative_to(src_root).parent),
                      "path": str(path.relative_to(self.root_dir)),
                      "type": "file"
                  })
        if src_docs["children"]:
            tree["children"].append(src_docs)

        return tree

    def _scan_directory_for_docs(self, path: Path) -> dict[str, Any]:
        """Recursively scan a directory for .md documentation files.

        Returns a nested dict with 'name' and 'children' keys representing
        the directory tree. Only directories containing at least one .md file
        (at any depth) are included. Hidden files are skipped.
        """
        node = {"name": path.name, "children": []}

        # Files first, then dirs
        for item in sorted(path.iterdir()):
            if item.name.startswith("."): continue

            if item.is_file() and item.suffix == ".md":
                node["children"].append({
                     "name": item.name,
                     "path": str(item.relative_to(self.root_dir)),
                     "type": "file"
                })
            elif item.is_dir():
                child_node = self._scan_directory_for_docs(item)
                # Only add if it has content
                if child_node["children"]:
                    node["children"].append(child_node)

        return node

    def get_doc_content(self, doc_path: str) -> str:
        """Read and return the content of a documentation file.

        Security: rejects path traversal, absolute paths, and non-.md files.
        """
        if ".." in doc_path:
            raise ValueError("Path traversal not allowed")
        if doc_path.startswith("/"):
            raise ValueError("Absolute paths not allowed")
        if not doc_path.endswith(".md"):
            raise ValueError("Only .md files are allowed")

        file_path = (self.root_dir / doc_path).resolve()
        root_resolved = self.root_dir.resolve()

        if not str(file_path).startswith(str(root_resolved)):
            raise ValueError("Path traversal not allowed")
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")

        return file_path.read_text(encoding="utf-8")

    def get_module_detail(self, name: str) -> dict[str, Any] | None:
        """Return enriched detail for a single module by name."""
        src_path = self.root_dir / "src" / "codomyrmex" / name

        if not src_path.is_dir() or not (src_path / "__init__.py").exists():
            return None

        description = self._get_description(src_path)
        if description == "No description available":
            description = self._get_description_from_markdown(src_path)

        test_path = self.root_dir / "src" / "codomyrmex" / "tests" / "unit" / name
        python_files = list(src_path.rglob("*.py"))

        return {
            "name": name,
            "status": "Active",
            "path": str(src_path.relative_to(self.root_dir)),
            "description": description,
            "submodules": self._get_submodules(src_path),
            "has_tests": test_path.exists(),
            "has_api_spec": (src_path / "API_SPECIFICATION.md").exists(),
            "has_mcp_spec": (src_path / "MCP_TOOL_SPECIFICATION.md").exists(),
            "has_readme": (src_path / "README.md").exists(),
            "python_file_count": len(python_files),
        }

    def _get_last_build_time(self) -> str:
        """Get the timestamp of the last git commit as a proxy for last build."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                capture_output=True, text=True,
                cwd=self.root_dir, timeout=5
            )
            timestamp = result.stdout.strip()
            return timestamp if timestamp else "N/A"
        except Exception:
            return "N/A"

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
        import re

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
            dirty_count = len([l for l in status_result.stdout.strip().split("\n") if l.strip()])

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
                except:
                    pass

    # ── PAI Awareness Methods ──────────────────────────────────────────

    def get_pai_missions(self) -> list[dict[str, Any]]:
        """Read PAI mission definitions from ~/.claude/MEMORY/STATE/missions/."""
        missions_dir = self._PAI_ROOT / "MEMORY" / "STATE" / "missions"
        if not missions_dir.exists():
            return []

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        missions: list[dict[str, Any]] = []

        for mission_dir in missions_dir.iterdir():
            if not mission_dir.is_dir():
                continue
            mission_file = mission_dir / "MISSION.yaml"
            if not mission_file.exists():
                continue
            try:
                data = yaml.safe_load(mission_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
            except Exception:
                continue

            # Merge progress.json if present
            progress: dict[str, Any] = {}
            progress_file = mission_dir / "progress.json"
            if progress_file.exists():
                try:
                    progress = _json.loads(progress_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            missions.append({
                "id": mission_dir.name,
                "title": data.get("title", mission_dir.name),
                "status": data.get("status", "unknown"),
                "priority": data.get("priority", "MEDIUM"),
                "description": data.get("description", ""),
                "success_criteria": data.get("success_criteria", []),
                "linked_projects": data.get("linked_projects", []),
                "completion_percentage": progress.get("completion_percentage", 0),
                "recent_activity": progress.get("recent_activity", []),
            })

        missions.sort(key=lambda m: priority_order.get(m["priority"], 99))
        return missions

    def get_pai_projects(self) -> list[dict[str, Any]]:
        """Read PAI project definitions from ~/.claude/MEMORY/STATE/projects/."""
        projects_dir = self._PAI_ROOT / "MEMORY" / "STATE" / "projects"
        if not projects_dir.exists():
            return []

        projects: list[dict[str, Any]] = []

        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            project_file = project_dir / "PROJECT.yaml"
            if not project_file.exists():
                continue
            try:
                data = yaml.safe_load(project_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
            except Exception:
                continue

            # Merge progress.json if present
            progress: dict[str, Any] = {}
            progress_file = project_dir / "progress.json"
            if progress_file.exists():
                try:
                    progress = _json.loads(progress_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            projects.append({
                "id": project_dir.name,
                "title": data.get("title", project_dir.name),
                "status": data.get("status", "unknown"),
                "goal": data.get("goal", ""),
                "priority": data.get("priority", "MEDIUM"),
                "parent_mission": data.get("parent_mission", ""),
                "tags": data.get("tags", []),
                "completion_percentage": progress.get("completion_percentage", 0),
                "task_counts": progress.get("task_counts", {}),
                "recent_activity": progress.get("recent_activity", []),
            })

        projects.sort(key=lambda p: (p["parent_mission"], p["title"]))
        return projects

    def get_pai_tasks(self, project_id: str) -> dict[str, Any]:
        """Parse TASKS.md for a specific PAI project.

        Raises ValueError for path traversal attempts.
        """
        if ".." in project_id or "/" in project_id:
            raise ValueError("Invalid project_id")

        tasks_file = (
            self._PAI_ROOT / "MEMORY" / "STATE" / "projects" / project_id / "TASKS.md"
        )
        if not tasks_file.exists():
            return {}

        try:
            content = tasks_file.read_text(encoding="utf-8")
        except Exception:
            return {}

        completed: list[str] = []
        remaining: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                completed.append(stripped[5:].strip())
            elif stripped.startswith("- [ ]"):
                remaining.append(stripped[5:].strip())

        return {
            "completed": completed,
            "remaining": remaining,
            "total": len(completed) + len(remaining),
            "done": len(completed),
        }

    def get_pai_telos(self) -> list[dict[str, Any]]:
        """Read TELOS life profile files from ~/.claude/skills/PAI/USER/TELOS/."""
        telos_dir = self._PAI_ROOT / "skills" / "PAI" / "USER" / "TELOS"
        if not telos_dir.exists():
            return []

        telos: list[dict[str, Any]] = []
        for md_file in telos_dir.iterdir():
            if not md_file.is_file() or md_file.suffix != ".md":
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                size = md_file.stat().st_size
            except Exception:
                content = ""
                size = 0
            telos.append({
                "name": md_file.stem,
                "filename": md_file.name,
                "size_bytes": size,
                "preview": content[:200],
            })

        telos.sort(key=lambda t: t["name"])
        return telos

    def get_pai_memory_overview(self) -> dict[str, Any]:
        """Stat ~/.claude/MEMORY/ subdirectories for counts."""
        memory_dir = self._PAI_ROOT / "MEMORY"
        if not memory_dir.exists():
            return {"directories": [], "total_files": 0, "work_sessions_count": 0}

        directories: list[dict[str, Any]] = []
        total_files = 0

        try:
            items = sorted(memory_dir.iterdir())
        except OSError:
            items = []

        for item in items:
            if not item.is_dir():
                total_files += 1
                continue
            try:
                file_count = sum(1 for f in item.rglob("*") if f.is_file())
                subdir_count = sum(1 for d in item.iterdir() if d.is_dir())
            except OSError:
                file_count = 0
                subdir_count = 0
            total_files += file_count
            directories.append({
                "name": item.name,
                "file_count": file_count,
                "subdir_count": subdir_count,
            })

        # Count work sessions
        work_dir = memory_dir / "WORK"
        work_sessions_count = 0
        if work_dir.exists():
            try:
                work_sessions_count = sum(1 for d in work_dir.iterdir() if d.is_dir())
            except OSError:
                pass

        return {
            "directories": directories,
            "total_files": total_files,
            "work_sessions_count": work_sessions_count,
        }

    def _build_pai_mermaid_graph(
        self,
        missions: list[dict[str, Any]],
        projects: list[dict[str, Any]],
    ) -> str:
        """Generate a Mermaid graph TD string from mission→project hierarchy."""

        def _sanitize(text: str) -> str:
            return re.sub(r"[^a-zA-Z0-9_]", "_", text)

        def _escape_label(text: str) -> str:
            return text.replace('"', "'").replace("<", "").replace(">", "")

        lines = ["graph TD"]

        # classDef for status-based styling
        lines.append("    classDef active fill:#10b981,stroke:#059669,color:#fff")
        lines.append("    classDef paused fill:#f59e0b,stroke:#d97706,color:#fff")
        lines.append("    classDef completed fill:#6b7280,stroke:#4b5563,color:#fff")
        lines.append("    classDef in_progress fill:#3b82f6,stroke:#2563eb,color:#fff")
        lines.append("    classDef blocked fill:#ef4444,stroke:#dc2626,color:#fff")
        lines.append("    classDef unknown fill:#94a3b8,stroke:#64748b,color:#fff")

        linked_project_ids: set[str] = set()

        for mission in missions:
            m_id = "M_" + _sanitize(mission.get("id", "unknown"))
            m_label = _escape_label(mission.get("title", "Untitled"))
            lines.append(f'    {m_id}["{m_label}"]')
            status_class = _sanitize(mission.get("status", "unknown"))
            lines.append(f"    class {m_id} {status_class}")

            for proj_ref in (mission.get("linked_projects") or []):
                p_id = "P_" + _sanitize(str(proj_ref))
                linked_project_ids.add(str(proj_ref))
                lines.append(f"    {m_id} --> {p_id}")

        for project in projects:
            p_id = "P_" + _sanitize(project.get("id", "unknown"))
            p_label = _escape_label(project.get("title", "Untitled"))
            lines.append(f'    {p_id}["{p_label}"]')
            status_class = _sanitize(project.get("status", "unknown"))
            lines.append(f"    class {p_id} {status_class}")

            # If it has a parent_mission but wasn't linked from mission side, add edge
            parent = project.get("parent_mission")
            if parent and project["id"] not in linked_project_ids:
                pm_id = "M_" + _sanitize(str(parent))
                lines.append(f"    {pm_id} --> {p_id}")

        return "\n".join(lines)

    def get_pai_awareness_data(self) -> dict[str, Any]:
        """Aggregate all PAI ecosystem data for the awareness dashboard."""
        try:
            missions = self.get_pai_missions()
        except Exception:
            missions = []
        try:
            projects = self.get_pai_projects()
        except Exception:
            projects = []
        try:
            telos = self.get_pai_telos()
        except Exception:
            telos = []
        try:
            memory = self.get_pai_memory_overview()
        except Exception:
            memory = {"directories": [], "total_files": 0, "work_sessions_count": 0}

        total_tasks = 0
        completed_tasks = 0
        for project in projects:
            tc = project.get("task_counts", {})
            # task_counts has: completed, in_progress, remaining, blocked, optional
            # Sum all to get total (there is no 'total' key in progress.json)
            total_tasks += sum(
                tc.get(k, 0)
                for k in ("completed", "in_progress", "remaining", "blocked", "optional")
            )
            completed_tasks += tc.get("completed", 0)

        overall_completion = (
            round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
        )

        return {
            "missions": missions,
            "projects": projects,
            "telos": telos,
            "memory": memory,
            "metrics": {
                "mission_count": len(missions),
                "project_count": len(projects),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "telos_files": len(telos),
                "overall_completion": overall_completion,
            },
            "mermaid_graph": self._safe_mermaid_graph(missions, projects),
        }

    def _safe_mermaid_graph(
        self,
        missions: list[dict[str, Any]],
        projects: list[dict[str, Any]],
    ) -> str:
        """Build mermaid graph with error isolation."""
        try:
            return self._build_pai_mermaid_graph(missions, projects)
        except Exception:
            return "graph TD\n    ERR[\"Graph unavailable\"]"

