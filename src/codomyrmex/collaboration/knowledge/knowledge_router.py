"""Knowledge query routing by expertise.

Routes knowledge queries to the agent with the highest relevant
expertise, using tag overlap scoring and recency weighting.
"""

from __future__ import annotations

import time

from codomyrmex.collaboration.knowledge.models import (
    ExpertiseProfile,
    QueryResult,
)
from codomyrmex.collaboration.knowledge.shared_pool import SharedMemoryPool


class KnowledgeRouter:
    """Route queries to the most expert agent.

    Scores agents by tag overlap and domain match, weighted by
    recency of their last contribution.

    Example::

        router = KnowledgeRouter(pool=pool)
        router.register_expert(ExpertiseProfile(
            agent_id="tester",
            domains={"testing": 0.9, "ci_cd": 0.7},
            tags=["pytest", "coverage"],
        ))
        result = router.query("How to write pytest fixtures?")
    """

    def __init__(
        self,
        pool: SharedMemoryPool | None = None,
        recency_weight: float = 0.2,
    ) -> None:
        """Execute   Init   operations natively."""
        self._pool = pool or SharedMemoryPool()
        self._experts: dict[str, ExpertiseProfile] = {}
        self._recency_weight = recency_weight

    @property
    def expert_count(self) -> int:
        """Number of registered experts."""
        return len(self._experts)

    @property
    def pool(self) -> SharedMemoryPool:
        """Underlying shared memory pool."""
        return self._pool

    def register_expert(self, profile: ExpertiseProfile) -> None:
        """Register or update an agent's expertise profile."""
        self._experts[profile.agent_id] = profile

    def unregister_expert(self, agent_id: str) -> bool:
        """Remove an expert. Returns True if found."""
        return self._experts.pop(agent_id, None) is not None

    def get_expert(self, agent_id: str) -> ExpertiseProfile | None:
        """Look up an expert profile."""
        return self._experts.get(agent_id)

    def route(self, query: str) -> tuple[str, float]:
        """Route a query to the best expert.

        Scoring:
        - Tag overlap: how many query terms match expert tags
        - Domain match: how many query terms match expert domains
        - Recency: boost for recently active experts

        Args:
            query: Knowledge query string.

        Returns:
            (agent_id, confidence) of the best match, or ("", 0.0).
        """
        if not self._experts:
            return ("", 0.0)

        query_terms = set(query.lower().split())
        now = time.time()
        best_agent = ""
        best_score = 0.0

        for agent_id, profile in self._experts.items():
            # Tag overlap
            expert_tags = set(t.lower() for t in profile.tags)
            tag_overlap = len(query_terms & expert_tags)

            # Domain match
            domain_score = 0.0
            for domain, confidence in profile.domains.items():
                if domain.lower() in query_terms or any(
                    domain.lower() in term for term in query_terms
                ):
                    domain_score += confidence

            # Recency boost (exponential decay, 1-day half-life)
            age_hours = (now - profile.last_active) / 3600
            recency = 1.0 / (1.0 + age_hours / 24.0)

            # Composite score
            score = (
                tag_overlap * 0.4
                + domain_score * 0.4
                + recency * self._recency_weight
            )

            if score > best_score:
                best_score = score
                best_agent = agent_id

        # Normalize confidence to [0, 1]
        confidence = min(1.0, best_score) if best_score > 0 else 0.0
        return (best_agent, confidence)

    def query(self, question: str, domains: list[str] | None = None) -> QueryResult:
        """Route a query and retrieve matching knowledge.

        Args:
            question: Knowledge query.
            domains: Optional domain filter.

        Returns:
            QueryResult with entries and routing info.
        """
        start = time.monotonic()

        agent_id, confidence = self.route(question)
        query_terms = question.lower().split()

        entries = self._pool.search_global(
            query_terms=query_terms,
            domains=domains,
            requesting_agent=agent_id,
        )

        elapsed_ms = (time.monotonic() - start) * 1000

        return QueryResult(
            query=question,
            entries=entries,
            routed_to=agent_id,
            confidence=confidence,
            search_time_ms=elapsed_ms,
        )

    def suggest_experts(self, query: str, n: int = 3) -> list[tuple[str, float]]:
        """Return top-N experts for a query.

        Args:
            query: Knowledge query.
            n: Maximum number of experts to return.

        Returns:
            List of (agent_id, score) tuples, descending.
        """
        if not self._experts:
            return []

        query_terms = set(query.lower().split())
        now = time.time()
        scored: list[tuple[str, float]] = []

        for agent_id, profile in self._experts.items():
            expert_tags = set(t.lower() for t in profile.tags)
            tag_overlap = len(query_terms & expert_tags)
            domain_score = sum(
                conf for dom, conf in profile.domains.items()
                if dom.lower() in query_terms
            )
            age_hours = (now - profile.last_active) / 3600
            recency = 1.0 / (1.0 + age_hours / 24.0)
            score = tag_overlap * 0.4 + domain_score * 0.4 + recency * self._recency_weight
            if score > 0:
                scored.append((agent_id, min(1.0, score)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n]


__all__ = ["KnowledgeRouter"]
