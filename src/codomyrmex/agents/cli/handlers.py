"""CLI Handlers for Agents Module.

Contains the logic for handling CLI commands for the agents module.
Intended to be called by the thin orchestrator script.
"""

import contextlib
import json
from pathlib import Path
from typing import Any

from codomyrmex.agents import AgentRequest, get_config
from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.codex import CodexClient
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.opencode import OpenCodeClient
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
)

# Optional droid import
with contextlib.suppress(ImportError):
    from codomyrmex.agents.droid import DroidController, create_default_controller

logger = get_logger(__name__)


def handle_info(args):
    try:
        logger.debug("Retrieving agents module information")

        config = get_config()
        info = {
            "module": "agents",
            "description": "Agent framework integrations",
            "config": config.to_dict()
            if hasattr(config, "to_dict")
            else config.__dict__,
        }

        print_section("Agents Module Information")
        output_format = getattr(args, "format", "text")
        print(format_output(info, format_type=output_format))
        print_section("", separator="")

        print_success("Information retrieved")
        return True

    except Exception as e:
        logger.exception("Unexpected error retrieving information")
        print_error("Unexpected error retrieving information", exception=e)
        return False


def _parse_context(context_str: str | None) -> dict[str, Any]:
    """Parse context JSON string."""
    if not context_str:
        return {}
    try:
        return json.loads(context_str)
    except json.JSONDecodeError as e:
        logger.warning("Invalid JSON context: %s, using empty context", e)
        return {}


def _create_agent_request(prompt: str, args: Any) -> AgentRequest:
    """Create AgentRequest from arguments."""
    context = _parse_context(getattr(args, "context", None))
    timeout = getattr(args, "timeout", None)
    return AgentRequest(
        prompt=prompt,
        context=context,
        timeout=timeout,
    )


def _handle_agent_execute(client_class, client_name: str, args: Any) -> bool:
    """Handle execute command for any agent."""
    try:
        if client_class is None:
            print_error(
                f"{client_name} client not available", context="Module not imported"
            )
            return False

        prompt = args.prompt
        logger.debug("Executing %s request: %s...", client_name, prompt[:50])

        client = client_class()
        request = _create_agent_request(prompt, args)
        response = client.execute(request)

        if response.is_success():
            print_section(f"{client_name} Response")
            print(response.content)
            if response.metadata:
                print_section("Metadata")
                output_format = getattr(args, "format", "text")
                print(format_output(response.metadata, format_type=output_format))
            print_section("", separator="")
            print_success(f"{client_name} execution completed")
            if getattr(args, "output", None):
                output_path = Path(args.output)
                output_path.write_text(response.content, encoding="utf-8")
                print_info(f"Output saved to {output_path}")
            return True
        print_error(f"{client_name} execution failed", context=response.error)
        return False

    except Exception as e:
        logger.exception("%s error", client_name)
        print_error(f"{client_name} error", context=str(e), exception=e)
        return False


def _handle_agent_stream(client_class, client_name: str, args: Any) -> bool:
    """Handle stream command for any agent."""
    try:
        if client_class is None:
            print_error(
                f"{client_name} client not available", context="Module not imported"
            )
            return False

        prompt = args.prompt
        logger.debug("Streaming %s response: %s...", client_name, prompt[:50])

        client = client_class()
        request = _create_agent_request(prompt, args)

        print_section(f"{client_name} Streaming Response")
        output_lines = []
        for chunk in client.stream(request):
            print(chunk, end="", flush=True)
            output_lines.append(chunk)

        print()  # New line after streaming
        print_section("", separator="")
        print_success(f"{client_name} streaming completed")

        if getattr(args, "output", None):
            output_path = Path(args.output)
            output_path.write_text("".join(output_lines), encoding="utf-8")
            print_info(f"Output saved to {output_path}")

        return True

    except Exception as e:
        logger.exception("%s streaming error", client_name)
        print_error(f"{client_name} streaming error", context=str(e), exception=e)
        return False


