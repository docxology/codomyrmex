"""Tests for agents.hermes._provider_router — ProviderRouter, ContextCompressor, UserModel, MCPBridgeManager.

Zero-Mock: All tests use real objects with filesystem I/O (tmp_path).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from codomyrmex.agents.hermes._provider_router import (
    ContextCompressor,
    MCPBridgeManager,
    ProviderRouter,
    UserModel,
)

if TYPE_CHECKING:
    from pathlib import Path

# ── ProviderRouter ────────────────────────────────────────────────────


class TestProviderRouter:
    """Verify provider routing logic."""

    def test_supported_providers(self) -> None:
        assert "openrouter" in ProviderRouter.SUPPORTED_PROVIDERS
        assert "ollama" in ProviderRouter.SUPPORTED_PROVIDERS
        assert "anthropic" in ProviderRouter.SUPPORTED_PROVIDERS

    def test_resolve_provider_with_ollama_available(self) -> None:
        """resolve_provider() should return *something* — either the primary or a fallback."""
        router = ProviderRouter(
            primary_provider="openrouter", fallback_provider="ollama"
        )
        # Even without an API key, it should either resolve or raise
        try:
            provider = router.resolve_provider()
            assert provider in ProviderRouter.SUPPORTED_PROVIDERS
        except RuntimeError:
            pass  # No credentials at all is acceptable on some machines

    def test_has_credentials_for_ollama_if_available(self) -> None:
        """If ollama binary is on PATH, it should register 'local' credentials."""
        import shutil

        router = ProviderRouter()
        if shutil.which("ollama"):
            assert router.has_credentials("ollama") is True
        else:
            assert router.has_credentials("ollama") is False

    def test_get_provider_status_returns_all_providers(self) -> None:
        router = ProviderRouter()
        status = router.get_provider_status()
        assert isinstance(status, dict)
        for provider in ProviderRouter.SUPPORTED_PROVIDERS:
            assert provider in status
            assert "has_credentials" in status[provider]
            assert "is_primary" in status[provider]
            assert "is_fallback" in status[provider]

    def test_custom_primary_marked_correctly(self) -> None:
        router = ProviderRouter(
            primary_provider="anthropic", fallback_provider="ollama"
        )
        status = router.get_provider_status()
        assert status["anthropic"]["is_primary"] is True
        assert status["ollama"]["is_fallback"] is True

    def test_env_path_loading_from_nonexistent(self, tmp_path: Path) -> None:
        """Loading from a nonexistent .env file should not crash."""
        router = ProviderRouter(env_path=str(tmp_path / "nonexistent.env"))
        # Should still resolve the provider status dict
        assert isinstance(router.get_provider_status(), dict)

    def test_env_path_loading_from_real_file(self, tmp_path: Path) -> None:
        """Loading from a real .env file should parse credentials."""
        env_file = tmp_path / ".env"
        env_file.write_text("OPENROUTER_API_KEY=sk-test-123\n")
        router = ProviderRouter(env_path=str(env_file))
        assert router.has_credentials("openrouter") is True


# ── ContextCompressor ─────────────────────────────────────────────────


class TestContextCompressor:
    """Verify context compression logic."""

    def test_estimate_tokens_empty(self) -> None:
        c = ContextCompressor()
        assert c.estimate_tokens([]) == 0

    def test_estimate_tokens_simple(self) -> None:
        c = ContextCompressor()
        msgs = [{"role": "user", "content": "a" * 400}]
        assert c.estimate_tokens(msgs) == 100  # 400 / 4

    def test_needs_compression_below_threshold(self) -> None:
        c = ContextCompressor(max_tokens=1000)
        msgs = [{"role": "user", "content": "short message"}]
        assert c.needs_compression(msgs) is False

    def test_needs_compression_above_threshold(self) -> None:
        c = ContextCompressor(max_tokens=10)
        msgs = [{"role": "user", "content": "a" * 1000}]
        assert c.needs_compression(msgs) is True

    def test_compress_returns_shorter_list(self) -> None:
        c = ContextCompressor(max_tokens=10, compression_ratio=0.5)
        msgs = [
            {"role": "user", "content": f"Message {i} " + "x" * 100} for i in range(20)
        ]
        compressed = c.compress(msgs)
        assert len(compressed) < len(msgs)

    def test_compress_preserves_head_and_tail(self) -> None:
        c = ContextCompressor(max_tokens=10, compression_ratio=0.5)
        msgs = [
            {"role": "user", "content": f"Message {i} " + "x" * 100} for i in range(20)
        ]
        compressed = c.compress(msgs)
        # Should have head + summary + tail (at least 3 entries)
        assert len(compressed) >= 3
        # A system summary message should exist somewhere in the middle
        system_msgs = [m for m in compressed if m["role"] == "system"]
        assert len(system_msgs) >= 1

    def test_compress_skips_when_not_needed(self) -> None:
        c = ContextCompressor(max_tokens=100_000)
        msgs = [{"role": "user", "content": "hello"}]
        result = c.compress(msgs)
        assert result == msgs

    def test_deduplicate_consecutive(self) -> None:
        msgs = [
            {"role": "user", "content": "same"},
            {"role": "user", "content": "same"},
            {"role": "user", "content": "different"},
        ]
        result = ContextCompressor._deduplicate(msgs)
        assert len(result) == 2


# ── UserModel ─────────────────────────────────────────────────────────


class TestUserModel:
    """Verify user model persistence."""

    def test_default_profile(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "user_model"))
        assert isinstance(model.profile, dict)
        assert "preferences" in model.profile
        assert "observations" in model.profile

    def test_set_and_get_preference(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        model.set_preference("language", "python")
        assert model.profile["preferences"]["language"] == "python"

    def test_add_observation(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        model.add_observation("Prefers functional style")
        assert "Prefers functional style" in model.profile["observations"]

    def test_record_session(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        model.record_session("sess1", "Refactored auth module")
        history = model.profile["session_history"]
        assert len(history) == 1
        assert history[0]["session_id"] == "sess1"

    def test_context_prompt_with_data(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        model.set_preference("style", "concise")
        model.add_observation("Uses type hints")
        prompt = model.get_context_prompt()
        assert "style=concise" in prompt
        assert "Uses type hints" in prompt

    def test_context_prompt_empty(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        assert model.get_context_prompt() == ""

    def test_persistence_across_instances(self, tmp_path: Path) -> None:
        storage = str(tmp_path / "um")
        m1 = UserModel(storage_dir=storage)
        m1.set_preference("editor", "vim")

        m2 = UserModel(storage_dir=storage)
        assert m2.profile["preferences"]["editor"] == "vim"

    def test_observation_cap_at_100(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        for i in range(110):
            model.add_observation(f"obs-{i}")
        assert len(model.profile["observations"]) == 100

    def test_session_history_cap_at_50(self, tmp_path: Path) -> None:
        model = UserModel(storage_dir=str(tmp_path / "um"))
        for i in range(60):
            model.record_session(f"s{i}", f"summary-{i}")
        assert len(model.profile["session_history"]) == 50


# ── MCPBridgeManager ──────────────────────────────────────────────────


class TestMCPBridgeManager:
    """Verify MCP bridge server management."""

    def test_register_and_list(self, tmp_path: Path) -> None:
        config = tmp_path / "mcp_servers.json"
        mgr = MCPBridgeManager(config_path=str(config))
        mgr.register_server(
            "test_server",
            command="python",
            args=["-m", "my_server"],
            transport="stdio",
            description="Test MCP server",
        )
        servers = mgr.list_servers()
        assert len(servers) == 1
        assert servers[0]["name"] == "test_server"
        assert servers[0]["command"] == "python"

    def test_unregister(self, tmp_path: Path) -> None:
        config = tmp_path / "mcp_servers.json"
        mgr = MCPBridgeManager(config_path=str(config))
        mgr.register_server("s1", command="echo")
        assert mgr.unregister_server("s1") is True
        assert mgr.unregister_server("s1") is False
        assert mgr.list_servers() == []

    def test_persistence(self, tmp_path: Path) -> None:
        config = tmp_path / "mcp_servers.json"
        mgr1 = MCPBridgeManager(config_path=str(config))
        mgr1.register_server("persistent", command="cat")

        mgr2 = MCPBridgeManager(config_path=str(config))
        assert len(mgr2.list_servers()) == 1
        assert mgr2.servers["persistent"]["command"] == "cat"

    def test_reload(self, tmp_path: Path) -> None:
        config = tmp_path / "mcp_servers.json"
        mgr = MCPBridgeManager(config_path=str(config))
        result = mgr.reload()
        assert isinstance(result, dict)
        assert "success" in result
        assert "servers_loaded" in result

    def test_nonexistent_config(self, tmp_path: Path) -> None:
        config = tmp_path / "nonexistent" / "mcp_servers.json"
        mgr = MCPBridgeManager(config_path=str(config))
        assert mgr.list_servers() == []

    def test_servers_returns_copy(self, tmp_path: Path) -> None:
        """Mutating the servers dict should not affect internal state."""
        config = tmp_path / "mcp_servers.json"
        mgr = MCPBridgeManager(config_path=str(config))
        mgr.register_server("s1", command="echo")
        servers = mgr.servers
        servers["s1"]["command"] = "mutated"
        assert mgr.servers["s1"]["command"] == "echo"

    def test_save_config_creates_parent_dirs(self, tmp_path: Path) -> None:
        """save_config should create intermediate directories."""
        config = tmp_path / "deep" / "nested" / "mcp_servers.json"
        mgr = MCPBridgeManager(config_path=str(config))
        mgr.register_server("s1", command="echo")
        assert config.exists()
        data = json.loads(config.read_text())
        assert "s1" in data


# ── ProviderRouter.get_rotation_models ──────────────────────────────


class TestProviderRouterRotation:
    """Verify rotation model reading logic."""

    def test_get_rotation_models_nonexistent(self, tmp_path: Path) -> None:
        """Should return empty list when no rotation config exists."""
        router = ProviderRouter(
            env_path=str(tmp_path / "nonexistent.env"),
        )
        # Point to a nonexistent rotation file
        router._rotation_path = str(tmp_path / "no_rotation.json")
        assert router.get_rotation_models() == []

    def test_get_rotation_models_returns_sorted(self, tmp_path: Path) -> None:
        """Models should be sorted by priority."""
        rotation_file = tmp_path / "rotation.json"
        rotation_file.write_text(json.dumps({
            "rotation_models": [
                {"model": "low-pri", "priority": 10},
                {"model": "high-pri", "priority": 1},
                {"model": "mid-pri", "priority": 5},
            ]
        }))
        router = ProviderRouter(env_path=str(tmp_path / ".env"))
        router._rotation_path = str(rotation_file)
        models = router.get_rotation_models()
        assert len(models) == 3
        assert models[0]["model"] == "high-pri"
        assert models[1]["model"] == "mid-pri"
        assert models[2]["model"] == "low-pri"

    def test_get_rotation_models_malformed_json(self, tmp_path: Path) -> None:
        """Should return empty list on invalid JSON, not crash."""
        rotation_file = tmp_path / "bad_rotation.json"
        rotation_file.write_text("{not valid json")
        router = ProviderRouter(env_path=str(tmp_path / ".env"))
        router._rotation_path = str(rotation_file)
        assert router.get_rotation_models() == []

    def test_get_rotation_models_missing_key(self, tmp_path: Path) -> None:
        """Should return empty list when rotation_models key is absent."""
        rotation_file = tmp_path / "rotation.json"
        rotation_file.write_text(json.dumps({"other_key": []}))
        router = ProviderRouter(env_path=str(tmp_path / ".env"))
        router._rotation_path = str(rotation_file)
        assert router.get_rotation_models() == []

    def test_get_rotation_models_missing_priority_defaults(self, tmp_path: Path) -> None:
        """Models without priority should sort to end (default 99)."""
        rotation_file = tmp_path / "rotation.json"
        rotation_file.write_text(json.dumps({
            "rotation_models": [
                {"model": "no-priority"},
                {"model": "has-priority", "priority": 1},
            ]
        }))
        router = ProviderRouter(env_path=str(tmp_path / ".env"))
        router._rotation_path = str(rotation_file)
        models = router.get_rotation_models()
        assert models[0]["model"] == "has-priority"
        assert models[1]["model"] == "no-priority"


# ── ContextCompressor edge cases ────────────────────────────────────


class TestContextCompressorEdgeCases:
    """Verify edge cases in context compression."""

    def test_deduplicate_empty(self) -> None:
        """Empty list should return empty list."""
        assert ContextCompressor._deduplicate([]) == []

    def test_deduplicate_single_message(self) -> None:
        """Single message should pass through unchanged."""
        msg = [{"role": "user", "content": "hello"}]
        assert ContextCompressor._deduplicate(msg) == msg

    def test_deduplicate_all_identical(self) -> None:
        """All identical consecutive messages should reduce to one."""
        msgs = [{"role": "user", "content": "same"}] * 5
        result = ContextCompressor._deduplicate(msgs)
        assert len(result) == 1

    def test_estimate_tokens_missing_content_key(self) -> None:
        """Messages without 'content' key should not crash."""
        c = ContextCompressor()
        msgs = [{"role": "system"}]
        assert c.estimate_tokens(msgs) == 0

    def test_compress_no_content_key(self) -> None:
        """Compressing messages without content key should not crash."""
        c = ContextCompressor(max_tokens=10)
        msgs = [{"role": "system"}] * 30
        result = c.compress(msgs)
        assert isinstance(result, list)

    def test_compress_truncates_long_messages(self) -> None:
        """Individual messages should be truncated if too long."""
        c = ContextCompressor(max_tokens=100, compression_ratio=0.5)
        msgs = [{"role": "user", "content": "x" * 10000} for _ in range(10)]
        result = c.compress(msgs)
        # All remaining messages should be shorter
        for msg in result:
            if msg.get("role") != "system":
                assert "[...truncated]" in msg.get("content", "") or len(msg.get("content", "")) < 10000
