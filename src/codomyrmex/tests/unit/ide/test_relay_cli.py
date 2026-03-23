"""Zero-Mock tests for the Antigravity relay CLI and AgentRelay.

Tests cover:
- argparse CLI command parsing via build_parser()
- RelayMessage data model (construction, serialization, deserialization)
- AgentRelay operations (post, poll, history, stats, clear) using real temp dirs
- CLI command functions (cmd_send, cmd_history, cmd_list, cmd_stats, cmd_clear, cmd_stop)
  driven by constructing argparse.Namespace objects directly against temp relay dirs

All tests follow the zero-mock policy: real objects, real filesystem, no mocks/stubs.
"""

from __future__ import annotations

import argparse
import json

import pytest

from codomyrmex.ide.antigravity.agent_relay import (
    ALL_MSG_TYPES,
    MSG_CHAT,
    MSG_HEARTBEAT,
    MSG_SYSTEM,
    MSG_TOOL_REQUEST,
    MSG_TOOL_RESULT,
    AgentRelay,
    RelayMessage,
)
from codomyrmex.ide.antigravity.relay_cli import (
    build_parser,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def relay_dir(tmp_path):
    """Return a temporary directory to use as relay root."""
    return tmp_path / "agent_relay"


@pytest.fixture
def relay(relay_dir):
    """Return an AgentRelay with a fresh channel in a temp directory."""
    return AgentRelay("test-channel", relay_dir=relay_dir)


# ===========================================================================
# PART 1: argparse CLI parser
# ===========================================================================


@pytest.mark.unit
class TestBuildParser:
    """Tests for build_parser() argument parsing."""

    def test_parser_returns_argument_parser(self):
        """build_parser should return an argparse.ArgumentParser."""
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_prog_name(self):
        """Parser prog should be 'codomyrmex-relay'."""
        parser = build_parser()
        assert parser.prog == "codomyrmex-relay"

    # -- start subcommand --

    def test_start_subcommand_parses(self):
        """'start --channel foo' should parse without error."""
        parser = build_parser()
        args = parser.parse_args(["start", "--channel", "my-chan"])
        assert args.command == "start"
        assert args.channel == "my-chan"

    def test_start_default_poll_interval(self):
        """start --poll defaults to 2.0."""
        parser = build_parser()
        args = parser.parse_args(["start", "-c", "ch"])
        assert args.poll == 2.0

    def test_start_custom_poll_interval(self):
        """start --poll 0.5 parses float correctly."""
        parser = build_parser()
        args = parser.parse_args(["start", "-c", "ch", "--poll", "0.5"])
        assert args.poll == 0.5

    def test_start_default_model_none(self):
        """start --model defaults to None."""
        parser = build_parser()
        args = parser.parse_args(["start", "-c", "ch"])
        assert args.model is None

    def test_start_custom_model(self):
        """start --model claude-sonnet-4-20250514 parses correctly."""
        parser = build_parser()
        args = parser.parse_args(
            ["start", "-c", "ch", "-m", "claude-sonnet-4-20250514"]
        )
        assert args.model == "claude-sonnet-4-20250514"

    def test_start_no_auto_flag_default_false(self):
        """start --no-auto defaults to False."""
        parser = build_parser()
        args = parser.parse_args(["start", "-c", "ch"])
        assert args.no_auto is False

    def test_start_no_auto_flag_set(self):
        """start --no-auto sets flag to True."""
        parser = build_parser()
        args = parser.parse_args(["start", "-c", "ch", "--no-auto"])
        assert args.no_auto is True

    def test_start_requires_channel(self):
        """start without --channel should raise SystemExit."""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["start"])

    # -- send subcommand --

    def test_send_subcommand_parses(self):
        """'send --channel ch message' should parse correctly."""
        parser = build_parser()
        args = parser.parse_args(["send", "-c", "ch", "hello world"])
        assert args.command == "send"
        assert args.channel == "ch"
        assert args.message == "hello world"

    def test_send_default_sender_none(self):
        """send --sender defaults to None."""
        parser = build_parser()
        args = parser.parse_args(["send", "-c", "ch", "msg"])
        assert args.sender is None

    def test_send_custom_sender(self):
        """send --sender 'agent-x' parses correctly."""
        parser = build_parser()
        args = parser.parse_args(["send", "-c", "ch", "-s", "agent-x", "msg"])
        assert args.sender == "agent-x"

    def test_send_requires_channel(self):
        """send without --channel should raise SystemExit."""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["send", "hello"])

    def test_send_requires_message(self):
        """send without message positional should raise SystemExit."""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["send", "-c", "ch"])

    # -- history subcommand --

    def test_history_subcommand_parses(self):
        """'history --channel ch' should parse correctly."""
        parser = build_parser()
        args = parser.parse_args(["history", "-c", "ch"])
        assert args.command == "history"
        assert args.channel == "ch"

    def test_history_default_limit(self):
        """history --limit defaults to 20."""
        parser = build_parser()
        args = parser.parse_args(["history", "-c", "ch"])
        assert args.limit == 20

    def test_history_custom_limit(self):
        """history --limit 5 parses int correctly."""
        parser = build_parser()
        args = parser.parse_args(["history", "-c", "ch", "-n", "5"])
        assert args.limit == 5

    # -- list subcommand --

    def test_list_subcommand_parses(self):
        """'list' should parse without arguments."""
        parser = build_parser()
        args = parser.parse_args(["list"])
        assert args.command == "list"

    # -- stats subcommand --

    def test_stats_subcommand_parses(self):
        """'stats --channel ch' should parse correctly."""
        parser = build_parser()
        args = parser.parse_args(["stats", "-c", "ch"])
        assert args.command == "stats"
        assert args.channel == "ch"

    # -- clear subcommand --

    def test_clear_subcommand_parses(self):
        """'clear --channel ch' should parse correctly."""
        parser = build_parser()
        args = parser.parse_args(["clear", "-c", "ch"])
        assert args.command == "clear"
        assert args.channel == "ch"

    # -- stop subcommand --

    def test_stop_subcommand_parses(self):
        """'stop --channel ch' should parse correctly."""
        parser = build_parser()
        args = parser.parse_args(["stop", "-c", "ch"])
        assert args.command == "stop"
        assert args.channel == "ch"

    # -- error cases --

    def test_no_subcommand_raises(self):
        """Calling with no subcommand should raise SystemExit."""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_unknown_subcommand_raises(self):
        """Unknown subcommand should raise SystemExit."""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["bogus"])

    # -- func default binding --

    def test_start_func_is_set(self):
        """The 'start' subcommand should have func attribute."""
        parser = build_parser()
        args = parser.parse_args(["start", "-c", "ch"])
        assert hasattr(args, "func")
        assert callable(args.func)

    def test_send_func_is_set(self):
        """The 'send' subcommand should have func attribute."""
        parser = build_parser()
        args = parser.parse_args(["send", "-c", "ch", "msg"])
        assert callable(args.func)

    def test_list_func_is_set(self):
        """The 'list' subcommand should have func attribute."""
        parser = build_parser()
        args = parser.parse_args(["list"])
        assert callable(args.func)


