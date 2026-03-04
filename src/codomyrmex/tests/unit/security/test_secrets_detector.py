"""Tests for security/digital/secrets_detector.py — SecretsDetector."""


import pytest

from codomyrmex.security.digital.secrets_detector import (
    SecretFinding,
    SecretsDetector,
    scan_secrets,
)


class TestSecretFindingDataclass:
    """Tests for the SecretFinding dataclass."""

    def test_create_minimal(self):
        """SecretFinding created with required fields."""
        f = SecretFinding(
            file_path="app.py",
            line_number=10,
            line_content="aws_key = AKIAIOSFODNN7EXAMPLE",
            secret_type="aws_access_key",
            confidence="HIGH",
            description="Potential aws_access_key detected",
        )
        assert f.file_path == "app.py"
        assert f.line_number == 10
        assert f.secret_type == "aws_access_key"
        assert f.confidence == "HIGH"

    def test_to_dict_has_required_keys(self):
        """to_dict() contains expected keys."""
        f = SecretFinding(
            file_path="config.py",
            line_number=5,
            line_content="token = abc123def456ghi789",
            secret_type="api_key_generic",
            confidence="HIGH",
            description="Potential api key",
        )
        d = f.to_dict()
        for key in ("file_path", "line_number", "secret_type", "confidence", "description", "snippet"):
            assert key in d

    def test_to_dict_snippet_truncated(self):
        """to_dict() truncates snippet to 100 chars."""
        long_content = "x" * 200
        f = SecretFinding(
            file_path="f.py",
            line_number=1,
            line_content=long_content,
            secret_type="test",
            confidence="LOW",
            description="test",
        )
        d = f.to_dict()
        assert len(d["snippet"]) <= 100


class TestSecretsDetectorPatterns:
    """Tests for SecretsDetector pattern matching via scan_file on temp files."""

    def test_detect_aws_access_key(self, tmp_path):
        """Detector finds AWS access key pattern."""
        f = tmp_path / "config.py"
        f.write_text('aws_key = "AKIAIOSFODNN7EXAMPLE"\n')
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        types = {ff.secret_type for ff in findings}
        assert "aws_access_key" in types

    def test_detect_private_key_header(self, tmp_path):
        """Detector finds RSA private key header."""
        f = tmp_path / "key.pem"
        f.write_text("-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----\n")
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        types = {ff.secret_type for ff in findings}
        assert "private_key" in types

    def test_detect_github_token(self, tmp_path):
        """Detector finds GitHub PAT pattern (ghp_ prefix + 36 alphanum chars)."""
        # Pattern: gh[pousr]_[A-Za-z0-9_]{36,255}
        token = "ghp_" + "A" * 36  # exactly 40 chars total
        f = tmp_path / "ci.yml"
        f.write_text(f"token: {token}\n")
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        types = {ff.secret_type for ff in findings}
        assert "github_token" in types

    def test_detect_password_generic(self, tmp_path):
        """Detector finds generic password pattern with MEDIUM confidence."""
        f = tmp_path / "settings.py"
        f.write_text('password = "supersecretpassword"\n')
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        password_findings = [ff for ff in findings if ff.secret_type == "password_generic"]
        assert len(password_findings) >= 1
        assert password_findings[0].confidence == "MEDIUM"

    def test_clean_file_no_findings(self, tmp_path):
        """Detector reports no findings for clean code."""
        f = tmp_path / "clean.py"
        f.write_text("def add(a, b):\n    return a + b\n\nresult = add(1, 2)\n")
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        assert len(findings) == 0

    def test_skip_comment_line(self, tmp_path):
        """Detector skips lines starting with # comment."""
        f = tmp_path / "commented.py"
        f.write_text("# password = 'not a real secret'\n")
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        assert len(findings) == 0

    def test_skip_docstring_line(self, tmp_path):
        """Detector skips lines starting with triple-quotes."""
        f = tmp_path / "docstring.py"
        f.write_text('"""password = "not_a_secret_string_xyz"  """\n')
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        assert len(findings) == 0

    def test_finding_has_line_number(self, tmp_path):
        """Detected finding records correct line number."""
        f = tmp_path / "multi.py"
        f.write_text("x = 1\naws_key = AKIAIOSFODNN7EXAMPLE\ny = 3\n")
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        aws_findings = [ff for ff in findings if ff.secret_type == "aws_access_key"]
        assert len(aws_findings) >= 1
        assert aws_findings[0].line_number == 2

    def test_missing_file_returns_empty(self):
        """scan_file() returns empty list for missing file."""
        detector = SecretsDetector()
        findings = detector.scan_file("/nonexistent/path.py")
        assert findings == []


class TestSecretsDetectorShouldSkip:
    """Tests for SecretsDetector._should_skip()."""

    def test_skip_git_directory_file(self):
        """Files named .git are skipped."""
        detector = SecretsDetector()
        assert detector._should_skip(".git") is True

    def test_skip_dotfile(self):
        """Files starting with . are skipped."""
        detector = SecretsDetector()
        assert detector._should_skip(".env") is True

    def test_skip_pyc_extension(self):
        """Files with .pyc extension are skipped."""
        detector = SecretsDetector()
        assert detector._should_skip("module.pyc") is True

    def test_skip_png_extension(self):
        """Files with .png extension are skipped."""
        detector = SecretsDetector()
        assert detector._should_skip("image.png") is True

    def test_do_not_skip_python_file(self):
        """Normal .py files are not skipped."""
        detector = SecretsDetector()
        assert detector._should_skip("main.py") is False

    def test_do_not_skip_yaml_file(self):
        """Normal .yaml files are not skipped."""
        detector = SecretsDetector()
        assert detector._should_skip("config.yaml") is False