def handle_agent_setup(client_class, client_name: str, args: Any) -> bool:
    """Generic handler for agent setup."""
    try:
        if client_class is None:
            print_error(
                f"{client_name} client not available", context="Module not imported"
            )
            return False

        client = client_class(config=get_config())
        print_section(f"Setting up {client_name}")
        client.setup()
        print_success(f"{client_name} setup completed")
        return True
    except Exception as e:
        logger.exception("Failed to set up %s", client_name)
        print_error(f"Error setting up {client_name}", exception=e)
        return False


def handle_agent_test(client_class, client_name: str, args: Any) -> bool:
    """Generic handler for agent connection test."""
    try:
        if client_class is None:
            print_error(
                f"{client_name} client not available", context="Module not imported"
            )
            return False

        client = client_class(config=get_config())
        print_section(f"Testing {client_name} Connection")
        result = client.test_connection()
        if result:
            print_success(f"{client_name} connection test passed")
        else:
            print_error(f"{client_name} connection test failed")
        return result
    except Exception as e:
        logger.exception("Failed to test %s connection", client_name)
        print_error(f"Error testing {client_name} connection", exception=e)
        return False


def _handle_cli_agent_check(client_class, client_name: str, args: Any) -> bool:
    """Generic check handler for CLI-based agents."""
    try:
        if client_class is None:
            print_error(
                f"{client_name} client not available", context="Module not imported"
            )
            return False

        client = client_class()
        available = client.is_available()

        print_section(f"{client_name} Availability Check")
        if available:
            print_success(f"{client_name} CLI is available")
            print_info(f"Command: {client.command}")
            print_info(f"Timeout: {client.timeout}s")
            if client.working_dir:
                print_info(f"Working directory: {client.working_dir}")
        else:
            print_warning(
                f"{client_name} CLI is not available",
                context="Command not found in PATH",
            )
            print_info(f"Make sure {client_name} is installed and in your PATH")

        return True

    except Exception as e:
        logger.exception("Error checking %s availability", client_name)
        print_error(f"Error checking {client_name} availability", exception=e)
        return False


def _handle_api_key_check(
    client_class, client_name: str, config_prefix: str, api_key_env: str, args: Any
) -> bool:
    """Generic check handler for API-key-based agents."""
    try:
        if client_class is None:
            print_error(
                f"{client_name} client not available", context="Module not imported"
            )
            return False

        config = get_config()
        print_section(f"{client_name} Configuration Check")

        has_api_key = bool(getattr(config, f"{config_prefix}_api_key", None))
        if has_api_key:
            print_success(f"{client_name} API key is configured")
        else:
            print_warning(
                f"{client_name} API key is not configured",
                context=f"set {api_key_env} environment variable",
            )

        print_info(f"Model: {getattr(config, f'{config_prefix}_model', 'unknown')}")
        print_info(
            f"Timeout: {getattr(config, f'{config_prefix}_timeout', 'unknown')}s"
        )
        print_info(
            f"Max tokens: {getattr(config, f'{config_prefix}_max_tokens', 'unknown')}"
        )
        print_info(
            f"Temperature: {getattr(config, f'{config_prefix}_temperature', 'unknown')}"
        )

        if not has_api_key:
            print_warning(f"{client_name} operations will fail without API key")

        return has_api_key

    except Exception as e:
        logger.exception("Error checking %s configuration", client_name)
        print_error(f"Error checking {client_name} configuration", exception=e)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch table — replaces 15 trivial one-liner pass-throughs
#
# CLI agents: availability checked via command lookup (e.g. jules/gemini/opencode)
# API-key agents: availability checked via config key + env-var hint
# ─────────────────────────────────────────────────────────────────────────────

_CLI_AGENTS = [
    ("jules", JulesClient, "Jules"),
    ("gemini", GeminiClient, "Gemini"),
    ("opencode", OpenCodeClient, "OpenCode"),
]

