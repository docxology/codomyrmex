import os

from codomyrmex.config_audits.mcp_tools import config_audit_directory, config_audit_file


def test_config_audit_file(tmp_path):
    config_path = tmp_path / "config.yaml"  # Use yaml so JSON lint rule doesn't fail parsing an invalid json, but we just need secret check
    config_path.write_text('api_key: "secret123"')
    os.chmod(config_path, 0o600)

    report = config_audit_file(str(config_path))

    assert "=== Configuration Audit Report ===" in report
    assert "SEC001" in report
    assert "Potential API key found in plain text" in report
    assert "[FAIL]" in report


def test_config_audit_directory(tmp_path):
    (tmp_path / "one.json").write_text('{"a": 1}')
    (tmp_path / "two.yaml").write_text('password: "mypassword"')

    for f in tmp_path.glob("*"):
        os.chmod(f, 0o600)

    report = config_audit_directory(str(tmp_path), pattern="*.*")

    assert "=== Configuration Audit Report ===" in report
    assert "Files Audited: 2" in report
    assert "SEC001" in report
    assert "[FAIL]" in report
    assert "[PASS]" in report
