"""Project context awareness for agents.

Provides file tree and module graph awareness for intelligent
tool and task routing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class FileInfo:
    """Information about a source file.

    Attributes:
        path: Relative path from project root.
        extension: File extension.
        size_bytes: File size.
        module: Inferred module name.
    """

    path: str
    extension: str = ""
    size_bytes: int = 0
    module: str = ""

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.extension and "." in self.path:
            self.extension = self.path.rsplit(".", 1)[-1]

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "path": self.path,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "module": self.module,
        }


@dataclass
class ProjectContext:
    """Full project awareness context.

    Attributes:
        root: Project root directory.
        files: All tracked source files.
        modules: Top-level module names.
        test_files: Test file paths.
    """

    root: str = ""
    files: list[FileInfo] = field(default_factory=list)
    modules: list[str] = field(default_factory=list)
    test_files: list[str] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        """Execute File Count operations natively."""
        return len(self.files)

    @property
    def module_count(self) -> int:
        """Execute Module Count operations natively."""
        return len(self.modules)

    def files_by_extension(self, ext: str) -> list[FileInfo]:
        """Execute Files By Extension operations natively."""
        return [f for f in self.files if f.extension == ext]

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "root": self.root,
            "file_count": self.file_count,
            "module_count": self.module_count,
            "test_count": len(self.test_files),
            "modules": self.modules,
        }


class ProjectScanner:
    """Scan a project directory to build ProjectContext.

    Usage::

        scanner = ProjectScanner()
        ctx = scanner.scan("/path/to/project")
        print(f"Found {ctx.file_count} files in {ctx.module_count} modules")
    """

    def __init__(
        self,
        extensions: set[str] | None = None,
        exclude_dirs: set[str] | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._extensions = extensions or {"py", "md", "toml", "yaml", "yml"}
        self._exclude_dirs = exclude_dirs or {
            "__pycache__", ".git", ".venv", "node_modules", ".eggs", "*.egg-info",
        }

    def scan(self, root: str | Path) -> ProjectContext:
        """Scan a project directory.

        Args:
            root: Project root directory.

        Returns:
            ``ProjectContext`` with all scanned info.
        """
        root_path = Path(root)
        if not root_path.is_dir():
            return ProjectContext(root=str(root))

        files: list[FileInfo] = []
        modules: set[str] = set()
        test_files: list[str] = []

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Exclude dirs
            dirnames[:] = [
                d for d in dirnames
                if d not in self._exclude_dirs and not d.endswith(".egg-info")
            ]

            rel_dir = os.path.relpath(dirpath, root_path)

            for fname in filenames:
                ext = fname.rsplit(".", 1)[-1] if "." in fname else ""
                if ext not in self._extensions:
                    continue

                rel_path = os.path.join(rel_dir, fname) if rel_dir != "." else fname
                full_path = os.path.join(dirpath, fname)

                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0

                # Infer module from first directory element
                parts = rel_path.split(os.sep)
                module = parts[0] if len(parts) > 1 else ""

                fi = FileInfo(
                    path=rel_path,
                    extension=ext,
                    size_bytes=size,
                    module=module,
                )
                files.append(fi)

                if module:
                    modules.add(module)

                if "test" in fname.lower() or "/tests/" in rel_path:
                    test_files.append(rel_path)

        ctx = ProjectContext(
            root=str(root_path),
            files=files,
            modules=sorted(modules),
            test_files=test_files,
        )

        logger.info(
            "Project scanned",
            extra={"files": ctx.file_count, "modules": ctx.module_count},
        )

        return ctx


class ToolSelector:
    """Select appropriate tools based on file type and task.

    Usage::

        selector = ToolSelector()
        tools = selector.select(file_ext="py", task_type="review")
        # Returns: ["code_reviewer", "anti_pattern_detector", "test_runner"]
    """

    _TOOL_MAP: dict[tuple[str, str], list[str]] = {
        ("py", "review"): ["code_reviewer", "anti_pattern_detector", "test_runner"],
        ("py", "test"): ["test_generator", "test_runner", "coverage_reporter"],
        ("py", "document"): ["docstring_generator", "readme_updater"],
        ("py", "refactor"): ["anti_pattern_detector", "code_reviewer"],
        ("md", "update"): ["documentation_generator", "spell_checker"],
        ("toml", "audit"): ["dependency_scanner", "sbom_generator"],
        ("yaml", "validate"): ["schema_validator", "config_checker"],
    }

    def select(
        self,
        file_ext: str = "",
        task_type: str = "",
    ) -> list[str]:
        """Select tools for a file type and task type.

        Args:
            file_ext: File extension (without dot).
            task_type: Task type (review, test, document, refactor, etc.).

        Returns:
            List of tool names.
        """
        key = (file_ext.lower().lstrip("."), task_type.lower())
        tools = self._TOOL_MAP.get(key, [])

        if not tools:
            # Fall back to extension-only matching
            for (ext, _), tool_list in self._TOOL_MAP.items():
                if ext == key[0]:
                    tools = tool_list
                    break

        return tools


__all__ = [
    "FileInfo",
    "ProjectContext",
    "ProjectScanner",
    "ToolSelector",
]