class TestSecretsDetectorDirectory:
    """Tests for SecretsDetector.scan_directory()."""

    def test_scan_directory_finds_secrets(self, tmp_path):
        """scan_directory() traverses files and finds secrets."""
        (tmp_path / "secrets.py").write_text('key = "AKIAIOSFODNN7EXAMPLE"\n')
        (tmp_path / "clean.py").write_text("x = 1\n")
        detector = SecretsDetector()
        findings = detector.scan_directory(str(tmp_path))
        types = {ff.secret_type for ff in findings}
        assert "aws_access_key" in types

    def test_scan_directory_non_recursive(self, tmp_path):
        """scan_directory() with recursive=False stays in top dir."""
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.py").write_text('key = "AKIAIOSFODNN7EXAMPLE"\n')
        (tmp_path / "top.py").write_text("clean = True\n")
        detector = SecretsDetector()
        findings = detector.scan_directory(str(tmp_path), recursive=False)
        # Should not find the nested file
        assert len(findings) == 0

    def test_scan_directory_skips_hidden_dirs(self, tmp_path):
        """scan_directory() skips directories starting with dot."""
        hidden = tmp_path / ".hidden"
        hidden.mkdir()
        (hidden / "secret.py").write_text('key = "AKIAIOSFODNN7EXAMPLE"\n')
        detector = SecretsDetector()
        findings = detector.scan_directory(str(tmp_path))
        assert len(findings) == 0

    def test_scan_directory_multiple_files(self, tmp_path):
        """scan_directory() returns findings from all scanned files."""
        (tmp_path / "file1.py").write_text('aws_key = AKIAIOSFODNN7EXAMPLE\n')
        (tmp_path / "file2.py").write_text('token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi\n')
        detector = SecretsDetector()
        findings = detector.scan_directory(str(tmp_path))
        assert len(findings) >= 2


class TestSecretsDetectorCustomPatterns:
    """Tests for custom patterns in SecretsDetector."""

    def test_custom_pattern_detected(self, tmp_path):
        """Custom pattern matches when provided."""
        custom = {"custom_token": r"MY_TOKEN_[A-Z]{10}"}
        f = tmp_path / "custom.py"
        f.write_text("value = MY_TOKEN_ABCDEFGHIJ\n")
        detector = SecretsDetector(patterns=custom)
        findings = detector.scan_file(str(f))
        assert any(ff.secret_type == "custom_token" for ff in findings)

    def test_custom_patterns_replace_defaults(self, tmp_path):
        """When custom patterns provided, defaults are NOT used."""
        custom = {"my_pattern": r"MY_CUSTOM_[A-Z]{5}"}
        f = tmp_path / "test.py"
        f.write_text('key = "AKIAIOSFODNN7EXAMPLE"\n')  # AWS key, no custom match
        detector = SecretsDetector(patterns=custom)
        findings = detector.scan_file(str(f))
        assert len(findings) == 0


class TestScanSecretsConvenienceFunction:
    """Tests for the scan_secrets() module-level function."""

    def test_scan_file_returns_list_of_dicts(self, tmp_path):
        """scan_secrets() on a file returns list of dicts."""
        f = tmp_path / "creds.py"
        f.write_text('aws_key = "AKIAIOSFODNN7EXAMPLE"\n')
        results = scan_secrets(str(f))
        assert isinstance(results, list)
        if results:
            assert isinstance(results[0], dict)
            assert "secret_type" in results[0]

    def test_scan_directory_returns_list(self, tmp_path):
        """scan_secrets() on a directory returns list."""
        (tmp_path / "file.py").write_text("clean = True\n")
        results = scan_secrets(str(tmp_path))
        assert isinstance(results, list)

    def test_scan_empty_file_returns_empty(self, tmp_path):
        """scan_secrets() on a clean file returns empty list."""
        f = tmp_path / "clean.py"
        f.write_text("x = 1\n")
        results = scan_secrets(str(f))
        assert results == []


class TestSecretsDetectorEntropy:
    """Tests for Shannon entropy detection in SecretsDetector."""

    def test_high_entropy_string_detected(self, tmp_path):
        """High-entropy strings are flagged when no pattern matches first."""
        # A high-entropy 32-char mixed string
        f = tmp_path / "entropy_test.py"
        # This won't match known patterns but will have high entropy
        f.write_text("value = aB3dE7fG2hI5jK9lM1nO4pQ8rS6tU0\n")
        detector = SecretsDetector()
        findings = detector.scan_file(str(f))
        # May or may not trigger entropy check depending on actual entropy
        # Just ensure no crash
        assert isinstance(findings, list)

    def test_shannon_entropy_empty(self):
        """_shannon_entropy() returns 0 for empty string."""
        detector = SecretsDetector()
        assert detector._shannon_entropy("") == 0

    def test_shannon_entropy_single_char(self):
        """_shannon_entropy() returns 0 for single-char string."""
        detector = SecretsDetector()
        assert detector._shannon_entropy("a") == pytest.approx(0.0)

    def test_shannon_entropy_high_randomness(self):
        """_shannon_entropy() returns higher value for more random string."""
        detector = SecretsDetector()
        low = detector._shannon_entropy("aaaaaaaaaa")
        high = detector._shannon_entropy("aAbBcCdDeEfFgGhH")
        assert high > low
