"""Relay CLI — command-line interface for the inter-agent relay.

Provides subcommands for managing relay channels and sending messages
between agent sessions.

Usage::

    # Start Claude Code endpoint
    codomyrmex relay start --channel collab-1 --model claude-sonnet-4-20250514

    # Send a message (from scripts or another terminal)
    codomyrmex relay send --channel collab-1 "Analyze the config module"

    # View history
    codomyrmex relay history --channel collab-1 --limit 20

    # List channels
    codomyrmex relay list

    # Stop endpoint
    codomyrmex relay stop --channel collab-1
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from typing import Any

from codomyrmex.ide.antigravity.agent_relay import AgentRelay


def cmd_start(args: argparse.Namespace) -> None:
    """Start a Claude Code endpoint on a relay channel."""
    from codomyrmex.ide.antigravity.live_bridge import ClaudeCodeEndpoint

    endpoint = ClaudeCodeEndpoint(
        args.channel,
        poll_interval=args.poll,
        model=args.model,
        auto_respond=not args.no_auto,
    )

    # Graceful shutdown
    def _shutdown(sig: int, frame: Any) -> None:
        """shutdown ."""
        print("\nShutting down...")
        endpoint.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    print(f"Starting Claude Code endpoint on channel: {args.channel}")
    print(f"  Model: {args.model or 'default'}")
    print(f"  Poll interval: {args.poll}s")
    print(f"  Auto-respond: {not args.no_auto}")
    print("Press Ctrl+C to stop.\n")

    endpoint.start()

    # Keep main thread alive
    try:
        while endpoint.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        endpoint.stop()


def cmd_send(args: argparse.Namespace) -> None:
    """Send a message to a relay channel."""
    relay = AgentRelay(args.channel)
    sender = args.sender or "cli"
    msg = relay.post_message(sender, args.message)
    print(f"Sent [{msg.id[:8]}] from {sender}: {args.message}")


def cmd_history(args: argparse.Namespace) -> None:
    """Display message history for a channel."""
    relay = AgentRelay(args.channel)
    messages = relay.get_history(limit=args.limit)

    if not messages:
        print(f"No messages in channel: {args.channel}")
        return

    for msg in messages:
        ts = msg.timestamp[:19]  # trim microseconds
        prefix = f"[{ts}] {msg.sender}"

        if msg.msg_type == "chat":
            print(f"{prefix}: {msg.content}")
        elif msg.msg_type == "tool_request":
            print(f"{prefix}: 🔧 {msg.tool_name}({json.dumps(msg.tool_args)})")
        elif msg.msg_type == "tool_result":
            status = "❌" if msg.metadata.get("error") else "✅"
            print(f"{prefix}: {status} result for {msg.request_id[:8]}: {msg.content[:100]}")
        elif msg.msg_type == "system":
            print(f"  ⚙️  {msg.content}")


def cmd_list(args: argparse.Namespace) -> None:
    """List all relay channels."""
    channels = AgentRelay.list_channels()
    if not channels:
        print("No relay channels found.")
        return

    print(f"{'Channel':<30} {'Messages':>10}")
    print("-" * 42)
    for ch_id in channels:
        relay = AgentRelay(ch_id)
        stats = relay.get_stats()
        print(f"{ch_id:<30} {stats['total_messages']:>10}")


def cmd_stats(args: argparse.Namespace) -> None:
    """Show channel statistics."""
    relay = AgentRelay(args.channel)
    stats = relay.get_stats()
    print(json.dumps(stats, indent=2))


def cmd_clear(args: argparse.Namespace) -> None:
    """Clear all messages in a channel."""
    relay = AgentRelay(args.channel)
    relay.clear()
    print(f"Cleared channel: {args.channel}")


def cmd_stop(args: argparse.Namespace) -> None:
    """Post a stop system message (signals endpoint to shut down)."""
    relay = AgentRelay(args.channel)
    relay.post_system("STOP requested via CLI")
    print(f"Stop signal sent to channel: {args.channel}")


def build_parser() -> argparse.ArgumentParser:
    """Build the relay CLI argument parser.

    Returns:
        Configured ``ArgumentParser``.
    """
    parser = argparse.ArgumentParser(
        prog="codomyrmex-relay",
        description="Inter-agent relay for Antigravity ↔ Claude Code chat",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="Start Claude Code endpoint")
    p_start.add_argument("--channel", "-c", required=True, help="Channel ID")
    p_start.add_argument("--poll", type=float, default=2.0, help="Poll interval (seconds)")
    p_start.add_argument("--model", "-m", default=None, help="Claude model")
    p_start.add_argument("--no-auto", action="store_true", help="Disable auto-respond")
    p_start.set_defaults(func=cmd_start)

    # send
    p_send = sub.add_parser("send", help="Send a message")
    p_send.add_argument("--channel", "-c", required=True, help="Channel ID")
    p_send.add_argument("--sender", "-s", default=None, help="Sender identity")
    p_send.add_argument("message", help="Message text")
    p_send.set_defaults(func=cmd_send)

    # history
    p_hist = sub.add_parser("history", help="View message history")
    p_hist.add_argument("--channel", "-c", required=True, help="Channel ID")
    p_hist.add_argument("--limit", "-n", type=int, default=20, help="Max messages")
    p_hist.set_defaults(func=cmd_history)

    # list
    p_list = sub.add_parser("list", help="List channels")
    p_list.set_defaults(func=cmd_list)

    # stats
    p_stats = sub.add_parser("stats", help="Channel statistics")
    p_stats.add_argument("--channel", "-c", required=True, help="Channel ID")
    p_stats.set_defaults(func=cmd_stats)

    # clear
    p_clear = sub.add_parser("clear", help="Clear channel messages")
    p_clear.add_argument("--channel", "-c", required=True, help="Channel ID")
    p_clear.set_defaults(func=cmd_clear)

    # stop
    p_stop = sub.add_parser("stop", help="Signal endpoint to stop")
    p_stop.add_argument("--channel", "-c", required=True, help="Channel ID")
    p_stop.set_defaults(func=cmd_stop)

    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
