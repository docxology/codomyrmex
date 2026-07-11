"""Tests for :mod:`codomyrmex.agents.hermes.gateway_verify`."""

from __future__ import annotations

import plistlib
from pathlib import Path

import pytest

from codomyrmex.agents.hermes import gateway_verify


def test_load_dotenv_values_parses_and_strips_quotes(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        '\n# c\n\nFOO=bar\n  TELEGRAM_BOT_TOKEN="abc:def"  \nEMPTY=\n',
        encoding="utf-8",
    )
    got = gateway_verify.load_dotenv_values(env_file)
    assert got["FOO"] == "bar"
    assert got["TELEGRAM_BOT_TOKEN"] == "abc:def"
    assert got["EMPTY"] == ""
    assert "c" not in got


def test_load_dotenv_values_missing_file() -> None:
    assert gateway_verify.load_dotenv_values(Path("/nonexistent/no.env")) == {}


def test_default_hermes_home_candidates() -> None:
    homes = gateway_verify.default_hermes_home_candidates()
    assert len(homes) == 1
    assert homes[0] == Path.home() / ".hermes"


def test_try_extract_gateway_launch_match() -> None:
    plist = {
        "Label": "ai.hermes.gateway",
        "ProgramArguments": [
            "/Users/x/.hermes/hermes-agent/venv/bin/python",
            "-m",
            "hermes_cli.main",
            "gateway",
            "run",
            "--replace",
        ],
        "EnvironmentVariables": {
            "HERMES_HOME": "/Users/x/.hermes",
        },
    }
    row = gateway_verify.try_extract_gateway_launch(plist)
    assert row is not None
    assert row.label == "ai.hermes.gateway"
    assert row.hermes_home == Path("/Users/x/.hermes")
    assert row.python_executable == Path(
        "/Users/x/.hermes/hermes-agent/venv/bin/python"
    )


def test_try_extract_gateway_launch_no_match() -> None:
    assert (
        gateway_verify.try_extract_gateway_launch(
            {"Label": "x", "ProgramArguments": ["python", "foo"]}
        )
        is None
    )


def test_try_extract_gateway_launch_from_xml_bytes() -> None:
    xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.gateway.test</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/h/venv/bin/python</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>gateway</string>
        <string>run</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_HOME</key>
        <string>/opt/hdata</string>
    </dict>
</dict>
</plist>
"""
    plist = plistlib.loads(xml)
    assert isinstance(plist, dict)
    row = gateway_verify.try_extract_gateway_launch(plist)
    assert row is not None
    assert row.label == "ai.hermes.gateway.test"
    assert row.hermes_home == Path("/opt/hdata")


def test_iter_hermes_gateway_launch_plists_skips_bad_files(tmp_path: Path) -> None:
    (tmp_path / "noise.txt").write_text("x", encoding="utf-8")
    bad = tmp_path / "bad.plist"
    bad.write_text("not a plist", encoding="utf-8")
    good_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.gateway.unit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/venv/bin/python</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>gateway</string>
        <string>run</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_HOME</key>
        <string>/tmp/hh</string>
    </dict>
</dict>
</plist>
"""
    (tmp_path / "good.plist").write_bytes(good_xml)
    rows = list(gateway_verify.iter_hermes_gateway_launch_plists(tmp_path))
    assert len(rows) == 1
    assert rows[0].label == "ai.hermes.gateway.unit"


def test_launchd_python_matches_repo(tmp_path: Path) -> None:
    repo = tmp_path / "hermes-agent"
    vpy = repo / "venv" / "bin" / "python"
    vpy.parent.mkdir(parents=True)
    vpy.write_text("", encoding="utf-8")
    row = gateway_verify.HermesGatewayLaunchPlist(
        label="x",
        hermes_home=None,
        python_executable=vpy,
    )
    assert gateway_verify.launchd_python_matches_repo(row, repo)


@pytest.mark.skipif(
    not gateway_verify.is_darwin(),
    reason="default_launch_agents_dir layout is macOS-specific",
)
def test_default_launch_agents_dir_exists_or_parent() -> None:
    d = gateway_verify.default_launch_agents_dir()
    assert d == Path.home() / "Library" / "LaunchAgents"
