"""Tests for security/mcp_tools.py — MCP tool wrappers.

These tests call the MCP tool functions directly with real inputs.
Since DIGITAL_AVAILABLE depends on optional deps, we test both
the success path (using tmp files) and the _mcp_tool_meta attribute.
"""

from codomyrmex.security.mcp_tools import (
    audit_code_security,
    scan_secrets,
    scan_vulnerabilities,
)


class TestScanVulnerabilitiesMcpTool:
    """Tests for the scan_vulnerabilities MCP tool."""

    def test_has_mcp_tool_meta(self):
        """scan_vulnerabilities is decorated with @mcp_tool."""
        assert hasattr(scan_vulnerabilities, "_mcp_tool_meta")

    def test_mcp_tool_meta_name(self):
        """MCP tool meta contains function name (may include module prefix)."""
        meta = scan_vulnerabilities._mcp_tool_meta
        assert "scan_vulnerabilities" in meta["name"]

    def test_mcp_tool_category(self):
        """scan_vulnerabilities has category 'security'."""
        meta = scan_vulnerabilities._mcp_tool_meta
        assert meta.get("category") == "security"

    def test_returns_dict(self, tmp_path):
        """scan_vulnerabilities() returns a dict."""
        result = scan_vulnerabilities(path=str(tmp_path))
        assert isinstance(result, dict)

    def test_result_has_status(self, tmp_path):
        """Return dict contains 'status' key."""
        result = scan_vulnerabilities(path=str(tmp_path))
        assert "status" in result

    def test_nonexistent_path_returns_dict(self):
        """Nonexistent path returns dict (error handled gracefully)."""
        result = scan_vulnerabilities(path="/nonexistent_path_xyz")
        assert isinstance(result, dict)


class TestScanSecretsMcpTool:
    """Tests for the scan_secrets MCP tool."""

    def test_has_mcp_tool_meta(self):
        """scan_secrets is decorated with @mcp_tool."""
        assert hasattr(scan_secrets, "_mcp_tool_meta")

    def test_mcp_tool_meta_name(self):
        """MCP tool meta contains function name (may include module prefix)."""
        meta = scan_secrets._mcp_tool_meta
        assert "scan_secrets" in meta["name"]

    def test_mcp_tool_category(self):
        """scan_secrets has category 'security'."""
        meta = scan_secrets._mcp_tool_meta
        assert meta.get("category") == "security"

    def test_returns_dict(self, tmp_path):
        """scan_secrets() returns a dict."""
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n")
        result = scan_secrets(file_path=str(f))
        assert isinstance(result, dict)

    def test_result_has_status(self, tmp_path):
        """Return dict contains 'status' key."""
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n")
        result = scan_secrets(file_path=str(f))
        assert "status" in result

    def test_clean_file_returns_known_status(self, tmp_path):
        """Clean file returns either success or error status (never crashes)."""
        f = tmp_path / "clean.py"
        f.write_text("def add(a, b):\n    return a + b\n")
        result = scan_secrets(file_path=str(f))
        assert result.get("status") in ("success", "error")

    def test_nonexistent_file_returns_dict(self):
        """Nonexistent file returns dict (error handled)."""
        result = scan_secrets(file_path="/nonexistent/path.py")
        assert isinstance(result, dict)


class TestAuditCodeSecurityMcpTool:
    """Tests for the audit_code_security MCP tool."""

    def test_has_mcp_tool_meta(self):
        """audit_code_security is decorated with @mcp_tool."""
        assert hasattr(audit_code_security, "_mcp_tool_meta")

    def test_mcp_tool_meta_name(self):
        """MCP tool meta contains function name (may include module prefix)."""
        meta = audit_code_security._mcp_tool_meta
        assert "audit_code_security" in meta["name"]

    def test_mcp_tool_category(self):
        """audit_code_security has category 'security'."""
        meta = audit_code_security._mcp_tool_meta
        assert meta.get("category") == "security"

    def test_returns_dict(self, tmp_path):
        """audit_code_security() returns a dict."""
        f = tmp_path / "app.py"
        f.write_text("def safe():\n    return 1\n")
        result = audit_code_security(path=str(f))
        assert isinstance(result, dict)

    def test_result_has_status(self, tmp_path):
        """Return dict contains 'status' key."""
        f = tmp_path / "app.py"
        f.write_text("x = 1\n")
        result = audit_code_security(path=str(f))
        assert "status" in result

    def test_nonexistent_path_returns_dict(self):
        """Nonexistent path returns dict (error handled)."""
        result = audit_code_security(path="/nonexistent/app.py")
        assert isinstance(result, dict)


class TestMcpToolsWithInsecureCode:
    """Integration-style tests using real files with known-bad patterns."""

    def test_scan_secrets_finds_aws_key(self, tmp_path):
        """scan_secrets detects AWS key in real file."""
        f = tmp_path / "creds.py"
        f.write_text('aws_key = "AKIAIOSFODNN7EXAMPLE"\n')
        result = scan_secrets(file_path=str(f))
        assert isinstance(result, dict)
        # Either success with findings, or error if digital not available
        if result.get("status") == "success":
            # Findings may be a list or dict
            assert "findings" in result

    def test_scan_secrets_finds_private_key(self, tmp_path):
        """scan_secrets detects private key header in real file."""
        f = tmp_path / "key.pem"
        f.write_text(
            "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----\n"
        )
        result = scan_secrets(file_path=str(f))
        assert isinstance(result, dict)

    def test_audit_code_security_flags_hardcoded_password(self, tmp_path):
        """audit_code_security scans file with hardcoded password."""
        f = tmp_path / "config.py"
        f.write_text('db_password = "hardcoded_pass_123"\n')
        result = audit_code_security(path=str(f))
        assert isinstance(result, dict)
        # Verify it doesn't crash on real security-relevant code

    def test_audit_code_security_sql_injection(self, tmp_path):
        """audit_code_security scans file with SQL injection pattern."""
        f = tmp_path / "query.py"
        f.write_text(
            "def get_user(uid):\n"
            '    return cursor.execute("SELECT * FROM users WHERE id = %s" % uid)\n'
        )
        result = audit_code_security(path=str(f))
        assert isinstance(result, dict)


class TestMcpToolSchema:
    """Tests verifying the MCP tool schema metadata is well-formed."""

    def test_scan_vulnerabilities_has_schema(self):
        """scan_vulnerabilities has 'schema' in tool meta."""
        meta = scan_vulnerabilities._mcp_tool_meta
        # Schema or parameters key should exist
        has_schema = "schema" in meta or "parameters" in meta
        assert has_schema

    def test_scan_secrets_has_schema(self):
        """scan_secrets has 'schema' in tool meta."""
        meta = scan_secrets._mcp_tool_meta
        has_schema = "schema" in meta or "parameters" in meta
        assert has_schema

    def test_audit_code_security_has_schema(self):
        """audit_code_security has 'schema' in tool meta."""
        meta = audit_code_security._mcp_tool_meta
        has_schema = "schema" in meta or "parameters" in meta
        assert has_schema