_API_KEY_AGENTS = [
    ("claude", ClaudeClient, "Claude", "claude", "ANTHROPIC_API_KEY"),
    ("codex", CodexClient, "Codex", "codex", "OPENAI_API_KEY"),
]

# Generate execute/stream/check handlers from the registry tables.
# The resulting names (handle_<agent>_execute, etc.) are identical to what
# was previously written out by hand, so all importers see the same interface.
for _name, _cls, _display in _CLI_AGENTS:
    globals()[f"handle_{_name}_execute"] = lambda args, c=_cls, d=_display: (
        _handle_agent_execute(c, d, args)
    )
    globals()[f"handle_{_name}_stream"] = lambda args, c=_cls, d=_display: (
        _handle_agent_stream(c, d, args)
    )
    globals()[f"handle_{_name}_check"] = lambda args, c=_cls, d=_display: (
        _handle_cli_agent_check(c, d, args)
    )

for _name, _cls, _display, _prefix, _env in _API_KEY_AGENTS:
    globals()[f"handle_{_name}_execute"] = lambda args, c=_cls, d=_display: (
        _handle_agent_execute(c, d, args)
    )
    globals()[f"handle_{_name}_stream"] = lambda args, c=_cls, d=_display: (
        _handle_agent_stream(c, d, args)
    )
    globals()[f"handle_{_name}_check"] = (
        lambda args, c=_cls, d=_display, p=_prefix, e=_env: _handle_api_key_check(
            c, d, p, e, args
        )
    )

del _name, _cls, _display  # clean up loop variables from module namespace


def handle_jules_help(args):
    try:
        if JulesClient is None:
            print_error("Jules client not available", context="Module not imported")
            return False

        client = JulesClient()
        help_info = client.get_jules_help()

        print_section("Jules Help")
        if help_info.get("available"):
            print(help_info.get("help_text", ""))
        else:
            print_warning(
                "Could not retrieve Jules help",
                context=help_info.get("error", "Unknown error"),
            )

        return help_info.get("available", False)

    except Exception as e:
        logger.exception("Error getting Jules help")
        print_error("Error getting Jules help", exception=e)
        return False


def handle_jules_command(args):
    try:
        if JulesClient is None:
            print_error("Jules client not available", context="Module not imported")
            return False

        client = JulesClient()
        command = args.cmd
        command_args = getattr(args, "args", []) or []

        logger.debug("Executing Jules command: %s with args: %s", command, command_args)

        result = client.execute_jules_command(command, command_args)

        print_section(f"Jules Command: {command}")
        if result.get("success"):
            print(result.get("output", ""))
            print_success("Jules command executed successfully")
        else:
            print_error(
                "Jules command failed", context=result.get("stderr", "Unknown error")
            )
            if result.get("stdout"):
                print("STDOUT:", result.get("stdout"))

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error executing Jules command")
        print_error("Error executing Jules command", exception=e)
        return False


def handle_opencode_init(args):
    try:
        if OpenCodeClient is None:
            print_error("OpenCode client not available", context="Module not imported")
            return False

        client = OpenCodeClient()
        project_path = getattr(args, "path", None)

        label = project_path or "current directory"
        logger.debug("Initializing OpenCode for project: %s", label)

        result = client.initialize_project(project_path)

        print_section("OpenCode Initialization")
        if result.get("success"):
            if result.get("output"):
                print(result.get("output"))
            print_success("OpenCode initialized successfully")
        else:
            print_error(
                "OpenCode initialization failed",
                context=result.get("error", "Unknown error"),
            )

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error initializing OpenCode")
        print_error("Error initializing OpenCode", exception=e)
        return False


def handle_opencode_version(args):
    try:
        if OpenCodeClient is None:
            print_error("OpenCode client not available", context="Module not imported")
            return False

        client = OpenCodeClient()
        version_info = client.get_opencode_version()

        print_section("OpenCode Version")
        if version_info.get("available"):
            print(version_info.get("version", "Unknown version"))
            print_success("OpenCode version retrieved")
        else:
            print_warning(
                "Could not retrieve OpenCode version",
                context=version_info.get("error", "Unknown error"),
            )

        return version_info.get("available", False)

    except Exception as e:
        logger.exception("Error getting OpenCode version")
        print_error("Error getting OpenCode version", exception=e)
        return False


