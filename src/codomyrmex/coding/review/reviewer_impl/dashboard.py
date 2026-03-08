"""CodeReviewer — DashboardMixin mixin."""

from __future__ import annotations

import os

from codomyrmex.coding.review.mixins.codesmells import CodeSmellsMixin
from codomyrmex.coding.review.mixins.complexity import ComplexityMixin
from codomyrmex.coding.review.mixins.deadcode import DeadCodeMixin
from codomyrmex.coding.review.mixins.metrics import MetricsMixin
from codomyrmex.coding.review.mixins.performance import PerformanceMixin
from codomyrmex.coding.review.mixins.refactoring import RefactoringMixin
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class DashboardMixin(CodeSmellsMixin, MetricsMixin, ComplexityMixin, DeadCodeMixin, PerformanceMixin, RefactoringMixin):
    """DashboardMixin mixin providing dashboard capabilities."""

    def _count_total_files(self) -> int:
        """Count total files in project."""
        count = 0
        for _root, dirs, files in os.walk(self.project_root):
            dirs[:] = [
                d
                for d in dirs
                if d not in {".git", "__pycache__", "node_modules", ".venv", "venv", ".pyscn"}
            ]
            count += len([f for f in files if f.endswith(".py")])
        return count

    def _count_total_lines(self) -> int:
        """Count total lines of code in project."""
        total_lines = 0
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [
                d
                for d in dirs
                if d not in {".git", "__pycache__", "node_modules", ".venv", "venv", ".pyscn"}
            ]
            for file in files:
                if file.endswith(".py"):
                    try:
                        with open(os.path.join(root, file), encoding="utf-8") as f:
                            total_lines += len(f.readlines())
                    except Exception as e:
                        logger.debug("Failed to count lines in file: %s", e)
        return total_lines
