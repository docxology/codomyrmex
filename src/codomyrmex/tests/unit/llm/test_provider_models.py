"""Unit tests for codomyrmex.llm.providers.models.

Covers: ProviderType (enum), Message (dataclass + to_dict branches),
CompletionResponse (dataclass + total_tokens property),
ProviderConfig (dataclass defaults and custom values).

Zero external dependencies — no network, no API keys, no mocks.
"""

import pytest

from codomyrmex.llm.providers.models import (
    CompletionResponse,
    Message,
    ProviderConfig,
    ProviderType,
)

# ─────────────────────────────────────────────────────────────────────────────
#  ProviderType enum
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProviderTypeEnum:
    """Every ProviderType member has the expected string value."""

    def test_openai_value(self):
        assert ProviderType.OPENAI.value == "openai"

    def test_anthropic_value(self):
        assert ProviderType.ANTHROPIC.value == "anthropic"

    def test_openrouter_value(self):
        assert ProviderType.OPENROUTER.value == "openrouter"

    def test_google_value(self):
        assert ProviderType.GOOGLE.value == "google"

    def test_ollama_value(self):
        assert ProviderType.OLLAMA.value == "ollama"

    def test_azure_openai_value(self):
        assert ProviderType.AZURE_OPENAI.value == "azure_openai"

    def test_cohere_value(self):
        assert ProviderType.COHERE.value == "cohere"

    def test_mistral_value(self):
        assert ProviderType.MISTRAL.value == "mistral"

    def test_all_members_count(self):
        """Exactly 8 members defined in the enum."""
        assert len(ProviderType) == 8

    def test_lookup_by_value(self):
        assert ProviderType("anthropic") is ProviderType.ANTHROPIC

    def test_members_are_unique(self):
        values = [m.value for m in ProviderType]
        assert len(values) == len(set(values))

    def test_is_enum_member(self):
        from enum import Enum
        assert isinstance(ProviderType.OPENAI, ProviderType)
        assert isinstance(ProviderType.OPENAI, Enum)

    @pytest.mark.parametrize(
        "member,expected",
        [
            (ProviderType.OPENAI, "openai"),
            (ProviderType.ANTHROPIC, "anthropic"),
            (ProviderType.OPENROUTER, "openrouter"),
            (ProviderType.GOOGLE, "google"),
            (ProviderType.OLLAMA, "ollama"),
            (ProviderType.AZURE_OPENAI, "azure_openai"),
            (ProviderType.COHERE, "cohere"),
            (ProviderType.MISTRAL, "mistral"),
        ],
    )
    def test_all_member_values_parametrized(self, member, expected):
        assert member.value == expected


# ─────────────────────────────────────────────────────────────────────────────
#  Message dataclass
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMessageDataclass:
    """Message construction and field storage."""

    def test_required_fields_stored(self):
        m = Message(role="user", content="Hello")
        assert m.role == "user"
        assert m.content == "Hello"

    def test_optional_name_defaults_to_none(self):
        m = Message(role="user", content="Hi")
        assert m.name is None

    def test_optional_tool_calls_defaults_to_none(self):
        m = Message(role="user", content="Hi")
        assert m.tool_calls is None

    def test_optional_tool_call_id_defaults_to_none(self):
        m = Message(role="user", content="Hi")
        assert m.tool_call_id is None

    def test_name_stored_when_provided(self):
        m = Message(role="tool", content="result", name="my_tool")
        assert m.name == "my_tool"

    def test_tool_calls_stored_when_provided(self):
        calls = [{"id": "call_1", "function": {"name": "foo"}}]
        m = Message(role="assistant", content="", tool_calls=calls)
        assert m.tool_calls == calls

    def test_tool_call_id_stored_when_provided(self):
        m = Message(role="tool", content="output", tool_call_id="call_abc")
        assert m.tool_call_id == "call_abc"

    @pytest.mark.parametrize("role", ["system", "user", "assistant", "tool"])
    def test_standard_roles_accepted(self, role):
        m = Message(role=role, content="text")
        assert m.role == role


