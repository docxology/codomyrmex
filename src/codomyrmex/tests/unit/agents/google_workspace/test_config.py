"""Unit tests for codomyrmex.agents.google_workspace.config."""

from codomyrmex.agents.google_workspace.config import GWSConfig, get_config


def test_gws_config_initialization():
    """Test GWSConfig initialization."""
    config = GWSConfig(
        token="token",
        credentials_file="creds.json",
        account="user@example.com",
        timeout=30,
        page_all=True,
    )
    assert config.token == "token"
    assert config.credentials_file == "creds.json"
    assert config.account == "user@example.com"
    assert config.timeout == 30
    assert config.page_all is True


def test_gws_config_properties():
    """Test GWSConfig properties."""
    # Test with token only
    config_token = GWSConfig(
        token="token",
        credentials_file="",
        account="",
        timeout=60,
        page_all=False,
    )
    assert config_token.has_token is True
    assert config_token.has_credentials is False
    assert config_token.has_auth is True

    # Test with credentials only
    config_creds = GWSConfig(
        token="",
        credentials_file="creds.json",
        account="",
        timeout=60,
        page_all=False,
    )
    assert config_creds.has_token is False
    assert config_creds.has_credentials is True
    assert config_creds.has_auth is True

    # Test with neither
    config_none = GWSConfig(
        token="",
        credentials_file="",
        account="",
        timeout=60,
        page_all=False,
    )
    assert config_none.has_token is False
    assert config_none.has_credentials is False
    assert config_none.has_auth is False


def test_get_config_defaults(monkeypatch):
    """Test get_config returns defaults when no env vars are set."""
    # Ensure relevant env vars are unset
    for var in [
        "GOOGLE_WORKSPACE_CLI_TOKEN",
        "GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE",
        "GOOGLE_WORKSPACE_CLI_ACCOUNT",
        "GWS_TIMEOUT",
        "GWS_PAGE_ALL",
    ]:
        monkeypatch.delenv(var, raising=False)

    config = get_config()
    assert config.token == ""
    assert config.credentials_file == ""
    assert config.account == ""
    assert config.timeout == 60  # Default timeout
    assert config.page_all is False


def test_get_config_from_env(monkeypatch):
    """Test get_config reads from environment variables."""
    monkeypatch.setenv("GOOGLE_WORKSPACE_CLI_TOKEN", "env_token")
    monkeypatch.setenv("GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE", "env_creds.json")
    monkeypatch.setenv("GOOGLE_WORKSPACE_CLI_ACCOUNT", "env_user@example.com")
    monkeypatch.setenv("GWS_TIMEOUT", "120")
    monkeypatch.setenv("GWS_PAGE_ALL", "true")

    config = get_config()
    assert config.token == "env_token"
    assert config.credentials_file == "env_creds.json"
    assert config.account == "env_user@example.com"
    assert config.timeout == 120
    assert config.page_all is True
