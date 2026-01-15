from typing import Any, Optional

from dataclasses import dataclass, field
import numpy as np

from codomyrmex.cerebrum.core.exceptions import CaseNotFoundError, InvalidCaseError
from codomyrmex.cerebrum.core.utils import (
    compute_cosine_similarity,
    compute_euclidean_distance,
    normalize_features,
)
from codomyrmex.logging_monitoring import get_logger

"""Case management for case-based reasoning."""

logger = get_logger(__name__)


@dataclass
class Case:
    """Represents a case in case-based reasoning.

    A case consists of features (problem description), context (additional
    information), and outcome (solution or result).
    """

    case_id: str
    features: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    outcome: Optional[Any] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate case after initialization."""
        if not self.case_id:
            raise InvalidCaseError("Case ID cannot be empty")
        if not self.features:
            raise InvalidCaseError("Case must have at least one feature")

    def to_dict(self) -> dict[str, Any]:
        """Convert case to dictionary."""
        return {
            "case_id": self.case_id,
            "features": self.features,
            "context": self.context,
            "outcome": self.outcome,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Case":
        """Create case from dictionary."""
        return cls(
            case_id=data["case_id"],
            features=data["features"],
            context=data.get("context", {}),
            outcome=data.get("outcome"),
            metadata=data.get("metadata", {}),
        )


class CaseBase:
    """Collection of cases with similarity search capabilities."""

    def __init__(self, similarity_metric: str = "euclidean"):
        """Initialize case base.

        Args:
            similarity_metric: Metric to use ("euclidean", "cosine")
        """
        self.cases: dict[str, Case] = {}
        self.similarity_metric = similarity_metric
        self.logger = get_logger(__name__)

    def add_case(self, case: Case) -> None:
        """Add a case to the case base.

        Args:
            case: Case to add
        """
        if case.case_id in self.cases:
            self.logger.warning(f"Case {case.case_id} already exists, updating")
        self.cases[case.case_id] = case
        self.logger.debug(f"Added case {case.case_id}")

    def get_case(self, case_id: str) -> Case:
        """Retrieve a case by ID.

        Args:
            case_id: Case identifier

        Returns:
            Case object

        Raises:
            CaseNotFoundError: If case not found
        """
        if case_id not in self.cases:
            raise CaseNotFoundError(f"Case {case_id} not found")
        return self.cases[case_id]

    def remove_case(self, case_id: str) -> None:
        """Remove a case from the case base.

        Args:
            case_id: Case identifier
        """
        if case_id in self.cases:
            del self.cases[case_id]
            self.logger.debug(f"Removed case {case_id}")

    def compute_similarity(self, case1: Case, case2: Case) -> float:
        """Compute similarity between two cases.

        Args:
            case1: First case
            case2: Second case

        Returns:
            Similarity score in [0, 1] (higher = more similar)
        """
        features1 = normalize_features(case1.features)
        features2 = normalize_features(case2.features)

        if self.similarity_metric == "euclidean":
            distance = compute_euclidean_distance(features1, features2)
            # Convert distance to similarity (inverse relationship)
            similarity = 1.0 / (1.0 + distance)
        elif self.similarity_metric == "cosine":
            similarity = compute_cosine_similarity(features1, features2)
        else:
            raise ValueError(f"Unknown similarity metric: {self.similarity_metric}")

        return similarity

    def retrieve_similar(
        self, query: Case, k: int = 10, threshold: float = 0.0
    ) -> list[tuple[Case, float]]:
        """Retrieve k most similar cases to the query.

        Args:
            query: Query case
            k: Number of cases to retrieve
            threshold: Minimum similarity threshold

        Returns:
            List of (case, similarity) tuples, sorted by similarity (descending)
        """
        similarities = []
        for case in self.cases.values():
            if case.case_id == query.case_id:
                continue  # Skip the query case itself
            similarity = self.compute_similarity(query, case)
            if similarity >= threshold:
                similarities.append((case, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def update_case(self, case_id: str, outcome: Any, **kwargs) -> None:
        """Update a case with new outcome or metadata.

        Args:
            case_id: Case identifier
            outcome: New outcome value
            **kwargs: Additional metadata to update
        """
        if case_id not in self.cases:
            raise CaseNotFoundError(f"Case {case_id} not found")

        case = self.cases[case_id]
        case.outcome = outcome
        case.metadata.update(kwargs)
        self.logger.debug(f"Updated case {case_id}")

    def size(self) -> int:
        """Get the number of cases in the case base."""
        return len(self.cases)

    def clear(self) -> None:
        """Clear all cases from the case base."""
        self.cases.clear()
        self.logger.debug("Cleared case base")

    def to_dict(self) -> dict[str, Any]:
        """Convert case base to dictionary."""
        return {
            "cases": {case_id: case.to_dict() for case_id, case in self.cases.items()},
            "similarity_metric": self.similarity_metric,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CaseBase":
        """Create case base from dictionary."""
        case_base = cls(similarity_metric=data.get("similarity_metric", "euclidean"))
        for case_data in data["cases"].values():
            case = Case.from_dict(case_data)
            case_base.add_case(case)
        return case_base


class CaseRetriever:
    """Retrieves similar cases using various strategies."""

    def __init__(self, case_base: CaseBase, weighting_strategy: str = "distance"):
        """Initialize case retriever.

        Args:
            case_base: Case base to search
            weighting_strategy: Strategy for weighting cases ("distance", "frequency", "hybrid")
        """
        self.case_base = case_base
        self.weighting_strategy = weighting_strategy
        self.logger = get_logger(__name__)

    def retrieve(
        self, query: Case, k: int = 10, threshold: float = 0.0
    ) -> list[tuple[Case, float]]:
        """Retrieve similar cases.

        Args:
            query: Query case
            k: Number of cases to retrieve
            threshold: Minimum similarity threshold

        Returns:
            List of (case, weight) tuples
        """
        similar_cases = self.case_base.retrieve_similar(query, k=k, threshold=threshold)

        if self.weighting_strategy == "distance":
            # Use similarity as weight directly
            return similar_cases
        elif self.weighting_strategy == "frequency":
            # Weight by frequency of case usage (if tracked in metadata)
            weighted = []
            for case, similarity in similar_cases:
                frequency = case.metadata.get("frequency", 1.0)
                weight = similarity * frequency
                weighted.append((case, weight))
            weighted.sort(key=lambda x: x[1], reverse=True)
            return weighted
        elif self.weighting_strategy == "hybrid":
            # Combine distance and frequency
            weighted = []
            for case, similarity in similar_cases:
                frequency = case.metadata.get("frequency", 1.0)
                weight = similarity * 0.7 + frequency * 0.3
                weighted.append((case, weight))
            weighted.sort(key=lambda x: x[1], reverse=True)
            return weighted
        else:
            return similar_cases
