"""Helpers for post-update Hermes gateway verification (no live Telegram here).

Used by ``scripts/agents/hermes/verify_hermes_gateway_post_update.py`` and unit tests.
"""

from __future__ import annotations

import plistlib
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HermesGatewayLaunchPlist:
    """launchd plist row for ``python -m hermes_cli.main gateway run``."""

    label: str
    hermes_home: Path | None
    python_executable: Path | None


def load_dotenv_values(path: Path) -> dict[str, str]:
    """Parse a minimal KEY=value .env file (comments and blank lines ignored)."""
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if key:
            out[key] = val
    return out


def default_hermes_home_candidates() -> list[Path]:
    """Default single-instance Hermes data directory (expand with CLI ``--hermes-home``)."""
    return [Path.home() / ".hermes"]


def _argv_is_hermes_gateway_run(argv: list) -> bool:
    if not isinstance(argv, list) or len(argv) < 5:
        return False
    try:
        m_idx = argv.index("-m")
    except ValueError:
        return False
    if m_idx + 1 >= len(argv):
        return False
    if argv[m_idx + 1] != "hermes_cli.main":
        return False
    rest = argv[m_idx + 2 :]
    return len(rest) >= 2 and rest[0] == "gateway" and rest[1] == "run"


def try_extract_gateway_launch(plist: dict) -> HermesGatewayLaunchPlist | None:
    """If *plist* describes a Hermes gateway launchd job, return its fields; else None."""
    label = plist.get("Label")
    if not isinstance(label, str) or not label:
        return None
    argv = plist.get("ProgramArguments")
    if not _argv_is_hermes_gateway_run(argv):
        return None
    env = plist.get("EnvironmentVariables")
    hermes_home: Path | None = None
    if isinstance(env, dict):
        hh = env.get("HERMES_HOME")
        if isinstance(hh, str) and hh.strip():
            hermes_home = Path(hh).expanduser()
    py_exe: Path | None = None
    if isinstance(argv, list) and argv and isinstance(argv[0], str):
        py_exe = Path(argv[0]).expanduser()
    return HermesGatewayLaunchPlist(
        label=label, hermes_home=hermes_home, python_executable=py_exe
    )


def load_plist_path(path: Path) -> dict:
    """Load an XML or binary plist; raises OSError / plistlib.InvalidFileException on failure."""
    data = path.read_bytes()
    if data[:8] == b"bplist00":
        return plistlib.loads(data)
    return plistlib.loads(data)


def iter_hermes_gateway_launch_plists(
    launch_agents_dir: Path,
):
    """Scan *launch_agents_dir* for plists that launch ``hermes_cli.main gateway run``."""
    if not launch_agents_dir.is_dir():
        return
    for plist_path in sorted(launch_agents_dir.glob("*.plist")):
        try:
            plist = load_plist_path(plist_path)
        except (OSError, TypeError, ValueError):
            continue
        if not isinstance(plist, dict):
            continue
        row = try_extract_gateway_launch(plist)
        if row is not None:
            yield row


def expected_hermes_venv_python(repo: Path) -> Path:
    """Canonical interpreter: ``<repo>/venv/bin/python``."""
    return (repo / "venv" / "bin" / "python").resolve()


def launchd_python_matches_repo(row: HermesGatewayLaunchPlist, repo: Path) -> bool:
    """True if plist's Python path equals the repo venv interpreter."""
    expected = expected_hermes_venv_python(repo)
    if row.python_executable is None:
        return False
    try:
        return row.python_executable.resolve() == expected
    except OSError:
        return False


def default_launch_agents_dir() -> Path:
    """``~/Library/LaunchAgents`` (macOS)."""
    return Path.home() / "Library" / "LaunchAgents"


def is_darwin() -> bool:
    return sys.platform == "darwin"
