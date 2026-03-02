import json
import os
from pathlib import Path

import pytest

from codomyrmex.config_audits.auditor import ConfigAuditor
from codomyrmex.config_audits.models import Severity


@pytest.fixture
def temp_config_dir(tmp_path):
    """Fixture to create a temporary directory for configuration files."""
    d = tmp_path / "configs"
    d.mkdir()
    return d


def test_audit_file_not_found(temp_config_dir):
    auditor = ConfigAuditor()
    result = auditor.audit_file(temp_config_dir / "non_existent.json")
    
    assert not result.success
    assert "File not found" in result.summary
    assert len(result.issues) == 1
    assert result.issues[0].rule_id == "SYS001"


def test_audit_valid_json(temp_config_dir):
    config_path = temp_config_dir / "valid.json"
    config_path.write_text('{"key": "value"}')
    os.chmod(config_path, 0o600)
    
    auditor = ConfigAuditor()
    result = auditor.audit_file(config_path)
    
    assert result.success
    assert result.is_compliant
    assert len(result.issues) == 0


def test_audit_invalid_json(temp_config_dir):
    config_path = temp_config_dir / "invalid.json"
    config_path.write_text('{"key": "value"')  # Missing closing brace
    os.chmod(config_path, 0o600)
    
    auditor = ConfigAuditor()
    result = auditor.audit_file(config_path)
    
    assert result.success
    assert not result.is_compliant
    assert any(i.rule_id == "SYN001" for i in result.issues)


def test_audit_hardcoded_secret(temp_config_dir):
    config_path = temp_config_dir / "secret.json"
    config_path.write_text('api_key: "abcde"')
    os.chmod(config_path, 0o600)
    
    auditor = ConfigAuditor()
    result = auditor.audit_file(config_path)
    
    assert result.success
    # SEC001 is HIGH, so it should NOT be compliant
    assert not result.is_compliant
    assert any(i.rule_id == "SEC001" for i in result.issues)


def test_audit_permissive_permissions(temp_config_dir):
    config_path = temp_config_dir / "permissive.json"
    config_path.write_text('{"key": "value"}')
    os.chmod(config_path, 0o666)  # World readable and writable
    
    auditor = ConfigAuditor()
    result = auditor.audit_file(config_path)
    
    assert result.success
    assert any(i.rule_id == "SEC002" for i in result.issues)
    # SEC002 is MEDIUM, so it should still be compliant by our definition
    assert result.is_compliant


def test_audit_prod_debug(temp_config_dir):
    config_path = temp_config_dir / "prod_config.json"
    config_path.write_text('{"debug": true}')
    os.chmod(config_path, 0o600)
    
    auditor = ConfigAuditor()
    result = auditor.audit_file(config_path)
    
    assert result.success
    assert not result.is_compliant
    assert any(i.rule_id == "OPS001" for i in result.issues)


def test_audit_directory(temp_config_dir):
    (temp_config_dir / "one.json").write_text('{"a": 1}')
    (temp_config_dir / "two.yaml").write_text('b: 2')
    
    for f in temp_config_dir.glob("*"):
        os.chmod(f, 0o600)
        
    auditor = ConfigAuditor()
    results = auditor.audit_directory(temp_config_dir)
    
    assert len(results) == 2
    assert all(r.success for r in results)


def test_generate_report(temp_config_dir):
    config_path = temp_config_dir / "issue.json"
    config_path.write_text('password: "abc"')
    os.chmod(config_path, 0o600)
    
    auditor = ConfigAuditor()
    result = auditor.audit_file(config_path)
    report = auditor.generate_report([result])
    
    assert "=== Configuration Audit Report ===" in report
    assert "SEC001" in report
    assert "Potential password found in plain text" in report
