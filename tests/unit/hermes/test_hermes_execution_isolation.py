"""Hermes config lookup and subprocess environment use only isolated test inputs."""

import json
import sys
from pathlib import Path

import pytest

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.hermes.client_pkg import HermesClient
from codomyrmex.agents.hermes.client_pkg.errors import HermesError
from codomyrmex.agents.hermes.hermes_paths import resolve_hermes_home

pytestmark = pytest.mark.unit
_KEYS = ("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY")


@pytest.fixture
def local_cli_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> HermesClient:
    """Execute an actual local CLI program; no backend or method is replaced."""
    for name in _KEYS:
        monkeypatch.delenv(name, raising=False)
    command = tmp_path / "local-hermes"
    command.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "if sys.argv[1] == 'config':\n"
        "    print('OpenRouter (not set)')\n"
        "elif sys.argv[1] == 'version':\n"
        "    print('local test CLI')\n"
        "else:\n"
        f"    keys = {_KEYS!r}\n"
        "    print(json.dumps({k: os.environ.get(k) == 'unit-only-' + k for k in keys}))\n",
        encoding="utf-8",
    )
    command.chmod(0o700)
    return HermesClient(
        config={
            "hermes_command": str(command),
            "hermes_backend": "cli",
            "hermes_skill_profile_disable": True,
        }
    )


def test_config_lookup_uses_configured_home(
    local_cli_client: HermesClient, hermes_test_home: Path
) -> None:
    assert resolve_hermes_home() == hermes_test_home
    assert not local_cli_client._is_cli_configured()
    (hermes_test_home / ".env").write_text(
        "OPENROUTER_API_KEY=unit-only-OPENROUTER_API_KEY\n", encoding="utf-8"
    )
    assert local_cli_client._is_cli_configured()


def test_unset_home_retains_legacy_path_metadata_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolving the default path does not load or create operator state."""
    monkeypatch.delenv("HERMES_HOME", raising=False)
    assert resolve_hermes_home() == Path.home() / ".hermes"


def test_subprocess_credentials_come_from_configured_home(
    local_cli_client: HermesClient, hermes_test_home: Path
) -> None:
    (hermes_test_home / ".env").write_text(
        "".join(f"{name}=unit-only-{name}\n" for name in _KEYS), encoding="utf-8"
    )
    response = local_cli_client._execute_via_cli(AgentRequest(prompt="local probe"))
    assert json.loads(response.content) == dict.fromkeys(_KEYS, True)


@pytest.mark.parametrize("backend", ["none", "nonexistent"])
def test_inactive_backend_fails_before_cli_lookup(tmp_path: Path, backend: str) -> None:
    """A nonexistent command cannot be invoked or used to inspect configuration."""
    client = HermesClient(
        config={
            "hermes_backend": backend,
            "hermes_command": str(tmp_path / "missing-cli"),
            "hermes_skill_profile_disable": True,
        }
    )
    request = AgentRequest(prompt="must not dispatch")
    with pytest.raises(HermesError, match="No supported Hermes backend"):
        client._execute_primary(request)
    with pytest.raises(HermesError, match="No supported Hermes backend"):
        list(client._stream_impl(request))