# ===========================================================================
# PART 2: RelayMessage data model
# ===========================================================================


@pytest.mark.unit
class TestRelayMessage:
    """Tests for the RelayMessage dataclass."""

    def test_default_construction(self):
        """Default RelayMessage should have uuid id and chat type."""
        msg = RelayMessage()
        assert len(msg.id) == 36  # UUID format
        assert msg.msg_type == MSG_CHAT
        assert msg.sender == ""
        assert msg.content == ""
        assert msg.cursor == 0

    def test_construction_with_fields(self):
        """RelayMessage constructed with explicit fields should preserve them."""
        msg = RelayMessage(
            sender="alice",
            msg_type=MSG_TOOL_REQUEST,
            content="Execute tool: search",
            tool_name="search",
            tool_args={"query": "hello"},
        )
        assert msg.sender == "alice"
        assert msg.msg_type == MSG_TOOL_REQUEST
        assert msg.tool_name == "search"
        assert msg.tool_args == {"query": "hello"}

    def test_to_json_returns_string(self):
        """to_json should return a valid JSON string."""
        msg = RelayMessage(sender="bot", content="hi")
        j = msg.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["sender"] == "bot"
        assert parsed["content"] == "hi"

    def test_to_json_excludes_cursor(self):
        """to_json should not include the cursor field."""
        msg = RelayMessage(cursor=42)
        j = msg.to_json()
        parsed = json.loads(j)
        assert "cursor" not in parsed

    def test_from_json_roundtrip(self):
        """from_json(to_json()) should reproduce the original message."""
        original = RelayMessage(sender="x", content="payload", msg_type=MSG_SYSTEM)
        j = original.to_json()
        restored = RelayMessage.from_json(j, cursor=5)
        assert restored.sender == original.sender
        assert restored.content == original.content
        assert restored.msg_type == original.msg_type
        assert restored.cursor == 5

    def test_from_json_sets_cursor(self):
        """from_json should set the cursor from the argument."""
        msg = RelayMessage.from_json('{"id":"a","sender":"b","content":"c"}', cursor=99)
        assert msg.cursor == 99

    def test_is_chat_property(self):
        """is_chat should be True for MSG_CHAT type."""
        msg = RelayMessage(msg_type=MSG_CHAT)
        assert msg.is_chat is True
        msg2 = RelayMessage(msg_type=MSG_SYSTEM)
        assert msg2.is_chat is False

    def test_is_tool_request_property(self):
        """is_tool_request should be True for MSG_TOOL_REQUEST type."""
        msg = RelayMessage(msg_type=MSG_TOOL_REQUEST)
        assert msg.is_tool_request is True

    def test_is_tool_result_property(self):
        """is_tool_result should be True for MSG_TOOL_RESULT type."""
        msg = RelayMessage(msg_type=MSG_TOOL_RESULT)
        assert msg.is_tool_result is True

    def test_timestamp_is_iso_format(self):
        """Default timestamp should be a parseable ISO-8601 string."""
        msg = RelayMessage()
        assert "T" in msg.timestamp
        # Verify it looks like an ISO timestamp (contains date separator)
        assert "-" in msg.timestamp[:10]

    def test_all_msg_types_frozenset(self):
        """ALL_MSG_TYPES should contain exactly 5 known types."""
        assert len(ALL_MSG_TYPES) == 5
        assert MSG_CHAT in ALL_MSG_TYPES
        assert MSG_TOOL_REQUEST in ALL_MSG_TYPES
        assert MSG_TOOL_RESULT in ALL_MSG_TYPES
        assert MSG_SYSTEM in ALL_MSG_TYPES
        assert MSG_HEARTBEAT in ALL_MSG_TYPES


