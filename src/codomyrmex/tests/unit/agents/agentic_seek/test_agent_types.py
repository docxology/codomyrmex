"""Tests for codomyrmex.agents.agentic_seek.agent_types.

Zero-mock tests covering enum membership, dataclass construction,
serialization, and language resolution.
"""

import time

import pytest

from codomyrmex.agents.agentic_seek.agent_types import (
    SUPPORTED_LANGUAGES,
    AgenticSeekAgentType,
    AgenticSeekConfig,
    AgenticSeekExecutionResult,
    AgenticSeekMemoryEntry,
    AgenticSeekProvider,
    AgenticSeekTaskStatus,
    AgenticSeekTaskStep,
    resolve_language,
)


# ===================================================================
# AgenticSeekAgentType
# ===================================================================

class TestAgenticSeekAgentType:
    """Enum membership, values, and from_string resolution."""

    def test_has_five_members(self):
        assert len(AgenticSeekAgentType) == 5

    @pytest.mark.parametrize("member,value", [
        (AgenticSeekAgentType.CODER, "coder"),
        (AgenticSeekAgentType.BROWSER, "browser"),
        (AgenticSeekAgentType.PLANNER, "planner"),
        (AgenticSeekAgentType.FILE, "file"),
        (AgenticSeekAgentType.CASUAL, "casual"),
    ])
    def test_member_values(self, member, value):
        assert member.value == value

    def test_from_string_lowercase(self):
        assert AgenticSeekAgentType.from_string("coder") is AgenticSeekAgentType.CODER

    def test_from_string_uppercase(self):
        assert AgenticSeekAgentType.from_string("BROWSER") is AgenticSeekAgentType.BROWSER

    def test_from_string_mixed_case(self):
        assert AgenticSeekAgentType.from_string("Planner") is AgenticSeekAgentType.PLANNER

    def test_from_string_with_whitespace(self):
        assert AgenticSeekAgentType.from_string("  file  ") is AgenticSeekAgentType.FILE

    def test_from_string_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown agent type"):
            AgenticSeekAgentType.from_string("nonexistent")


# ===================================================================
# AgenticSeekProvider
# ===================================================================

class TestAgenticSeekProvider:
    def test_has_nine_members(self):
        assert len(AgenticSeekProvider) == 9

    def test_ollama_value(self):
        assert AgenticSeekProvider.OLLAMA.value == "ollama"

    def test_server_value(self):
        assert AgenticSeekProvider.SERVER.value == "server"


# ===================================================================
# AgenticSeekConfig
# ===================================================================

class TestAgenticSeekConfig:
    def test_default_construction(self):
        cfg = AgenticSeekConfig()
        assert cfg.is_local is True
        assert cfg.provider_name == "ollama"
        assert cfg.provider_model == "deepseek-r1:14b"
        assert cfg.agent_name == "Friday"
        assert cfg.languages == ["en"]
        assert cfg.headless_browser is True

    def test_custom_construction(self):
        cfg = AgenticSeekConfig(
            provider_name="openai",
            provider_model="gpt-4",
            is_local=False,
            languages=["en", "zh"],
        )
        assert cfg.provider_name == "openai"
        assert cfg.is_local is False
        assert cfg.languages == ["en", "zh"]

    def test_frozen(self):
        cfg = AgenticSeekConfig()
        with pytest.raises(AttributeError):
            cfg.provider_name = "lm-studio"  # type: ignore[misc]

    def test_to_ini_dict_has_sections(self):
        cfg = AgenticSeekConfig()
        ini = cfg.to_ini_dict()
        assert "MAIN" in ini
        assert "BROWSER" in ini
        assert ini["MAIN"]["provider_name"] == "ollama"
        assert ini["BROWSER"]["headless_browser"] == "True"

    def test_to_ini_dict_languages_joined(self):
        cfg = AgenticSeekConfig(languages=["en", "zh", "fr"])
        ini = cfg.to_ini_dict()
        assert ini["MAIN"]["languages"] == "en zh fr"


# ===================================================================
# AgenticSeekMemoryEntry
# ===================================================================

