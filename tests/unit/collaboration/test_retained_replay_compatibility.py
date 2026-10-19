"""Real retained delivery, including callbacks that publish during replay."""

import pytest

from codomyrmex.collaboration.communication.broadcaster import Broadcaster
from codomyrmex.collaboration.protocols import AgentMessage


@pytest.mark.parametrize(
    ("retention", "expected"), [(-1, []), (0, []), (1, ["new"]), (2, ["old", "new"])]
)
def test_retention_replays_only_retained_messages(retention, expected):
    broadcaster = Broadcaster(retention_count=retention)
    broadcaster.create_topic("synthetic")
    for content in ["old", "new"]:
        broadcaster.publish_sync("synthetic", AgentMessage(content=content))
    seen = []
    broadcaster.subscribe(
        "synthetic",
        "reader",
        lambda message: seen.append(message.content),
        replay_retained=True,
    )
    assert seen == expected


def test_replay_handler_can_publish_into_same_topic():
    broadcaster = Broadcaster(retention_count=1)
    broadcaster.create_topic("synthetic")
    broadcaster.publish_sync("synthetic", AgentMessage(content="old"))
    seen = []

    def handler(message):
        seen.append(message.content)
        if message.content == "old":
            broadcaster.publish_sync("synthetic", AgentMessage(content="new"))

    subscription = broadcaster.subscribe(
        "synthetic", "reader", handler, replay_retained=True
    )
    assert seen == ["old", "new"]
    assert broadcaster.unsubscribe(subscription)
    replayed = []
    broadcaster.subscribe(
        "synthetic",
        "later",
        lambda message: replayed.append(message.content),
        replay_retained=True,
    )
    assert replayed == ["new"]
