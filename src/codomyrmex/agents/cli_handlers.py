from pathlib import Path
from typing import Any, Optional
import json

from dataclasses import fields

from codomyrmex.agents import  get_config, AgentRequest
from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.codex import CodexClient
from codomyrmex.agents.droid import (
from codomyrmex.agents.exceptions import (
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.opencode import OpenCodeClient
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.utils.cli_helpers import (




"""
CLI Handlers for Agents Module

This module contains the logic for handling CLI commands for the agents module.
It is intended to be called by the thin orchestrator script.
"""


    AgentError,
    ClaudeError,
    CodexError,
    GeminiError,
    JulesError,
    OpenCodeError,
)
    format_output,
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
)

# Import agent clients
try:
except ImportError:
    JulesClient = None

try:
except ImportError:
    ClaudeClient = None

try:
except ImportError:
    CodexClient = None

try:
except ImportError:
    OpenCodeClient = None

try:
except ImportError:
    GeminiClient = None

try:
        DroidController,
        create_default_controller,
    )
except ImportError:
    DroidController = None
    create_default_controller = None

logger = get_logger(__name__)

def handle_info(args):
    """Handle info command."""
    try:
        if getattr(args, "verbose", False):
            logger.info("Retrieving agents module information")

        config = get_config()
        info = {
            "module": "agents",
            "description": "Agent framework integrations",
            "config": config.to_dict() if hasattr(config, 'to_dict') else config.__dict__,
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


# ============================================================================
# Common Agent Operations (execute, stream, check)
# ============================================================================

def _parse_context(context_str: Optional[str]) -> dict[str, Any]:
    """Parse context JSON string."""
    if not context_str:
        return {}
    try:
        return json.loads(context_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON context: {e}, using empty context")
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
            print_error(f"{client_name} client not available", context="Module not imported")
            return False

        prompt = args.prompt
        if getattr(args, "verbose", False):
            logger.info(f"Executing {client_name} request: {prompt[:50]}...")

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
        else:
            print_error(f"{client_name} execution failed", context=response.error)
            return False

    except (AgentError, ClaudeError, CodexError, GeminiError, JulesError, OpenCodeError) as e:
        logger.error(f"{client_name} error: {str(e)}")
        print_error(f"{client_name} error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during {client_name} execution")
        print_error(f"Unexpected error during {client_name} execution", exception=e)
        return False


def _handle_agent_stream(client_class, client_name: str, args: Any) -> bool:
    """Handle stream command for any agent."""
    try:
        if client_class is None:
            print_error(f"{client_name} client not available", context="Module not imported")
            return False

        prompt = args.prompt
        if getattr(args, "verbose", False):
            logger.info(f"Streaming {client_name} response: {prompt[:50]}...")

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

    except (AgentError, ClaudeError, CodexError, GeminiError, JulesError, OpenCodeError) as e:
        logger.error(f"{client_name} streaming error: {str(e)}")
        print_error(f"{client_name} streaming error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during {client_name} streaming")
        print_error(f"Unexpected error during {client_name} streaming", exception=e)
        return False


# ============================================================================
# Jules Agent Handlers
# ============================================================================

def handle_jules_execute(args):
    """Handle jules execute command."""
    return _handle_agent_execute(JulesClient, "Jules", args)


def handle_jules_stream(args):
    """Handle jules stream command."""
    return _handle_agent_stream(JulesClient, "Jules", args)


def handle_jules_check(args):
    """Handle jules check command."""
    try:
        if JulesClient is None:
            print_error("Jules client not available", context="Module not imported")
            return False

        client = JulesClient()
        available = client._check_jules_available()

        print_section("Jules Availability Check")
        if available:
            print_success("Jules CLI is available")
            print_info(f"Command: {client.jules_command}")
            print_info(f"Timeout: {client.timeout}s")
            if client.working_dir:
                print_info(f"Working directory: {client.working_dir}")
        else:
            print_warning("Jules CLI is not available", context="Command not found in PATH")
            print_info("Make sure Jules is installed and in your PATH")

        return True

    except Exception as e:
        logger.exception("Error checking Jules availability")
        print_error("Error checking Jules availability", exception=e)
        return False


def handle_jules_help(args):
    """Handle jules help command."""
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
            print_warning("Could not retrieve Jules help", context=help_info.get("error", "Unknown error"))

        return help_info.get("available", False)

    except Exception as e:
        logger.exception("Error getting Jules help")
        print_error("Error getting Jules help", exception=e)
        return False


def handle_jules_command(args):
    """Handle jules command execution."""
    try:
        if JulesClient is None:
            print_error("Jules client not available", context="Module not imported")
            return False

        client = JulesClient()
        command = args.cmd
        command_args = getattr(args, "args", []) or []

        if getattr(args, "verbose", False):
            logger.info(f"Executing Jules command: {command} with args: {command_args}")

        result = client.execute_jules_command(command, command_args)

        print_section(f"Jules Command: {command}")
        if result.get("success"):
            print(result.get("output", ""))
            print_success("Jules command executed successfully")
        else:
            print_error("Jules command failed", context=result.get("stderr", "Unknown error"))
            if result.get("stdout"):
                print("STDOUT:", result.get("stdout"))

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error executing Jules command")
        print_error("Error executing Jules command", exception=e)
        return False


# ============================================================================
# Claude Agent Handlers
# ============================================================================

def handle_claude_execute(args):
    """Handle claude execute command."""
    return _handle_agent_execute(ClaudeClient, "Claude", args)


def handle_claude_stream(args):
    """Handle claude stream command."""
    return _handle_agent_stream(ClaudeClient, "Claude", args)


def handle_claude_check(args):
    """Handle claude check command."""
    try:
        if ClaudeClient is None:
            print_error("Claude client not available", context="Module not imported")
            return False

        config = get_config()
        print_section("Claude Configuration Check")

        has_api_key = bool(config.claude_api_key)
        if has_api_key:
            print_success("Claude API key is configured")
        else:
            print_warning("Claude API key is not configured", context="Set ANTHROPIC_API_KEY environment variable")

        print_info(f"Model: {config.claude_model}")
        print_info(f"Timeout: {config.claude_timeout}s")
        print_info(f"Max tokens: {config.claude_max_tokens}")
        print_info(f"Temperature: {config.claude_temperature}")

        if not has_api_key:
            print_warning("Claude operations will fail without API key")

        return has_api_key

    except Exception as e:
        logger.exception("Error checking Claude configuration")
        print_error("Error checking Claude configuration", exception=e)
        return False


# ============================================================================
# Codex Agent Handlers
# ============================================================================

def handle_codex_execute(args):
    """Handle codex execute command."""
    return _handle_agent_execute(CodexClient, "Codex", args)


def handle_codex_stream(args):
    """Handle codex stream command."""
    return _handle_agent_stream(CodexClient, "Codex", args)


def handle_codex_check(args):
    """Handle codex check command."""
    try:
        if CodexClient is None:
            print_error("Codex client not available", context="Module not imported")
            return False

        config = get_config()
        print_section("Codex Configuration Check")

        has_api_key = bool(config.codex_api_key)
        if has_api_key:
            print_success("Codex API key is configured")
        else:
            print_warning("Codex API key is not configured", context="Set OPENAI_API_KEY environment variable")

        print_info(f"Model: {config.codex_model}")
        print_info(f"Timeout: {config.codex_timeout}s")
        print_info(f"Max tokens: {config.codex_max_tokens}")
        print_info(f"Temperature: {config.codex_temperature}")

        if not has_api_key:
            print_warning("Codex operations will fail without API key")

        return has_api_key

    except Exception as e:
        logger.exception("Error checking Codex configuration")
        print_error("Error checking Codex configuration", exception=e)
        return False


# ============================================================================
# OpenCode Agent Handlers
# ============================================================================

def handle_opencode_execute(args):
    """Handle opencode execute command."""
    return _handle_agent_execute(OpenCodeClient, "OpenCode", args)


def handle_opencode_stream(args):
    """Handle opencode stream command."""
    return _handle_agent_stream(OpenCodeClient, "OpenCode", args)


def handle_opencode_check(args):
    """Handle opencode check command."""
    try:
        if OpenCodeClient is None:
            print_error("OpenCode client not available", context="Module not imported")
            return False

        client = OpenCodeClient()
        available = client._check_opencode_available()

        print_section("OpenCode Availability Check")
        if available:
            print_success("OpenCode CLI is available")
            print_info(f"Command: {client.opencode_command}")
            print_info(f"Timeout: {client.timeout}s")
            if client.working_dir:
                print_info(f"Working directory: {client.working_dir}")
        else:
            print_warning("OpenCode CLI is not available", context="Command not found in PATH")
            print_info("Make sure OpenCode is installed and in your PATH")

        return True

    except Exception as e:
        logger.exception("Error checking OpenCode availability")
        print_error("Error checking OpenCode availability", exception=e)
        return False


def handle_opencode_init(args):
    """Handle opencode init command."""
    try:
        if OpenCodeClient is None:
            print_error("OpenCode client not available", context="Module not imported")
            return False

        client = OpenCodeClient()
        project_path = getattr(args, "path", None)

        if getattr(args, "verbose", False):
            logger.info(f"Initializing OpenCode for project: {project_path or 'current directory'}")

        result = client.initialize_project(project_path)

        print_section("OpenCode Initialization")
        if result.get("success"):
            if result.get("output"):
                print(result.get("output"))
            print_success("OpenCode initialized successfully")
        else:
            print_error("OpenCode initialization failed", context=result.get("error", "Unknown error"))

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error initializing OpenCode")
        print_error("Error initializing OpenCode", exception=e)
        return False


def handle_opencode_version(args):
    """Handle opencode version command."""
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
            print_warning("Could not retrieve OpenCode version", context=version_info.get("error", "Unknown error"))

        return version_info.get("available", False)

    except Exception as e:
        logger.exception("Error getting OpenCode version")
        print_error("Error getting OpenCode version", exception=e)
        return False


# ============================================================================
# Gemini Agent Handlers
# ============================================================================

def handle_gemini_execute(args):
    """Handle gemini execute command."""
    return _handle_agent_execute(GeminiClient, "Gemini", args)


def handle_gemini_stream(args):
    """Handle gemini stream command."""
    return _handle_agent_stream(GeminiClient, "Gemini", args)


def handle_gemini_check(args):
    """Handle gemini check command."""
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()
        available = client._check_gemini_available()
        config = get_config()

        print_section("Gemini Availability Check")
        if available:
            print_success("Gemini CLI is available")
            print_info(f"Command: {client.gemini_command}")
            print_info(f"Timeout: {client.timeout}s")
            print_info(f"Auth method: {config.gemini_auth_method}")
            if client.working_dir:
                print_info(f"Working directory: {client.working_dir}")
        else:
            print_warning("Gemini CLI is not available", context="Command not found in PATH")
            print_info("Make sure Gemini is installed and in your PATH")

        return True

    except Exception as e:
        logger.exception("Error checking Gemini availability")
        print_error("Error checking Gemini availability", exception=e)
        return False


def handle_gemini_chat_save(args):
    """Handle gemini chat save command."""
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()
        tag = args.tag
        prompt = getattr(args, "prompt", None)

        if getattr(args, "verbose", False):
            logger.info(f"Saving Gemini chat session: {tag}")

        result = client.save_chat(tag, prompt)

        print_section(f"Gemini Chat Save: {tag}")
        if result.get("success"):
            print_success("Chat session saved successfully")
        else:
            print_error("Failed to save chat session", context=result.get("error", "Unknown error"))

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error saving Gemini chat")
        print_error("Error saving Gemini chat", exception=e)
        return False


def handle_gemini_chat_resume(args):
    """Handle gemini chat resume command."""
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()
        tag = args.tag

        if getattr(args, "verbose", False):
            logger.info(f"Resuming Gemini chat session: {tag}")

        result = client.resume_chat(tag)

        print_section(f"Gemini Chat Resume: {tag}")
        if result.get("success"):
            if result.get("output"):
                print(result.get("output"))
            print_success("Chat session resumed successfully")
        else:
            print_error("Failed to resume chat session", context=result.get("error", "Unknown error"))

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error resuming Gemini chat")
        print_error("Error resuming Gemini chat", exception=e)
        return False


def handle_gemini_chat_list(args):
    """Handle gemini chat list command."""
    try:
        if GeminiClient is None:
            print_error("Gemini client not available", context="Module not imported")
            return False

        client = GeminiClient()

        if getattr(args, "verbose", False):
            logger.info("Listing Gemini chat sessions")

        result = client.list_chats()

        print_section("Gemini Chat Sessions")
        if result.get("success"):
            if result.get("output"):
                print(result.get("output"))
            else:
                print_info("No chat sessions found")
            print_success("Chat sessions listed")
        else:
            print_error("Failed to list chat sessions", context=result.get("error", "Unknown error"))

        return result.get("success", False)

    except Exception as e:
        logger.exception("Error listing Gemini chats")
        print_error("Error listing Gemini chats", exception=e)
        return False


# ============================================================================
# Droid Agent Handlers
# ============================================================================

# Global droid controller instance (singleton pattern)
_droid_controller: Optional[Any] = None


def _get_droid_controller() -> Optional[Any]:
    """Get or create droid controller instance."""
    global _droid_controller
    if _droid_controller is None and create_default_controller is not None:
        try:
            _droid_controller = create_default_controller()
        except Exception as e:
            logger.error(f"Failed to create droid controller: {e}")
            return None
    return _droid_controller


def handle_droid_start(args):
    """Handle droid start command."""
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
    """Handle droid stop command."""
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
    """Handle droid status command."""
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
    """Handle droid config show command."""
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
