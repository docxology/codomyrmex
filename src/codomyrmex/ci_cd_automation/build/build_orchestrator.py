"""Safe, standard-library build orchestration primitives.

The build surface intentionally accepts argument-vector commands rather than
shell strings.  Build configuration is commonly supplied by a repository, so
callers must opt into shell parsing themselves if a shell is genuinely part of
their trusted build contract.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import uuid
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_BUILD_HISTORY: list[dict[str, Any]] = []
_HISTORY_LOCK = threading.Lock()
_SUPPORTED_LANGUAGES = ["python", "javascript", "java", "cpp", "c", "go", "rust"]


def _command_args(command: Sequence[str] | str) -> list[str]:
    """Normalize an argument-vector command without invoking a shell."""
    if isinstance(command, str):
        raise TypeError("Build commands must be argument lists, not shell strings")
    args = [str(part) for part in command]
    if not args or any(not part for part in args):
        raise ValueError("Build commands must contain at least one non-empty argument")
    return args


def check_build_environment() -> dict[str, Any]:
    """Return availability information for common build tools."""
    python_path = shutil.which("python") or sys.executable
    result: dict[str, Any] = {
        "python_available": bool(python_path),
        "python_path": python_path,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "working_directory": str(Path.cwd()),
    }
    for executable in ("git", "node", "npm", "uv"):
        result[f"{executable}_available"] = shutil.which(executable) is not None
    return result


def run_build_command(
    command: Sequence[str],
    cwd: str | os.PathLike[str] | None = None,
    timeout: float = 300,
) -> tuple[bool, str, str]:
    """Run one trusted build command without shell interpretation."""
    detail = _run_build_command_detailed(command, cwd=cwd, timeout=timeout)
    return detail["success"], detail["stdout"], detail["stderr"]


def _run_build_command_detailed(
    command: Sequence[str],
    cwd: str | os.PathLike[str] | None = None,
    timeout: float = 300,
) -> dict[str, Any]:
    """Run a command and retain a machine-readable terminal status."""
    try:
        args = _command_args(command)
    except (TypeError, ValueError) as exc:
        logger.error("Invalid build command: %s", exc)
        return {
            "success": False,
            "status": "invalid",
            "stdout": "",
            "stderr": str(exc),
        }
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or timeout <= 0
    ):
        error = "Build timeout must be a positive number"
        logger.error(error)
        return {
            "success": False,
            "status": "invalid",
            "stdout": "",
            "stderr": error,
        }
    try:
        completed = subprocess.run(
            args,
            cwd=os.fspath(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        logger.error("Build command timed out: %s", exc)
        return {
            "success": False,
            "status": "timed_out",
            "stdout": exc.stdout or "",
            "stderr": str(exc),
        }
    except OSError as exc:
        logger.error("Build command failed to start: %s", exc)
        return {
            "success": False,
            "status": "failed",
            "stdout": "",
            "stderr": str(exc),
        }

    success = completed.returncode == 0
    return {
        "success": success,
        "status": "success" if success else "failed",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "returncode": completed.returncode,
    }


def _copy_source(source: Path, output: Path) -> None:
    """Copy a file or directory into an output location."""
    if source.is_dir():
        output.mkdir(parents=True, exist_ok=True)
        for child in source.iterdir():
            destination = output / child.name
            if child.is_dir():
                shutil.copytree(child, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(child, destination)
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output)


def _resolve_output_path(
    value: str | os.PathLike[str],
    output_root: str | os.PathLike[str] | None = None,
) -> tuple[Path, Path]:
    """Resolve an output and its cleanup boundary.

    A configured output root is a hard containment boundary.  The artifact
    must be a child of that root, never the root itself, so rollback can never
    remove the caller's whole output directory.
    """
    output = Path(value).expanduser()
    if not output.is_absolute():
        output = Path.cwd() / output
    output = output.resolve()

    if output_root is None:
        return output, output.parent

    root = Path(output_root).expanduser()
    if not root.is_absolute():
        root = Path.cwd() / root
    root = root.resolve()
    try:
        relative = output.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"output_path {output} must be contained by output_root {root}"
        ) from exc
    if not relative.parts:
        raise ValueError("output_path must be below output_root, not the root itself")
    return output, root


def synthesize_build_artifact(
    source_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    artifact_type: str = "executable",
) -> bool:
    """Create a build artifact by copying a source file or source tree.

    ``package`` preserves a source directory tree.  ``executable`` preserves
    source contents and adds a small import marker for single-file Python
    sources so the resulting artifact remains directly inspectable and
    executable by the caller's normal Python entrypoint.
    """
    source = Path(source_path)
    output = Path(output_path)
    if not source.exists():
        logger.warning("Build source does not exist: %s", source)
        return False
    if artifact_type not in {"executable", "package", "archive", "copy"}:
        logger.error("Unsupported artifact type: %s", artifact_type)
        return False
    if artifact_type == "executable" and source.is_dir():
        logger.error("Executable artifacts require a source file: %s", source)
        return False

    try:
        if artifact_type == "archive":
            _create_deterministic_archive(source, output)
        elif artifact_type in {"package", "copy"}:
            _copy_source(source, output)
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == ".py":
                content = source.read_text(encoding="utf-8")
                content = "import sys  # build artifact runtime marker\n" + content
                output.write_text(content, encoding="utf-8")
            else:
                shutil.copy2(source, output)
            try:
                output.chmod(output.stat().st_mode | 0o111)
            except OSError:
                logger.debug("Could not mark build artifact executable: %s", output)
        return output.exists()
    except (OSError, UnicodeError, ValueError) as exc:
        logger.error("Failed to synthesize build artifact %s: %s", output, exc)
        return False


def _create_deterministic_archive(source: Path, output: Path) -> None:
    """Write a deterministic ZIP with safe, relative member names."""
    if source.is_symlink():
        raise ValueError("Archive source symlinks are not supported")
    output.parent.mkdir(parents=True, exist_ok=True)
    root_name = f".{output.stem}-source"
    entries: list[tuple[str, Path | None]] = []
    if source.is_dir():
        entries.append((root_name + "/", None))
        for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
            if path.is_symlink():
                raise ValueError(f"Archive source contains symlink: {path}")
            relative = path.relative_to(source).as_posix()
            member = f"{root_name}/{relative}"
            if path.is_dir():
                entries.append((member.rstrip("/") + "/", None))
            elif path.is_file():
                entries.append((member, path))
            else:
                raise ValueError(f"Unsupported archive source entry: {path}")
    elif source.is_file():
        entries.append((f"{root_name}/{source.name}", source))
    else:
        raise ValueError(f"Unsupported archive source: {source}")

    temporary = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for member, path in entries:
                info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (
                    0o755 << 16 if member.endswith("/") else 0o644 << 16
                )
                archive.writestr(info, b"" if path is None else path.read_bytes())
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def validate_build_output(output_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Validate an artifact's existence, size, and known format invariants.

    Build outputs are not limited to Python files: explicit copy and compiler
    commands may produce native binaries, text files, or other opaque files.
    Those are valid when non-empty; Python and ZIP artifacts receive the extra
    format checks that can be performed without guessing their toolchain.
    """
    output = Path(output_path)
    result: dict[str, Any] = {
        "path": str(output),
        "exists": output.exists(),
        "is_file": output.is_file(),
        "is_directory": output.is_dir(),
        "size_bytes": 0,
        "errors": [],
        "valid": False,
    }
    if not output.exists():
        result["errors"].append(f"Output does not exist: {output}")
        return result

    try:
        if output.is_file():
            result["size_bytes"] = output.stat().st_size
            if result["size_bytes"] == 0:
                result["errors"].append("Output file is empty")
            elif output.suffix == ".py":
                source = output.read_text(encoding="utf-8")
                compile(source, str(output), "exec")
                result["valid"] = True
            elif output.suffix.lower() == ".zip":
                if zipfile.is_zipfile(output):
                    result["valid"] = True
                else:
                    result["errors"].append("Output ZIP file is invalid")
            else:
                result["valid"] = True
        elif output.is_dir():
            files = [path for path in output.rglob("*") if path.is_file()]
            result["size_bytes"] = sum(path.stat().st_size for path in files)
            result["valid"] = bool(files)
            if not files:
                result["errors"].append("Output directory is empty")
        else:
            result["errors"].append("Output is neither a regular file nor directory")
    except (OSError, UnicodeError, SyntaxError) as exc:
        result["errors"].append(str(exc))
    return result


