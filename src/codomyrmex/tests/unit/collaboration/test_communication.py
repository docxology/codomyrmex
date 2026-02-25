"""
Tests for collaboration communication submodule.
"""


import pytest

from codomyrmex.collaboration.communication import (
    Broadcaster,
    ChannelManager,
    ChannelState,
    ConversationTracker,
    DirectMessenger,
    MessageQueue,
    QueueChannel,
)
from codomyrmex.collaboration.exceptions import MessageDeliveryError
from codomyrmex.collaboration.protocols import AgentMessage


class TestMessageQueue:
    """Tests for MessageQueue."""

    def test_queue_creation(self):
        """Test creating a message queue."""
        queue = MessageQueue()

        assert queue.size == 0
        assert queue.is_empty is True
        assert queue.is_full is False

    def test_queue_with_max_size(self):
        """Test queue with maximum size."""
        queue = MessageQueue(max_size=2)

        assert queue.is_full is False

    @pytest.mark.asyncio
    async def test_queue_put_and_get(self):
        """Test putting and getting messages."""
        queue = MessageQueue()
        message = AgentMessage(
            sender_id="sender-1",
            receiver_id="receiver-1",
            content="Hello",
        )

        await queue.put(message)
        assert queue.size == 1

        received = await queue.get()
        assert received.content == "Hello"
        assert queue.size == 0

    def test_queue_put_nowait(self):
        """Test putting message without waiting."""
        queue = MessageQueue()
        message = AgentMessage(
            sender_id="sender-1",
            content="Immediate",
        )

        queue.put_nowait(message)
        assert queue.size == 1

    def test_queue_get_nowait(self):
        """Test getting message without waiting."""
        queue = MessageQueue()
        message = AgentMessage(sender_id="sender-1", content="Test")

        queue.put_nowait(message)
        received = queue.get_nowait()

        assert received is not None
        assert received.content == "Test"

        # Empty queue returns None
        assert queue.get_nowait() is None

    def test_queue_clear(self):
        """Test clearing the queue."""
        queue = MessageQueue()
        queue.put_nowait(AgentMessage(sender_id="s1", content="1"))
        queue.put_nowait(AgentMessage(sender_id="s2", content="2"))

        cleared = queue.clear()

        assert cleared == 2
        assert queue.is_empty is True


class TestQueueChannel:
    """Tests for QueueChannel."""

    def test_channel_creation(self):
        """Test creating a queue channel."""
        channel = QueueChannel(
            channel_id="ch-123",
            name="Test Channel",
        )

        assert channel.channel_id == "ch-123"
        assert channel.name == "Test Channel"
        assert channel.state == ChannelState.OPEN

    @pytest.mark.asyncio
    async def test_channel_send_receive(self):
        """Test sending and receiving on channel."""
        channel = QueueChannel(name="Test Channel")
        message = AgentMessage(
            sender_id="sender-1",
            content="Channel message",
        )

        await channel.send(message)
        received = await channel.receive(timeout=1.0)

        assert received.content == "Channel message"

    def test_channel_close(self):
        """Test closing a channel."""
        channel = QueueChannel(name="Test Channel")

        channel.close()

        assert channel.state == ChannelState.CLOSED

    def test_channel_pause_resume(self):
        """Test pausing and resuming channel."""
        channel = QueueChannel(name="Test Channel")

        channel.pause()
        assert channel.state == ChannelState.PAUSED

        channel.resume()
        assert channel.state == ChannelState.OPEN

    def test_channel_get_info(self):
        """Test getting channel info."""
        channel = QueueChannel(
            channel_id="ch-456",
            name="Info Channel",
        )

        info = channel.get_info()

        assert info.channel_id == "ch-456"
        assert info.name == "Info Channel"
        assert info.state == ChannelState.OPEN


class TestChannelManager:
    """Tests for ChannelManager."""

    def test_manager_creation(self):
        """Test creating a channel manager."""
        manager = ChannelManager()

        assert manager.list_channels() == []

    def test_manager_create_channel(self):
        """Test creating channels through manager."""
        manager = ChannelManager()

        channel = manager.create_channel("test-channel")

        assert channel.name == "test-channel"
        assert len(manager.list_channels()) == 1

    def test_manager_get_channel(self):
        """Test getting channel by ID."""
        manager = ChannelManager()
        channel = manager.create_channel("test-channel")

        retrieved = manager.get_channel(channel.channel_id)

        assert retrieved is channel

    def test_manager_get_channel_by_name(self):
        """Test getting channel by name."""
        manager = ChannelManager()
        manager.create_channel("named-channel")

        retrieved = manager.get_channel_by_name("named-channel")

        assert retrieved is not None
        assert retrieved.name == "named-channel"

    def test_manager_close_channel(self):
        """Test closing channel through manager."""
        manager = ChannelManager()
        channel = manager.create_channel("test-channel")

        result = manager.close_channel(channel.channel_id)

        assert result is True
        assert len(manager.list_channels()) == 0

    def test_manager_close_all(self):
        """Test closing all channels."""
        manager = ChannelManager()
        manager.create_channel("channel-1")
        manager.create_channel("channel-2")

        manager.close_all()

        assert len(manager.list_channels()) == 0


