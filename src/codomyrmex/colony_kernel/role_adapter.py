"""Role adapter — agents earn roles through consequence history.

Roles are never hard-assigned at startup; they emerge from the observable
track record of each agent. Two assignment algorithms coexist:

Specialization-based (standalone API, assign_role):
  1. trust >= 0.8 AND test_fix/bug_repair actions -> REPAIR_ANT
  2. trust >= 0.8 AND doc_write/memory_index actions -> MEMORY_ANT
  3. trust >= 0.85 AND security_scan/vulnerability_fix actions -> GUARD_ANT
  4. total_proposals >= 20 AND acceptance >= 70% -> DISPATCHER
  5. trust < 0.3 OR recent_consecutive_failures >= 3 -> SANDBOX
  6. default -> SANDBOX (new agents start in sandbox)

Trust-score-based (kernel API, infer_role/update):
  SANDBOX -> REPAIR_ANT (trust >= 0.20, proposals >= 3)
  REPAIR_ANT -> MEMORY_ANT (trust >= 0.35)
  MEMORY_ANT -> DISPATCHER (trust >= 0.50)
  DISPATCHER -> GUARD_ANT (trust >= 0.70)

No external dependencies; relies only on stdlib and the models contract.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from codomyrmex.colony_kernel.models import (
    AgentRole,
    AgentTrustProfile,
    ConsequenceRecord,
    compute_trust_delta,
)

# ---------------------------------------------------------------------------
# ConsequenceMemory protocol and in-memory implementation
# ---------------------------------------------------------------------------


@runtime_checkable
class ConsequenceMemoryProtocol(Protocol):
    """Structural protocol for consequence-memory stores."""

    def store_record(self, record: ConsequenceRecord) -> None:
        """Persist a consequence record."""
        ...

    def get_profile(self, agent_id: str) -> AgentTrustProfile | None:
        """Return the current profile for *agent_id*, or ``None`` if unknown."""
        ...

    def save_profile(self, profile: AgentTrustProfile) -> None:
        """Persist an updated profile."""
        ...

    def records_for_agent(self, agent_id: str) -> list[ConsequenceRecord]:
        """Return all stored records for *agent_id*, oldest first."""
        ...


@dataclass
class ConsequenceMemory:
    """In-process, in-memory consequence store.

    Satisfies :class:`ConsequenceMemoryProtocol`. Intended for single-process
    use; a persistent implementation can be swapped in without changing
    RoleAdapter as long as it satisfies the protocol.
    """

    _profiles: dict[str, AgentTrustProfile] = field(default_factory=dict, init=False)
    _records: dict[str, list[ConsequenceRecord]] = field(
        default_factory=dict, init=False
    )

    def store_record(self, record: ConsequenceRecord) -> None:
        agent_id = record.proposal.agent_id
        if agent_id not in self._records:
            self._records[agent_id] = []
        self._records[agent_id].append(record)

    def get_profile(self, agent_id: str) -> AgentTrustProfile | None:
        return self._profiles.get(agent_id)

    def save_profile(self, profile: AgentTrustProfile) -> None:
        self._profiles[profile.agent_id] = profile

    def records_for_agent(self, agent_id: str) -> list[ConsequenceRecord]:
        return list(self._records.get(agent_id, []))

    def all_profiles(self) -> list[AgentTrustProfile]:
        return list(self._profiles.values())


# ---------------------------------------------------------------------------
# Default trust score for new agents
# ---------------------------------------------------------------------------

_DEFAULT_TRUST_SCORE: float = 0.1
_REPAIR_ACTION_TYPES: frozenset[str] = frozenset({"test_fix", "bug_repair"})
_MEMORY_ACTION_TYPES: frozenset[str] = frozenset({"doc_write", "memory_index"})
_GUARD_ACTION_TYPES: frozenset[str] = frozenset({"security_scan", "vulnerability_fix"})

# Kernel-compatible trust-score thresholds
_ROLE_REPAIR_MIN_TRUST = 0.20
_ROLE_MEMORY_MIN_TRUST = 0.35
_ROLE_DISPATCHER_MIN_TRUST = 0.50
_ROLE_GUARD_MIN_TRUST = 0.70
_ROLE_MIN_PROPOSALS_FOR_PROMOTION = 3


def _successful_action_types(records: list[ConsequenceRecord]) -> set[str]:
    """Return the set of action_types where tests_passed=True and repair_needed=False."""
    return {
        r.proposal.action_type
        for r in records
        if r.tests_passed and not r.repair_needed
    }


def _consecutive_failures(records: list[ConsequenceRecord]) -> int:
    """Count consecutive failures at the end of the record history."""
    count = 0
    for record in reversed(records):
        if not record.tests_passed:
            count += 1
        else:
            break
    return count


# ---------------------------------------------------------------------------
# RoleAdapter
# ---------------------------------------------------------------------------


class RoleAdapter:
    """Assigns roles to agents based on their consequence history.

    Provides two APIs:
    - Specialization-based (standalone): assign_role(agent_id), get_profile(),
      update_profile(record), agents_by_role(role), role_stats()
    - Trust-score-based (kernel): infer_role(profile), update(profile)

    Args:
        consequence_memory: ConsequenceMemoryProtocol instance. Pass None
            to create an internal in-memory ConsequenceMemory (kernel usage).
    """

    def __init__(
        self,
        consequence_memory: ConsequenceMemoryProtocol | None = None,
    ) -> None:
        if consequence_memory is None:
            self._memory: ConsequenceMemoryProtocol = ConsequenceMemory()
        else:
            self._memory = consequence_memory

    # ------------------------------------------------------------------
    # Specialization-based API (standalone)
    # ------------------------------------------------------------------

    def assign_role(self, agent_id: str) -> AgentRole:
        """Assign a role to *agent_id* based on trust, specialisation, and history.

        Returns the appropriate AgentRole following the 6 specialization rules.
        """
        profile = self.get_profile(agent_id)
        records = self._memory.records_for_agent(agent_id)
        successful = _successful_action_types(records)
        trust = profile.trust_score

        # Rule 5: low trust or consecutive failures -> SANDBOX
        if trust < 0.3 or _consecutive_failures(records) >= 3:
            return AgentRole.SANDBOX

        # Rule 3: GUARD_ANT requires trust >= 0.85 and security actions
        if trust >= 0.85 and successful & _GUARD_ACTION_TYPES:
            return AgentRole.GUARD_ANT

        # Rule 1: REPAIR_ANT requires trust >= 0.8 and repair actions
        if trust >= 0.8 and successful & _REPAIR_ACTION_TYPES:
            return AgentRole.REPAIR_ANT

        # Rule 2: MEMORY_ANT requires trust >= 0.8 and memory actions
        if trust >= 0.8 and successful & _MEMORY_ACTION_TYPES:
            return AgentRole.MEMORY_ANT

        # Rule 4: DISPATCHER requires >= 20 proposals and >= 70% acceptance
        total = profile.total_proposals
        accepted = profile.accepted_proposals
        if total >= 20 and total > 0 and (accepted / total) >= 0.70:
            return AgentRole.DISPATCHER

        # Rule 6: default
        return AgentRole.SANDBOX

    def get_profile(self, agent_id: str) -> AgentTrustProfile:
        """Return the profile for *agent_id*, creating a SANDBOX default if absent."""
        profile = self._memory.get_profile(agent_id)
        if profile is None:
            profile = AgentTrustProfile(
                agent_id=agent_id,
                role=AgentRole.SANDBOX,
                trust_score=_DEFAULT_TRUST_SCORE,
            )
            self._memory.save_profile(profile)
        return profile

    def update_profile(self, record: ConsequenceRecord) -> AgentTrustProfile:
        """Apply *record* to the agent's profile, recompute role, and persist.

        Returns the updated AgentTrustProfile.
        """
        agent_id = record.proposal.agent_id
        profile = self.get_profile(agent_id)

        # Compute and apply trust delta
        delta = compute_trust_delta(record)
        profile.apply_delta(delta)
        profile.total_proposals += 1
        if record.tests_passed and not record.repair_needed:
            profile.accepted_proposals += 1
        profile.consequence_history.append(record.consequence_id)
        profile.last_updated = time.time()

        # Store the record and refresh role
        self._memory.store_record(record)
        profile.role = self.assign_role(agent_id)
        self._memory.save_profile(profile)
        return profile

    def agents_by_role(self, role: AgentRole) -> list[str]:
        """Return the sorted agent IDs currently assigned to *role*."""
        if not isinstance(self._memory, ConsequenceMemory):
            return []
        return sorted(
            p.agent_id
            for p in self._memory.all_profiles()
            if p.role == role
        )

    def role_stats(self) -> dict[AgentRole, int]:
        """Return a dict mapping AgentRole to the count of agents in that role.

        All AgentRole values are always present (with count 0 if none).
        """
        counts: dict[AgentRole, int] = dict.fromkeys(AgentRole, 0)
        if not isinstance(self._memory, ConsequenceMemory):
            return counts
        for profile in self._memory.all_profiles():
            # Refresh role for each profile before counting
            role = self.assign_role(profile.agent_id)
            counts[role] = counts.get(role, 0) + 1
        return counts

    # ------------------------------------------------------------------
    # Trust-score-based API (kernel-compatible)
    # ------------------------------------------------------------------

    @staticmethod
    def infer_role(profile: AgentTrustProfile) -> AgentRole:
        """Return the role that fits *profile* based on trust score.

        Kernel-compatible trust-score-only algorithm.
        An agent with fewer than _ROLE_MIN_PROPOSALS_FOR_PROMOTION total
        proposals remains SANDBOX regardless of trust score.
        """
        if profile.total_proposals < _ROLE_MIN_PROPOSALS_FOR_PROMOTION:
            return AgentRole.SANDBOX

        trust = profile.trust_score
        if trust >= _ROLE_GUARD_MIN_TRUST:
            return AgentRole.GUARD_ANT
        if trust >= _ROLE_DISPATCHER_MIN_TRUST:
            return AgentRole.DISPATCHER
        if trust >= _ROLE_MEMORY_MIN_TRUST:
            return AgentRole.MEMORY_ANT
        if trust >= _ROLE_REPAIR_MIN_TRUST:
            return AgentRole.REPAIR_ANT
        return AgentRole.SANDBOX

    def update(self, profile: AgentTrustProfile) -> bool:
        """Recompute and update role on *profile* in-place using trust-score algorithm.

        Returns True if the role changed, False otherwise.
        """
        new_role = self.infer_role(profile)
        if new_role != profile.role:
            profile.role = new_role
            profile.last_updated = time.time()
            return True
        return False


__all__ = [
    "ConsequenceMemory",
    "ConsequenceMemoryProtocol",
    "RoleAdapter",
]
