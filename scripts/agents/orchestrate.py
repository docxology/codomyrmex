#!/usr/bin/env python3
"""
Title: Agents Module CLI
Agents Module Orchestrator

Thin orchestrator script providing CLI access to agents module functionality.
Calls actual module functions from codomyrmex.agents.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger
from codomyrmex.utils.cli_helpers import print_error

# Import handlers
try:
    from codomyrmex.agents.cli_handlers import (
        handle_info,
        handle_jules_execute,
        handle_jules_stream,
        handle_jules_check,
        handle_jules_help,
        handle_jules_command,
        handle_claude_execute,
        handle_claude_stream,
        handle_claude_check,
        handle_codex_execute,
        handle_codex_stream,
        handle_codex_check,
        handle_opencode_execute,
        handle_opencode_stream,
        handle_opencode_check,
        handle_opencode_init,
        handle_opencode_version,
        handle_gemini_execute,
        handle_gemini_stream,
        handle_gemini_check,
        handle_gemini_chat_save,
        handle_gemini_chat_resume,
        handle_gemini_chat_list,
        handle_droid_start,
        handle_droid_stop,
        handle_droid_status,
        handle_droid_config_show,
    )
except ImportError as e:
    # Handle case where package is not installed in environment
    print(f"Error importing codomyrmex modules: {e}")
    sys.exit(1)

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Agents Module Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--format", "-f", choices=["text", "json", "yaml"], default="text", help="Output format"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Show agents module information")

    # Jules commands
    jules_parser = subparsers.add_parser("jules", help="Jules agent operations")
    jules_subs = jules_parser.add_subparsers(dest="subcommand", help="Jules subcommands")
    
    jules_exec = jules_subs.add_parser("execute", help="Execute Jules request")
    jules_exec.add_argument("prompt", help="Prompt text")
    jules_exec.add_argument("--context", "-c", help="Context JSON")
    jules_exec.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    jules_exec.add_argument("--output", "-o", help="Output file path")

    jules_stream = jules_subs.add_parser("stream", help="Stream Jules capabilities")
    jules_stream.add_argument("prompt", help="Prompt text")
    jules_stream.add_argument("--context", "-c", help="Context JSON")
    jules_stream.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    jules_stream.add_argument("--output", "-o", help="Output file path")

    jules_subs.add_parser("check", help="Check Jules availability")
    jules_subs.add_parser("help", help="Show Jules help")
    
    jules_cmd = jules_subs.add_parser("command", help="Run raw Jules command")
    jules_cmd.add_argument("cmd", help="Command to run")
    jules_cmd.add_argument("args", nargs="*", help="Command arguments")

    # Claude commands
    claude_parser = subparsers.add_parser("claude", help="Claude agent operations")
    claude_subs = claude_parser.add_subparsers(dest="subcommand", help="Claude subcommands")
    
    claude_exec = claude_subs.add_parser("execute", help="Execute Claude request")
    claude_exec.add_argument("prompt", help="Prompt text")
    claude_exec.add_argument("--context", "-c", help="Context JSON")
    claude_exec.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    claude_exec.add_argument("--output", "-o", help="Output file path")

    claude_stream = claude_subs.add_parser("stream", help="Stream Claude response")
    claude_stream.add_argument("prompt", help="Prompt text")
    claude_stream.add_argument("--context", "-c", help="Context JSON")
    claude_stream.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    claude_stream.add_argument("--output", "-o", help="Output file path")

    claude_subs.add_parser("check", help="Check Claude configuration")

    # Codex commands
    codex_parser = subparsers.add_parser("codex", help="Codex agent operations")
    codex_subs = codex_parser.add_subparsers(dest="subcommand", help="Codex subcommands")
    
    codex_exec = codex_subs.add_parser("execute", help="Execute Codex request")
    codex_exec.add_argument("prompt", help="Prompt text")
    codex_exec.add_argument("--context", "-c", help="Context JSON")
    codex_exec.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    codex_exec.add_argument("--output", "-o", help="Output file path")

    codex_stream = codex_subs.add_parser("stream", help="Stream Codex response")
    codex_stream.add_argument("prompt", help="Prompt text")
    codex_stream.add_argument("--context", "-c", help="Context JSON")
    codex_stream.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    codex_stream.add_argument("--output", "-o", help="Output file path")

    codex_subs.add_parser("check", help="Check Codex configuration")

    # OpenCode commands
    opencode_parser = subparsers.add_parser("opencode", help="OpenCode agent operations")
    opencode_subs = opencode_parser.add_subparsers(dest="subcommand", help="OpenCode subcommands")
    
    opencode_exec = opencode_subs.add_parser("execute", help="Execute OpenCode request")
    opencode_exec.add_argument("prompt", help="Prompt text")
    opencode_exec.add_argument("--context", "-c", help="Context JSON")
    opencode_exec.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    opencode_exec.add_argument("--output", "-o", help="Output file path")

    opencode_stream = opencode_subs.add_parser("stream", help="Stream OpenCode response")
    opencode_stream.add_argument("prompt", help="Prompt text")
    opencode_stream.add_argument("--context", "-c", help="Context JSON")
    opencode_stream.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    opencode_stream.add_argument("--output", "-o", help="Output file path")

    opencode_subs.add_parser("check", help="Check OpenCode availability")
    
    opencode_init = opencode_subs.add_parser("init", help="Initialize OpenCode project")
    opencode_init.add_argument("--path", "-p", help="Project path")
    
    opencode_subs.add_parser("version", help="Get OpenCode version")

    # Gemini commands
    gemini_parser = subparsers.add_parser("gemini", help="Gemini agent operations")
    gemini_subs = gemini_parser.add_subparsers(dest="subcommand", help="Gemini subcommands")
    
    gemini_exec = gemini_subs.add_parser("execute", help="Execute Gemini request")
    gemini_exec.add_argument("prompt", help="Prompt text")
    gemini_exec.add_argument("--context", "-c", help="Context JSON")
    gemini_exec.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    gemini_exec.add_argument("--output", "-o", help="Output file path")

    gemini_stream = gemini_subs.add_parser("stream", help="Stream Gemini response")
    gemini_stream.add_argument("prompt", help="Prompt text")
    gemini_stream.add_argument("--context", "-c", help="Context JSON")
    gemini_stream.add_argument("--timeout", "-t", type=int, help="Timeout seconds")
    gemini_stream.add_argument("--output", "-o", help="Output file path")

    gemini_subs.add_parser("check", help="Check Gemini availability")
    
    gemini_save = gemini_subs.add_parser("save-chat", help="Save chat session")
    gemini_save.add_argument("tag", help="Session tag")
    gemini_save.add_argument("--prompt", "-p", help="Initial prompt")
    
    gemini_resume = gemini_subs.add_parser("resume-chat", help="Resume chat session")
    gemini_resume.add_argument("tag", help="Session tag")
    
    gemini_subs.add_parser("list-chats", help="List chat sessions")

    # Droid commands
    droid_parser = subparsers.add_parser("droid", help="Droid autonomous agent operations")
    droid_subs = droid_parser.add_subparsers(dest="subcommand", help="Droid subcommands")
    
    droid_subs.add_parser("start", help="Start droid controller")
    droid_subs.add_parser("stop", help="Stop droid controller")
    droid_subs.add_parser("status", help="Get droid status")
    droid_subs.add_parser("config", help="Show droid configuration")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    if args.command == "info":
        return 0 if handle_info(args) else 1
    
    elif args.command == "jules":
        if not args.subcommand:
            jules_parser.print_help()
            return 1
        handlers = {
            "execute": handle_jules_execute,
            "stream": handle_jules_stream,
            "check": handle_jules_check,
            "help": handle_jules_help,
            "command": handle_jules_command,
        }
        handler = handlers.get(args.subcommand)
        return 0 if handler and handler(args) else 1

    elif args.command == "claude":
        if not args.subcommand:
            claude_parser.print_help()
            return 1
        handlers = {
            "execute": handle_claude_execute,
            "stream": handle_claude_stream,
            "check": handle_claude_check,
        }
        handler = handlers.get(args.subcommand)
        return 0 if handler and handler(args) else 1

    elif args.command == "codex":
        if not args.subcommand:
            codex_parser.print_help()
            return 1
        handlers = {
            "execute": handle_codex_execute,
            "stream": handle_codex_stream,
            "check": handle_codex_check,
        }
        handler = handlers.get(args.subcommand)
        return 0 if handler and handler(args) else 1

    elif args.command == "opencode":
        if not args.subcommand:
            opencode_parser.print_help()
            return 1
        handlers = {
            "execute": handle_opencode_execute,
            "stream": handle_opencode_stream,
            "check": handle_opencode_check,
            "init": handle_opencode_init,
            "version": handle_opencode_version,
        }
        handler = handlers.get(args.subcommand)
        return 0 if handler and handler(args) else 1

    elif args.command == "gemini":
        if not args.subcommand:
            gemini_parser.print_help()
            return 1
        handlers = {
            "execute": handle_gemini_execute,
            "stream": handle_gemini_stream,
            "check": handle_gemini_check,
            "save-chat": handle_gemini_chat_save,
            "resume-chat": handle_gemini_chat_resume,
            "list-chats": handle_gemini_chat_list,
        }
        handler = handlers.get(args.subcommand)
        return 0 if handler and handler(args) else 1

    elif args.command == "droid":
        if not args.subcommand:
            droid_parser.print_help()
            return 1
        handlers = {
            "start": handle_droid_start,
            "stop": handle_droid_stop,
            "status": handle_droid_status,
            "config": handle_droid_config_show,
        }
        handler = handlers.get(args.subcommand)
        return 0 if handler and handler(args) else 1

    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())
