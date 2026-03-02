"""
A/B Testing and Experimentation Framework

Feature flag extensions for experimentation.
"""

import hashlib
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class VariantType(Enum):
    """Experiment variant types."""
    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class Variant:
    """An experiment variant."""
    name: str
    weight: float = 0.5  # Allocation weight
    value: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Experiment:
    """An A/B test experiment."""
    id: str
    name: str
    variants: list[Variant] = field(default_factory=list)
    enabled: bool = True
    start_date: datetime | None = None
    end_date: datetime | None = None
    traffic_percentage: float = 100.0  # % of users in experiment
    targeting_rules: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        now = datetime.now()
        if not self.enabled:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


@dataclass
class Assignment:
    """User's experiment assignment."""
    experiment_id: str
    variant_name: str
    user_id: str
    assigned_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExperimentEvent:
    """An experiment analytics event."""
    experiment_id: str
    variant_name: str
    user_id: str
    event_type: str
    value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ExperimentManager:
    """Manage A/B test experiments."""

    def __init__(self):
        self._experiments: dict[str, Experiment] = {}
        self._assignments: dict[str, dict[str, Assignment]] = {}
        self._events: list[ExperimentEvent] = []
        self._lock = threading.Lock()

    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        variants: list[Variant] | None = None,
        **kwargs,
    ) -> Experiment:
        """Create a new experiment."""
        if variants is None:
            variants = [
                Variant("control", 0.5),
                Variant("treatment", 0.5),
            ]

        experiment = Experiment(
            id=experiment_id,
            name=name,
            variants=variants,
            **kwargs,
        )

        with self._lock:
            self._experiments[experiment_id] = experiment
            self._assignments[experiment_id] = {}

        return experiment

    def get_experiment(self, experiment_id: str) -> Experiment | None:
        """Get an experiment."""
        return self._experiments.get(experiment_id)

    def get_variant(
        self,
        experiment_id: str,
        user_id: str,
        user_attributes: dict[str, Any] | None = None,
    ) -> Variant | None:
        """Get variant for user (deterministic assignment)."""
        experiment = self._experiments.get(experiment_id)
        if not experiment or not experiment.is_active:
            return None

        # Check targeting rules
        if not self._matches_targeting(experiment, user_attributes or {}):
            return None

        # Check if in traffic percentage
        if not self._in_traffic(experiment_id, user_id, experiment.traffic_percentage):
            return None

        # Check existing assignment
        with self._lock:
            if user_id in self._assignments.get(experiment_id, {}):
                assignment = self._assignments[experiment_id][user_id]
                return next(
                    (v for v in experiment.variants if v.name == assignment.variant_name),
                    None
                )

        # Assign variant deterministically
        variant = self._assign_variant(experiment, user_id)

        with self._lock:
            self._assignments[experiment_id][user_id] = Assignment(
                experiment_id=experiment_id,
                variant_name=variant.name,
                user_id=user_id,
            )

        return variant

    def _assign_variant(self, experiment: Experiment, user_id: str) -> Variant:
        """Assign user to variant deterministically."""
        # Hash user_id + experiment_id for deterministic assignment
        hash_input = f"{experiment.id}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 10000) / 10000.0

        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                return variant

        return experiment.variants[-1]

    def _in_traffic(
        self,
        experiment_id: str,
        user_id: str,
        percentage: float,
    ) -> bool:
        """Check if user is in experiment traffic."""
        hash_input = f"{experiment_id}:traffic:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 10000) / 100.0
        return bucket < percentage

    def _matches_targeting(
        self,
        experiment: Experiment,
        user_attributes: dict[str, Any],
    ) -> bool:
        """Check if user matches targeting rules."""
        rules = experiment.targeting_rules
        if not rules:
            return True

        for key, expected in rules.items():
            actual = user_attributes.get(key)
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        return True

    def track_event(
        self,
        experiment_id: str,
        user_id: str,
        event_type: str,
        value: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track experiment event."""
        assignment = self._assignments.get(experiment_id, {}).get(user_id)
        if not assignment:
            return

        event = ExperimentEvent(
            experiment_id=experiment_id,
            variant_name=assignment.variant_name,
            user_id=user_id,
            event_type=event_type,
            value=value,
            metadata=metadata or {},
        )

        with self._lock:
            self._events.append(event)

    def get_results(self, experiment_id: str) -> dict[str, Any]:
        """Get experiment results summary."""
        assignments = self._assignments.get(experiment_id, {})
        events = [e for e in self._events if e.experiment_id == experiment_id]

        # Count assignments by variant
        variant_counts = {}
        for assignment in assignments.values():
            variant_counts[assignment.variant_name] = (
                variant_counts.get(assignment.variant_name, 0) + 1
            )

        # Count conversions by variant
        conversions = {}
        for event in events:
            if event.event_type == "conversion":
                conversions[event.variant_name] = (
                    conversions.get(event.variant_name, 0) + 1
                )

        # Calculate conversion rates
        rates = {}
        for variant_name, count in variant_counts.items():
            conv_count = conversions.get(variant_name, 0)
            rates[variant_name] = conv_count / count if count > 0 else 0.0

        return {
            "experiment_id": experiment_id,
            "total_assignments": len(assignments),
            "by_variant": variant_counts,
            "conversions": conversions,
            "conversion_rates": rates,
            "event_count": len(events),
        }


__all__ = [
    "Experiment",
    "Variant",
    "VariantType",
    "Assignment",
    "ExperimentEvent",
    "ExperimentManager",
]