class TestAgenticSeekMemoryEntry:
    def test_construction(self):
        entry = AgenticSeekMemoryEntry(role="user", content="Hello")
        assert entry.role == "user"
        assert entry.content == "Hello"
        assert isinstance(entry.timestamp, float)

    def test_to_dict(self):
        entry = AgenticSeekMemoryEntry(role="assistant", content="Hi")
        d = entry.to_dict()
        assert d == {"role": "assistant", "content": "Hi"}

    def test_timestamp_default(self):
        before = time.time()
        entry = AgenticSeekMemoryEntry(role="system", content="init")
        after = time.time()
        assert before <= entry.timestamp <= after


# ===================================================================
# AgenticSeekTaskStatus
# ===================================================================

class TestAgenticSeekTaskStatus:
    def test_has_four_members(self):
        assert len(AgenticSeekTaskStatus) == 4

    @pytest.mark.parametrize("member,value", [
        (AgenticSeekTaskStatus.PENDING, "pending"),
        (AgenticSeekTaskStatus.RUNNING, "running"),
        (AgenticSeekTaskStatus.COMPLETED, "completed"),
        (AgenticSeekTaskStatus.FAILED, "failed"),
    ])
    def test_member_values(self, member, value):
        assert member.value == value


# ===================================================================
# AgenticSeekTaskStep
# ===================================================================

class TestAgenticSeekTaskStep:
    def test_construction(self):
        step = AgenticSeekTaskStep(
            agent_type=AgenticSeekAgentType.CODER,
            task_id=1,
            description="Write code",
        )
        assert step.agent_type is AgenticSeekAgentType.CODER
        assert step.task_id == 1
        assert step.dependencies == []
        assert step.status is AgenticSeekTaskStatus.PENDING
        assert step.result is None

    def test_with_dependencies(self):
        step = AgenticSeekTaskStep(
            agent_type=AgenticSeekAgentType.BROWSER,
            task_id=2,
            description="Search",
            dependencies=[1],
        )
        assert step.dependencies == [1]


# ===================================================================
# AgenticSeekExecutionResult
# ===================================================================

class TestAgenticSeekExecutionResult:
    def test_success_str(self):
        r = AgenticSeekExecutionResult(
            code="print(1)", feedback="1", success=True,
            tool_type="python", execution_time=0.5,
        )
        s = str(r)
        assert "✓" in s
        assert "python" in s

    def test_failure_str(self):
        r = AgenticSeekExecutionResult(
            code="x", feedback="error", success=False,
            tool_type="bash", execution_time=0.1,
        )
        s = str(r)
        assert "✗" in s


# ===================================================================
# resolve_language
# ===================================================================

class TestResolveLanguage:
    def test_canonical_name(self):
        assert resolve_language("python") == "python"

    def test_alias_py(self):
        assert resolve_language("py") == "python"

    def test_alias_golang(self):
        assert resolve_language("golang") == "go"

    def test_alias_sh(self):
        assert resolve_language("sh") == "bash"

    def test_alias_shell(self):
        assert resolve_language("shell") == "bash"

    def test_case_insensitive(self):
        assert resolve_language("PYTHON") == "python"

    def test_unknown_returns_none(self):
        assert resolve_language("rust") is None

    def test_empty_returns_none(self):
        assert resolve_language("") is None


# ===================================================================
# SUPPORTED_LANGUAGES
# ===================================================================

class TestSupportedLanguages:
    def test_has_five_languages(self):
        assert len(SUPPORTED_LANGUAGES) == 5

    @pytest.mark.parametrize("lang", ["python", "c", "go", "java", "bash"])
    def test_has_required_keys(self, lang):
        meta = SUPPORTED_LANGUAGES[lang]
        assert "extension" in meta
        assert "runner" in meta
        assert "aliases" in meta

    def test_python_extension(self):
        assert SUPPORTED_LANGUAGES["python"]["extension"] == ".py"

    def test_bash_extension(self):
        assert SUPPORTED_LANGUAGES["bash"]["extension"] == ".sh"
