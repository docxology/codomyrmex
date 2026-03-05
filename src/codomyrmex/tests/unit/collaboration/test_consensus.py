"""Unit tests for collaboration/coordination/consensus.py.

Covers VotingMechanism, ConsensusBuilder, Vote, Proposal, VotingResult, and
the async reach_consensus() path that raises ConsensusError when all agents fail.
"""

import pytest

from codomyrmex.collaboration.coordination.consensus import (
    ConsensusBuilder,
    Proposal,
    Vote,
    VoteType,
    VotingMechanism,
    VotingResult,
)
from codomyrmex.collaboration.exceptions import ConsensusError

pytestmark = pytest.mark.unit


class TestVote:
    """Tests for the Vote dataclass."""

    def test_vote_yes_stored(self):
        v = Vote(voter_id="a1", vote=VoteType.YES)
        assert v.vote == VoteType.YES

    def test_vote_no_stored(self):
        v = Vote(voter_id="a1", vote=VoteType.NO)
        assert v.vote == VoteType.NO

    def test_vote_abstain_stored(self):
        v = Vote(voter_id="a1", vote=VoteType.ABSTAIN)
        assert v.vote == VoteType.ABSTAIN

    def test_voter_id_stored(self):
        v = Vote(voter_id="voter-7", vote=VoteType.YES)
        assert v.voter_id == "voter-7"

    def test_reason_defaults_to_none(self):
        v = Vote(voter_id="a1", vote=VoteType.YES)
        assert v.reason is None

    def test_reason_can_be_set(self):
        v = Vote(voter_id="a1", vote=VoteType.YES, reason="I agree")
        assert v.reason == "I agree"

    def test_to_dict_contains_expected_keys(self):
        v = Vote(voter_id="a1", vote=VoteType.YES, reason="ok")
        d = v.to_dict()
        assert "voter_id" in d and "vote" in d and "timestamp" in d and "reason" in d

    def test_to_dict_vote_is_string_value(self):
        v = Vote(voter_id="a1", vote=VoteType.YES)
        assert v.to_dict()["vote"] == "yes"


class TestProposal:
    """Tests for the Proposal dataclass."""

    def test_proposal_fields_stored(self):
        p = Proposal(
            proposal_id="p-1",
            title="Test",
            description="desc",
            proposer_id="agent-1",
        )
        assert p.proposal_id == "p-1"
        assert p.title == "Test"
        assert p.proposer_id == "agent-1"

    def test_deadline_defaults_to_none(self):
        p = Proposal(proposal_id="p-1", title="T", description="D", proposer_id="a")
        assert p.deadline is None

    def test_metadata_defaults_to_empty(self):
        p = Proposal(proposal_id="p-1", title="T", description="D", proposer_id="a")
        assert p.metadata == {}

    def test_to_dict_contains_proposal_id(self):
        p = Proposal(proposal_id="p-1", title="T", description="D", proposer_id="a")
        assert p.to_dict()["proposal_id"] == "p-1"


class TestVotingResult:
    """Tests for the VotingResult dataclass."""

    def _make_result(self, **kwargs):
        defaults = {
            "proposal_id": "p-1",
            "passed": True,
            "votes_for": 3,
            "votes_against": 1,
            "abstentions": 0,
            "total_voters": 4,
            "quorum_met": True,
        }
        defaults.update(kwargs)
        return VotingResult(**defaults)

    def test_participation_rate_all_voted(self):
        r = self._make_result(
            votes_for=3, votes_against=1, abstentions=0, total_voters=4
        )
        assert r.participation_rate == 1.0

    def test_participation_rate_zero_voters(self):
        r = self._make_result(
            votes_for=0, votes_against=0, abstentions=0, total_voters=0
        )
        assert r.participation_rate == 0.0

    def test_participation_rate_partial(self):
        r = self._make_result(
            votes_for=1, votes_against=1, abstentions=0, total_voters=4
        )
        assert r.participation_rate == 0.5

    def test_to_dict_passed_key(self):
        r = self._make_result(passed=True)
        assert r.to_dict()["passed"] is True

    def test_to_dict_quorum_met_key(self):
        r = self._make_result(quorum_met=True)
        assert r.to_dict()["quorum_met"] is True


