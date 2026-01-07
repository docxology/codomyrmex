#!/usr/bin/env python3
"""
Agents Module Orchestrator

Thin orchestrator script providing CLI access to agents module functionality.
Calls actual module functions from codomyrmex.agents.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.agents.exceptions import (
    AgentError,
    ClaudeError,
    CodexError,
    GeminiError,
    JulesError,
    OpenCodeError,
)

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        print_warning,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        print_warning,
    )

# Import module functions
from codomyrmex.agents import AgentInterface, get_config, AgentRequest, AgentResponse
from codomyrmex.agents.core import AgentCapabilities

# Import agent clients
try:
    from codomyrmex.agents.jules import JulesClient
except ImportError:
    JulesClient = None

try:
    from codomyrmex.agents.claude import ClaudeClient
except ImportError:
    ClaudeClient = None

try:
    from codomyrmex.agents.codex import CodexClient
except ImportError:
    CodexClient = None

try:
    from codomyrmex.agents.opencode import OpenCodeClient
except ImportError:
    OpenCodeClient = None

try:
    from codomyrmex.agents.gemini import GeminiClient
except ImportError:
    GeminiClient = None

try:
    from codomyrmex.agents.droid import (
        DroidController,
        DroidConfig,
        create_default_controller,
        save_config_to_file,
        load_config_from_file,
        TodoManager,
        TodoItem,
    )
except ImportError:
    DroidController = None
    DroidConfig = None
    create_default_controller = None
    save_config_to_file = None
    load_config_from_file = None
    TodoManager = None
    TodoItem = None

try:
    from codomyrmex.agents.generic import AgentOrchestrator, TaskPlanner, Task, TaskStatus, MessageBus, Message
except ImportError:
    AgentOrchestrator = None
    TaskPlanner = None
    Task = None
    TaskStatus = None
    MessageBus = None
    Message = None

try:
    from codomyrmex.agents.theory import (
        AgentArchitecture,
        ReactiveArchitecture,
        DeliberativeArchitecture,
        HybridArchitecture,
        ReasoningModel,
        SymbolicReasoningModel,
        NeuralReasoningModel,
        HybridReasoningModel,
    )
except ImportError:
    AgentArchitecture = None

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

# Global task planner instance
_task_planner: Optional[Any] = None

# Global message bus instance
_message_bus: Optional[Any] = None


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
        logger.exception("Error getting droid configuration")
        print_error("Error getting droid configuration", exception=e)
        return False


def handle_droid_config_set(args):
    """Handle droid config set command."""
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_error("Droid controller not initialized")
            return False

        overrides = {}
        for kv in getattr(args, "overrides", []):
            if "=" not in kv:
                print_warning(f"Invalid key=value format: {kv}")
                continue
            key, value = kv.split("=", 1)
            # Try to convert to appropriate type
            try:
                if value.lower() in ("true", "false"):
                    overrides[key] = value.lower() == "true"
                elif value.isdigit():
                    overrides[key] = int(value)
                else:
                    try:
                        overrides[key] = float(value)
                    except ValueError:
                        overrides[key] = value
            except Exception:
                overrides[key] = value

        controller.update_config(**overrides)
        print_section("Droid Configuration")
        print_success("Configuration updated")
        return True

    except Exception as e:
        logger.exception("Error updating droid configuration")
        print_error("Error updating droid configuration", exception=e)
        return False


def handle_droid_metrics(args):
    """Handle droid metrics command."""
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_warning("Droid controller not initialized")
            return False

        metrics = controller.metrics
        print_section("Droid Metrics")
        output_format = getattr(args, "format", "text")
        print(format_output(metrics, format_type=output_format))
        print_success("Metrics retrieved")
        return True

    except Exception as e:
        logger.exception("Error getting droid metrics")
        print_error("Error getting droid metrics", exception=e)
        return False


def handle_droid_metrics_reset(args):
    """Handle droid metrics reset command."""
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_warning("Droid controller not initialized")
            return False

        controller.reset_metrics()
        print_section("Droid Metrics")
        print_success("Metrics reset")
        return True

    except Exception as e:
        logger.exception("Error resetting droid metrics")
        print_error("Error resetting droid metrics", exception=e)
        return False


def handle_droid_config_save(args):
    """Handle droid config save command."""
    try:
        if DroidController is None or save_config_to_file is None:
            print_error("Droid controller not available", context="Module not imported")
            return False

        controller = _get_droid_controller()
        if controller is None:
            print_error("Droid controller not initialized")
            return False

        file_path = Path(args.file)
        save_config_to_file(controller.config, file_path)
        
        print_section("Droid Configuration")
        print_success(f"Configuration saved to {file_path}")
        return True

    except Exception as e:
        logger.exception("Error saving droid configuration")
        print_error("Error saving droid configuration", exception=e)
        return False


def handle_droid_config_load(args):
    """Handle droid config load command."""
    try:
        if DroidController is None or load_config_from_file is None:
            print_error("Droid controller not available", context="Module not imported")
            return False

        file_path = Path(args.file)
        if not file_path.exists():
            print_error("Configuration file not found", context=str(file_path))
            return False

        config = load_config_from_file(file_path)
        global _droid_controller
        _droid_controller = DroidController(config)
        _droid_controller.start()
        
        print_section("Droid Configuration")
        print_success(f"Configuration loaded from {file_path}")
        return True

    except Exception as e:
        logger.exception("Error loading droid configuration")
        print_error("Error loading droid configuration", exception=e)
        return False


def handle_droid_execute_task(args):
    """Handle droid execute-task command."""
    try:
        controller = _get_droid_controller()
        if controller is None:
            print_error("Droid controller not initialized")
            return False

        operation_id = args.operation_id
        handler_path = getattr(args, "handler", None)

        if handler_path:
            # Resolve handler from path
            from codomyrmex.agents.droid.run_todo_droid import resolve_handler
            handler = resolve_handler(handler_path)
        else:
            # Use a simple handler that just returns success
            def handler(*args, **kwargs):
                return f"Task {operation_id} executed"
            handler = handler

        if getattr(args, "verbose", False):
            logger.info(f"Executing droid task: {operation_id}")

        result = controller.execute_task(operation_id, handler)
        
        print_section(f"Droid Task: {operation_id}")
        print_success("Task executed successfully")
        if result:
            print_info(f"Result: {result}")
        return True

    except Exception as e:
        logger.exception("Error executing droid task")
        print_error("Error executing droid task", exception=e)
        return False


def handle_droid_todo_load(args):
    """Handle droid todo load command."""
    try:
        if TodoManager is None:
            print_error("TodoManager not available", context="Module not imported")
            return False
        
        todo_file = getattr(args, "file", "todo_list.txt")
        manager = TodoManager(todo_file)
        
        todo_items, completed_items = manager.load()
        
        print_section(f"TODO List: {todo_file}")
        print_info(f"TODO items: {len(todo_items)}")
        print_info(f"Completed items: {len(completed_items)}")
        
        if todo_items:
            print_section("TODO Items")
            for item in todo_items:
                print(f"  - {item.task_name} | {item.description} | {item.outcomes}")
        
        if completed_items:
            print_section("Completed Items")
            for item in completed_items:
                print(f"  - {item.task_name} | {item.description} | {item.outcomes}")
        
        print_success("TODO list loaded")
        return True

    except Exception as e:
        logger.exception("Error loading TODO list")
        print_error("Error loading TODO list", exception=e)
        return False


def handle_droid_todo_save(args):
    """Handle droid todo save command."""
    try:
        if TodoManager is None:
            print_error("TodoManager not available", context="Module not imported")
            return False
        
        todo_file = getattr(args, "file", "todo_list.txt")
        manager = TodoManager(todo_file)
        
        # Load existing items
        todo_items, completed_items = manager.load()
        
        # Save them back
        manager.save(todo_items, completed_items)
        
        print_section("TODO List")
        print_success(f"TODO list saved to {todo_file}")
        return True

    except Exception as e:
        logger.exception("Error saving TODO list")
        print_error("Error saving TODO list", exception=e)
        return False


def handle_droid_todo_validate(args):
    """Handle droid todo validate command."""
    try:
        if TodoManager is None:
            print_error("TodoManager not available", context="Module not imported")
            return False
        
        todo_file = getattr(args, "file", "todo_list.txt")
        manager = TodoManager(todo_file)
        
        is_valid, issues = manager.validate()
        
        print_section(f"TODO Validation: {todo_file}")
        if is_valid:
            print_success("TODO file is valid")
        else:
            print_warning(f"TODO file has {len(issues)} issue(s):")
            for line_num, line_text, error_msg in issues:
                print_error(f"Line {line_num}: {error_msg}", context=line_text)
        
        return is_valid

    except Exception as e:
        logger.exception("Error validating TODO list")
        print_error("Error validating TODO list", exception=e)
        return False


def handle_droid_todo_migrate(args):
    """Handle droid todo migrate command."""
    try:
        if TodoManager is None:
            print_error("TodoManager not available", context="Module not imported")
            return False
        
        todo_file = getattr(args, "file", "todo_list.txt")
        manager = TodoManager(todo_file)
        
        changed = manager.migrate_to_three_columns()
        
        print_section("TODO Migration")
        if changed > 0:
            print_success(f"Migrated {changed} line(s) to 3-column format")
        else:
            print_info("No migration needed (already in 3-column format)")
        return True

    except Exception as e:
        logger.exception("Error migrating TODO list")
        print_error("Error migrating TODO list", exception=e)
        return False


def handle_droid_todo_list(args):
    """Handle droid todo list command."""
    try:
        if TodoManager is None:
            print_error("TodoManager not available", context="Module not imported")
            return False
        
        todo_file = getattr(args, "file", "todo_list.txt")
        manager = TodoManager(todo_file)
        
        todo_items, completed_items = manager.load()
        
        print_section(f"TODO List: {todo_file}")
        
        if todo_items:
            print_section("TODO Items")
            for i, item in enumerate(todo_items, 1):
                print(f"{i}. {item.task_name} | {item.description} | {item.outcomes}")
        else:
            print_info("No TODO items")
        
        if completed_items:
            print_section("Completed Items")
            for i, item in enumerate(completed_items, 1):
                print(f"{i}. {item.task_name} | {item.description} | {item.outcomes}")
        else:
            print_info("No completed items")
        
        print_success("TODO list displayed")
        return True

    except Exception as e:
        logger.exception("Error listing TODO items")
        print_error("Error listing TODO items", exception=e)
        return False


# ============================================================================
# Task Planner Handlers
# ============================================================================

def _get_task_planner() -> Optional[Any]:
    """Get or create task planner instance."""
    global _task_planner
    if _task_planner is None and TaskPlanner is not None:
        try:
            _task_planner = TaskPlanner()
        except Exception as e:
            logger.error(f"Failed to create task planner: {e}")
            return None
    return _task_planner


def handle_task_create(args):
    """Handle task create command."""
    try:
        if TaskPlanner is None:
            print_error("Task planner not available", context="Module not imported")
            return False

        planner = _get_task_planner()
        if planner is None:
            print_error("Failed to create task planner")
            return False

        description = args.description
        dependencies = getattr(args, "dependencies", None)
        if dependencies:
            dependencies = [d.strip() for d in dependencies.split(",")]
        
        metadata = _parse_context(getattr(args, "metadata", None))

        task = planner.create_task(
            description=description,
            dependencies=dependencies,
            metadata=metadata,
        )

        print_section("Task Created")
        print_success(f"Task created: {task.id}")
        print_info(f"Description: {task.description}")
        if task.dependencies:
            print_info(f"Dependencies: {', '.join(task.dependencies)}")
        return True

    except Exception as e:
        logger.exception("Error creating task")
        print_error("Error creating task", exception=e)
        return False


def handle_task_list(args):
    """Handle task list command."""
    try:
        planner = _get_task_planner()
        if planner is None:
            print_error("Task planner not initialized")
            return False

        tasks = planner.get_all_tasks()
        
        print_section("All Tasks")
        if tasks:
            output_format = getattr(args, "format", "text")
            task_info = []
            for task in tasks:
                task_info.append({
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "dependencies": task.dependencies,
                })

            if output_format == "json":
                print(format_output(task_info, format_type="json"))
            else:
                for info in task_info:
                    deps_str = ", ".join(info["dependencies"]) if info["dependencies"] else "none"
                    print(f"{info['id']:15} | {info['status']:15} | {info['description']}")
                    if info["dependencies"]:
                        print(f"  Dependencies: {deps_str}")
        else:
            print_info("No tasks")

        print_success("Task list retrieved")
        return True

    except Exception as e:
        logger.exception("Error listing tasks")
        print_error("Error listing tasks", exception=e)
        return False


def handle_task_get(args):
    """Handle task get command."""
    try:
        planner = _get_task_planner()
        if planner is None:
            print_error("Task planner not initialized")
            return False

        task_id = args.id
        task = planner.get_task(task_id)

        if not task:
            print_error("Task not found", context=task_id)
            return False

        print_section(f"Task: {task.id}")
        output_format = getattr(args, "format", "text")
        task_info = {
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "dependencies": task.dependencies,
            "result": str(task.result) if task.result is not None else None,
            "error": task.error,
            "metadata": task.metadata,
        }
        print(format_output(task_info, format_type=output_format))
        print_success("Task retrieved")
        return True

    except Exception as e:
        logger.exception("Error getting task")
        print_error("Error getting task", exception=e)
        return False


def handle_task_update(args):
    """Handle task update command."""
    try:
        planner = _get_task_planner()
        if planner is None:
            print_error("Task planner not initialized")
            return False

        task_id = args.id
        status_str = getattr(args, "status", None)
        result = getattr(args, "result", None)
        error = getattr(args, "error", None)

        if status_str:
            try:
                status = TaskStatus(status_str.lower())
            except ValueError:
                print_error("Invalid status", context=f"Valid values: {[s.value for s in TaskStatus]}")
                return False
        else:
            status = None

        planner.update_task_status(
            task_id=task_id,
            status=status,
            result=result,
            error=error,
        )

        print_section("Task Update")
        print_success(f"Task {task_id} updated")
        return True

    except Exception as e:
        logger.exception("Error updating task")
        print_error("Error updating task", exception=e)
        return False


def handle_task_ready(args):
    """Handle task ready command."""
    try:
        planner = _get_task_planner()
        if planner is None:
            print_error("Task planner not initialized")
            return False

        ready_tasks = planner.get_ready_tasks()
        
        print_section("Ready Tasks")
        if ready_tasks:
            output_format = getattr(args, "format", "text")
            task_info = []
            for task in ready_tasks:
                task_info.append({
                    "id": task.id,
                    "description": task.description,
                    "dependencies": task.dependencies,
                })

            if output_format == "json":
                print(format_output(task_info, format_type="json"))
            else:
                for info in task_info:
                    print(f"{info['id']:15} | {info['description']}")
        else:
            print_info("No ready tasks")

        print_success(f"Found {len(ready_tasks)} ready task(s)")
        return True

    except Exception as e:
        logger.exception("Error getting ready tasks")
        print_error("Error getting ready tasks", exception=e)
        return False


def handle_task_order(args):
    """Handle task order command."""
    try:
        planner = _get_task_planner()
        if planner is None:
            print_error("Task planner not initialized")
            return False

        execution_order = planner.get_task_execution_order()
        
        print_section("Task Execution Order")
        if execution_order:
            output_format = getattr(args, "format", "text")
            task_info = []
            for i, task in enumerate(execution_order, 1):
                task_info.append({
                    "order": i,
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                })

            if output_format == "json":
                print(format_output(task_info, format_type="json"))
            else:
                for info in task_info:
                    print(f"{info['order']:3}. {info['id']:15} | {info['status']:15} | {info['description']}")
        else:
            print_info("No tasks")

        print_success("Execution order retrieved")
        return True

    except Exception as e:
        logger.exception("Error getting task execution order")
        print_error("Error getting task execution order", exception=e)
        return False


def handle_task_clear(args):
    """Handle task clear command."""
    try:
        planner = _get_task_planner()
        if planner is None:
            print_error("Task planner not initialized")
            return False

        # TaskPlanner doesn't have a clear method, so we create a new instance
        global _task_planner
        _task_planner = TaskPlanner()
        
        print_section("Task Planner")
        print_success("All tasks cleared")
        return True

    except Exception as e:
        logger.exception("Error clearing tasks")
        print_error("Error clearing tasks", exception=e)
        return False


# ============================================================================
# Message Bus Handlers
# ============================================================================

def _get_message_bus() -> Optional[Any]:
    """Get or create message bus instance."""
    global _message_bus
    if _message_bus is None and MessageBus is not None:
        try:
            _message_bus = MessageBus()
        except Exception as e:
            logger.error(f"Failed to create message bus: {e}")
            return None
    return _message_bus


def handle_message_subscribe(args):
    """Handle message subscribe command."""
    try:
        if MessageBus is None:
            print_error("Message bus not available", context="Module not imported")
            return False

        bus = _get_message_bus()
        if bus is None:
            print_error("Failed to create message bus")
            return False

        message_type = args.type
        handler_path = getattr(args, "handler", None)

        # Create a simple handler that logs messages
        def message_handler(message):
            print(f"[{message.message_type}] {message.sender}: {message.content}")

        if handler_path:
            # Try to resolve handler from path (simplified - would need proper handler resolution)
            print_warning("Custom handler paths not fully supported, using default handler")

        bus.subscribe(message_type, message_handler)
        
        print_section("Message Subscription")
        print_success(f"Subscribed to message type: {message_type}")
        return True

    except Exception as e:
        logger.exception("Error subscribing to messages")
        print_error("Error subscribing to messages", exception=e)
        return False


def handle_message_publish(args):
    """Handle message publish command."""
    try:
        if MessageBus is None or Message is None:
            print_error("Message bus not available", context="Module not imported")
            return False

        bus = _get_message_bus()
        if bus is None:
            print_error("Failed to create message bus")
            return False

        message_type = args.type
        content = args.content
        sender = getattr(args, "sender", "cli")
        metadata = _parse_context(getattr(args, "metadata", None))

        message = Message(
            sender=sender,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
        )

        bus.publish(message)
        
        print_section("Message Published")
        print_success(f"Published message of type: {message_type}")
        return True

    except Exception as e:
        logger.exception("Error publishing message")
        print_error("Error publishing message", exception=e)
        return False


def handle_message_send(args):
    """Handle message send command."""
    try:
        if MessageBus is None:
            print_error("Message bus not available", context="Module not imported")
            return False

        bus = _get_message_bus()
        if bus is None:
            print_error("Failed to create message bus")
            return False

        sender = args.sender
        recipient = args.recipient
        message_type = args.type
        content = args.content
        metadata = _parse_context(getattr(args, "metadata", None))

        message = bus.send(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            metadata=metadata,
        )
        
        print_section("Message Sent")
        print_success(f"Sent message to {recipient}")
        print_info(f"Message ID: {message.id}")
        return True

    except Exception as e:
        logger.exception("Error sending message")
        print_error("Error sending message", exception=e)
        return False


def handle_message_broadcast(args):
    """Handle message broadcast command."""
    try:
        if MessageBus is None:
            print_error("Message bus not available", context="Module not imported")
            return False

        bus = _get_message_bus()
        if bus is None:
            print_error("Failed to create message bus")
            return False

        sender = args.sender
        message_type = args.type
        content = args.content
        metadata = _parse_context(getattr(args, "metadata", None))

        message = bus.broadcast(
            sender=sender,
            message_type=message_type,
            content=content,
            metadata=metadata,
        )
        
        print_section("Message Broadcast")
        print_success(f"Broadcast message of type: {message_type}")
        print_info(f"Message ID: {message.id}")
        return True

    except Exception as e:
        logger.exception("Error broadcasting message")
        print_error("Error broadcasting message", exception=e)
        return False


def handle_message_history(args):
    """Handle message history command."""
    try:
        bus = _get_message_bus()
        if bus is None:
            print_error("Message bus not initialized")
            return False

        message_type = getattr(args, "type", None)
        limit = getattr(args, "limit", None)
        if limit:
            limit = int(limit)

        messages = bus.get_message_history(message_type=message_type, limit=limit)
        
        print_section("Message History")
        if messages:
            output_format = getattr(args, "format", "text")
            message_info = []
            for msg in messages:
                message_info.append({
                    "id": msg.id,
                    "sender": msg.sender,
                    "recipient": msg.recipient,
                    "type": msg.message_type,
                    "content": str(msg.content)[:100],  # Truncate long content
                    "timestamp": msg.timestamp,
                })

            if output_format == "json":
                print(format_output(message_info, format_type="json"))
            else:
                for info in message_info:
                    recipient_str = info["recipient"] or "broadcast"
                    print(f"{info['id']:36} | {info['sender']:15} -> {recipient_str:15} | {info['type']:20} | {info['content']}")
        else:
            print_info("No messages in history")

        print_success(f"Retrieved {len(messages)} message(s)")
        return True

    except Exception as e:
        logger.exception("Error getting message history")
        print_error("Error getting message history", exception=e)
        return False


# ============================================================================
# Orchestrator Handlers
# ============================================================================

def _get_agent_client(agent_name: str):
    """Get agent client by name."""
    clients = {
        "jules": JulesClient,
        "claude": ClaudeClient,
        "codex": CodexClient,
        "opencode": OpenCodeClient,
        "gemini": GeminiClient,
    }
    return clients.get(agent_name.lower())


def handle_orchestrate_parallel(args):
    """Handle orchestrate parallel command."""
    try:
        if AgentOrchestrator is None:
            print_error("Agent orchestrator not available", context="Module not imported")
            return False

        prompt = args.prompt
        agent_names = getattr(args, "agents", "").split(",") if getattr(args, "agents", None) else []

        if not agent_names:
            print_error("No agents specified", context="Use --agents to specify agents")
            return False

        agents = []
        for name in agent_names:
            name = name.strip()
            client_class = _get_agent_client(name)
            if client_class is None:
                print_warning(f"Unknown agent: {name}")
                continue
            try:
                agents.append(client_class())
            except Exception as e:
                print_warning(f"Failed to initialize {name}: {e}")
                continue

        if not agents:
            print_error("No valid agents available")
            return False

        orchestrator = AgentOrchestrator(agents)
        request = _create_agent_request(prompt, args)
        responses = orchestrator.execute_parallel(request)

        print_section("Parallel Execution Results")
        for i, response in enumerate(responses):
            agent_name = response.metadata.get("agent_name", f"Agent {i+1}")
            print_section(f"{agent_name} Response")
            if response.is_success():
                print(response.content)
                print_success(f"{agent_name} completed successfully")
            else:
                print_error(f"{agent_name} failed", context=response.error)

        print_section("", separator="")
        print_success("Parallel execution completed")
        return True

    except Exception as e:
        logger.exception("Error in parallel orchestration")
        print_error("Error in parallel orchestration", exception=e)
        return False


def handle_orchestrate_sequential(args):
    """Handle orchestrate sequential command."""
    try:
        if AgentOrchestrator is None:
            print_error("Agent orchestrator not available", context="Module not imported")
            return False

        prompt = args.prompt
        agent_names = getattr(args, "agents", "").split(",") if getattr(args, "agents", None) else []

        if not agent_names:
            print_error("No agents specified", context="Use --agents to specify agents")
            return False

        agents = []
        for name in agent_names:
            name = name.strip()
            client_class = _get_agent_client(name)
            if client_class is None:
                print_warning(f"Unknown agent: {name}")
                continue
            try:
                agents.append(client_class())
            except Exception as e:
                print_warning(f"Failed to initialize {name}: {e}")
                continue

        if not agents:
            print_error("No valid agents available")
            return False

        orchestrator = AgentOrchestrator(agents)
        request = _create_agent_request(prompt, args)
        stop_on_success = getattr(args, "stop_on_success", False)
        responses = orchestrator.execute_sequential(request, stop_on_success=stop_on_success)

        print_section("Sequential Execution Results")
        for i, response in enumerate(responses):
            agent_name = response.metadata.get("agent_name", f"Agent {i+1}")
            print_section(f"{agent_name} Response")
            if response.is_success():
                print(response.content)
                print_success(f"{agent_name} completed successfully")
                if stop_on_success:
                    print_info("Stopped after first success")
                    break
            else:
                print_error(f"{agent_name} failed", context=response.error)

        print_section("", separator="")
        print_success("Sequential execution completed")
        return True

    except Exception as e:
        logger.exception("Error in sequential orchestration")
        print_error("Error in sequential orchestration", exception=e)
        return False


def handle_orchestrate_fallback(args):
    """Handle orchestrate fallback command."""
    try:
        if AgentOrchestrator is None:
            print_error("Agent orchestrator not available", context="Module not imported")
            return False

        prompt = args.prompt
        agent_names = getattr(args, "agents", "").split(",") if getattr(args, "agents", None) else []

        if not agent_names:
            print_error("No agents specified", context="Use --agents to specify agents")
            return False

        agents = []
        for name in agent_names:
            name = name.strip()
            client_class = _get_agent_client(name)
            if client_class is None:
                print_warning(f"Unknown agent: {name}")
                continue
            try:
                agents.append(client_class())
            except Exception as e:
                print_warning(f"Failed to initialize {name}: {e}")
                continue

        if not agents:
            print_error("No valid agents available")
            return False

        orchestrator = AgentOrchestrator(agents)
        request = _create_agent_request(prompt, args)
        response = orchestrator.execute_with_fallback(request)

        print_section("Fallback Execution Result")
        if response.is_success():
            print(response.content)
            agent_name = response.metadata.get("agent_name", "Unknown")
            print_success(f"Success with {agent_name}")
        else:
            print_error("All agents failed", context=response.error)

        print_section("", separator="")
        return response.is_success()

    except Exception as e:
        logger.exception("Error in fallback orchestration")
        print_error("Error in fallback orchestration", exception=e)
        return False


def handle_orchestrate_list(args):
    """Handle orchestrate list command."""
    try:
        print_section("Available Agents")
        agents_info = []

        agent_list = [
            ("jules", JulesClient, "Jules CLI integration"),
            ("claude", ClaudeClient, "Claude API integration"),
            ("codex", CodexClient, "OpenAI Codex API integration"),
            ("opencode", OpenCodeClient, "OpenCode CLI integration"),
            ("gemini", GeminiClient, "Gemini CLI integration"),
        ]

        for name, client_class, description in agent_list:
            available = client_class is not None
            try:
                if client_class:
                    # Try to create instance to check if it works
                    test_client = client_class()
                    available = True
            except Exception:
                available = False

            agents_info.append({
                "name": name,
                "available": available,
                "description": description,
            })

        output_format = getattr(args, "format", "text")
        if output_format == "json":
            print(format_output(agents_info, format_type="json"))
        else:
            for agent in agents_info:
                status = "✓" if agent["available"] else "✗"
                print(f"{status} {agent['name']:15} - {agent['description']}")

        print_success("Agent list retrieved")
        return True

    except Exception as e:
        logger.exception("Error listing agents")
        print_error("Error listing agents", exception=e)
        return False


def handle_orchestrate_select(args):
    """Handle orchestrate select command."""
    try:
        if AgentOrchestrator is None:
            print_error("Agent orchestrator not available", context="Module not imported")
            return False

        capability = args.capability
        agent_names = getattr(args, "agents", "").split(",") if getattr(args, "agents", None) else []

        # Build agent list
        agents = []
        if agent_names:
            for name in agent_names:
                name = name.strip()
                client_class = _get_agent_client(name)
                if client_class is None:
                    print_warning(f"Unknown agent: {name}")
                    continue
                try:
                    agents.append(client_class())
                except Exception as e:
                    print_warning(f"Failed to initialize {name}: {e}")
                    continue
        else:
            # Use all available agents
            agent_list = [
                ("jules", JulesClient),
                ("claude", ClaudeClient),
                ("codex", CodexClient),
                ("opencode", OpenCodeClient),
                ("gemini", GeminiClient),
            ]
            for name, client_class in agent_list:
                if client_class is None:
                    continue
                try:
                    agents.append(client_class())
                except Exception:
                    continue

        if not agents:
            print_error("No valid agents available")
            return False

        orchestrator = AgentOrchestrator(agents)
        selected_agents = orchestrator.select_agent_by_capability(capability, agents)

        print_section(f"Agents Supporting Capability: {capability}")
        if selected_agents:
            output_format = getattr(args, "format", "text")
            agent_info = []
            for agent in selected_agents:
                agent_name = getattr(agent, "name", str(agent))
                capabilities = agent.get_capabilities()
                agent_info.append({
                    "name": agent_name,
                    "capabilities": [cap.value for cap in capabilities],
                })

            if output_format == "json":
                print(format_output(agent_info, format_type="json"))
            else:
                for info in agent_info:
                    caps_str = ", ".join(info["capabilities"])
                    print(f"{info['name']:15} - {caps_str}")

            print_success(f"Found {len(selected_agents)} agent(s) supporting {capability}")
        else:
            print_warning(f"No agents found supporting capability: {capability}")
            print_info("Available capabilities:")
            for cap in AgentCapabilities:
                print(f"  - {cap.value}")

        return True

    except Exception as e:
        logger.exception("Error selecting agents by capability")
        print_error("Error selecting agents by capability", exception=e)
        return False


# ============================================================================
# Theory Handlers
# ============================================================================

def handle_theory_info(args):
    """Handle theory info command."""
    try:
        print_section("Theory Module Information")
        info = {
            "module": "theory",
            "description": "Theoretical foundations for agentic systems",
            "components": {
                "architectures": [
                    "ReactiveArchitecture",
                    "DeliberativeArchitecture",
                    "HybridArchitecture",
                ],
                "reasoning_models": [
                    "SymbolicReasoningModel",
                    "NeuralReasoningModel",
                    "HybridReasoningModel",
                ],
            },
        }

        output_format = getattr(args, "format", "text")
        print(format_output(info, format_type=output_format))
        print_success("Theory module information retrieved")
        return True

    except Exception as e:
        logger.exception("Error getting theory info")
        print_error("Error getting theory info", exception=e)
        return False


def handle_theory_architectures(args):
    """Handle theory architectures command."""
    try:
        print_section("Agent Architectures")
        architectures = [
            {
                "name": "ReactiveArchitecture",
                "description": "Simple stimulus-response agents",
                "available": ReactiveArchitecture is not None,
            },
            {
                "name": "DeliberativeArchitecture",
                "description": "Planning-based agents with internal state",
                "available": DeliberativeArchitecture is not None,
            },
            {
                "name": "HybridArchitecture",
                "description": "Combination of reactive and deliberative",
                "available": HybridArchitecture is not None,
            },
        ]

        output_format = getattr(args, "format", "text")
        print(format_output(architectures, format_type=output_format))
        print_success("Architectures listed")
        return True

    except Exception as e:
        logger.exception("Error listing architectures")
        print_error("Error listing architectures", exception=e)
        return False


def handle_theory_reasoning(args):
    """Handle theory reasoning command."""
    try:
        print_section("Reasoning Models")
        models = [
            {
                "name": "SymbolicReasoningModel",
                "description": "Rule-based symbolic reasoning",
                "available": SymbolicReasoningModel is not None,
            },
            {
                "name": "NeuralReasoningModel",
                "description": "Neural network-based reasoning",
                "available": NeuralReasoningModel is not None,
            },
            {
                "name": "HybridReasoningModel",
                "description": "Combination of symbolic and neural reasoning",
                "available": HybridReasoningModel is not None,
            },
        ]

        output_format = getattr(args, "format", "text")
        print(format_output(models, format_type=output_format))
        print_success("Reasoning models listed")
        return True

    except Exception as e:
        logger.exception("Error listing reasoning models")
        print_error("Error listing reasoning models", exception=e)
        return False


# ============================================================================
# Config Management Handlers
# ============================================================================

def handle_config_show(args):
    """Handle config show command."""
    try:
        config = get_config()
        print_section("Agent Configuration")
        output_format = getattr(args, "format", "text")
        print(format_output(config.to_dict(), format_type=output_format))
        print_success("Configuration retrieved")
        return True

    except Exception as e:
        logger.exception("Error getting configuration")
        print_error("Error getting configuration", exception=e)
        return False


def handle_config_set(args):
    """Handle config set command."""
    try:
        from codomyrmex.agents.config import AgentConfig
        
        config = get_config()
        overrides = {}
        
        for kv in getattr(args, "overrides", []):
            if "=" not in kv:
                print_warning(f"Invalid key=value format: {kv}")
                continue
            
            key, value = kv.split("=", 1)
            # Try to convert to appropriate type
            try:
                if value.lower() in ("true", "false"):
                    overrides[key] = value.lower() == "true"
                elif value.isdigit():
                    overrides[key] = int(value)
                else:
                    try:
                        overrides[key] = float(value)
                    except ValueError:
                        overrides[key] = value
            except Exception:
                overrides[key] = value
        
        # Update config attributes directly
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                print_warning(f"Unknown configuration key: {key}")
        
        # Re-initialize to apply environment variables
        # Create new config with current values as defaults, then apply overrides
        config_dict = {}
        for field_name in dir(config):
            if not field_name.startswith('_') and field_name not in ['to_dict', 'validate', '__post_init__']:
                try:
                    config_dict[field_name] = getattr(config, field_name)
                except:
                    pass
        
        # Apply overrides
        config_dict.update(overrides)
        new_config = AgentConfig(**config_dict)
        set_config(new_config)
        
        print_section("Configuration Update")
        print_success("Configuration updated")
        if getattr(args, "verbose", False):
            print_info(f"Updated keys: {', '.join(overrides.keys())}")
        return True

    except Exception as e:
        logger.exception("Error updating configuration")
        print_error("Error updating configuration", exception=e)
        return False


def handle_config_reset(args):
    """Handle config reset command."""
    try:
        reset_config()
        print_section("Configuration Reset")
        print_success("Configuration reset to defaults")
        return True

    except Exception as e:
        logger.exception("Error resetting configuration")
        print_error("Error resetting configuration", exception=e)
        return False


def handle_config_validate(args):
    """Handle config validate command."""
    try:
        config = get_config()
        errors = config.validate()
        
        print_section("Configuration Validation")
        if not errors:
            print_success("Configuration is valid")
            return True
        else:
            print_warning(f"Configuration has {len(errors)} issue(s):")
            for error in errors:
                print_error(error, context="Validation error")
            return False

    except Exception as e:
        logger.exception("Error validating configuration")
        print_error("Error validating configuration", exception=e)
        return False


# ============================================================================
# Main CLI Setup
# ============================================================================

def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Agents operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
  %(prog)s jules execute "Write a Python function"
  %(prog)s claude check
  %(prog)s orchestrate parallel "Analyze code" --agents jules,claude
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    parser.add_argument(
        "--output", "-o", help="Save output to file"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get agents module information")

    # Config subcommands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config commands")
    
    config_subparsers.add_parser("show", help="Show current configuration")
    config_reset = config_subparsers.add_parser("reset", help="Reset configuration to defaults")
    config_validate = config_subparsers.add_parser("validate", help="Validate configuration")
    config_set = config_subparsers.add_parser("set", help="Set configuration values")
    config_set.add_argument("overrides", nargs="+", help="Key=value pairs")

    # Jules subcommands
    jules_parser = subparsers.add_parser("jules", help="Jules agent operations")
    jules_subparsers = jules_parser.add_subparsers(dest="jules_command", help="Jules commands")
    
    jules_execute = jules_subparsers.add_parser("execute", help="Execute prompt with Jules")
    jules_execute.add_argument("prompt", help="Prompt to execute")
    jules_execute.add_argument("--timeout", type=int, help="Timeout in seconds")
    jules_execute.add_argument("--context", help="Additional context as JSON")
    
    jules_stream = jules_subparsers.add_parser("stream", help="Stream response from Jules")
    jules_stream.add_argument("prompt", help="Prompt to execute")
    jules_stream.add_argument("--timeout", type=int, help="Timeout in seconds")
    jules_stream.add_argument("--context", help="Additional context as JSON")
    
    jules_check = jules_subparsers.add_parser("check", help="Check Jules availability")
    jules_help = jules_subparsers.add_parser("help", help="Get Jules help")
    jules_cmd = jules_subparsers.add_parser("command", help="Execute Jules command")
    jules_cmd.add_argument("cmd", help="Jules command name")
    jules_cmd.add_argument("args", nargs="*", help="Command arguments")

    # Claude subcommands
    claude_parser = subparsers.add_parser("claude", help="Claude agent operations")
    claude_subparsers = claude_parser.add_subparsers(dest="claude_command", help="Claude commands")
    
    claude_execute = claude_subparsers.add_parser("execute", help="Execute prompt with Claude")
    claude_execute.add_argument("prompt", help="Prompt to execute")
    claude_execute.add_argument("--timeout", type=int, help="Timeout in seconds")
    claude_execute.add_argument("--context", help="Additional context as JSON")
    
    claude_stream = claude_subparsers.add_parser("stream", help="Stream response from Claude")
    claude_stream.add_argument("prompt", help="Prompt to execute")
    claude_stream.add_argument("--timeout", type=int, help="Timeout in seconds")
    claude_stream.add_argument("--context", help="Additional context as JSON")
    
    claude_check = claude_subparsers.add_parser("check", help="Check Claude configuration")

    # Codex subcommands
    codex_parser = subparsers.add_parser("codex", help="Codex agent operations")
    codex_subparsers = codex_parser.add_subparsers(dest="codex_command", help="Codex commands")
    
    codex_execute = codex_subparsers.add_parser("execute", help="Execute prompt with Codex")
    codex_execute.add_argument("prompt", help="Prompt to execute")
    codex_execute.add_argument("--timeout", type=int, help="Timeout in seconds")
    codex_execute.add_argument("--context", help="Additional context as JSON")
    
    codex_stream = codex_subparsers.add_parser("stream", help="Stream response from Codex")
    codex_stream.add_argument("prompt", help="Prompt to execute")
    codex_stream.add_argument("--timeout", type=int, help="Timeout in seconds")
    codex_stream.add_argument("--context", help="Additional context as JSON")
    
    codex_check = codex_subparsers.add_parser("check", help="Check Codex configuration")

    # OpenCode subcommands
    opencode_parser = subparsers.add_parser("opencode", help="OpenCode agent operations")
    opencode_subparsers = opencode_parser.add_subparsers(dest="opencode_command", help="OpenCode commands")
    
    opencode_execute = opencode_subparsers.add_parser("execute", help="Execute prompt with OpenCode")
    opencode_execute.add_argument("prompt", help="Prompt to execute")
    opencode_execute.add_argument("--timeout", type=int, help="Timeout in seconds")
    opencode_execute.add_argument("--context", help="Additional context as JSON")
    
    opencode_stream = opencode_subparsers.add_parser("stream", help="Stream response from OpenCode")
    opencode_stream.add_argument("prompt", help="Prompt to execute")
    opencode_stream.add_argument("--timeout", type=int, help="Timeout in seconds")
    opencode_stream.add_argument("--context", help="Additional context as JSON")
    
    opencode_check = opencode_subparsers.add_parser("check", help="Check OpenCode availability")
    opencode_init = opencode_subparsers.add_parser("init", help="Initialize OpenCode for project")
    opencode_init.add_argument("--path", help="Project path (default: current directory")
    opencode_version = opencode_subparsers.add_parser("version", help="Get OpenCode version")

    # Gemini subcommands
    gemini_parser = subparsers.add_parser("gemini", help="Gemini agent operations")
    gemini_subparsers = gemini_parser.add_subparsers(dest="gemini_command", help="Gemini commands")
    
    gemini_execute = gemini_subparsers.add_parser("execute", help="Execute prompt with Gemini")
    gemini_execute.add_argument("prompt", help="Prompt to execute")
    gemini_execute.add_argument("--timeout", type=int, help="Timeout in seconds")
    gemini_execute.add_argument("--context", help="Additional context as JSON")
    
    gemini_stream = gemini_subparsers.add_parser("stream", help="Stream response from Gemini")
    gemini_stream.add_argument("prompt", help="Prompt to execute")
    gemini_stream.add_argument("--timeout", type=int, help="Timeout in seconds")
    gemini_stream.add_argument("--context", help="Additional context as JSON")
    
    gemini_check = gemini_subparsers.add_parser("check", help="Check Gemini availability")
    
    gemini_chat = gemini_subparsers.add_parser("chat", help="Gemini chat operations")
    gemini_chat_subparsers = gemini_chat.add_subparsers(dest="chat_command", help="Chat commands")
    gemini_chat_save = gemini_chat_subparsers.add_parser("save", help="Save chat session")
    gemini_chat_save.add_argument("tag", help="Chat session tag")
    gemini_chat_save.add_argument("--prompt", help="Optional prompt to save")
    gemini_chat_resume = gemini_chat_subparsers.add_parser("resume", help="Resume chat session")
    gemini_chat_resume.add_argument("tag", help="Chat session tag")
    gemini_chat_list = gemini_chat_subparsers.add_parser("list", help="List chat sessions")

    # Droid subcommands
    droid_parser = subparsers.add_parser("droid", help="Droid controller operations")
    droid_subparsers = droid_parser.add_subparsers(dest="droid_command", help="Droid commands")
    
    droid_subparsers.add_parser("start", help="Start droid controller")
    droid_subparsers.add_parser("stop", help="Stop droid controller")
    droid_subparsers.add_parser("status", help="Get droid status")
    
    droid_config = droid_subparsers.add_parser("config", help="Droid configuration")
    droid_config_subparsers = droid_config.add_subparsers(dest="config_command", help="Config commands")
    droid_config_subparsers.add_parser("show", help="Show configuration")
    droid_config_set = droid_config_subparsers.add_parser("set", help="Set configuration")
    droid_config_set.add_argument("overrides", nargs="+", help="Key=value pairs")
    droid_config_save = droid_config_subparsers.add_parser("save", help="Save configuration to file")
    droid_config_save.add_argument("file", help="Output file path")
    droid_config_load = droid_config_subparsers.add_parser("load", help="Load configuration from file")
    droid_config_load.add_argument("file", help="Input file path")
    
    droid_execute_task = droid_subparsers.add_parser("execute-task", help="Execute a specific task")
    droid_execute_task.add_argument("operation_id", help="Operation ID")
    droid_execute_task.add_argument("--handler", help="Handler path (optional)")
    
    droid_todo = droid_subparsers.add_parser("todo", help="TODO list management")
    droid_todo_subparsers = droid_todo.add_subparsers(dest="todo_command", help="TODO commands")
    droid_todo_load = droid_todo_subparsers.add_parser("load", help="Load TODO list")
    droid_todo_load.add_argument("--file", default="todo_list.txt", help="TODO file path")
    droid_todo_save = droid_todo_subparsers.add_parser("save", help="Save TODO list")
    droid_todo_save.add_argument("--file", default="todo_list.txt", help="TODO file path")
    droid_todo_validate = droid_todo_subparsers.add_parser("validate", help="Validate TODO file")
    droid_todo_validate.add_argument("--file", default="todo_list.txt", help="TODO file path")
    droid_todo_migrate = droid_todo_subparsers.add_parser("migrate", help="Migrate TODO file to 3-column format")
    droid_todo_migrate.add_argument("--file", default="todo_list.txt", help="TODO file path")
    droid_todo_list = droid_todo_subparsers.add_parser("list", help="List TODO items")
    droid_todo_list.add_argument("--file", default="todo_list.txt", help="TODO file path")
    
    droid_metrics = droid_subparsers.add_parser("metrics", help="Droid metrics")
    droid_metrics_subparsers = droid_metrics.add_subparsers(dest="metrics_command", help="Metrics commands")
    droid_metrics_subparsers.add_parser("show", help="Show metrics")
    droid_metrics_subparsers.add_parser("reset", help="Reset metrics")

    # Orchestrator subcommands
    orchestrate_parser = subparsers.add_parser("orchestrate", help="Multi-agent orchestration")
    orchestrate_subparsers = orchestrate_parser.add_subparsers(dest="orchestrate_command", help="Orchestration commands")
    
    orchestrate_parallel = orchestrate_subparsers.add_parser("parallel", help="Execute on multiple agents in parallel")
    orchestrate_parallel.add_argument("prompt", help="Prompt to execute")
    orchestrate_parallel.add_argument("--agents", required=True, help="Comma-separated list of agents")
    orchestrate_parallel.add_argument("--timeout", type=int, help="Timeout in seconds")
    orchestrate_parallel.add_argument("--context", help="Additional context as JSON")
    
    orchestrate_sequential = orchestrate_subparsers.add_parser("sequential", help="Execute on multiple agents sequentially")
    orchestrate_sequential.add_argument("prompt", help="Prompt to execute")
    orchestrate_sequential.add_argument("--agents", required=True, help="Comma-separated list of agents")
    orchestrate_sequential.add_argument("--stop-on-success", action="store_true", help="Stop after first success")
    orchestrate_sequential.add_argument("--timeout", type=int, help="Timeout in seconds")
    orchestrate_sequential.add_argument("--context", help="Additional context as JSON")
    
    orchestrate_fallback = orchestrate_subparsers.add_parser("fallback", help="Execute with fallback strategy")
    orchestrate_fallback.add_argument("prompt", help="Prompt to execute")
    orchestrate_fallback.add_argument("--agents", required=True, help="Comma-separated list of agents")
    orchestrate_fallback.add_argument("--timeout", type=int, help="Timeout in seconds")
    orchestrate_fallback.add_argument("--context", help="Additional context as JSON")
    
    orchestrate_subparsers.add_parser("list", help="List available agents")
    
    orchestrate_select = orchestrate_subparsers.add_parser("select", help="Select agents by capability")
    orchestrate_select.add_argument("--capability", required=True, help="Capability to filter by")
    orchestrate_select.add_argument("--agents", help="Comma-separated list of agents to check (default: all)")

    # Theory subcommands
    theory_parser = subparsers.add_parser("theory", help="Theory module operations")
    theory_subparsers = theory_parser.add_subparsers(dest="theory_command", help="Theory commands")
    theory_subparsers.add_parser("info", help="Show theory module information")
    theory_subparsers.add_parser("architectures", help="List agent architectures")
    theory_subparsers.add_parser("reasoning", help="Show reasoning models")

    # Task Planner subcommands
    task_parser = subparsers.add_parser("task", help="Task planning operations")
    task_subparsers = task_parser.add_subparsers(dest="task_command", help="Task commands")
    
    task_create = task_subparsers.add_parser("create", help="Create a new task")
    task_create.add_argument("description", help="Task description")
    task_create.add_argument("--dependencies", help="Comma-separated list of task IDs")
    task_create.add_argument("--metadata", help="Task metadata as JSON")
    
    task_subparsers.add_parser("list", help="List all tasks")
    
    task_get = task_subparsers.add_parser("get", help="Get task details")
    task_get.add_argument("id", help="Task ID")
    
    task_update = task_subparsers.add_parser("update", help="Update task status")
    task_update.add_argument("id", help="Task ID")
    task_update.add_argument("--status", choices=["pending", "in_progress", "completed", "failed", "cancelled"], help="New status")
    task_update.add_argument("--result", help="Task result")
    task_update.add_argument("--error", help="Error message")
    
    task_subparsers.add_parser("ready", help="Get ready tasks")
    task_subparsers.add_parser("order", help="Get task execution order")
    task_subparsers.add_parser("clear", help="Clear all tasks")

    # Message Bus subcommands
    message_parser = subparsers.add_parser("message", help="Message bus operations")
    message_subparsers = message_parser.add_subparsers(dest="message_command", help="Message commands")
    
    message_subscribe = message_subparsers.add_parser("subscribe", help="Subscribe to message type")
    message_subscribe.add_argument("type", help="Message type")
    message_subscribe.add_argument("--handler", help="Handler path (optional, uses default)")
    
    message_publish = message_subparsers.add_parser("publish", help="Publish a message")
    message_publish.add_argument("type", help="Message type")
    message_publish.add_argument("content", help="Message content")
    message_publish.add_argument("--sender", default="cli", help="Sender name")
    message_publish.add_argument("--metadata", help="Metadata as JSON")
    
    message_send = message_subparsers.add_parser("send", help="Send message to recipient")
    message_send.add_argument("sender", help="Sender name")
    message_send.add_argument("recipient", help="Recipient name")
    message_send.add_argument("type", help="Message type")
    message_send.add_argument("content", help="Message content")
    message_send.add_argument("--metadata", help="Metadata as JSON")
    
    message_broadcast = message_subparsers.add_parser("broadcast", help="Broadcast message")
    message_broadcast.add_argument("sender", help="Sender name")
    message_broadcast.add_argument("type", help="Message type")
    message_broadcast.add_argument("content", help="Message content")
    message_broadcast.add_argument("--metadata", help="Metadata as JSON")
    
    message_history = message_subparsers.add_parser("history", help="Get message history")
    message_history.add_argument("--type", help="Filter by message type")
    message_history.add_argument("--limit", type=int, help="Limit number of messages")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "info": handle_info,
    }

    # Config handlers
    if args.command == "config" and hasattr(args, "config_command"):
        handlers = {
            "show": handle_config_show,
            "set": handle_config_set,
            "reset": handle_config_reset,
            "validate": handle_config_validate,
        }
        handler = handlers.get(args.config_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Jules handlers
    if args.command == "jules" and hasattr(args, "jules_command"):
        handlers = {
            "execute": handle_jules_execute,
            "stream": handle_jules_stream,
            "check": handle_jules_check,
            "help": handle_jules_help,
            "command": handle_jules_command,
        }
        handler = handlers.get(args.jules_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Claude handlers
    if args.command == "claude" and hasattr(args, "claude_command"):
        handlers = {
            "execute": handle_claude_execute,
            "stream": handle_claude_stream,
            "check": handle_claude_check,
        }
        handler = handlers.get(args.claude_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Codex handlers
    if args.command == "codex" and hasattr(args, "codex_command"):
        handlers = {
            "execute": handle_codex_execute,
            "stream": handle_codex_stream,
            "check": handle_codex_check,
        }
        handler = handlers.get(args.codex_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # OpenCode handlers
    if args.command == "opencode" and hasattr(args, "opencode_command"):
        handlers = {
            "execute": handle_opencode_execute,
            "stream": handle_opencode_stream,
            "check": handle_opencode_check,
            "init": handle_opencode_init,
            "version": handle_opencode_version,
        }
        handler = handlers.get(args.opencode_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Gemini handlers
    if args.command == "gemini" and hasattr(args, "gemini_command"):
        if args.gemini_command == "chat" and hasattr(args, "chat_command"):
            handlers = {
                "save": handle_gemini_chat_save,
                "resume": handle_gemini_chat_resume,
                "list": handle_gemini_chat_list,
            }
            handler = handlers.get(args.chat_command)
            if handler:
                success = handler(args)
                return 0 if success else 1
        else:
            handlers = {
                "execute": handle_gemini_execute,
                "stream": handle_gemini_stream,
                "check": handle_gemini_check,
            }
            handler = handlers.get(args.gemini_command)
            if handler:
                success = handler(args)
                return 0 if success else 1

    # Droid handlers
    if args.command == "droid" and hasattr(args, "droid_command"):
        if args.droid_command == "config" and hasattr(args, "config_command"):
            handlers = {
                "show": handle_droid_config_show,
                "set": handle_droid_config_set,
                "save": handle_droid_config_save,
                "load": handle_droid_config_load,
            }
            handler = handlers.get(args.config_command)
            if handler:
                success = handler(args)
                return 0 if success else 1
        elif args.droid_command == "todo" and hasattr(args, "todo_command"):
            handlers = {
                "load": handle_droid_todo_load,
                "save": handle_droid_todo_save,
                "validate": handle_droid_todo_validate,
                "migrate": handle_droid_todo_migrate,
                "list": handle_droid_todo_list,
            }
            handler = handlers.get(args.todo_command)
            if handler:
                success = handler(args)
                return 0 if success else 1
        elif args.droid_command == "metrics" and hasattr(args, "metrics_command"):
            handlers = {
                "show": handle_droid_metrics,
                "reset": handle_droid_metrics_reset,
            }
            handler = handlers.get(args.metrics_command)
            if handler:
                success = handler(args)
                return 0 if success else 1
        else:
            handlers = {
                "start": handle_droid_start,
                "stop": handle_droid_stop,
                "status": handle_droid_status,
                "execute-task": handle_droid_execute_task,
            }
            handler = handlers.get(args.droid_command)
            if handler:
                success = handler(args)
                return 0 if success else 1

    # Orchestrator handlers
    if args.command == "orchestrate" and hasattr(args, "orchestrate_command"):
        handlers = {
            "parallel": handle_orchestrate_parallel,
            "sequential": handle_orchestrate_sequential,
            "fallback": handle_orchestrate_fallback,
            "list": handle_orchestrate_list,
            "select": handle_orchestrate_select,
        }
        handler = handlers.get(args.orchestrate_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Theory handlers
    if args.command == "theory" and hasattr(args, "theory_command"):
        handlers = {
            "info": handle_theory_info,
            "architectures": handle_theory_architectures,
            "reasoning": handle_theory_reasoning,
        }
        handler = handlers.get(args.theory_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Task handlers
    if args.command == "task" and hasattr(args, "task_command"):
        handlers = {
            "create": handle_task_create,
            "list": handle_task_list,
            "get": handle_task_get,
            "update": handle_task_update,
            "ready": handle_task_ready,
            "order": handle_task_order,
            "clear": handle_task_clear,
        }
        handler = handlers.get(args.task_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Message handlers
    if args.command == "message" and hasattr(args, "message_command"):
        handlers = {
            "subscribe": handle_message_subscribe,
            "publish": handle_message_publish,
            "send": handle_message_send,
            "broadcast": handle_message_broadcast,
            "history": handle_message_history,
        }
        handler = handlers.get(args.message_command)
        if handler:
            success = handler(args)
            return 0 if success else 1

    # Default handler
    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())

