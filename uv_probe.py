"""TEMPORARY diagnostic plugin — remove before merge.

Records every process the suite spawns, with the caller's file and line, so a
`uv` invocation that rebuilds the project environment names itself. The 3.12
matrix leg finishes with `.venv` at 3.11, so something in the suite runs uv
without `--python`; the stub gate in `tests/unit/release/test_environment_safety.py`
proves no *test* passes `"uv"` to a subprocess, so the caller is production code
invoked by a test.

Loaded with `-p uv_probe`; writes to `$UV_PROBE_LOG` (default `uv-probe.log`).
"""

from __future__ import annotations

import os
import subprocess
import time
import traceback
from pathlib import Path

_LOG = Path(os.environ.get("UV_PROBE_LOG", "uv-probe.log"))
_INTERESTING = ("uv",)
_original_init = subprocess.Popen.__init__


def _caller() -> str:
    frames = [
        f"{Path(frame.filename).name}:{frame.lineno} in {frame.name}"
        for frame in traceback.extract_stack()
        if "uv_probe" not in frame.filename and "subprocess.py" not in frame.filename
    ]
    return " <- ".join(reversed(frames[-4:]))


def _record(kind: str, argv: list[str], cwd: object, env: object) -> None:
    try:
        environment = env if isinstance(env, dict) else os.environ
        uv_env = {
            key: value for key, value in environment.items() if key.startswith("UV_")
        }
        with _LOG.open("a", encoding="utf-8") as handle:
            handle.write(
                f"{time.strftime('%H:%M:%S')} pid={os.getpid()} {kind} "
                f"argv={argv[:8]} cwd={cwd!r} uv_env={uv_env} caller={_caller()}\n"
            )
    except Exception:  # a diagnostic must never break the suite
        pass


def _describe(args: object) -> list[str]:
    if isinstance(args, (list, tuple)):
        return [str(item) for item in args]
    return [str(args)]


def _patched_init(self, args, *positional, **keyword):  # type: ignore[no-untyped-def]
    argv = _describe(args)
    program = Path(argv[0]).name if argv else ""
    if program in _INTERESTING or program.startswith("python"):
        _record(
            "spawn",
            argv,
            keyword.get("cwd"),
            keyword.get("env"),
        )
    return _original_init(self, args, *positional, **keyword)


subprocess.Popen.__init__ = _patched_init  # type: ignore[method-assign]