class TestVotingMechanism:
    """Tests for VotingMechanism."""

    def test_invalid_quorum_raises_consensus_error(self):
        with pytest.raises(ConsensusError):
            VotingMechanism(quorum=1.5)

    def test_invalid_threshold_raises_consensus_error(self):
        with pytest.raises(ConsensusError):
            VotingMechanism(threshold=-0.1)

    def test_create_proposal_returns_proposal(self):
        vm = VotingMechanism()
        p = vm.create_proposal("Title", "Desc", "agent-1")
        assert isinstance(p, Proposal)
        assert p.title == "Title"

    def test_proposal_id_is_uuid_string(self):
        vm = VotingMechanism()
        p = vm.create_proposal("T", "D", "a")
        assert len(p.proposal_id) == 36

    def test_cast_vote_unknown_proposal_raises(self):
        vm = VotingMechanism()
        with pytest.raises(ConsensusError):
            vm.cast_vote("nonexistent-id", "voter-1", VoteType.YES)

    def test_cast_vote_returns_vote_object(self):
        vm = VotingMechanism()
        p = vm.create_proposal("T", "D", "a")
        v = vm.cast_vote(p.proposal_id, "voter-1", VoteType.YES, reason="ok")
        assert isinstance(v, Vote)
        assert v.vote == VoteType.YES

    def test_get_votes_returns_cast_votes(self):
        vm = VotingMechanism()
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.YES)
        vm.cast_vote(p.proposal_id, "v2", VoteType.NO)
        votes = vm.get_votes(p.proposal_id)
        assert len(votes) == 2

    def test_tally_unknown_proposal_raises(self):
        vm = VotingMechanism()
        with pytest.raises(ConsensusError):
            vm.tally_votes("nonexistent-id", total_voters=3)

    def test_tally_majority_yes_passes(self):
        vm = VotingMechanism(quorum=0.5, threshold=0.5)
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.YES)
        vm.cast_vote(p.proposal_id, "v2", VoteType.YES)
        vm.cast_vote(p.proposal_id, "v3", VoteType.NO)
        result = vm.tally_votes(p.proposal_id, total_voters=4)
        assert result.passed is True
        assert result.votes_for == 2
        assert result.votes_against == 1

    def test_tally_majority_no_fails(self):
        vm = VotingMechanism(quorum=0.5, threshold=0.6)
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.NO)
        vm.cast_vote(p.proposal_id, "v2", VoteType.NO)
        vm.cast_vote(p.proposal_id, "v3", VoteType.YES)
        result = vm.tally_votes(p.proposal_id, total_voters=4)
        assert result.passed is False

    def test_tally_quorum_not_met_fails(self):
        vm = VotingMechanism(quorum=0.8, threshold=0.5)
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.YES)
        result = vm.tally_votes(p.proposal_id, total_voters=10)
        assert result.quorum_met is False
        assert result.passed is False

    def test_abstention_counted_separately(self):
        vm = VotingMechanism()
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.ABSTAIN)
        result = vm.tally_votes(p.proposal_id, total_voters=1)
        assert result.abstentions == 1
        assert result.votes_for == 0

    def test_get_result_returns_result_after_tally(self):
        vm = VotingMechanism()
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.YES)
        vm.tally_votes(p.proposal_id, total_voters=1)
        r = vm.get_result(p.proposal_id)
        assert isinstance(r, VotingResult)

    def test_get_result_returns_none_for_unknown(self):
        vm = VotingMechanism()
        assert vm.get_result("unknown") is None

    def test_duplicate_vote_overwrites(self):
        vm = VotingMechanism()
        p = vm.create_proposal("T", "D", "a")
        vm.cast_vote(p.proposal_id, "v1", VoteType.NO)
        vm.cast_vote(p.proposal_id, "v1", VoteType.YES)
        votes = vm.get_votes(p.proposal_id)
        assert len(votes) == 1
        assert votes[0].vote == VoteType.YES