def validate_build_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate the minimal build configuration contract."""
    errors: list[str] = []
    if not isinstance(config, dict):
        return False, ["Build configuration must be a mapping"]
    if "name" in config and not isinstance(config["name"], str):
        errors.append("name must be a string")
    if "name" in config and not config["name"].strip():
        errors.append("name must not be empty")
    commands = config.get("build_commands", [])
    if commands is not None and not isinstance(commands, list):
        errors.append("build_commands must be a list")
    elif isinstance(commands, list):
        for index, command in enumerate(commands):
            if not isinstance(command, (list, tuple)) or not command:
                errors.append(
                    f"build_commands[{index}] must be a non-empty argument list"
                )
            elif any(not isinstance(part, (str, int, float)) for part in command):
                errors.append(
                    f"build_commands[{index}] must contain only scalar arguments"
                )
    timeout = config.get("timeout", 300)
    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        errors.append("timeout must be a positive number")
    artifacts = config.get("artifacts", [])
    if artifacts is not None and not isinstance(artifacts, list):
        errors.append("artifacts must be a list")
    source_path = config.get("source_path")
    output_path = config.get("output_path") or config.get("output_dir")
    if bool(source_path) != bool(output_path):
        errors.append(
            "source_path and output_path/output_dir must be provided together"
        )
    return not errors, errors


def validate_build_dependencies(dependencies: Sequence[str] | None) -> dict[str, Any]:
    """Report importable Python dependencies without installing anything."""
    available: list[str] = []
    missing: list[str] = []
    for dependency in dependencies or []:
        try:
            __import__(dependency)
        except (ImportError, ModuleNotFoundError):
            missing.append(dependency)
        else:
            available.append(dependency)
    return {"valid": not missing, "missing": missing, "available": available}


def get_supported_languages() -> list[str]:
    """Return language labels supported for explicit build commands.

    These labels are metadata only; this package does not invoke a compiler
    implicitly.  Supply the actual compiler or packager as an argument-vector
    entry in ``build_commands``.
    """
    return list(_SUPPORTED_LANGUAGES)


def create_build_manifest(config: dict[str, Any]) -> dict[str, Any]:
    """Create a serializable manifest for a build configuration."""
    serializable_config = json.loads(json.dumps(config, default=str))
    return {
        "manifest_version": "1.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "build_config": serializable_config,
    }


def optimize_build_config(config: dict[str, Any]) -> dict[str, Any]:
    """Return a conservative optimized copy of a build configuration."""
    optimized = dict(config)
    optimized.setdefault("parallel_jobs", max(1, min(os.cpu_count() or 1, 8)))
    optimized.setdefault("cache_enabled", True)
    optimized.setdefault("optimization_level", "balanced")
    return optimized


def parallel_build_execution(
    build_tasks: Sequence[dict[str, Any]], max_workers: int | None = None
) -> list[dict[str, Any]]:
    """Execute independent argument-vector build tasks concurrently."""
    if not build_tasks:
        return []

    def execute(task: dict[str, Any]) -> dict[str, Any]:
        started = time.monotonic()
        try:
            success, stdout, stderr = run_build_command(
                task["command"], task.get("cwd"), task.get("timeout", 300)
            )
            return {
                "task": task.get("name", "unnamed"),
                "success": success,
                "duration": round(time.monotonic() - started, 3),
                "output": stdout,
                "error": stderr,
            }
        except (KeyError, TypeError, ValueError) as exc:
            return {
                "task": task.get("name", "unnamed"),
                "success": False,
                "duration": round(time.monotonic() - started, 3),
                "output": "",
                "error": str(exc),
            }

    results: list[dict[str, Any] | None] = [None] * len(build_tasks)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(execute, task): index
            for index, task in enumerate(build_tasks)
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return [result for result in results if result is not None]


def incremental_build_check(
    source_files: Sequence[str | os.PathLike[str]], build_cache: dict[str, Any]
) -> bool:
    """Return whether any source file is newer than the supplied cache."""
    cached_mtime = float(build_cache.get("last_build_mtime", 0))
    for source_file in source_files:
        path = Path(source_file)
        if not path.exists() or path.stat().st_mtime > cached_mtime:
            return True
    return False


def cleanup_build_artifacts(
    artifacts: Sequence[str | os.PathLike[str]],
    *,
    allowed_root: str | os.PathLike[str] | None = None,
) -> bool:
    """Remove explicitly listed artifacts, optionally constrained to a root."""
    success = True
    root = Path(allowed_root).resolve() if allowed_root is not None else None
    for artifact in artifacts:
        path = Path(artifact)
        if root is not None:
            resolved = path.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                logger.error("Refusing to remove artifact outside %s: %s", root, path)
                success = False
                continue
            if resolved == root:
                logger.error("Refusing to remove the cleanup root itself: %s", root)
                success = False
                continue
        try:
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            elif path.exists() or path.is_symlink():
                path.unlink()
        except OSError as exc:
            logger.error("Failed to remove build artifact %s: %s", path, exc)
            success = False
    return success


def get_build_metrics(build_results: dict[str, Any]) -> dict[str, Any]:
    """Derive stable summary metrics from a build result mapping."""
    success_value = bool(
        build_results.get("success", build_results.get("overall_success", False))
    )
    artifacts = build_results.get(
        "artifacts", build_results.get("artifacts_created", 0)
    )
    artifact_count = (
        len(artifacts)
        if isinstance(artifacts, (list, tuple, set))
        else int(artifacts or 0)
    )
    return {
        "build_success_rate": 1.0 if success_value else 0.0,
        "average_build_time": float(build_results.get("duration", 0.0) or 0.0),
        "artifact_creation_rate": float(artifact_count),
    }


def export_build_report(build_data: dict[str, Any], format: str = "json") -> str:
    """Serialize build data as JSON, YAML, or XML."""
    normalized = format.lower()
    if normalized == "json":
        return json.dumps(build_data, indent=2, default=str)
    if normalized in {"yaml", "yml"}:
        try:
            import yaml

            return yaml.safe_dump(build_data, sort_keys=False)
        except ImportError:
            return "\n".join(f"{key}: {value}" for key, value in build_data.items())
    if normalized == "xml":
        root = ET.Element("build")
        for key, value in build_data.items():
            child = ET.SubElement(root, str(key))
            child.text = (
                json.dumps(value, default=str)
                if isinstance(value, (dict, list))
                else str(value)
            )
        return ET.tostring(root, encoding="unicode")
    raise ValueError(f"Unsupported build report format: {format}")


def import_build_config(config_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Load a JSON or YAML build configuration."""
    path = Path(config_path)
    with path.open(encoding="utf-8") as handle:
        if path.suffix.lower() == ".json":
            data = json.load(handle)
        elif path.suffix.lower() in {".yaml", ".yml"}:
            import yaml

            data = yaml.safe_load(handle)
        else:
            raise ValueError(f"Unsupported build config format: {path.suffix}")
    if not isinstance(data, dict):
        raise ValueError("Build configuration must contain a mapping")
    return data


