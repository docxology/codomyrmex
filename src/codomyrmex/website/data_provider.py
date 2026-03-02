"""Data aggregation layer for the Codomyrmex website.

Provides DataProvider, which scans the project directory to collect
module metadata, agent integrations, scripts, configuration files,
documentation trees, CI/CD pipeline status, and system health metrics.
"""

import importlib.util
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

from .health_mixin import HealthProviderMixin
from .pai_mixin import PAIProviderMixin


class DataProvider(HealthProviderMixin, PAIProviderMixin):
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


    def get_mcp_tools(self) -> dict[str, Any]:
        """Return MCP tools, resources, and prompts from the PAI bridge."""
        try:
            from codomyrmex.agents.pai.mcp_bridge import get_skill_manifest
            manifest = get_skill_manifest()

            # Classify tools as safe vs destructive using trust gateway patterns
            destructive_patterns = {
                "write", "delete", "remove", "execute", "run", "drop",
                "create", "update", "modify", "set", "reset", "clear",
                "purge", "destroy", "kill", "terminate", "send", "push",
                "mutate", "shutdown", "stop",
            }

            tools = []
            for tool in manifest.get("tools", []):
                name = tool.get("name", "")
                parts = name.lower().split(".")
                last_part = parts[-1] if parts else ""
                is_destructive = any(last_part.startswith(p) for p in destructive_patterns)
                tools.append({
                    "name": name,
                    "description": tool.get("description", ""),
                    "category": tool.get("category", "general"),
                    "is_destructive": is_destructive,
                })

            return {
                "tools": tools,
                "resources": manifest.get("resources", []),
                "prompts": manifest.get("prompts", []),
            }
        except Exception as exc:
            logger.warning("Failed to load MCP tools: %s", exc)
            return {"tools": [], "resources": [], "prompts": [], "error": str(exc)}

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
            except Exception as e:
                logger.debug("Failed to parse __init__.py docstring in %s: %s", path, e)
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

        except Exception as e:
            logger.debug("Failed to extract script metadata from %s: %s", script_path, e)
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
            if item.name.startswith("."):
                continue

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
            "has_pai_md": (src_path / "PAI.md").exists(),
            "has_agents_md": (src_path / "AGENTS.md").exists(),
            "has_spec_md": (src_path / "SPEC.md").exists(),
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