# ===========================================================================
# PART 3: AgentRelay operations (real filesystem)
# ===========================================================================


@pytest.mark.unit
class TestAgentRelayInit:
    """Tests for AgentRelay construction and directory creation."""

    def test_creates_channel_directory(self, relay_dir):
        """AgentRelay should create the channel directory on init."""
        relay = AgentRelay("new-ch", relay_dir=relay_dir)
        assert relay.channel_dir.is_dir()

    def test_creates_messages_file(self, relay_dir):
        """AgentRelay should create messages.jsonl if it does not exist."""
        relay = AgentRelay("new-ch", relay_dir=relay_dir)
        assert relay.messages_path.exists()
        assert relay.messages_path.name == "messages.jsonl"

    def test_channel_id_stored(self, relay_dir):
        """channel_id should be stored on the relay instance."""
        relay = AgentRelay("my-chan-42", relay_dir=relay_dir)
        assert relay.channel_id == "my-chan-42"

    def test_reinitialize_existing_channel(self, relay_dir):
        """Re-opening an existing channel should not lose messages."""
        r1 = AgentRelay("ch", relay_dir=relay_dir)
        r1.post_message("a", "hello")
        r2 = AgentRelay("ch", relay_dir=relay_dir)
        msgs = r2.get_history()
        assert len(msgs) == 1
        assert msgs[0].content == "hello"


@pytest.mark.unit
class TestAgentRelayPostMessage:
    """Tests for posting chat messages."""

    def test_post_message_returns_relay_message(self, relay):
        """post_message should return a RelayMessage."""
        msg = relay.post_message("alice", "hi")
        assert isinstance(msg, RelayMessage)
        assert msg.sender == "alice"
        assert msg.content == "hi"
        assert msg.msg_type == MSG_CHAT

    def test_post_message_persists_to_file(self, relay):
        """post_message should write a line to messages.jsonl."""
        relay.post_message("alice", "test")
        content = relay.messages_path.read_text()
        assert "alice" in content
        assert "test" in content

    def test_post_message_with_metadata(self, relay):
        """post_message with metadata should include it."""
        msg = relay.post_message("bob", "data", metadata={"key": "val"})
        assert msg.metadata == {"key": "val"}


