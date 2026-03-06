"""Zero-mock tests for coding.execution core functions.

Covers: validate_timeout, validate_language, validate_session_id,
SUPPORTED_LANGUAGES structure, execute_code non-Docker paths.

No mocks. No MagicMock. No monkeypatch.
"""

from __future__ import annotations

import pytest

from codomyrmex.coding.execution.executor import (
    DEFAULT_TIMEOUT,
    MAX_TIMEOUT,
    MIN_TIMEOUT,
    validate_timeout,
)
from codomyrmex.coding.execution.language_support import (
    SUPPORTED_LANGUAGES,
    validate_language,
)
from codomyrmex.coding.execution.session_manager import validate_session_id


@pytest.mark.unit
class TestValidateTimeout:
    """Tests for validate_timeout boundary conditions."""

    def test_none_returns_default_timeout(self):
        """None input yields the DEFAULT_TIMEOUT constant (30s)."""
        result = validate_timeout(None)
        assert result == DEFAULT_TIMEOUT
        assert result == 30

    def test_zero_clamped_to_min_timeout(self):
        """Zero is below minimum; should be clamped to MIN_TIMEOUT."""
        result = validate_timeout(0)
        assert result == MIN_TIMEOUT
        assert result == 1

    def test_negative_clamped_to_min_timeout(self):
        """Negative values are clamped to MIN_TIMEOUT."""
        result = validate_timeout(-50)
        assert result == MIN_TIMEOUT

    def test_over_max_clamped_to_max_timeout(self):
        """Values exceeding MAX_TIMEOUT are clamped to MAX_TIMEOUT."""
        result = validate_timeout(9999)
        assert result == MAX_TIMEOUT
        assert result == 300

    def test_exactly_min_timeout_passes_through(self):
        """MIN_TIMEOUT itself is returned unchanged."""
        result = validate_timeout(MIN_TIMEOUT)
        assert result == MIN_TIMEOUT

    def test_exactly_max_timeout_passes_through(self):
        """MAX_TIMEOUT itself is returned unchanged."""
        result = validate_timeout(MAX_TIMEOUT)
        assert result == MAX_TIMEOUT

    def test_mid_range_value_unchanged(self):
        """Mid-range values (1 <= x <= 300) are returned unchanged."""
        result = validate_timeout(60)
        assert result == 60

    def test_boundary_just_above_zero(self):
        """Value of 1 (exact minimum) is returned as-is."""
        result = validate_timeout(1)
        assert result == 1

    def test_boundary_just_below_max(self):
        """Value of 299 is below max, returned as-is."""
        result = validate_timeout(299)
        assert result == 299

    def test_value_301_clamped(self):
        """Value 301 (one above max) is clamped to MAX_TIMEOUT."""
        result = validate_timeout(301)
        assert result == MAX_TIMEOUT


@pytest.mark.unit
class TestValidateLanguage:
    """Tests for validate_language with all supported and unsupported values."""

    def test_python_supported(self):
        assert validate_language("python") is True

    def test_javascript_supported(self):
        assert validate_language("javascript") is True

    def test_java_supported(self):
        assert validate_language("java") is True

    def test_cpp_supported(self):
        assert validate_language("cpp") is True

    def test_c_supported(self):
        assert validate_language("c") is True

    def test_go_supported(self):
        assert validate_language("go") is True

    def test_rust_supported(self):
        assert validate_language("rust") is True

    def test_bash_supported(self):
        assert validate_language("bash") is True

    def test_cobol_not_supported(self):
        assert validate_language("cobol") is False

    def test_empty_string_not_supported(self):
        assert validate_language("") is False

    def test_uppercase_python_not_supported(self):
        """Language names are case-sensitive."""
        assert validate_language("Python") is False

    def test_uppercase_javascript_not_supported(self):
        assert validate_language("JavaScript") is False

    def test_sql_not_supported(self):
        assert validate_language("sql") is False

    def test_ruby_not_supported(self):
        assert validate_language("ruby") is False

    def test_php_not_supported(self):
        assert validate_language("php") is False

    def test_r_not_supported(self):
        assert validate_language("r") is False


@pytest.mark.unit
class TestSupportedLanguagesStructure:
    """Tests for SUPPORTED_LANGUAGES dictionary contents."""

    def test_all_8_languages_present(self):
        """SUPPORTED_LANGUAGES contains exactly the 8 documented languages."""
        expected = {"python", "javascript", "java", "cpp", "c", "go", "rust", "bash"}
        assert expected == set(SUPPORTED_LANGUAGES.keys())

    def test_each_language_has_image_key(self):
        """Every language config has a Docker image specified."""
        for lang, config in SUPPORTED_LANGUAGES.items():
            assert "image" in config, f"Language {lang} missing 'image' key"
            assert isinstance(config["image"], str)
            assert config["image"], f"Language {lang} has empty image"

    def test_each_language_has_extension_key(self):
        """Every language config has a file extension."""
        for lang, config in SUPPORTED_LANGUAGES.items():
            assert "extension" in config, f"Language {lang} missing 'extension' key"
            assert isinstance(config["extension"], str)

    def test_each_language_has_command_key(self):
        """Every language config has an execution command (list)."""
        for lang, config in SUPPORTED_LANGUAGES.items():
            assert "command" in config, f"Language {lang} missing 'command' key"
            assert isinstance(config["command"], list)
            assert len(config["command"]) >= 1

    def test_each_language_has_timeout_factor(self):
        """Every language config has a positive timeout_factor."""
        for lang, config in SUPPORTED_LANGUAGES.items():
            assert "timeout_factor" in config, (
                f"Language {lang} missing 'timeout_factor'"
            )
            assert config["timeout_factor"] >= 1.0  # type: ignore

    def test_python_extension_is_py(self):
        assert SUPPORTED_LANGUAGES["python"]["extension"] == "py"

    def test_javascript_extension_is_js(self):
        assert SUPPORTED_LANGUAGES["javascript"]["extension"] == "js"

    def test_bash_extension_is_sh(self):
        assert SUPPORTED_LANGUAGES["bash"]["extension"] == "sh"

    def test_cpp_extension_is_cpp(self):
        assert SUPPORTED_LANGUAGES["cpp"]["extension"] == "cpp"

    def test_java_extension_is_java(self):
        assert SUPPORTED_LANGUAGES["java"]["extension"] == "java"

    def test_go_extension_is_go(self):
        assert SUPPORTED_LANGUAGES["go"]["extension"] == "go"

    def test_rust_extension_is_rs(self):
        assert SUPPORTED_LANGUAGES["rust"]["extension"] == "rs"

    def test_compiled_languages_have_higher_timeout_factor(self):
        """Compiled languages (java, cpp, c, rust) have higher timeout factors."""
        compiled = ["java", "cpp", "c", "rust"]
        interpreted = ["python", "javascript", "bash"]
        compiled_min = min(
            SUPPORTED_LANGUAGES[lang]["timeout_factor"] for lang in compiled
        )
        interpreted_max = max(
            SUPPORTED_LANGUAGES[lang]["timeout_factor"] for lang in interpreted
        )
        assert compiled_min >= interpreted_max  # type: ignore


