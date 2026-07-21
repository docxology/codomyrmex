"""Security contract tests for the MCP launcher defaults."""

from __future__ import annotations

import sys

from tests.support.repo_paths import REPO_ROOT

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.model_context_protocol.run_mcp_server import (
    build_parser,
    resolve_profile,
)


def test_http_launcher_defaults_to_loopback_and_readonly() -> None:
    args = build_parser().parse_args(["--transport", "http"])

    assert args.host == "127.0.0.1"
    assert resolve_profile(args.transport, args.profile) == "readonly"


def test_stdio_launcher_keeps_full_profile_for_local_clients() -> None:
    args = build_parser().parse_args(["--transport", "stdio"])

    assert resolve_profile(args.transport, args.profile) == "full"


def test_launcher_requires_explicit_profile_to_expose_full_http_tools() -> None:
    args = build_parser().parse_args(["--transport", "http", "--profile", "full"])

    assert resolve_profile(args.transport, args.profile) == "full"
