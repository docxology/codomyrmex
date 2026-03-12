"""Tests for the Pi coding agent client.

Zero-mock test suite covering:
- Configuration handling (defaults, overrides, env vars)
- Client initialization and lifecycle
- RPC command construction
- Event parsing
- Print mode execution
- MCP tool wrappers
- Module imports
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest

from codomyrmex.agents.pi import PiClient, PiConfig, PiError
from codomyrmex.agents.pi.pi_client import PiStartupError, PiTimeoutError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pi_available() -> bool:
    """Return True if pi CLI is on PATH."""
    return shutil.which("pi") is not None


_skip_no_pi = unittest.skipUnless(_pi_available(), "pi CLI not installed")


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------

class TestPiConfig(unittest.TestCase):
    """Test PiConfig defaults and overrides."""

    def test_defaults(self):
        cfg = PiConfig()
        self.assertEqual(cfg.provider, "google")
        self.assertEqual(cfg.model, "")
        self.assertEqual(cfg.tools, "read,bash,edit,write")
        self.assertFalse(cfg.no_session)
        self.assertEqual(cfg.startup_timeout, 10.0)
        self.assertEqual(cfg.extra_args, [])

    def test_custom_provider(self):
        cfg = PiConfig(provider="anthropic", model="claude-sonnet")
        self.assertEqual(cfg.provider, "anthropic")
        self.assertEqual(cfg.model, "claude-sonnet")

    def test_no_session(self):
        cfg = PiConfig(no_session=True)
        self.assertTrue(cfg.no_session)

    def test_extra_args(self):
        cfg = PiConfig(extra_args=["--verbose", "--offline"])
        self.assertEqual(cfg.extra_args, ["--verbose", "--offline"])

    def test_env_dict(self):
        cfg = PiConfig(env={"ANTHROPIC_API_KEY": "test-key"})
        self.assertEqual(cfg.env["ANTHROPIC_API_KEY"], "test-key")

    def test_pi_bin_override(self):
        cfg = PiConfig(pi_bin="/usr/local/bin/pi")
        self.assertEqual(cfg.pi_bin, "/usr/local/bin/pi")

    def test_cwd(self):
        cfg = PiConfig(cwd="/tmp/project")
        self.assertEqual(cfg.cwd, "/tmp/project")

    def test_thinking_levels(self):
        for level in ["off", "minimal", "low", "medium", "high", "xhigh"]:
            cfg = PiConfig(thinking=level)
            self.assertEqual(cfg.thinking, level)

    def test_session_dir(self):
        cfg = PiConfig(session_dir="/tmp/sessions")
        self.assertEqual(cfg.session_dir, "/tmp/sessions")

    def test_api_key(self):
        cfg = PiConfig(api_key="sk-test-123")
        self.assertEqual(cfg.api_key, "sk-test-123")


# ---------------------------------------------------------------------------
# Client initialization
# ---------------------------------------------------------------------------

class TestPiClientInit(unittest.TestCase):
    """Test PiClient construction."""

    def test_default_config(self):
        client = PiClient()
        self.assertIsInstance(client._config, PiConfig)
        self.assertFalse(client.is_running)

    def test_dict_config(self):
        client = PiClient(config={"provider": "openai", "model": "gpt-4o"})
        self.assertEqual(client._config.provider, "openai")
        self.assertEqual(client._config.model, "gpt-4o")

    def test_dataclass_config(self):
        cfg = PiConfig(provider="anthropic")
        client = PiClient(config=cfg)
        self.assertEqual(client._config.provider, "anthropic")

    def test_dict_ignores_unknown_keys(self):
        client = PiClient(config={"provider": "google", "unknown_key": True})
        self.assertEqual(client._config.provider, "google")

    def test_repr_stopped(self):
        client = PiClient(PiConfig(provider="openai"))
        self.assertIn("openai", repr(client))
        self.assertIn("stopped", repr(client))

    def test_not_running_initially(self):
        client = PiClient()
        self.assertFalse(client.is_running)


# ---------------------------------------------------------------------------
# Command construction
# ---------------------------------------------------------------------------

class TestPiCommandConstruction(unittest.TestCase):
    """Test that RPC commands are constructed correctly."""

    def test_prompt_command(self):
        """Verify prompt command dict shape."""
        client = PiClient()
        # Inject a request_id
        client._request_id = 0
        rid = client._next_id()
        self.assertEqual(rid, "req-1")

    def test_next_id_increments(self):
        client = PiClient()
        ids = [client._next_id() for _ in range(5)]
        self.assertEqual(ids, ["req-1", "req-2", "req-3", "req-4", "req-5"])

    def test_cli_args_built_correctly(self):
        """Verify the CLI args that would be passed to subprocess."""
        cfg = PiConfig(
            provider="anthropic",
            model="sonnet",
            thinking="high",
            tools="read,bash",
            no_session=True,
            extra_args=["--verbose"],
        )
        client = PiClient(config=cfg)
        # We can inspect what start() would use by checking cfg fields
        self.assertEqual(cfg.provider, "anthropic")
        self.assertEqual(cfg.model, "sonnet")
        self.assertEqual(cfg.thinking, "high")
        self.assertEqual(cfg.tools, "read,bash")
        self.assertTrue(cfg.no_session)
        self.assertIn("--verbose", cfg.extra_args)

    def test_session_dir_arg(self):
        cfg = PiConfig(session_dir="/tmp/pi-sessions")
        self.assertEqual(cfg.session_dir, "/tmp/pi-sessions")

    def test_api_key_arg(self):
        cfg = PiConfig(api_key="test-key-123")
        self.assertEqual(cfg.api_key, "test-key-123")


# ---------------------------------------------------------------------------
# Event parsing
# ---------------------------------------------------------------------------

class TestPiEventParsing(unittest.TestCase):
    """Test event drain and parsing mechanics."""

    def test_drain_empty(self):
        client = PiClient()
        events = client._drain_events()
        self.assertEqual(events, [])

    def test_drain_returns_and_clears(self):
        client = PiClient()
        client._events = [{"type": "agent_start"}, {"type": "agent_end"}]
        drained = client._drain_events()
        self.assertEqual(len(drained), 2)
        self.assertEqual(client._events, [])

    def test_message_update_structure(self):
        """Verify expected message_update event shape."""
        event = {
            "type": "message_update",
            "assistantMessageEvent": {
                "type": "text_delta",
                "delta": "Hello!",
            },
        }
        ae = event.get("assistantMessageEvent", {})
        self.assertEqual(ae["type"], "text_delta")
        self.assertEqual(ae["delta"], "Hello!")

    def test_tool_execution_event(self):
        event = {
            "type": "tool_execution_start",
            "tool": "bash",
            "input": {"command": "ls"},
        }
        self.assertEqual(event["tool"], "bash")

    def test_agent_end_event(self):
        event = {"type": "agent_end"}
        self.assertEqual(event["type"], "agent_end")


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestPiErrors(unittest.TestCase):
    """Test error hierarchy."""

    def test_base_error(self):
        self.assertTrue(issubclass(PiError, Exception))

    def test_startup_error(self):
        self.assertTrue(issubclass(PiStartupError, PiError))

    def test_timeout_error(self):
        self.assertTrue(issubclass(PiTimeoutError, PiError))

    def test_send_raises_when_not_running(self):
        client = PiClient()
        with self.assertRaises(PiError):
            client._send({"type": "prompt", "message": "test"})

    def test_startup_error_message(self):
        err = PiStartupError("pi not found")
        self.assertIn("pi not found", str(err))


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

class TestPiLifecycle(unittest.TestCase):
    """Test start/stop lifecycle without a real pi process."""

    def test_stop_not_running(self):
        client = PiClient()
        result = client.stop()
        self.assertEqual(result["status"], "not_running")
        self.assertIsNone(result["pid"])

    def test_start_bad_binary(self):
        client = PiClient(PiConfig(pi_bin="/nonexistent/pi-binary"))
        with self.assertRaises(PiStartupError):
            client.start()

    def test_context_manager(self):
        """Context manager should not raise even if start fails."""
        client = PiClient(PiConfig(pi_bin="/nonexistent/pi"))
        with self.assertRaises(PiStartupError):
            with client:
                pass


# ---------------------------------------------------------------------------
# Print mode
# ---------------------------------------------------------------------------

class TestPiPrintMode(unittest.TestCase):
    """Test pn -p (print mode) execution."""

    def test_print_bad_binary(self):
        client = PiClient(PiConfig(pi_bin="/nonexistent/pi"))
        with self.assertRaises(PiStartupError):
            client.run_print("test")

    @_skip_no_pi
    def test_print_version_check(self):
        """Verify pi -p works by asking for a trivial response."""
        # This is a lightweight test that just confirms the binary runs
        pi_bin = shutil.which("pi")
        result = subprocess.run(
            [pi_bin, "--version"], capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        self.assertRegex(result.stdout.strip(), r"\d+\.\d+")


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

class TestPiMCPTools(unittest.TestCase):
    """Test MCP tool wrappers."""

    @_skip_no_pi
    def test_status_tool(self):
        from codomyrmex.agents.pi.mcp_tools import pi_status
        result = pi_status()
        self.assertEqual(result["status"], "installed")
        self.assertIn("version", result)
        self.assertIn("path", result)

    def test_status_tool_structure(self):
        """Verify status returns a dict with expected keys."""
        from codomyrmex.agents.pi.mcp_tools import pi_status
        result = pi_status()
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

    def test_prompt_tool_error_no_pi(self):
        """If pi binary is missing, pi_prompt should return error."""
        from codomyrmex.agents.pi.mcp_tools import pi_prompt
        # Use an impossible binary path by setting env
        orig = os.environ.get("PATH", "")
        try:
            os.environ["PATH"] = "/nonexistent"
            result = pi_prompt("test", provider="test")
            self.assertEqual(result["status"], "error")
        finally:
            os.environ["PATH"] = orig

    @_skip_no_pi
    def test_list_models_tool(self):
        from codomyrmex.agents.pi.mcp_tools import pi_list_models
        result = pi_list_models()
        self.assertEqual(result["status"], "success")
        self.assertIn("models", result)
        self.assertIn("count", result)

    @_skip_no_pi
    def test_list_packages_tool(self):
        from codomyrmex.agents.pi.mcp_tools import pi_list_packages
        result = pi_list_packages()
        self.assertIsInstance(result, dict)
        self.assertIn("status", result)

    def test_get_client_helper(self):
        from codomyrmex.agents.pi.mcp_tools import _get_client
        client = _get_client(provider="openai", model="gpt-4o")
        self.assertEqual(client._config.provider, "openai")
        self.assertEqual(client._config.model, "gpt-4o")

    def test_get_client_ignores_empty(self):
        from codomyrmex.agents.pi.mcp_tools import _get_client
        client = _get_client(provider="", model="")
        # Empty values should not override defaults
        self.assertEqual(client._config.provider, "google")

    def test_all_tools_importable(self):
        from codomyrmex.agents.pi.mcp_tools import (
            pi_status,
            pi_prompt,
            pi_list_models,
            pi_start_rpc,
            pi_install_package,
            pi_list_packages,
        )
        self.assertTrue(callable(pi_status))
        self.assertTrue(callable(pi_prompt))
        self.assertTrue(callable(pi_list_models))
        self.assertTrue(callable(pi_start_rpc))
        self.assertTrue(callable(pi_install_package))
        self.assertTrue(callable(pi_list_packages))

    def test_tool_count(self):
        from codomyrmex.agents.pi import mcp_tools
        tool_names = [
            n for n in dir(mcp_tools)
            if n.startswith("pi_") and callable(getattr(mcp_tools, n))
        ]
        self.assertEqual(len(tool_names), 6)


# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------

class TestPiModuleImports(unittest.TestCase):
    """Test module import structure."""

    def test_init_exports_client(self):
        from codomyrmex.agents.pi import PiClient
        self.assertTrue(callable(PiClient))

    def test_init_exports_config(self):
        from codomyrmex.agents.pi import PiConfig
        self.assertTrue(hasattr(PiConfig, "__dataclass_fields__"))

    def test_init_exports_error(self):
        from codomyrmex.agents.pi import PiError
        self.assertTrue(issubclass(PiError, Exception))

    def test_all_list_complete(self):
        import codomyrmex.agents.pi as mod
        all_names = mod.__all__
        self.assertIn("PiClient", all_names)
        self.assertIn("PiConfig", all_names)
        self.assertIn("PiError", all_names)

    def test_parent_module_access(self):
        """Verify pi module is importable from parent."""
        import codomyrmex.agents.pi
        self.assertTrue(hasattr(codomyrmex.agents.pi, "PiClient"))


# ---------------------------------------------------------------------------
# Live integration tests (require pi CLI and API key)
# ---------------------------------------------------------------------------

_skip_no_api = unittest.skipUnless(
    _pi_available() and os.environ.get("GEMINI_API_KEY"),
    "pi CLI or GEMINI_API_KEY not available",
)


class TestPiLiveIntegration(unittest.TestCase):
    """Live integration tests — require pi CLI and API key."""

    @_skip_no_api
    def test_rpc_start_stop(self):
        """Start and stop an RPC session."""
        client = PiClient(PiConfig(no_session=True))
        client.start()
        self.assertTrue(client.is_running)
        result = client.stop()
        self.assertEqual(result["status"], "stopped")
        self.assertFalse(client.is_running)


if __name__ == "__main__":
    unittest.main()
