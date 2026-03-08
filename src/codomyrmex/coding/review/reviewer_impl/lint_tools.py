"""CodeReviewer — LintToolsMixin mixin."""

from __future__ import annotations

from codomyrmex.coding.review.mixins.pyscn import PyscnMixin
from codomyrmex.coding.review.mixins.traditional import TraditionalMixin


class LintToolsMixin(PyscnMixin, TraditionalMixin):
    """LintToolsMixin mixin providing lint_tools capabilities."""
