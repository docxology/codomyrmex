"""MCP tools for the documentation module."""

import hashlib
import re
from pathlib import Path

from codomyrmex.model_context_protocol.decorators import mcp_tool

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MODULE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _resolve_module(module_name: str) -> tuple[Path | None, str | None]:
    """Resolve one top-level package module without permitting path traversal."""
    if not MODULE_NAME_RE.fullmatch(module_name):
        return None, "module_name must be a lowercase Python package name"

    module_path = (PACKAGE_ROOT / module_name).resolve()
    if (
        module_path.parent != PACKAGE_ROOT
        or not (module_path / "__init__.py").is_file()
    ):
        return None, f"Module {module_name} not found."
    return module_path, None


@mcp_tool(category="documentation")
def generate_module_docs(module_name: str, dry_run: bool = True) -> dict:
    """Plan or generate one module's source-derived ``PAI.md``.

    Args:
        module_name: Top-level package name under ``src/codomyrmex``.
        dry_run: When true (the default), hash the proposed content without
            writing it. Set false explicitly to replace the module's ``PAI.md``.

    Returns:
        Portable status, execution flags, target path, and content hash.
    """
    module_path, error = _resolve_module(module_name)
    if module_path is None:
        return {
            "status": "error",
            "message": error,
            "executed": False,
            "dry_run": dry_run,
        }

    try:
        from codomyrmex.documentation import generate_pai_md, write_pai_md

        content = generate_pai_md(module_name, module_path)
        relative_path = (module_path / "PAI.md").relative_to(REPOSITORY_ROOT).as_posix()
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if not dry_run:
            write_pai_md(module_name, module_path)
        return {
            "status": "success",
            "message": (
                f"PAI documentation planned for {module_name}"
                if dry_run
                else f"PAI documentation generated for {module_name}"
            ),
            "operation": "generate_pai_md",
            "paths": [relative_path],
            "content_sha256": digest,
            "executed": not dry_run,
            "dry_run": dry_run,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "executed": False,
            "dry_run": dry_run,
        }


@mcp_tool(category="documentation")
def audit_rasp_compliance(module_name: str | None = None) -> dict:
    """Audit the repository for RASP (README, AGENTS, SPEC, PAI) compliance.

    Args:
        module_name: Optional module name to audit specifically. If not provided, audits the whole repo.

    Returns:
        Audit report detailing missing files.
    """
    try:
        from codomyrmex.documentation.quality.audit import find_rasp_gaps

        if module_name:
            module_path, error = _resolve_module(module_name)
            if module_path is None:
                return {"status": "error", "message": error}
            scope = module_path
        else:
            scope = PACKAGE_ROOT

        gaps = find_rasp_gaps(scope)
        missing_count = sum(len(files) for files in gaps.values())

        return {
            "status": "success",
            "compliant": missing_count == 0,
            "missing_count": missing_count,
            "modules_with_gaps": len(gaps),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