def get_build_history(limit: int = 20) -> list[dict[str, Any]]:
    """Return the most recent in-process build records."""
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise ValueError("limit must be a non-negative integer")
    with _HISTORY_LOCK:
        return deepcopy(_BUILD_HISTORY[-limit:] if limit else [])[::-1]


def monitor_build_progress(build_id: str) -> dict[str, Any]:
    """Return the current in-process status for a build ID."""
    with _HISTORY_LOCK:
        for record in reversed(_BUILD_HISTORY):
            if record.get("build_id") == build_id:
                return deepcopy(record)
    return {"build_id": build_id, "status": "not_found"}


def rollback_build(build_id: str) -> bool:
    """Remove artifacts recorded for a known build and report success."""
    with _HISTORY_LOCK:
        record = next(
            (
                item
                for item in reversed(_BUILD_HISTORY)
                if item.get("build_id") == build_id
            ),
            None,
        )
    if record is None:
        return False
    return cleanup_build_artifacts(
        record.get("owned_artifacts", []), allowed_root=record.get("output_root")
    )


def _record_build(record: dict[str, Any]) -> None:
    with _HISTORY_LOCK:
        _BUILD_HISTORY.append(deepcopy(record))
        del _BUILD_HISTORY[:-100]


def orchestrate_build_pipeline(
    build_config: dict[str, Any] | None = None,
    *,
    project_path: str | os.PathLike[str] | None = None,
    language: str | None = None,
    output_dir: str | os.PathLike[str] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    """Run configured build commands and/or synthesize a source artifact.

    The returned mapping retains both ``success`` and ``overall_success`` so the
    CLI and current build-synthesis contract tests can inspect both outcomes.
    """
    config = dict(build_config or {})
    config.update({key: value for key, value in overrides.items() if value is not None})
    if project_path is not None:
        config.setdefault("project_path", os.fspath(project_path))
    if language is not None:
        config.setdefault("language", language)
    if output_dir is not None:
        config.setdefault("output_dir", os.fspath(output_dir))

    valid, validation_errors = validate_build_config(config)
    result: dict[str, Any] = {
        "build_id": uuid.uuid4().hex,
        "success": False,
        "overall_success": False,
        "stages": [],
        "artifacts": [],
        "owned_artifacts": [],
        "errors": list(validation_errors),
        "warnings": [],
        "duration": 0.0,
        "status": "pending",
    }
    if not valid:
        result["status"] = "invalid"
        _record_build(result)
        return result

    started = time.monotonic()
    cwd = config.get("project_path") or config.get("cwd")
    dependencies = validate_build_dependencies(config.get("dependencies"))
    if dependencies["missing"]:
        result["errors"].append(
            f"Missing build dependencies: {', '.join(dependencies['missing'])}"
        )
        result["status"] = "invalid"

    commands = config.get("build_commands") or []
    timeout = config.get("timeout", 300)
    for command in commands if not result["errors"] else []:
        stage_started = time.monotonic()
        detail = _run_build_command_detailed(command, cwd=cwd, timeout=timeout)
        result["stages"].append(
            {
                "command": list(command),
                "success": detail["success"],
                "status": detail["status"],
                "duration": round(time.monotonic() - stage_started, 3),
                "output": detail["stdout"],
                "error": detail["stderr"],
            }
        )
        if not detail["success"]:
            result["errors"].append(
                detail["stderr"] or f"Build command failed: {command}"
            )
            result["status"] = detail["status"]
            break

    source_path = config.get("source_path")
    target_path_value = config.get("output_path") or config.get("output_dir")
    target_path = None
    output_root = None
    if target_path_value:
        try:
            target_path, output_root = _resolve_output_path(
                target_path_value, config.get("output_root")
            )
        except (TypeError, ValueError) as exc:
            result["errors"].append(str(exc))
    if source_path and target_path and not result["errors"]:
        artifact_type = config.get("artifact_type", "package")
        existed_before = target_path.exists() or target_path.is_symlink()
        if synthesize_build_artifact(source_path, target_path, artifact_type):
            result["artifacts"].append(str(target_path))
            if not existed_before:
                result["owned_artifacts"].append(str(target_path))
            else:
                result["warnings"].append(
                    "Existing output was updated; it is not owned by this build and will not be removed on rollback"
                )
            result["output_root"] = str(output_root)
        else:
            result["errors"].append("Artifact synthesis failed")

    result["duration"] = round(time.monotonic() - started, 3)
    result["success"] = not result["errors"] and all(
        stage["success"] for stage in result["stages"]
    )
    result["overall_success"] = result["success"]
    if result["success"]:
        result["status"] = "success"
    elif result["status"] == "pending":
        result["status"] = "failed"
    if result["success"] and not result["stages"] and not result["artifacts"]:
        result["status"] = "noop"
        result["warnings"].append("No build command or artifact was requested")
    _record_build(result)
    return result