class TestBroadcaster:
    """Tests for Broadcaster."""

    def test_broadcaster_creation(self):
        """Test creating a broadcaster."""
        broadcaster = Broadcaster()

        assert broadcaster.list_topics() == []

    def test_broadcaster_create_topic(self):
        """Test creating a topic."""
        broadcaster = Broadcaster()

        broadcaster.create_topic("test-topic")

        topics = broadcaster.list_topics()
        assert len(topics) == 1
        assert topics[0].topic == "test-topic"

    def test_broadcaster_subscribe(self):
        """Test subscribing to a topic."""
        broadcaster = Broadcaster()
        received = []

        def handler(msg):
            received.append(msg)

        sub_id = broadcaster.subscribe(
            "test-topic",
            "subscriber-1",
            handler,
        )

        assert sub_id is not None
        info = broadcaster.get_topic_info("test-topic")
        assert info.subscriber_count == 1

    def test_broadcaster_unsubscribe(self):
        """Test unsubscribing from a topic."""
        broadcaster = Broadcaster()

        sub_id = broadcaster.subscribe(
            "test-topic",
            "subscriber-1",
            lambda msg: None,
        )

        result = broadcaster.unsubscribe(sub_id)

        assert result is True
        info = broadcaster.get_topic_info("test-topic")
        assert info.subscriber_count == 0

    @pytest.mark.asyncio
    async def test_broadcaster_publish(self):
        """Test publishing to a topic."""
        broadcaster = Broadcaster()
        received = []

        def handler(msg):
            received.append(msg.content)

        broadcaster.subscribe("test-topic", "sub-1", handler)

        message = AgentMessage(sender_id="publisher", content="Hello")
        count = await broadcaster.publish("test-topic", message)

        assert count == 1
        assert received == ["Hello"]

    def test_broadcaster_delete_topic(self):
        """Test deleting a topic."""
        broadcaster = Broadcaster()
        broadcaster.create_topic("delete-me")

        result = broadcaster.delete_topic("delete-me")

        assert result is True
        assert broadcaster.get_topic_info("delete-me") is None


class TestDirectMessenger:
    """Tests for DirectMessenger."""

    def test_messenger_creation(self):
        """Test creating a direct messenger."""
        messenger = DirectMessenger(default_timeout=10.0)

        assert messenger is not None

    def test_messenger_register_handler(self):
        """Test registering a handler."""
        messenger = DirectMessenger()

        async def handler(msg):
            return "received"

        messenger.register_handler("agent-1", handler)

        # Should not raise
        messenger.unregister_handler("agent-1")

    @pytest.mark.asyncio
    async def test_messenger_send(self):
        """Test sending a direct message."""
        messenger = DirectMessenger()
        received = []

        async def handler(msg):
            received.append(msg.content)

        messenger.register_handler("receiver", handler)

        await messenger.send("sender", "receiver", "Hello Direct")

        assert received == ["Hello Direct"]

    @pytest.mark.asyncio
    async def test_messenger_send_no_handler(self):
        """Test sending to unregistered receiver."""
        messenger = DirectMessenger()

        with pytest.raises(MessageDeliveryError):
            await messenger.send("sender", "nobody", "Hello")

    @pytest.mark.asyncio
    async def test_messenger_request(self):
        """Test request-response pattern."""
        messenger = DirectMessenger()

        async def handler(msg):
            return f"Response to: {msg.content}"

        messenger.register_handler("responder", handler)

        result = await messenger.request(
            "requester",
            "responder",
            "What is 2+2?",
            timeout=5.0,
        )

        assert result == "Response to: What is 2+2?"

    def test_messenger_get_message_log(self):
        """Test getting message log."""
        messenger = DirectMessenger()

        log = messenger.get_message_log()

        assert isinstance(log, list)


class TestConversationTracker:
    """Tests for ConversationTracker."""

    def test_tracker_creation(self):
        """Test creating a conversation tracker."""
        tracker = ConversationTracker()

        assert tracker is not None

    def test_tracker_start_conversation(self):
        """Test starting a conversation."""
        tracker = ConversationTracker()

        conv_id = tracker.start_conversation(["agent-1", "agent-2"])

        assert conv_id is not None
        assert tracker.get_conversation(conv_id) == []

    def test_tracker_add_message(self):
        """Test adding message to conversation."""
        tracker = ConversationTracker()
        conv_id = tracker.start_conversation(["agent-1", "agent-2"])

        message = AgentMessage(sender_id="agent-1", content="Hi")
        tracker.add_message(conv_id, message)

        messages = tracker.get_conversation(conv_id)
        assert len(messages) == 1
        assert messages[0].content == "Hi"

    def test_tracker_get_agent_conversations(self):
        """Test getting conversations for an agent."""
        tracker = ConversationTracker()

        conv_id = tracker.start_conversation(["agent-1", "agent-2"])

        convos = tracker.get_agent_conversations("agent-1")
        assert conv_id in convos

    def test_tracker_end_conversation(self):
        """Test ending a conversation."""
        tracker = ConversationTracker()
        conv_id = tracker.start_conversation(["agent-1"])

        result = tracker.end_conversation(conv_id)

        assert result is True
        assert tracker.get_conversation(conv_id) == []
