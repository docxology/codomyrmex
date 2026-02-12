"""EpistemicEngine — orchestrator for truth verification."""

from __future__ import annotations

from typing import List

from codomyrmex.meme.epistemic.models import Fact, Belief, Evidence, EpistemicState
from codomyrmex.meme.epistemic.truth import verify_claim


class EpistemicEngine:
    """Engine for managing knowledge, truth, and belief systems."""

    def __init__(self) -> None:
        self.state = EpistemicState()

    def add_fact(self, fact: Fact) -> None:
        """Register a new fact."""
        self.state.facts.append(fact)

    def assess_claim(self, statement: str, evidence: List[Evidence]) -> Fact:
        """Verify a statement against provided evidence and update state."""
        fact = verify_claim(statement, evidence)
        # If high confidence, accept as fact
        if fact.confidence > 0.8:
            self.add_fact(fact)
        return fact
        
    def detect_contradictions(self) -> List[str]:
        """Identify contradictions between facts and beliefs."""
        conflicts = []
        # Placeholder for real semantic contradiction logic
        # For now just checking direct negation strings
        for belief in self.state.beliefs:
            for fact in self.state.facts:
                if f"not {fact.statement}" in belief.statement:
                    conflicts.append(f"Conflict: {belief.statement} vs Fact: {fact.statement}")
        return conflicts
