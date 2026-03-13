"""Unit tests for the PBFT Consensus Module.

Zero-Mock Policy: Constructs an authentic network of independent nodes
messaging securely without Mocks, validating standard routing,
tolerated fault drop-offs, and adversarial payload spoofing behaviors.
"""

import pytest

from codomyrmex.collaboration.pbft_consensus import (
    Message,
    MessageType,
    PBFTNetwork,
)


@pytest.mark.unit
def test_pbft_consensus_success():
    """Test standard PBFT consensus with zero faults correctly executes payload."""
    network = PBFTNetwork(node_count=4)
    assert network.f == 1

    network.client_request("consensus_payload_1")

    # Verify all nodes reached consensus and updated their logs
    for node in network.nodes.values():
        assert node.executed_sequence == 1
        assert node.log[1] == "consensus_payload_1"


@pytest.mark.unit
def test_pbft_with_tolerated_fault():
    """Test PBFT mechanism succeeds even when 1 node drops all messages."""
    # N=4, f=1. We will make 1 node adversarial (it drops messages entirely)
    network = PBFTNetwork(node_count=4)
    network.nodes["node_3"].is_adversarial = True

    network.client_request("payload_fault_tolerant")

    # 3 honest nodes should reach consensus via 2f+1 commits
    for i in range(3):
        node = network.nodes[f"node_{i}"]
        assert node.executed_sequence == 1
        assert node.log[1] == "payload_fault_tolerant"

    # Adversarial node did nothing
    assert network.nodes["node_3"].executed_sequence == 0


@pytest.mark.unit
def test_pbft_advancing_sequential_messages():
    """Test sequential requests process linearly across complete quorum."""
    network = PBFTNetwork(node_count=4)

    network.client_request("msg_A")
    network.client_request("msg_B")

    for node in network.nodes.values():
        assert node.executed_sequence == 2
        assert node.log[1] == "msg_A"
        assert node.log[2] == "msg_B"


@pytest.mark.unit
def test_pbft_above_fault_tolerance_fails():
    """Test PBFT consensus halts if Byzantine faults > theoretical threshold."""
    # N=4, f=1. Let's make 2 nodes adversarial!
    network = PBFTNetwork(node_count=4)
    network.nodes["node_2"].is_adversarial = True
    network.nodes["node_3"].is_adversarial = True

    network.client_request("will_fail_to_execute")

    # The remaining 2 nodes cannot form a quorum (need 2f+1 = 3 for commit)
    honest = network.nodes["node_1"]

    # Pre-prepares and prepares will propagate to honest nodes
    assert 1 in honest.pre_prepares
    # But commits won't reach quorum
    assert honest.executed_sequence == 0


@pytest.mark.unit
def test_pbft_adversary_broadcasts_conflicting_payload():
    """Test PBFT ignores adversarial bad actor spoofing PREPARE payloads."""
    network = PBFTNetwork(node_count=4)
    network.nodes["node_3"].is_adversarial = True

    primary_node = network.nodes["node_0"]
    seq = 1

    # Manual leader broadcast bypassing client strictness
    msg = Message(
        type=MessageType.PRE_PREPARE,
        view=0,
        sequence_number=seq,
        payload="true_data",
        sender_id="node_0",
    )
    for node in network.nodes.values():
        node.receive(msg)

    # Before process_queue fully evaluates valid PREPAREs, inject adversarial lie
    network.broadcast(
        Message(
            type=MessageType.PREPARE,
            view=0,
            sequence_number=seq,
            payload="malicious_lie",
            sender_id="node_3",
        )
    )

    network.process_queue()

    # Honest nodes should STILL reach consensus on true_data
    assert network.nodes["node_1"].log[1] == "true_data"