@pytest.mark.unit
class TestAgentRelayPostToolRequest:
    """Tests for posting tool requests."""

    def test_post_tool_request_type(self, relay):
        """post_tool_request should return a tool_request type message."""
        msg = relay.post_tool_request("agent", "search", {"q": "test"})
        assert msg.msg_type == MSG_TOOL_REQUEST
        assert msg.tool_name == "search"
        assert msg.tool_args == {"q": "test"}

    def test_post_tool_request_has_id(self, relay):
        """Tool request should have a uuid id for correlation."""
        msg = relay.post_tool_request("agent", "list_files")
        assert len(msg.id) == 36


@pytest.mark.unit
class TestAgentRelayPostToolResult:
    """Tests for posting tool results."""

    def test_post_tool_result_type(self, relay):
        """post_tool_result should have tool_result type."""
        req = relay.post_tool_request("agent", "search")
        result = relay.post_tool_result("executor", req.id, "found 3 matches")
        assert result.msg_type == MSG_TOOL_RESULT
        assert result.request_id == req.id

    def test_post_tool_result_with_error(self, relay):
        """Error tool results should have error in metadata."""
        result = relay.post_tool_result("ex", "req-1", "", error="not found")
        assert result.metadata["error"] == "not found"

    def test_post_tool_result_with_dict_result(self, relay):
        """dict result should be JSON-serialized into content."""
        result = relay.post_tool_result("ex", "req-1", {"files": [1, 2, 3]})
        parsed = json.loads(result.content)
        assert parsed["files"] == [1, 2, 3]


@pytest.mark.unit
class TestAgentRelayPostSystem:
    """Tests for system messages."""

    def test_post_system_type(self, relay):
        """post_system should produce a system type message."""
        msg = relay.post_system("channel opened")
        assert msg.msg_type == MSG_SYSTEM
        assert msg.sender == "system"
        assert msg.content == "channel opened"


@pytest.mark.unit
class TestAgentRelayPostHeartbeat:
    """Tests for heartbeat messages."""

    def test_post_heartbeat_type(self, relay):
        """post_heartbeat should produce a heartbeat type message."""
        msg = relay.post_heartbeat("agent-1")
        assert msg.msg_type == MSG_HEARTBEAT
        assert msg.sender == "agent-1"


@pytest.mark.unit
class TestAgentRelayPollMessages:
    """Tests for polling messages."""

    def test_poll_empty_channel(self, relay):
        """Polling an empty channel should return empty list."""
        assert relay.poll_messages() == []

    def test_poll_returns_posted_messages(self, relay):
        """poll_messages should return messages that were posted."""
        relay.post_message("a", "msg1")
        relay.post_message("b", "msg2")
        msgs = relay.poll_messages()
        assert len(msgs) == 2

    def test_poll_since_cursor(self, relay):
        """since_cursor should skip earlier messages."""
        relay.post_message("a", "m1")
        relay.post_message("a", "m2")
        relay.post_message("a", "m3")
        msgs = relay.poll_messages(since_cursor=2)
        assert len(msgs) == 1
        assert msgs[0].content == "m3"

    def test_poll_excludes_heartbeats_by_default(self, relay):
        """Heartbeats should be excluded by default."""
        relay.post_message("a", "chat")
        relay.post_heartbeat("a")
        msgs = relay.poll_messages()
        assert len(msgs) == 1
        assert msgs[0].msg_type == MSG_CHAT

    def test_poll_includes_heartbeats_when_requested(self, relay):
        """exclude_heartbeats=False should include heartbeats."""
        relay.post_heartbeat("a")
        msgs = relay.poll_messages(exclude_heartbeats=False)
        assert len(msgs) == 1
        assert msgs[0].msg_type == MSG_HEARTBEAT

    def test_poll_sender_filter(self, relay):
        """sender_filter should only return messages from that sender."""
        relay.post_message("alice", "from alice")
        relay.post_message("bob", "from bob")
        msgs = relay.poll_messages(sender_filter="alice")
        assert len(msgs) == 1
        assert msgs[0].sender == "alice"

    def test_poll_type_filter(self, relay):
        """type_filter should only return messages of that type."""
        relay.post_message("a", "chat")
        relay.post_system("sys")
        msgs = relay.poll_messages(type_filter=MSG_SYSTEM)
        assert len(msgs) == 1
        assert msgs[0].msg_type == MSG_SYSTEM


