from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from time import time
from typing import Any


@dataclass
class TopicMessage:
    topic: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time)


@dataclass
class TopicInfo:
    name: str
    total_published: int
    subscriber_count: int
    latched: bool = False


@dataclass
class _TopicState:
    name: str
    latched: bool = False
    total_published: int = 0
    last_message: TopicMessage | None = None
    subscribers: list[Callable[[TopicMessage], Any]] = field(default_factory=list)


class ROS2Bridge:
    def __init__(self, node_name: str = "codomyrmex", history_depth: int = 100) -> None:
        self.node_name = node_name
        self.history_depth = history_depth
        self.is_connected = False
        self.total_messages = 0
        self._topics: dict[str, _TopicState] = {}
        self._history: dict[str, deque[TopicMessage]] = defaultdict(
            lambda: deque(maxlen=history_depth)
        )

    async def connect(self) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False

    def create_topic(self, name: str, latched: bool = False) -> None:
        self._topics.setdefault(name, _TopicState(name=name, latched=latched))
        self._topics[name].latched = latched

    async def publish(self, topic: str, payload: dict[str, Any]) -> TopicMessage:
        if topic not in self._topics:
            self.create_topic(topic)
        state = self._topics[topic]
        message = TopicMessage(topic=topic, payload=dict(payload))
        state.total_published += 1
        state.last_message = message
        self.total_messages += 1
        self._history[topic].append(message)
        await self._deliver(state, message)
        return message

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[TopicMessage], Any],
        replay_latched: bool = False,
    ) -> None:
        if topic not in self._topics:
            self.create_topic(topic)
        state = self._topics[topic]
        state.subscribers.append(handler)
        if replay_latched and state.latched and state.last_message is not None:
            await self._call_handler(handler, state.last_message)

    def simulate_message(self, topic: str, payload: dict[str, Any]) -> None:
        if topic not in self._topics:
            self.create_topic(topic)
        state = self._topics[topic]
        message = TopicMessage(topic=topic, payload=dict(payload))
        for handler in list(state.subscribers):
            result = handler(message)
            if inspect.isawaitable(result):
                asyncio.create_task(result)

    def get_history(self, topic: str, last_n: int | None = None) -> list[TopicMessage]:
        history = list(self._history.get(topic, []))
        return history[-last_n:] if last_n is not None else history

    def clear_history(self, topic: str | None = None) -> None:
        if topic is None:
            self._history.clear()
            return
        self._history.pop(topic, None)

    def list_topics(self) -> list[TopicInfo]:
        return [
            TopicInfo(
                name=state.name,
                total_published=state.total_published,
                subscriber_count=len(state.subscribers),
                latched=state.latched,
            )
            for state in self._topics.values()
        ]

    async def _deliver(self, state: _TopicState, message: TopicMessage) -> None:
        for handler in list(state.subscribers):
            await self._call_handler(handler, message)

    async def _call_handler(
        self, handler: Callable[[TopicMessage], Any], message: TopicMessage
    ) -> None:
        result = handler(message)
        if inspect.isawaitable(result):
            await result
