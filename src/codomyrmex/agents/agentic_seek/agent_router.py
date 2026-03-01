"""Heuristic agent router for agenticSeek query classification.

Mirrors the routing logic of ``sources.router.AgentRouter`` in the
upstream agenticSeek project, but uses lightweight keyword + heuristic
classification instead of requiring the ``transformers`` / ``torch``
ML dependencies.

Reference: https://github.com/Fosowl/agenticSeek/blob/main/sources/router.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from codomyrmex.agents.agentic_seek.agent_types import AgenticSeekAgentType

# ---------------------------------------------------------------------------
# Keyword dictionaries
# ---------------------------------------------------------------------------

_CODER_KEYWORDS: frozenset[str] = frozenset({
    "code", "script", "program", "function", "class", "debug", "compile",
    "python", "java", "golang", "go lang", "bash", "shell", "c language",
    "algorithm", "implement", "refactor", "unittest", "pytest", "coding",
    "bug", "error", "exception", "traceback", "syntax", "variable",
    "loop", "recursion", "api", "endpoint", "sdk", "library",
})

_BROWSER_KEYWORDS: frozenset[str] = frozenset({
    "search", "browse", "web", "website", "url", "link", "google",
    "online", "internet", "download", "page", "navigate", "scrape",
    "http", "html", "css", "find online", "look up", "research online",
})

_FILE_KEYWORDS: frozenset[str] = frozenset({
    "file", "folder", "directory", "rename", "move", "copy", "delete",
    "create file", "read file", "write file", "find file", "locate",
    "path", "disk", "filesystem", "ls", "mkdir", "rm", "cp", "mv",
})

_PLANNER_KEYWORDS: frozenset[str] = frozenset({
    "plan", "step by step", "break down", "organise", "organize",
    "project", "workflow", "pipeline", "schedule", "roadmap",
    "multi-step", "complex task", "divide", "strategy",
})

# Complexity indicators
_HIGH_COMPLEXITY_INDICATORS: frozenset[str] = frozenset({
    "then", "after that", "next", "finally", "step", "steps",
    "first", "second", "third", "multiple", "complex",
    "and also", "in addition", "furthermore", "combine",
    "integrate", "pipeline", "workflow", "end to end",
})


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

@dataclass
class AgenticSeekRouter:
    """Lightweight heuristic router for agenticSeek agent selection.

    Classifies user queries into the appropriate ``AgenticSeekAgentType``
    using keyword matching and structural heuristics.  This avoids the
    ``transformers`` + ``torch`` dependency of the upstream ML-based
    router while providing solid accuracy for common query patterns.

    Attributes:
        default_agent: Fallback agent type when no keywords match.
    """

    default_agent: AgenticSeekAgentType = AgenticSeekAgentType.CASUAL

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def classify_query(self, query: str) -> AgenticSeekAgentType:
        """Select the best agent type for a user query.

        Strategy:

        1. Try keyword classification.
        2. If no keywords match, fall back to ``default_agent``.

        Args:
            query: Raw user prompt.

        Returns:
            The recommended ``AgenticSeekAgentType``.
        """
        if not query or not query.strip():
            return self.default_agent

        keyword_result = self._keyword_classify(query)
        if keyword_result is not None:
            return keyword_result

        return self._heuristic_classify(query)

    def estimate_complexity(self, query: str) -> str:
        """Estimate task complexity (``"LOW"`` or ``"HIGH"``).

        A query is considered **HIGH** complexity when it contains
        indicators of multi-step work (e.g. *"then"*, *"after that"*,
        *"step by step"*).

        Args:
            query: Raw user prompt.

        Returns:
            ``"LOW"`` or ``"HIGH"``.
        """
        if not query:
            return "LOW"
        lower = query.lower()
        matches = sum(1 for kw in _HIGH_COMPLEXITY_INDICATORS if kw in lower)
        # Two or more complexity indicators → high
        return "HIGH" if matches >= 2 else "LOW"

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _keyword_classify(self, query: str) -> AgenticSeekAgentType | None:
        """Score each agent type by keyword overlap.

        Returns the type with the highest score, or ``None`` if no
        keywords matched at all.
        """
        lower = query.lower()
        scores: dict[AgenticSeekAgentType, int] = {
            AgenticSeekAgentType.CODER: _score(lower, _CODER_KEYWORDS),
            AgenticSeekAgentType.BROWSER: _score(lower, _BROWSER_KEYWORDS),
            AgenticSeekAgentType.FILE: _score(lower, _FILE_KEYWORDS),
            AgenticSeekAgentType.PLANNER: _score(lower, _PLANNER_KEYWORDS),
        }
        best_type = max(scores, key=scores.get)  # type: ignore[arg-type]
        if scores[best_type] == 0:
            return None
        return best_type

    def _heuristic_classify(self, query: str) -> AgenticSeekAgentType:
        """Structural heuristics when keyword matching fails.

        - Contains code fences → CODER
        - Contains URLs → BROWSER
        - Contains file-path-like patterns → FILE
        - Otherwise → default (CASUAL)
        """
        if "```" in query:
            return AgenticSeekAgentType.CODER
        if re.search(r"https?://", query):
            return AgenticSeekAgentType.BROWSER
        if re.search(r"[/\\]\w+\.\w+", query):
            return AgenticSeekAgentType.FILE
        return self.default_agent


# ---------------------------------------------------------------------------
# Scoring helper
# ---------------------------------------------------------------------------

def _score(text: str, keywords: frozenset[str]) -> int:
    """Count how many keywords from *keywords* appear in *text*."""
    return sum(1 for kw in keywords if kw in text)