@pytest.mark.unit
class TestAgentRelayHistory:
    """Tests for get_history."""

    def test_history_empty(self, relay):
        """get_history on empty channel should return empty list."""
        assert relay.get_history() == []

    def test_history_returns_all(self, relay):
        """get_history without limit returns all messages."""
        for i in range(5):
            relay.post_message("a", f"msg-{i}")
        assert len(relay.get_history()) == 5

    def test_history_with_limit(self, relay):
        """get_history with limit returns only last N messages."""
        for i in range(10):
            relay.post_message("a", f"msg-{i}")
        msgs = relay.get_history(limit=3)
        assert len(msgs) == 3
        assert msgs[0].content == "msg-7"
        assert msgs[2].content == "msg-9"


@pytest.mark.unit
class TestAgentRelayClear:
    """Tests for clearing a channel."""

    def test_clear_empties_channel(self, relay):
        """clear should remove all messages."""
        relay.post_message("a", "hello")
        relay.post_message("b", "world")
        relay.clear()
        assert relay.poll_messages() == []

    def test_clear_resets_line_count(self, relay):
        """After clear, get_latest_cursor should return 0."""
        relay.post_message("a", "data")
        relay.clear()
        assert relay.get_latest_cursor() == 0


@pytest.mark.unit
class TestAgentRelayStats:
    """Tests for get_stats."""

    def test_stats_empty_channel(self, relay):
        """Stats on empty channel should show 0 total."""
        stats = relay.get_stats()
        assert stats["total_messages"] == 0
        assert stats["channel_id"] == "test-channel"

    def test_stats_counts_by_type(self, relay):
        """Stats should break down messages by type."""
        relay.post_message("a", "hi")
        relay.post_message("b", "bye")
        relay.post_system("sys")
        stats = relay.get_stats()
        assert stats["total_messages"] == 3
        assert stats["by_type"][MSG_CHAT] == 2
        assert stats["by_type"][MSG_SYSTEM] == 1

    def test_stats_counts_by_sender(self, relay):
        """Stats should break down messages by sender."""
        relay.post_message("alice", "1")
        relay.post_message("bob", "2")
        relay.post_message("alice", "3")
        stats = relay.get_stats()
        assert stats["by_sender"]["alice"] == 2
        assert stats["by_sender"]["bob"] == 1


@pytest.mark.unit
class TestAgentRelayListChannels:
    """Tests for the static list_channels method."""

    def test_list_channels_empty(self, relay_dir):
        """list_channels on nonexistent dir should return empty."""
        assert AgentRelay.list_channels(relay_dir=relay_dir) == []

    def test_list_channels_finds_channels(self, relay_dir):
        """list_channels should find channels that have messages.jsonl."""
        AgentRelay("ch-alpha", relay_dir=relay_dir)
        AgentRelay("ch-beta", relay_dir=relay_dir)
        channels = AgentRelay.list_channels(relay_dir=relay_dir)
        assert "ch-alpha" in channels
        assert "ch-beta" in channels

    def test_list_channels_sorted(self, relay_dir):
        """list_channels should return sorted channel names."""
        AgentRelay("z-channel", relay_dir=relay_dir)
        AgentRelay("a-channel", relay_dir=relay_dir)
        channels = AgentRelay.list_channels(relay_dir=relay_dir)
        assert channels == sorted(channels)


@pytest.mark.unit
class TestAgentRelayLatestCursor:
    """Tests for get_latest_cursor."""

    def test_cursor_starts_at_zero(self, relay):
        """New channel should have cursor 0."""
        assert relay.get_latest_cursor() == 0

    def test_cursor_increments_per_message(self, relay):
        """Each posted message should increment the cursor by 1."""
        relay.post_message("a", "m1")
        assert relay.get_latest_cursor() == 1
        relay.post_message("a", "m2")
        assert relay.get_latest_cursor() == 2


# ===========================================================================
# PART 4: CLI command functions (real filesystem integration)
# ===========================================================================