# ─────────────────────────────────────────────────────────────────────────────
#  Message.to_dict()
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMessageToDict:
    """to_dict() covers all four conditional branches."""

    def test_minimal_message_has_role_and_content(self):
        m = Message(role="user", content="Hello")
        d = m.to_dict()
        assert d == {"role": "user", "content": "Hello"}

    def test_minimal_message_omits_none_fields(self):
        m = Message(role="user", content="Hello")
        d = m.to_dict()
        assert "name" not in d
        assert "tool_calls" not in d
        assert "tool_call_id" not in d

    def test_name_included_when_set(self):
        m = Message(role="tool", content="ok", name="calculator")
        d = m.to_dict()
        assert d["name"] == "calculator"

    def test_name_excluded_when_none(self):
        m = Message(role="user", content="Hi", name=None)
        d = m.to_dict()
        assert "name" not in d

    def test_tool_calls_included_when_set(self):
        calls = [{"id": "c1"}]
        m = Message(role="assistant", content="", tool_calls=calls)
        d = m.to_dict()
        assert d["tool_calls"] == calls

    def test_tool_calls_excluded_when_none(self):
        m = Message(role="assistant", content="hi", tool_calls=None)
        d = m.to_dict()
        assert "tool_calls" not in d

    def test_tool_call_id_included_when_set(self):
        m = Message(role="tool", content="result", tool_call_id="call_99")
        d = m.to_dict()
        assert d["tool_call_id"] == "call_99"

    def test_tool_call_id_excluded_when_none(self):
        m = Message(role="tool", content="result", tool_call_id=None)
        d = m.to_dict()
        assert "tool_call_id" not in d

    def test_all_fields_present_when_all_set(self):
        calls = [{"id": "c2"}]
        m = Message(
            role="assistant",
            content="done",
            name="agent",
            tool_calls=calls,
            tool_call_id="call_1",
        )
        d = m.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "done"
        assert d["name"] == "agent"
        assert d["tool_calls"] == calls
        assert d["tool_call_id"] == "call_1"

    def test_returns_dict_type(self):
        m = Message(role="user", content="x")
        assert type(m.to_dict()) is dict

    def test_content_preserved_verbatim(self):
        text = "line1\nline2\ttabbed  spaces"
        m = Message(role="user", content=text)
        assert m.to_dict()["content"] == text

    def test_empty_tool_calls_list_is_included(self):
        """An empty list is still truthy-false but not None — included per source."""
        m = Message(role="assistant", content="", tool_calls=[])
        d = m.to_dict()
        # Source: `if self.tool_calls:` — empty list is falsy, so it's excluded
        assert "tool_calls" not in d


# ─────────────────────────────────────────────────────────────────────────────
#  CompletionResponse dataclass
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCompletionResponseDataclass:
    """CompletionResponse construction, field storage, total_tokens property."""

    def test_required_fields_stored(self):
        resp = CompletionResponse(
            content="hello",
            model="gpt-4",
            provider=ProviderType.OPENAI,
        )
        assert resp.content == "hello"
        assert resp.model == "gpt-4"
        assert resp.provider is ProviderType.OPENAI

    def test_finish_reason_defaults_to_none(self):
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.ANTHROPIC
        )
        assert resp.finish_reason is None

    def test_usage_defaults_to_none(self):
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.ANTHROPIC
        )
        assert resp.usage is None

    def test_tool_calls_defaults_to_none(self):
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.ANTHROPIC
        )
        assert resp.tool_calls is None

    def test_raw_response_defaults_to_none(self):
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.ANTHROPIC
        )
        assert resp.raw_response is None

    def test_finish_reason_stored(self):
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.OPENAI, finish_reason="stop"
        )
        assert resp.finish_reason == "stop"

    def test_usage_stored(self):
        usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.OPENAI, usage=usage
        )
        assert resp.usage == usage

    def test_tool_calls_stored(self):
        calls = [{"id": "c1", "function": {"name": "search"}}]
        resp = CompletionResponse(
            content="", model="m", provider=ProviderType.OPENAI, tool_calls=calls
        )
        assert resp.tool_calls == calls

    def test_raw_response_stored(self):
        raw = {"id": "resp-1", "object": "chat.completion"}
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.OPENAI, raw_response=raw
        )
        assert resp.raw_response == raw

    @pytest.mark.parametrize("provider", list(ProviderType))
    def test_all_provider_types_accepted(self, provider):
        resp = CompletionResponse(content="x", model="m", provider=provider)
        assert resp.provider is provider


