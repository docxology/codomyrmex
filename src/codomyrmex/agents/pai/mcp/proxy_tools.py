
"""MCP proxy tools."""
import importlib
import inspect
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[5]

def _get_package_version() -> str:
    try:
        from importlib.metadata import version
        return version("codomyrmex")
    except ImportError:
        return "unknown"

def _tool_list_modules(**_kwargs: Any) -> dict[str, Any]:
    """List all available Codomyrmex modules."""
    import codomyrmex
    modules = codomyrmex.list_modules()
    return {"modules": modules, "count": len(modules)}

def _tool_module_info(*, module_name: str) -> dict[str, Any]:
    """Get info about a specific Codomyrmex module (docstring, exports, path)."""
    try:
        mod = importlib.import_module(f"codomyrmex.{module_name}")
    except ImportError as exc:
        return {"error": f"Module not found: {module_name}", "detail": str(exc)}

    exports = getattr(mod, "__all__", [n for n in dir(mod) if not n.startswith("_")])
    doc = (mod.__doc__ or "").strip()
    mod_path = getattr(mod, "__file__", None)

    return {
        "module": module_name,
        "docstring": doc[:500] if doc else None,
        "exports": exports[:50],
        "export_count": len(exports),
        "path": str(mod_path) if mod_path else None,
    }

def _tool_list_module_functions(*, module: str = "") -> dict[str, Any]:
    """List all public callable functions in a Codomyrmex module.

    Args:
        module: Module path (e.g. 'encryption', 'cache', 'validation').
                Automatically prefixed with 'codomyrmex.'.

    Returns:
        Dict with function names, signatures, and docstrings.
    """
    full_path = f"codomyrmex.{module}" if not module.startswith("codomyrmex.") else module
    try:
        mod = importlib.import_module(full_path)
    except ImportError as e:
        return {"error": f"Module {full_path} not found: {e}"}

    functions = []
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            sig = str(inspect.signature(obj))
        except (ValueError, TypeError):
            sig = "(...)"
        doc = inspect.getdoc(obj) or ""
        if len(doc) > 200:
            doc = doc[:200] + "..."
        functions.append({"name": name, "signature": sig, "docstring": doc})

    classes = []
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if name.startswith("_"):
            continue
        doc = inspect.getdoc(obj) or ""
        if len(doc) > 200:
            doc = doc[:200] + "..."
        methods = [m for m in dir(obj) if not m.startswith("_") and callable(getattr(obj, m, None))]
        classes.append({"name": name, "docstring": doc, "public_methods": methods[:20]})

    return {
        "module": full_path,
        "functions": functions,
        "classes": classes,
        "total_callables": len(functions) + len(classes),
    }

def _tool_call_module_function(*, function: str = "", kwargs: dict | None = None) -> dict[str, Any]:
    """Call any public function from any Codomyrmex module.

    Args:
        function: Fully qualified function path (e.g. 'encryption.encrypt').
                  Will be auto-prefixed with 'codomyrmex.' if not already.
        kwargs: Keyword arguments to pass to the function.

    Returns:
        Dict with 'result' key (function return value) or 'error' key.
    """
    if kwargs is None:
        kwargs = {}
    if not function.startswith("codomyrmex."):
        function = f"codomyrmex.{function}"

    parts = function.rsplit(".", 1)
    if len(parts) != 2:
        return {"error": f"Invalid function path: {function!r}. Expected 'module.function'."}

    module_path, func_name = parts
    if func_name.startswith("_"):
        return {"error": f"Cannot call private function {func_name!r}."}

    try:
        mod = importlib.import_module(module_path)
    except ImportError as e:
        return {"error": f"Module {module_path} not found: {e}"}

    func = getattr(mod, func_name, None)
    if func is None or not callable(func):
        available = [n for n in dir(mod) if not n.startswith("_") and callable(getattr(mod, n, None))]
        return {"error": f"Function {func_name!r} not found in {module_path}.", "available": available[:30]}

    try:
        result = func(**kwargs)
        try:
            import json as _json
            _json.dumps(result)
        except (TypeError, ValueError):
            result = str(result)
        return {"result": result}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