def handle_gemini_chat_save(args):
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()
        tag = args.tag
        prompt = getattr(args, "prompt", None)

        logger.debug("Saving Gemini chat session: %s", tag)

        result = client.save_chat(tag, prompt)

        print_section(f"Gemini Chat Save: {tag}")
        if result.get("success"):
            print_success("Chat session saved successfully")
        else:
            print_error(
                "Failed to save chat session",
                context=result.get("error", "Unknown error"),
            )

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error saving Gemini chat")
        print_error("Error saving Gemini chat", exception=e)
        return False


def handle_gemini_chat_resume(args):
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()
        tag = args.tag

        logger.debug("Resuming Gemini chat session: %s", tag)

        result = client.resume_chat(tag)

        print_section(f"Gemini Chat Resume: {tag}")
        if result.get("success"):
            if result.get("output"):
                print(result.get("output"))
            print_success("Chat session resumed successfully")
        else:
            print_error(
                "Failed to resume chat session",
                context=result.get("error", "Unknown error"),
            )

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error resuming Gemini chat")
        print_error("Error resuming Gemini chat", exception=e)
        return False


def handle_gemini_chat_list(args):
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()

        logger.debug("Listing Gemini chat sessions")

        result = client.list_chats()

        print_section("Gemini Chat Sessions")
        if result.get("success"):
            if result.get("output"):
                print(result.get("output"))
            else:
                print_info("No chat sessions found")
            print_success("Chat sessions listed")
        else:
            print_error(
                "Failed to list chat sessions",
                context=result.get("error", "Unknown error"),
            )

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error listing Gemini chats")
        print_error("Error listing Gemini chats", exception=e)
        return False


# Global droid controller instance (singleton pattern)
_droid_controller: Any | None = None


def _get_droid_controller() -> Any | None:
    """Get or create droid controller instance."""
    global _droid_controller
    if _droid_controller is None and create_default_controller is not None:
        try:
            _droid_controller = create_default_controller()
        except Exception as _exc:
            logger.exception("Failed to create droid controller")
            raise
    return _droid_controller


def handle_droid_start(args):
    try:
        if DroidController is None:
            print_error("Droid controller not available", context="Module not imported")
            return False

        controller = _get_droid_controller()
        if controller is None:
            print_error("Failed to create droid controller")
            return False

        controller.start()
        print_section("Droid Controller")
        print_success("Droid controller started")
        return True

    except Exception as e:
        logger.exception("Error starting droid controller")
        print_error("Error starting droid controller", exception=e)
        return False


def handle_droid_stop(args):
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_warning("Droid controller not running")
            return True

        controller.stop()
        print_section("Droid Controller")
        print_success("Droid controller stopped")
        return True

    except Exception as e:
        logger.exception("Error stopping droid controller")
        print_error("Error stopping droid controller", exception=e)
        return False


def handle_droid_status(args):
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_warning("Droid controller not initialized")
            return False

        status = controller.status
        metrics = controller.metrics

        print_section("Droid Controller Status")
        print_info(f"Status: {status.value}")
        print_section("Metrics")
        output_format = getattr(args, "format", "text")
        print(format_output(metrics, format_type=output_format))
        print_success("Status retrieved")
        return True

    except Exception as e:
        logger.exception("Error getting droid status")
        print_error("Error getting droid status", exception=e)
        return False


def handle_droid_config_show(args):
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_warning("Droid controller not initialized")
            return False

        config = controller.config
        print_section("Droid Configuration")
        output_format = getattr(args, "format", "text")
        print(format_output(config.to_dict(), format_type=output_format))
        print_success("Configuration retrieved")
        return True

    except Exception as e:
        logger.exception("Error showing droid config")
        print_error("Error showing droid config", exception=e)
        return False