# ─────────────────────────────────────────────────────────────────────────────
#  CompletionResponse.total_tokens property
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestCompletionResponseTotalTokens:
    """total_tokens covers both the None-usage and populated-usage branches."""

    def test_total_tokens_returns_zero_when_usage_is_none(self):
        resp = CompletionResponse(
            content="x", model="m", provider=ProviderType.ANTHROPIC
        )
        assert resp.total_tokens == 0

    def test_total_tokens_returns_value_from_usage(self):
        resp = CompletionResponse(
            content="x",
            model="m",
            provider=ProviderType.OPENAI,
            usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
        )
        assert resp.total_tokens == 15

    def test_total_tokens_returns_zero_when_key_missing_from_usage(self):
        """If usage dict exists but lacks 'total_tokens', returns 0 (dict.get default)."""
        resp = CompletionResponse(
            content="x",
            model="m",
            provider=ProviderType.OPENAI,
            usage={"prompt_tokens": 5, "completion_tokens": 10},
        )
        assert resp.total_tokens == 0

    def test_total_tokens_with_zero_in_usage(self):
        resp = CompletionResponse(
            content="x",
            model="m",
            provider=ProviderType.OPENAI,
            usage={"total_tokens": 0},
        )
        assert resp.total_tokens == 0

    def test_total_tokens_large_value(self):
        resp = CompletionResponse(
            content="x",
            model="m",
            provider=ProviderType.OPENAI,
            usage={"total_tokens": 128_000},
        )
        assert resp.total_tokens == 128_000

    def test_total_tokens_is_int(self):
        resp = CompletionResponse(
            content="x",
            model="m",
            provider=ProviderType.OPENAI,
            usage={"total_tokens": 42},
        )
        assert isinstance(resp.total_tokens, int)


# ─────────────────────────────────────────────────────────────────────────────
#  ProviderConfig dataclass
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestProviderConfigDataclass:
    """ProviderConfig default values and custom overrides."""

    def test_all_defaults_are_none_or_typed(self):
        cfg = ProviderConfig()
        assert cfg.api_key is None
        assert cfg.base_url is None
        assert cfg.organization is None
        assert cfg.timeout == 60.0
        assert cfg.max_retries == 3
        assert cfg.default_model is None
        assert cfg.extra_headers == {}

    def test_api_key_stored(self):
        cfg = ProviderConfig(api_key="sk-test")
        assert cfg.api_key == "sk-test"

    def test_base_url_stored(self):
        cfg = ProviderConfig(base_url="https://api.openai.com/v1")
        assert cfg.base_url == "https://api.openai.com/v1"

    def test_organization_stored(self):
        cfg = ProviderConfig(organization="org-123")
        assert cfg.organization == "org-123"

    def test_custom_timeout(self):
        cfg = ProviderConfig(timeout=120.0)
        assert cfg.timeout == 120.0

    def test_custom_max_retries(self):
        cfg = ProviderConfig(max_retries=5)
        assert cfg.max_retries == 5

    def test_default_model_stored(self):
        cfg = ProviderConfig(default_model="claude-3-5-sonnet-20241022")
        assert cfg.default_model == "claude-3-5-sonnet-20241022"

    def test_extra_headers_stored(self):
        headers = {"X-Custom": "value", "Authorization": "Bearer tok"}
        cfg = ProviderConfig(extra_headers=headers)
        assert cfg.extra_headers["X-Custom"] == "value"

    def test_extra_headers_are_independent_across_instances(self):
        """Different instances must not share the same extra_headers dict."""
        cfg1 = ProviderConfig()
        cfg2 = ProviderConfig()
        cfg1.extra_headers["key"] = "val"
        assert "key" not in cfg2.extra_headers

    def test_all_fields_set_together(self):
        cfg = ProviderConfig(
            api_key="k",
            base_url="https://example.com",
            organization="org-x",
            timeout=30.0,
            max_retries=1,
            default_model="gpt-4",
            extra_headers={"H": "V"},
        )
        assert cfg.api_key == "k"
        assert cfg.base_url == "https://example.com"
        assert cfg.organization == "org-x"
        assert cfg.timeout == 30.0
        assert cfg.max_retries == 1
        assert cfg.default_model == "gpt-4"
        assert cfg.extra_headers == {"H": "V"}

    def test_timeout_default_is_float(self):
        cfg = ProviderConfig()
        assert isinstance(cfg.timeout, float)

    def test_max_retries_default_is_int(self):
        cfg = ProviderConfig()
        assert isinstance(cfg.max_retries, int)