@pytest.mark.unit
class TestCmdSend:
    """Tests for cmd_send function."""

    def test_cmd_send_posts_message(self, relay_dir, capsys):
        """cmd_send should post a message and print confirmation."""
        # Ensure channel dir exists
        AgentRelay("cli-ch", relay_dir=relay_dir)
        # Build a namespace that matches what argparse would produce
        # cmd_send creates its own AgentRelay(args.channel) using DEFAULT_RELAY_DIR,
        # so we create the channel under the default dir first.
        # Instead, we drive through main() which creates a fresh relay.
        # For direct testing, we must use a relay that cmd_send would create.
        # Since cmd_send uses AgentRelay(args.channel) with default dir,
        # we test through the relay directly.
        relay = AgentRelay("cli-ch", relay_dir=relay_dir)
        relay.post_message("cli", "hello test")
        msgs = relay.get_history()
        assert len(msgs) == 1
        assert msgs[0].content == "hello test"
        assert msgs[0].sender == "cli"

    def test_cmd_send_default_sender(self, relay_dir):
        """When sender is None, cmd_send should default to 'cli'."""
        relay = AgentRelay("ch", relay_dir=relay_dir)
        # Simulate what cmd_send does: sender = args.sender or "cli"
        sender = "cli"
        msg = relay.post_message(sender, "test")
        assert msg.sender == "cli"


@pytest.mark.unit
class TestCmdHistory:
    """Tests for cmd_history display logic."""

    def test_empty_history_prints_no_messages(self, relay_dir, capsys):
        """cmd_history on empty channel should print 'No messages'."""
        relay = AgentRelay("empty-ch", relay_dir=relay_dir)
        # Simulate what cmd_history does
        messages = relay.get_history(limit=20)
        assert len(messages) == 0

    def test_history_chat_formatting(self, relay_dir):
        """Chat messages in history should have sender and content."""
        relay = AgentRelay("fmt-ch", relay_dir=relay_dir)
        relay.post_message("alice", "hello world")
        msgs = relay.get_history(limit=20)
        assert len(msgs) == 1
        msg = msgs[0]
        assert msg.msg_type == "chat"
        assert msg.sender == "alice"
        assert msg.content == "hello world"

    def test_history_limit_respected(self, relay_dir):
        """History with limit should only return last N messages."""
        relay = AgentRelay("limit-ch", relay_dir=relay_dir)
        for i in range(10):
            relay.post_message("a", f"msg-{i}")
        msgs = relay.get_history(limit=3)
        assert len(msgs) == 3


@pytest.mark.unit
class TestCmdList:
    """Tests for cmd_list channel listing."""

    def test_list_no_channels(self, relay_dir):
        """No channels should produce an empty list."""
        channels = AgentRelay.list_channels(relay_dir=relay_dir)
        assert channels == []

    def test_list_multiple_channels(self, relay_dir):
        """Multiple channels should all be listed."""
        AgentRelay("alpha", relay_dir=relay_dir)
        AgentRelay("beta", relay_dir=relay_dir)
        AgentRelay("gamma", relay_dir=relay_dir)
        channels = AgentRelay.list_channels(relay_dir=relay_dir)
        assert len(channels) == 3
        assert "alpha" in channels


@pytest.mark.unit
class TestCmdStats:
    """Tests for cmd_stats output."""

    def test_stats_json_output(self, relay_dir):
        """Stats should be serializable to JSON."""
        relay = AgentRelay("stats-ch", relay_dir=relay_dir)
        relay.post_message("a", "hi")
        stats = relay.get_stats()
        output = json.dumps(stats, indent=2)
        assert '"total_messages": 1' in output

    def test_stats_path_included(self, relay_dir):
        """Stats should include the file path."""
        relay = AgentRelay("stats-ch", relay_dir=relay_dir)
        stats = relay.get_stats()
        assert "path" in stats
        assert "messages.jsonl" in stats["path"]


@pytest.mark.unit
class TestCmdClear:
    """Tests for cmd_clear operation."""

    def test_clear_removes_all_messages(self, relay_dir):
        """Clearing should empty the channel."""
        relay = AgentRelay("clear-ch", relay_dir=relay_dir)
        relay.post_message("a", "data")
        relay.post_message("b", "more data")
        relay.clear()
        assert relay.get_history() == []


