"""CodeReviewer — AnalysisPatternsMixin mixin."""

from __future__ import annotations

from codomyrmex.coding.review.mixins.architecture import ArchitectureMixin
from codomyrmex.coding.review.mixins.complexity import ComplexityMixin
from codomyrmex.coding.review.mixins.deadcode import DeadCodeMixin
from codomyrmex.coding.review.mixins.refactoring import RefactoringMixin


class AnalysisPatternsMixin(
    ArchitectureMixin, ComplexityMixin, DeadCodeMixin, RefactoringMixin
):
    """AnalysisPatternsMixin mixin providing analysis capabilities."""
