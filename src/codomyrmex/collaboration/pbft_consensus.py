"""Practical Byzantine Fault Tolerance (PBFT) Consensus Mechanism.

Provides robust adversarial fault-tolerant message phases for distributed
agent collaboration networks, allowing them to agree on shared states
even when a subset of nodes are faulty or malicious.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any


class MessageType(Enum):
    """PBFT Message Phases."""

    REQUEST = "REQUEST"
    PRE_PREPARE = "PRE_PREPARE"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"
    REPLY = "REPLY"


@dataclass(frozen=True)
class Message:
    """A consensus message passed between nodes."""

    type: MessageType
    view: int
    sequence_number: int
    payload: Any
    sender_id: str


class PBFTNode:
    """A single node participating in PBFT consensus."""

    def __init__(self, node_id: str, network: "PBFTNetwork") -> None:
        """Initialize PBFT node parameters and phases logs."""
        self.node_id = node_id
        self.network = network
        self.view = 0

        # Logs to store messages received during different phases
        self.pre_prepares: dict[int, Message] = {}
        self.prepares: dict[int, set[str]] = defaultdict(set)
        self.commits: dict[int, set[str]] = defaultdict(set)

        self.executed_sequence: int = 0
        self.log: dict[int, Any] = {}

        # Adversarial flag for testing
        self.is_adversarial = False

    def receive(self, message: Message) -> None:
        """Handle incoming consensus messages."""
        if message.view < self.view:
            return  # Stale message
        if self.is_adversarial:
            # Adversarial nodes ignore strict logic and drop messages
            # or intentionally spoof responses under manual test conditions
            return

        if message.type == MessageType.PRE_PREPARE:
            self._handle_pre_prepare(message)
        elif message.type == MessageType.PREPARE:
            self._handle_prepare(message)
        elif message.type == MessageType.COMMIT:
            self._handle_commit(message)

    def _handle_pre_prepare(self, msg: Message) -> None:
        """Process a PRE_PREPARE message from the leader."""
        seq = msg.sequence_number
        if seq not in self.pre_prepares:
            self.pre_prepares[seq] = msg
            # Broadcast PREPARE to all nodes
            self.network.broadcast(
                Message(
                    type=MessageType.PREPARE,
                    view=self.view,
                    sequence_number=seq,
                    payload=msg.payload,
                    sender_id=self.node_id,
                )
            )

    def _handle_prepare(self, msg: Message) -> None:
        """Process a PREPARE message from a replica."""
        seq = msg.sequence_number
        if seq not in self.pre_prepares:
            return  # Must have seen the pre_prepare first theoretically

        # Verify the prepare matches the pre_prepare payload
        if self.pre_prepares[seq].payload != msg.payload:
            return  # Conflicting payload

        self.prepares[seq].add(msg.sender_id)

        # Need 2f matching PREPARE messages
        if len(self.prepares[seq]) >= 2 * self.network.f:
            # Broadcast COMMIT
            if seq not in self.commits or self.node_id not in self.commits[seq]:
                self.commits[seq].add(self.node_id)
                self.network.broadcast(
                    Message(
                        type=MessageType.COMMIT,
                        view=self.view,
                        sequence_number=seq,
                        payload=msg.payload,
                        sender_id=self.node_id,
                    )
                )

    def _handle_commit(self, msg: Message) -> None:
        """Process a COMMIT message from a replica."""
        seq = msg.sequence_number
        if seq not in self.pre_prepares:
            return

        if self.pre_prepares[seq].payload != msg.payload:
            return

        self.commits[seq].add(msg.sender_id)

        # Need 2f + 1 matching COMMIT messages
        if len(self.commits[seq]) >= 2 * self.network.f + 1:
            if seq == self.executed_sequence + 1:
                self._execute(seq, msg.payload)

    def _execute(self, seq: int, payload: Any) -> None:
        """Execute the confirmed consensus payload."""
        self.log[seq] = payload
        self.executed_sequence = seq


class PBFTNetwork:
    """A simulated network managing robust message transport for PBFT nodes."""

    def __init__(self, node_count: int) -> None:
        """Initialize PBFT network with N nodes."""
        self.nodes: dict[str, PBFTNode] = {}
        for i in range(node_count):
            node_id = f"node_{i}"
            self.nodes[node_id] = PBFTNode(node_id, self)

        # Tolerated faults f = floor((N-1)/3)
        self.f = (node_count - 1) // 3

        # Primary leader is node_0 (view 0)
        self.primary_id = "node_0"

        self.message_queue: list[Message] = []

    def broadcast(self, message: Message) -> None:
        """Enqueue a message to be processed by all nodes."""
        self.message_queue.append(message)

    def process_queue(self) -> None:
        """Process all pending messages in the network."""
        while self.message_queue:
            msg = self.message_queue.pop(0)
            for node in self.nodes.values():
                node.receive(msg)

    def client_request(self, payload: Any) -> None:
        """Client sends a request directly to the primary leader."""
        seq = self.nodes[self.primary_id].executed_sequence + 1

        primary_node = self.nodes[self.primary_id]
        if not primary_node.is_adversarial:
            msg = Message(
                type=MessageType.PRE_PREPARE,
                view=primary_node.view,
                sequence_number=seq,
                payload=payload,
                sender_id=self.primary_id,
            )
            primary_node.receive(msg)
            for node_id, node in self.nodes.items():
                if node_id != self.primary_id:
                    node.receive(msg)

        self.process_queue()
