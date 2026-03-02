"""SystemOpsMixin functionality."""

import os
import subprocess
import time
from typing import Any

from codomyrmex.agents.core import (
    AgentRequest,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class SystemOpsMixin:
    """SystemOpsMixin class."""

    def scan_directory(
        self,
        path: str,
        max_depth: int = 3,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Scan directory for project context.

        Scans a directory structure to understand the project layout,
        useful for providing context in agentic coding workflows.

        Args:
            path: Directory path to scan
            max_depth: Maximum directory depth (default: 3)
            include_patterns: Glob patterns to include (e.g., ["*.py", "*.js"])
            exclude_patterns: Glob patterns to exclude (e.g., ["node_modules", "__pycache__"])

        Returns:
            Dictionary containing:
                - success: Whether scan succeeded
                - structure: Hierarchical dict of directory
                - file_count: Total files found
                - files: List of file paths
                - summary: Directory summary

        Example:
            >>> result = client.scan_directory("/path/to/project")
            >>> print(result["structure"])
        """
        import fnmatch

        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"Directory not found: {path}",
                "structure": {},
                "file_count": 0,
                "files": [],
            }

        # Default exclusions
        default_exclude = [
            "__pycache__", "node_modules", ".git", ".venv", "venv",
            "*.pyc", "*.pyo", ".DS_Store", "*.egg-info",
        ]
        exclude = (exclude_patterns or []) + default_exclude

        def should_exclude(name: str) -> bool:
            """should Exclude ."""
            return any(fnmatch.fnmatch(name, pat) for pat in exclude)

        def should_include(name: str) -> bool:
            """should Include ."""
            if not include_patterns:
                return True
            return any(fnmatch.fnmatch(name, pat) for pat in include_patterns)

        def scan_dir(dir_path: str, depth: int) -> dict:
            """scan Dir ."""
            if depth > max_depth:
                return {"type": "directory", "truncated": True}

            result: dict[str, Any] = {"type": "directory", "children": {}}

            try:
                for entry in os.scandir(dir_path):
                    if should_exclude(entry.name):
                        continue

                    if entry.is_dir():
                        result["children"][entry.name] = scan_dir(entry.path, depth + 1)
                    elif entry.is_file() and should_include(entry.name):
                        result["children"][entry.name] = {
                            "type": "file",
                            "size": entry.stat().st_size,
                        }
            except PermissionError:
                result["error"] = "Permission denied"

            return result

        structure = scan_dir(path, 0)

        # Collect all file paths
        files: list[str] = []

        def collect_files(node: dict, current_path: str) -> None:
            """collect Files ."""
            for name, child in node.get("children", {}).items():
                child_path = os.path.join(current_path, name)
                if child.get("type") == "file":
                    files.append(child_path)
                elif child.get("type") == "directory":
                    collect_files(child, child_path)

        collect_files(structure, path)

        return {
            "success": True,
            "structure": structure,
            "file_count": len(files),
            "files": files,
            "summary": f"Scanned {len(files)} files in {path}",
        }

    def run_command(
        self,
        command: str,
        cwd: str | None = None,
        timeout: int = 60,
        capture_output: bool = True,
    ) -> dict[str, Any]:
        """Execute a shell command with optional AI analysis.

        Runs the specified command and returns the output. Can optionally
        analyze the output for errors or issues.

        Args:
            command: Shell command to execute
            cwd: Working directory for command execution
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            Dictionary containing:
                - success: Whether command executed successfully
                - return_code: Process return code
                - stdout: Standard output
                - stderr: Standard error
                - duration: Execution time in seconds

        Example:
            >>> result = client.run_command("ls -la")
            >>> print(result["stdout"])
        """

        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,  # SECURITY: Intentional — run_command is an agent shell executor
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )
            duration = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout if capture_output else "",
                "stderr": result.stderr if capture_output else "",
                "duration": duration,
                "command": command,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "duration": timeout,
                "command": command,
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": time.time() - start_time,
                "command": command,
            }

    def get_project_structure(
        self,
        path: str,
        max_depth: int = 4,
        include_analysis: bool = False,
    ) -> dict[str, Any]:
        """Get comprehensive project structure analysis.

        Scans the project directory and optionally uses AI to analyze
        the project type, dependencies, and structure.

        Args:
            path: Root directory of the project
            max_depth: Maximum scan depth
            include_analysis: Whether to include AI-powered analysis

        Returns:
            Dictionary containing:
                - success: Whether scan succeeded
                - structure: Directory tree
                - file_count: Total files
                - language_breakdown: Files by language
                - analysis: AI analysis (if requested)

        Example:
            >>> result = client.get_project_structure("/path/to/project")
            >>> print(result["language_breakdown"])
        """
        from collections import defaultdict

        # First, do a basic scan
        scan_result = self.scan_directory(path, max_depth=max_depth)

        if not scan_result["success"]:
            return scan_result

        # Analyze language breakdown
        lang_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".java": "Java", ".cpp": "C++", ".c": "C", ".go": "Go",
            ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
            ".kt": "Kotlin", ".scala": "Scala", ".cs": "C#",
            ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
            ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
            ".sh": "Shell", ".bash": "Shell",
        }

        language_breakdown: dict[str, int] = defaultdict(int)
        for file_path in scan_result.get("files", []):
            ext = os.path.splitext(file_path)[1].lower()
            lang = lang_map.get(ext, "Other")
            language_breakdown[lang] += 1

        result = {
            "success": True,
            "path": path,
            "structure": scan_result["structure"],
            "file_count": scan_result["file_count"],
            "files": scan_result["files"],
            "language_breakdown": dict(language_breakdown),
        }

        # Optionally add AI analysis
        if include_analysis and self.test_connection():
            system_prompt = """You are a software architect analyzing a project.
Provide a brief analysis including:
1. Project type (web app, library, CLI tool, etc.)
2. Primary language/framework
3. Notable patterns or architecture
Be concise."""

            files_summary = "\n".join(scan_result["files"][:50])
            langs = ", ".join(f"{k}: {v}" for k, v in sorted(
                language_breakdown.items(), key=lambda x: -x[1]
            )[:5])

            prompt = f"""Analyze this project structure:
Path: {path}
Files: {scan_result['file_count']}
Languages: {langs}

Sample files:
{files_summary}"""

            try:
                response = self.execute(AgentRequest(
                    prompt=prompt,
                    context={"system": system_prompt}
                ))
                if response.is_success():
                    result["analysis"] = response.content
                    result["tokens_used"] = response.tokens_used
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                logger.debug("Optional analysis step failed: %s", e)
                pass  # Analysis is optional

        return result