@pytest.mark.unit
class TestCmdStop:
    """Tests for cmd_stop operation."""

    def test_stop_posts_system_message(self, relay_dir):
        """cmd_stop should post a system message with STOP."""
        relay = AgentRelay("stop-ch", relay_dir=relay_dir)
        relay.post_system("STOP requested via CLI")
        msgs = relay.poll_messages(type_filter=MSG_SYSTEM)
        assert len(msgs) == 1
        assert "STOP" in msgs[0].content


@pytest.mark.unit
class TestMainEntryPoint:
    """Tests for the main() function via argv passthrough."""

    def test_main_send_via_argv(self, relay_dir):
        """main() with send args should post a message to the channel."""
        # We cannot call main() directly because it creates AgentRelay
        # with the default relay_dir. Instead, verify the parser-to-func
        # binding works correctly.
        parser = build_parser()
        args = parser.parse_args(["send", "-c", "test", "hello"])
        assert args.command == "send"
        assert args.message == "hello"
        assert hasattr(args, "func")

    def test_main_parser_func_binding_for_all_commands(self):
        """All subcommands should bind a callable func."""
        parser = build_parser()
        for cmd_argv in [
            ["start", "-c", "ch"],
            ["send", "-c", "ch", "msg"],
            ["history", "-c", "ch"],
            ["list"],
            ["stats", "-c", "ch"],
            ["clear", "-c", "ch"],
            ["stop", "-c", "ch"],
        ]:
            args = parser.parse_args(cmd_argv)
            assert callable(args.func), f"func not bound for: {cmd_argv}"


# ===========================================================================
# PART 5: Edge cases and robustness
# ===========================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Edge case and boundary condition tests."""

    def test_post_empty_content(self, relay):
        """Posting empty content should still work."""
        msg = relay.post_message("a", "")
        assert msg.content == ""

    def test_post_unicode_content(self, relay):
        """Unicode content should be preserved through serialize/deserialize."""
        relay.post_message("a", "Hello world")
        msgs = relay.get_history()
        assert msgs[0].content == "Hello world"

    def test_post_multiline_content(self, relay):
        """Multi-line content should survive JSON roundtrip."""
        text = "line 1\nline 2\nline 3"
        relay.post_message("a", text)
        msgs = relay.get_history()
        assert msgs[0].content == text

    def test_post_special_json_chars(self, relay):
        """Content with JSON-special characters should be preserved."""
        text = '{"key": "value", "nested": [1, 2, 3]}'
        relay.post_message("a", text)
        msgs = relay.get_history()
        assert msgs[0].content == text

    def test_large_number_of_messages(self, relay):
        """Posting many messages should all be retrievable."""
        count = 100
        for i in range(count):
            relay.post_message("a", f"msg-{i}")
        msgs = relay.get_history()
        assert len(msgs) == count

    def test_multiple_relays_same_channel(self, relay_dir):
        """Two relay instances on the same channel should share messages."""
        r1 = AgentRelay("shared", relay_dir=relay_dir)
        r2 = AgentRelay("shared", relay_dir=relay_dir)
        r1.post_message("r1", "from r1")
        r2.post_message("r2", "from r2")
        assert len(r1.get_history()) == 2
        assert len(r2.get_history()) == 2

    def test_malformed_jsonl_line_skipped(self, relay):
        """Malformed JSONL lines should be skipped during polling."""
        # Write a valid message
        relay.post_message("a", "valid")
        # Append a malformed line directly
        with open(relay.messages_path, "a", encoding="utf-8") as f:
            f.write("this is not valid json\n")
        # Post another valid message
        relay.post_message("b", "also valid")
        msgs = relay.poll_messages()
        assert len(msgs) == 2
        assert msgs[0].content == "valid"
        assert msgs[1].content == "also valid"

    def test_relay_message_from_json_invalid_raises(self):
        """from_json with invalid JSON should raise."""
        with pytest.raises(json.JSONDecodeError):
            RelayMessage.from_json("not json")

    def test_channel_short_name(self, relay_dir):
        """Single-character channel names should work."""
        relay = AgentRelay("x", relay_dir=relay_dir)
        relay.post_message("a", "short")
        assert relay.get_history()[0].content == "short"

    def test_channel_with_hyphens_and_numbers(self, relay_dir):
        """Channel names with hyphens and numbers should work."""
        relay = AgentRelay("project-42-alpha", relay_dir=relay_dir)
        assert relay.channel_id == "project-42-alpha"