class TestConsensusBuilder:
    """Tests for ConsensusBuilder."""

    def test_propose_value_and_retrieve(self):
        b = ConsensusBuilder()
        b.propose_value("key", "agent-1", 42)
        proposals = b.get_proposals("key")
        assert proposals["agent-1"] == 42

    def test_multiple_agents_propose(self):
        b = ConsensusBuilder()
        b.propose_value("k", "a1", "val")
        b.propose_value("k", "a2", "val")
        b.propose_value("k", "a3", "other")
        assert len(b.get_proposals("k")) == 3

    def test_check_consensus_reached(self):
        b = ConsensusBuilder(convergence_threshold=0.6)
        b.propose_value("k", "a1", "agreed")
        b.propose_value("k", "a2", "agreed")
        b.propose_value("k", "a3", "agreed")
        b.propose_value("k", "a4", "other")
        result = b.check_consensus("k", total_agents=4)
        assert result == "agreed"

    def test_check_consensus_not_reached(self):
        b = ConsensusBuilder(convergence_threshold=0.9)
        b.propose_value("k", "a1", "x")
        b.propose_value("k", "a2", "y")
        assert b.check_consensus("k", total_agents=2) is None

    def test_check_consensus_unknown_key_returns_none(self):
        b = ConsensusBuilder()
        assert b.check_consensus("missing-key", total_agents=3) is None

    def test_get_consensus_returns_none_before_check(self):
        b = ConsensusBuilder()
        b.propose_value("k", "a1", "v")
        assert b.get_consensus("k") is None

    def test_get_consensus_returns_value_after_check(self):
        b = ConsensusBuilder(convergence_threshold=0.5)
        b.propose_value("k", "a1", "agreed")
        b.check_consensus("k", total_agents=1)
        assert b.get_consensus("k") == "agreed"

    def test_clear_specific_key(self):
        b = ConsensusBuilder()
        b.propose_value("k", "a1", "v")
        b.clear("k")
        assert b.get_proposals("k") == {}

    def test_clear_all(self):
        b = ConsensusBuilder()
        b.propose_value("k1", "a1", "v1")
        b.propose_value("k2", "a1", "v2")
        b.clear()
        assert b.get_proposals("k1") == {}
        assert b.get_proposals("k2") == {}

    def test_propose_overrides_previous_value_for_same_agent(self):
        b = ConsensusBuilder()
        b.propose_value("k", "a1", "first")
        b.propose_value("k", "a1", "second")
        assert b.get_proposals("k")["a1"] == "second"

    def test_numeric_consensus(self):
        b = ConsensusBuilder(convergence_threshold=0.5)
        b.propose_value("timeout", "a1", 30)
        b.propose_value("timeout", "a2", 30)
        result = b.check_consensus("timeout", total_agents=2)
        assert result == 30


class TestConsensusBuilderReachConsensus:
    """Tests for the async reach_consensus() method."""

    @pytest.mark.asyncio
    async def test_all_agents_fail_raises_consensus_error(self):
        from codomyrmex.collaboration.agents.base import CollaborativeAgent

        builder = ConsensusBuilder()
        agents = [
            CollaborativeAgent(agent_id="a1", name="Agent 1"),
            CollaborativeAgent(agent_id="a2", name="Agent 2"),
        ]

        def always_fail(agent):
            raise RuntimeError("agent unavailable")

        with pytest.raises(ConsensusError):
            await builder.reach_consensus(
                key="test-key",
                agents=agents,
                value_fn=always_fail,
                max_rounds=1,
            )

    @pytest.mark.asyncio
    async def test_all_agree_returns_consensus_value(self):
        from codomyrmex.collaboration.agents.base import CollaborativeAgent

        builder = ConsensusBuilder(convergence_threshold=0.5)
        agents = [
            CollaborativeAgent(agent_id="a1", name="Agent 1"),
            CollaborativeAgent(agent_id="a2", name="Agent 2"),
        ]

        def always_agree(agent):
            return "consensus-value"

        result = await builder.reach_consensus(
            key="agreement",
            agents=agents,
            value_fn=always_agree,
            max_rounds=3,
        )
        assert result == "consensus-value"

    @pytest.mark.asyncio
    async def test_no_consensus_after_max_rounds_returns_none(self):
        from codomyrmex.collaboration.agents.base import CollaborativeAgent

        builder = ConsensusBuilder(convergence_threshold=1.0)
        agents = [
            CollaborativeAgent(agent_id="a1", name="Agent 1"),
            CollaborativeAgent(agent_id="a2", name="Agent 2"),
        ]
        counter = {"n": 0}

        def alternating(agent):
            counter["n"] += 1
            return f"value-{agent.agent_id}"

        result = await builder.reach_consensus(
            key="no-agreement",
            agents=agents,
            value_fn=alternating,
            max_rounds=2,
        )
        assert result is None
