"""CodeReviewer — ReportingMixin mixin."""

from __future__ import annotations

from codomyrmex.coding.review.mixins.reporting import (
    ReportingMixin as _ReportingMixinBase,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class ReportingMixin(_ReportingMixinBase):
    """ReportingMixin mixin providing reporting capabilities."""

    def _get_score_color(self, score: float) -> str:
        """Get color for score display."""
        if score >= 90:
            return "#28a745"  # Green
        if score >= 80:
            return "#ffc107"  # Yellow
        if score >= 70:
            return "#fd7e14"  # Orange
        return "#dc3545"  # Red