@pytest.mark.unit
class TestValidateSessionId:
    """Tests for validate_session_id input validation."""

    def test_none_returns_none(self):
        """None input returns None."""
        assert validate_session_id(None) is None

    def test_valid_alphanumeric_session(self):
        """Pure alphanumeric session IDs are accepted."""
        result = validate_session_id("user123")
        assert result == "user123"

    def test_valid_session_with_underscores(self):
        """Session IDs with underscores are accepted."""
        result = validate_session_id("user_123_session")
        assert result == "user_123_session"

    def test_valid_session_with_hyphens(self):
        """Session IDs with hyphens are accepted."""
        result = validate_session_id("session-abc-def")
        assert result == "session-abc-def"

    def test_valid_mixed_session(self):
        """Mixed alphanumeric, underscore, hyphen IDs are accepted."""
        result = validate_session_id("user-123_session")
        assert result == "user-123_session"

    def test_special_chars_at_sign_returns_none(self):
        """Session IDs with @ are rejected."""
        assert validate_session_id("user@domain") is None

    def test_special_chars_bang_returns_none(self):
        """Session IDs with ! are rejected."""
        assert validate_session_id("user!123") is None

    def test_special_chars_space_returns_none(self):
        """Session IDs with spaces are rejected."""
        assert validate_session_id("user 123") is None

    def test_special_chars_slash_returns_none(self):
        """Session IDs with slashes are rejected."""
        assert validate_session_id("user/123") is None

    def test_special_chars_dot_returns_none(self):
        """Session IDs with dots are rejected."""
        assert validate_session_id("user.session") is None

    def test_too_long_64_chars_is_accepted(self):
        """Session ID of exactly 64 chars is at the boundary — accepted."""
        session_id = "a" * 64
        result = validate_session_id(session_id)
        assert result == session_id

    def test_too_long_65_chars_is_rejected(self):
        """Session ID of 65 chars exceeds limit — rejected."""
        session_id = "a" * 65
        result = validate_session_id(session_id)
        assert result is None

    def test_too_long_100_chars_is_rejected(self):
        """Session ID of 100 chars is rejected."""
        result = validate_session_id("a" * 100)
        assert result is None

    def test_single_char_session_accepted(self):
        """Single character session ID is valid."""
        result = validate_session_id("x")
        assert result == "x"

    def test_empty_string_is_accepted(self):
        """Empty string passes structural validation (no invalid chars, len 0 <= 64)."""
        result = validate_session_id("")
        assert result == ""


@pytest.mark.unit
class TestExecuteCodeNonDockerPaths:
    """Tests for execute_code validation paths that don't need Docker."""

    def test_unsupported_language_returns_setup_error(self):
        """execute_code with unsupported language returns setup_error without Docker."""
        from codomyrmex.coding.execution.executor import execute_code

        result = execute_code("cobol", "DISPLAY 'hello'.")
        assert result["status"] == "setup_error"
        assert result["exit_code"] == -1
        assert (
            "cobol" in result["error_message"].lower()
            or "not supported" in result["error_message"].lower()
        )

    def test_unsupported_language_has_empty_stdout(self):
        """Unsupported language produces empty stdout."""
        from codomyrmex.coding.execution.executor import execute_code

        result = execute_code("ruby", "puts 'hello'")
        assert result["stdout"] == ""

    def test_empty_code_returns_setup_error(self):
        """Empty code string returns setup_error without attempting execution."""
        from codomyrmex.coding.execution.executor import execute_code

        result = execute_code("python", "")
        assert result["status"] == "setup_error"
        assert result["exit_code"] == -1

    def test_none_code_returns_setup_error(self):
        """None code (passed as None) returns setup_error."""
        from codomyrmex.coding.execution.executor import execute_code

        result = execute_code("python", None)
        assert result["status"] == "setup_error"

    def test_result_has_all_required_keys(self):
        """Result dict always has the documented keys even on error."""
        from codomyrmex.coding.execution.executor import execute_code

        result = execute_code("unknownlang", "code")
        required_keys = {
            "stdout",
            "stderr",
            "exit_code",
            "execution_time",
            "status",
            "error_message",
        }
        assert required_keys.issubset(result.keys())
