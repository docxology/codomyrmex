#!/usr/bin/env python3
"""Unified post-``hermes update`` checks: repo, doctor, Codomyrmex + upstream Telegram tests.

Usage::

    uv run python scripts/agents/hermes/verify_hermes_gateway_post_update.py
    uv run python scripts/agents/hermes/verify_hermes_gateway_post_update.py --launchd
    uv run python scripts/agents/hermes/verify_hermes_gateway_post_update.py \\
        --hermes-home ~/.hermes --hermes-home ~/other/.hermes

Optional ``--hermes-home`` (repeatable): Telegram ``getMe`` per home when ``TELEGRAM_BOT_TOKEN``
is set in that home's ``.env`` (tokens are never printed).

``--launchd`` (macOS): list gateway plists under ``~/Library/LaunchAgents`` and warn if the
Python path does not match ``<repo>/venv/bin/python``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Bootstrap path when not installed as a package
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
try:
    from codomyrmex.agents.hermes.gateway_verify import (
        default_launch_agents_dir,
        is_darwin,
        iter_hermes_gateway_launch_plists,
        launchd_python_matches_repo,
        load_dotenv_values,
    )
    from codomyrmex.agents.hermes.hermes_client import HermesClient
    from codomyrmex.agents.hermes.hermes_paths import (
        discover_hermes_cli_binary,
        require_hermes_agent_repo,
    )
except ImportError:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
    from codomyrmex.agents.hermes.gateway_verify import (
        default_launch_agents_dir,
        is_darwin,
        iter_hermes_gateway_launch_plists,
        launchd_python_matches_repo,
        load_dotenv_values,
    )
    from codomyrmex.agents.hermes.hermes_client import HermesClient
    from codomyrmex.agents.hermes.hermes_paths import (
        discover_hermes_cli_binary,
        require_hermes_agent_repo,
    )


_CX_GATEWAY_TESTS = [
    "src/codomyrmex/tests/unit/hermes/test_hermes_gateway_config.py",
    "src/codomyrmex/tests/integration/hermes/test_gateway_identity_resolution.py",
    "src/codomyrmex/tests/integration/hermes/test_gateway_directory_sync.py",
    "src/codomyrmex/tests/integration/hermes/test_gateway_adapter_latency.py",
]


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )


def _print_section(title: str) -> None:
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def _telegram_getme(token: str, timeout_s: int = 25) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            body = json.loads(resp.read().decode())
    except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError) as e:
        return False, type(e).__name__
    if not body.get("ok"):
        desc = body.get("description")
        if isinstance(desc, str) and desc:
            return False, desc[:200]
        return False, "telegram_api_error"
    un = (body.get("result") or {}).get("username", "?")
    return True, f"@{un}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Hermes gateway install after hermes update."
    )
    parser.add_argument(
        "--hermes-home",
        action="append",
        default=[],
        metavar="PATH",
        help="Repeatable: HERMES_HOME to run Telegram getMe when .env has token.",
    )
    parser.add_argument(
        "--launchd",
        action="store_true",
        help="macOS: scan ~/Library/LaunchAgents for Hermes gateway plists.",
    )
    args = parser.parse_args()
    failures = 0

    try:
        repo = require_hermes_agent_repo()
    except FileNotFoundError:
        print(
            "ERROR: Hermes agent repository not found (see codomyrmex hermes paths).",
            file=sys.stderr,
        )
        return 1

    cli = discover_hermes_cli_binary()
    if not cli:
        print(
            "ERROR: hermes CLI not found. Set HERMES_CLI_PATH or install under "
            f"{repo}/venv/bin/hermes",
            file=sys.stderr,
        )
        return 1

    _print_section("Git (hermes-agent)")
    gr = _run(["git", "-C", str(repo), "log", "-1", "--oneline"])
    if gr.returncode != 0:
        print(gr.stderr or gr.stdout, file=sys.stderr)
        failures += 1
    else:
        print(gr.stdout.strip())

    _print_section("Hermes CLI version")
    vr = _run([cli, "--version"], cwd=repo)
    if vr.returncode != 0:
        print(vr.stderr or vr.stdout, file=sys.stderr)
        failures += 1
    else:
        print(vr.stdout.strip())

    _print_section("Hermes doctor (via HermesClient)")
    try:
        client = HermesClient()
    except Exception:
        print("ERROR: HermesClient initialization failed", file=sys.stderr)
        failures += 1
    else:
        doc = client.run_doctor()
        if not doc.get("success"):
            print(
                doc.get("error") or doc.get("stderr") or "doctor failed",
                file=sys.stderr,
            )
            failures += 1
        else:
            out = doc.get("output") or ""
            for line in out.splitlines()[:15]:
                print(line)
            if len(out.splitlines()) > 15:
                print(f"... ({len(out.splitlines()) - 15} more lines)")
            print("OK hermes doctor")

    _print_section("Codomyrmex gateway pytest subset")
    cx_cmd = ["uv", "run", "pytest", "-q", "--tb=short", *_CX_GATEWAY_TESTS]
    cx_env = {**os.environ, "HYPOTHESIS_NO_NPY": "1"}
    cx = _run(cx_cmd, cwd=_REPO_ROOT, env=cx_env)
    print(cx.stdout, end="")
    if cx.stderr:
        print(cx.stderr, end="", file=sys.stderr)
    if cx.returncode != 0:
        failures += 1
    else:
        print("OK codomyrmex gateway tests")

    venv_py = repo / "venv" / "bin" / "python"
    _print_section("Upstream hermes-agent Telegram tests")
    if not venv_py.is_file():
        print(f"SKIP: no venv interpreter at {venv_py}")
    else:
        tg_dir = repo / "tests" / "gateway"
        paths: list[Path] = []
        if tg_dir.is_dir():
            paths.extend(sorted(tg_dir.glob("test_telegram*.py")))
            paths.extend(sorted(tg_dir.glob("test_telegram_network*.py")))
        paths = list(dict.fromkeys(paths))
        if not paths:
            print(f"SKIP: no test_telegram*.py under {tg_dir}")
        else:
            up_cmd = [
                str(venv_py),
                "-m",
                "pytest",
                "-q",
                "--tb=short",
                *[str(p) for p in paths],
            ]
            up = _run(up_cmd, cwd=repo)
            print(up.stdout, end="")
            if up.stderr:
                print(up.stderr, end="", file=sys.stderr)
            if up.returncode != 0:
                failures += 1
            else:
                print("OK upstream telegram tests")

    if args.hermes_home:
        _print_section("Telegram getMe (optional)")
        for raw in args.hermes_home:
            home = Path(raw).expanduser().resolve()
            env_path = home / ".env"
            vals = load_dotenv_values(env_path)
            tok = vals.get("TELEGRAM_BOT_TOKEN")
            if not tok:
                print(f"{home}: SKIP (Telegram bot env not set in .env)")
                continue
            ok, info = _telegram_getme(tok)
            if ok:
                print(f"{home}: getMe ok {info}")
            else:
                print(f"{home}: getMe FAIL {info}", file=sys.stderr)
                failures += 1

    if args.launchd:
        _print_section("launchd gateway plists")
        if not is_darwin():
            print("SKIP: not macOS")
        else:
            lad = default_launch_agents_dir()
            rows = list(iter_hermes_gateway_launch_plists(lad))
            if not rows:
                print(f"No Hermes gateway plists under {lad}")
            for row in rows:
                match = launchd_python_matches_repo(row, repo)
                hh = row.hermes_home or "(no HERMES_HOME)"
                py = row.python_executable or "(unknown python)"
                flag = "OK" if match else "WARN"
                print(f"  [{flag}] {row.label} HERMES_HOME={hh} python={py}")
                if not match:
                    failures += 1

    _print_section("Summary")
    if failures:
        print(f"FAILED with {failures} issue(s)")
        return 1
    print("All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