def _tool_get_module_readme(*, module: str = "") -> dict[str, Any]:
    """Read the README.md for a Codomyrmex module.

    Args:
        module: Module name (e.g. 'encryption', 'cache').

    Returns:
        Dict with README contents or error.
    """
    full_path = f"codomyrmex.{module}" if not module.startswith("codomyrmex.") else module
    try:
        mod = importlib.import_module(full_path)
    except ImportError as e:
        return {"error": f"Module {full_path} not found: {e}"}

    mod_dir = Path(getattr(mod, "__file__", "")).parent
    readme = mod_dir / "README.md"
    if not readme.exists():
        spec = mod_dir / "SPEC.md"
        if spec.exists():
            readme = spec
        else:
            return {"error": f"No README.md or SPEC.md found in {mod_dir}"}

    content = readme.read_text()
    if len(content) > 5000:
        content = content[:5000] + "\n\n... (truncated)"

    return {"module": full_path, "path": str(readme), "content": content}

def _tool_pai_status(**_kwargs: Any) -> dict[str, Any]:
    """Get PAI installation status via PAIBridge."""
    from codomyrmex.agents.pai import PAIBridge
    bridge = PAIBridge()
    return bridge.get_status()

def _tool_pai_awareness(**_kwargs: Any) -> dict[str, Any]:
    """Get full PAI awareness data (missions, projects, tasks, TELOS, memory)."""
    try:
        from codomyrmex.website.data_provider import DataProvider
        dp = DataProvider(root_dir=_PROJECT_ROOT)
        return dp.get_pai_awareness_data()
    except (ImportError, AttributeError, OSError) as exc:
        logger.warning("PAI awareness data unavailable: %s", exc)
        return {"error": str(exc)}

def _tool_run_tests(*, module: str | None = None, verbose: bool = False) -> dict[str, Any]:
    """Run pytest for a specific module or the whole project."""
    cmd = [sys.executable, "-m", "pytest"]
    if module:
        # Map module name to test path
        test_path = _PROJECT_ROOT / "src" / "codomyrmex" / "tests" / "unit" / module
        if test_path.is_dir():
            cmd.append(str(test_path))
        else:
            cmd.extend(["-k", module])
    if verbose:
        cmd.append("-v")
    cmd.append("--tb=short")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(_PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "returncode": result.returncode,
            "passed": result.returncode == 0,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"error": "Test execution timed out (120s limit)"}
    except (subprocess.SubprocessError, OSError) as exc:
        return {"error": str(exc)}

def _tool_list_workflows(project_root=None, **_kwargs: Any) -> dict[str, Any]:
    """List available Claude Code workflows from .agent/workflows.

    Parses YAML frontmatter to extract descriptions.

    Args:
        project_root: Optional override for the project root directory.
            Falls back to the module-level ``_PROJECT_ROOT`` when *None*.
    """
    root = Path(project_root) if project_root is not None else _PROJECT_ROOT
    workflows_dir = root / ".agent" / "workflows"
    if not workflows_dir.exists():
        return {"workflows": [], "count": 0, "error": "No workflow directory found"}

    results = []
    warnings = []

    for item in workflows_dir.glob("*.md"):
        try:
            content = item.read_text(encoding="utf-8")
            # Parse YAML frontmatter
            description = "No description"
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if isinstance(frontmatter, dict):
                            description = frontmatter.get("description", description)
                    except yaml.YAMLError:
                        warnings.append(f"Invalid YAML frontmatter in {item.name}")

            results.append({
                "name": item.stem, # filename without .md
                "description": description,
                "filepath": str(item),
                "size_bytes": item.stat().st_size,
            })
        except OSError as e:
            warnings.append(f"Failed to read {item.name}: {e}")

    return {
        "workflows": sorted(results, key=lambda x: x["name"]),
        "count": len(results),
        "warnings": warnings
    }

