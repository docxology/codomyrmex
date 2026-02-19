"""
Quality scoring for LLM outputs.

Provides heuristic-based quality analysis across multiple dimensions
without requiring an LLM dependency. Useful for fast, deterministic
quality estimation in evaluation pipelines.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


class QualityDimension(Enum):
    """Dimensions along which LLM output quality is measured."""
    COHERENCE = "coherence"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    CONCISENESS = "conciseness"
    ACCURACY = "accuracy"


@dataclass
class DimensionScore:
    """Score for a single quality dimension with explanation.

    Attributes:
        dimension: The quality dimension being scored.
        score: Numeric score from 0.0 to 1.0.
        explanation: Human-readable explanation of the score.
        raw_metrics: Raw metrics that contributed to this score.
    """
    dimension: QualityDimension
    score: float
    explanation: str = ""
    raw_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Full quality report across all dimensions.

    Attributes:
        scores: Mapping from dimension to its DimensionScore.
        overall_score: Weighted average across all dimensions.
        output_text: The output text that was analyzed.
        context_text: The context provided for analysis.
        metadata: Additional metadata about the analysis.
    """
    scores: dict[QualityDimension, DimensionScore] = field(default_factory=dict)
    overall_score: float = 0.0
    output_text: str = ""
    context_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_score(self, dimension: QualityDimension) -> float:
        """Get the score for a specific dimension.

        Args:
            dimension: The quality dimension.

        Returns:
            The score, or 0.0 if the dimension was not scored.
        """
        ds = self.scores.get(dimension)
        return ds.score if ds else 0.0

    def get_explanation(self, dimension: QualityDimension) -> str:
        """Get the explanation for a specific dimension.

        Args:
            dimension: The quality dimension.

        Returns:
            The explanation string, or empty string if not available.
        """
        ds = self.scores.get(dimension)
        return ds.explanation if ds else ""

    @property
    def weakest_dimension(self) -> QualityDimension | None:
        """The dimension with the lowest score."""
        if not self.scores:
            return None
        return min(self.scores, key=lambda d: self.scores[d].score)

    @property
    def strongest_dimension(self) -> QualityDimension | None:
        """The dimension with the highest score."""
        if not self.scores:
            return None
        return max(self.scores, key=lambda d: self.scores[d].score)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a plain dictionary."""
        return {
            "overall_score": self.overall_score,
            "scores": {
                dim.value: {
                    "score": ds.score,
                    "explanation": ds.explanation,
                    "raw_metrics": ds.raw_metrics,
                }
                for dim, ds in self.scores.items()
            },
            "weakest": self.weakest_dimension.value if self.weakest_dimension else None,
            "strongest": self.strongest_dimension.value if self.strongest_dimension else None,
            "metadata": self.metadata,
        }

    def to_result(self) -> "Result | None":
        """Convert to a codomyrmex Result if schemas are available."""
        if Result is None or ResultStatus is None:
            return None

        status = (
            ResultStatus.SUCCESS
            if self.overall_score >= 0.5
            else ResultStatus.PARTIAL
            if self.overall_score >= 0.25
            else ResultStatus.FAILURE
        )
        return Result(
            status=status,
            data=self.to_dict(),
            message=f"Quality score: {self.overall_score:.2f}/1.00",
            metadata={"overall_score": self.overall_score},
        )


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens."""
    return re.findall(r"[a-zA-Z']+", text.lower())


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s.strip()]


class QualityAnalyzer:
    """Heuristic-based quality analyzer for LLM outputs.

    Scores output text across five quality dimensions using pure
    heuristic methods -- no LLM calls required.

    Args:
        dimension_weights: Custom weights per dimension. If not provided,
            all dimensions are weighted equally.
    """

    # Completion markers that indicate the text reached a natural end
    _COMPLETION_MARKERS = [
        ".", "!", "?",           # Sentence-ending punctuation
        "```",                   # Closed code block
        "in conclusion",
        "in summary",
        "to summarize",
        "therefore",
        "thus",
        "finally",
        "overall",
    ]

    # Indicators that the text may be incomplete
    _INCOMPLETION_MARKERS = [
        "...",
        "etc",
        "and so on",
        "to be continued",
        "TODO",
        "FIXME",
        "TBD",
    ]

    def __init__(
        self,
        dimension_weights: dict[QualityDimension, float] | None = None,
    ) -> None:
        self._weights = dimension_weights or {
            QualityDimension.COHERENCE: 1.0,
            QualityDimension.RELEVANCE: 1.0,
            QualityDimension.COMPLETENESS: 1.0,
            QualityDimension.CONCISENESS: 1.0,
            QualityDimension.ACCURACY: 1.0,
        }

    def analyze(self, output: str, context: str = "") -> QualityReport:
        """Analyze the quality of an LLM output.

        Args:
            output: The model output text to evaluate.
            context: Optional context (prompt, reference, or topic) used
                to evaluate relevance.

        Returns:
            A QualityReport with scores across all dimensions.
        """
        scores: dict[QualityDimension, DimensionScore] = {}

        scores[QualityDimension.COHERENCE] = self._score_coherence(output)
        scores[QualityDimension.RELEVANCE] = self._score_relevance(output, context)
        scores[QualityDimension.COMPLETENESS] = self._score_completeness(output)
        scores[QualityDimension.CONCISENESS] = self._score_conciseness(output)
        scores[QualityDimension.ACCURACY] = self._score_accuracy(output, context)

        # Weighted average
        total_weight = sum(
            self._weights.get(dim, 1.0) for dim in scores
        )
        if total_weight > 0:
            overall = sum(
                ds.score * self._weights.get(dim, 1.0)
                for dim, ds in scores.items()
            ) / total_weight
        else:
            overall = 0.0

        return QualityReport(
            scores=scores,
            overall_score=round(overall, 6),
            output_text=output,
            context_text=context,
            metadata={
                "weights": {d.value: w for d, w in self._weights.items()},
                "analyzer": "heuristic",
            },
        )

    def _score_coherence(self, output: str) -> DimensionScore:
        """Score coherence based on sentence length variance and word repetition.

        Coherence heuristics:
        - Low variance in sentence lengths indicates consistent structure.
        - Low immediate word repetition indicates natural flow.
        """
        if not output.strip():
            return DimensionScore(
                dimension=QualityDimension.COHERENCE,
                score=0.0,
                explanation="Empty output has no coherence.",
                raw_metrics={"sentence_count": 0},
            )

        sentences = _split_sentences(output)
        sentence_count = len(sentences)

        if sentence_count <= 1:
            # Single sentence: check it has reasonable length
            word_count = len(_tokenize(output))
            score = min(1.0, word_count / 5) if word_count > 0 else 0.0
            return DimensionScore(
                dimension=QualityDimension.COHERENCE,
                score=round(score, 6),
                explanation=f"Single sentence with {word_count} words.",
                raw_metrics={"sentence_count": 1, "word_count": word_count},
            )

        # Sentence length variance
        lengths = [len(_tokenize(s)) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        # Normalize: low std_dev relative to mean is good
        cv = std_dev / mean_len if mean_len > 0 else 0
        length_score = max(0.0, 1.0 - cv)

        # Word repetition: check for consecutive duplicate words
        words = _tokenize(output)
        if len(words) > 1:
            consecutive_repeats = sum(
                1 for i in range(1, len(words)) if words[i] == words[i - 1]
            )
            repeat_ratio = consecutive_repeats / (len(words) - 1)
            repetition_score = max(0.0, 1.0 - repeat_ratio * 5)
        else:
            repetition_score = 1.0

        score = round((length_score * 0.6 + repetition_score * 0.4), 6)

        return DimensionScore(
            dimension=QualityDimension.COHERENCE,
            score=score,
            explanation=f"Sentence length CV={cv:.2f}, consecutive repeat ratio={repeat_ratio if len(words) > 1 else 0:.3f}.",
            raw_metrics={
                "sentence_count": sentence_count,
                "mean_sentence_length": round(mean_len, 2),
                "length_std_dev": round(std_dev, 2),
                "cv": round(cv, 4),
                "length_score": round(length_score, 4),
                "repetition_score": round(repetition_score, 4),
            },
        )

    def _score_relevance(self, output: str, context: str) -> DimensionScore:
        """Score relevance based on keyword overlap with context.

        If no context is provided, returns a neutral score of 0.5.
        """
        if not context.strip():
            return DimensionScore(
                dimension=QualityDimension.RELEVANCE,
                score=0.5,
                explanation="No context provided; relevance cannot be fully assessed.",
                raw_metrics={"context_provided": False},
            )

        if not output.strip():
            return DimensionScore(
                dimension=QualityDimension.RELEVANCE,
                score=0.0,
                explanation="Empty output has no relevance.",
                raw_metrics={"context_provided": True, "overlap": 0.0},
            )

        # Stopwords to exclude from overlap calculation
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "shall", "should", "may", "might", "must", "can",
            "could", "of", "in", "to", "for", "with", "on", "at", "from",
            "by", "about", "as", "into", "through", "during", "before",
            "after", "above", "below", "between", "and", "but", "or",
            "nor", "not", "so", "yet", "both", "either", "neither", "each",
            "every", "all", "any", "few", "more", "most", "other", "some",
            "such", "no", "only", "own", "same", "than", "too", "very",
            "just", "because", "if", "when", "while", "that", "this",
            "these", "those", "it", "its", "i", "me", "my", "we", "us",
            "our", "you", "your", "he", "him", "his", "she", "her", "they",
            "them", "their", "what", "which", "who", "whom",
        }

        context_words = set(_tokenize(context)) - stopwords
        output_words = set(_tokenize(output)) - stopwords

        if not context_words:
            return DimensionScore(
                dimension=QualityDimension.RELEVANCE,
                score=0.5,
                explanation="Context contains only stopwords.",
                raw_metrics={"context_provided": True, "context_keywords": 0},
            )

        overlap = context_words & output_words
        overlap_ratio = len(overlap) / len(context_words)

        # Scale: 0.3 overlap is already quite good
        score = min(1.0, overlap_ratio / 0.4)
        score = round(score, 6)

        return DimensionScore(
            dimension=QualityDimension.RELEVANCE,
            score=score,
            explanation=f"Keyword overlap: {len(overlap)}/{len(context_words)} context keywords found in output.",
            raw_metrics={
                "context_provided": True,
                "context_keywords": len(context_words),
                "output_keywords": len(output_words),
                "overlap_count": len(overlap),
                "overlap_ratio": round(overlap_ratio, 4),
            },
        )

    def _score_completeness(self, output: str) -> DimensionScore:
        """Score completeness by checking for completion vs. incompletion markers."""
        if not output.strip():
            return DimensionScore(
                dimension=QualityDimension.COMPLETENESS,
                score=0.0,
                explanation="Empty output is incomplete.",
                raw_metrics={},
            )

        output_lower = output.lower().strip()

        # Check for completion markers
        completion_signals = 0
        found_completion = []
        for marker in self._COMPLETION_MARKERS:
            if output_lower.endswith(marker) or marker in output_lower:
                completion_signals += 1
                found_completion.append(marker)

        # Check for incompletion markers
        incompletion_signals = 0
        found_incompletion = []
        for marker in self._INCOMPLETION_MARKERS:
            if marker.lower() in output_lower:
                incompletion_signals += 1
                found_incompletion.append(marker)

        # Ends with sentence-ending punctuation is a strong signal
        ends_with_punct = output_lower[-1] in ".!?)" if output_lower else False

        # Length-based heuristic: very short outputs are likely incomplete
        word_count = len(_tokenize(output))
        length_factor = min(1.0, word_count / 10)

        # Combine signals
        completion_score = min(1.0, completion_signals * 0.2)
        incompletion_penalty = min(0.5, incompletion_signals * 0.15)
        punct_bonus = 0.3 if ends_with_punct else 0.0

        score = max(0.0, min(1.0,
            completion_score + punct_bonus + length_factor * 0.3 - incompletion_penalty
        ))
        score = round(score, 6)

        return DimensionScore(
            dimension=QualityDimension.COMPLETENESS,
            score=score,
            explanation=f"Found {completion_signals} completion markers, "
                        f"{incompletion_signals} incompletion markers. "
                        f"Ends with punctuation: {ends_with_punct}.",
            raw_metrics={
                "completion_signals": completion_signals,
                "incompletion_signals": incompletion_signals,
                "ends_with_punctuation": ends_with_punct,
                "word_count": word_count,
                "length_factor": round(length_factor, 4),
                "found_completion": found_completion,
                "found_incompletion": found_incompletion,
            },
        )

    def _score_conciseness(self, output: str) -> DimensionScore:
        """Score conciseness based on ratio of unique words to total words.

        High unique-word ratio means less repetition and more
        information density, which is a proxy for conciseness.
        """
        if not output.strip():
            return DimensionScore(
                dimension=QualityDimension.CONCISENESS,
                score=0.0,
                explanation="Empty output.",
                raw_metrics={},
            )

        words = _tokenize(output)
        total = len(words)

        if total == 0:
            return DimensionScore(
                dimension=QualityDimension.CONCISENESS,
                score=0.0,
                explanation="No words found in output.",
                raw_metrics={"total_words": 0},
            )

        unique = len(set(words))
        unique_ratio = unique / total

        # Word frequency analysis: penalize heavily repeated words
        counter = Counter(words)
        max_freq = counter.most_common(1)[0][1] if counter else 0
        max_freq_ratio = max_freq / total

        # High unique ratio is good (close to 1.0 for short text, naturally lower for long text)
        # Adjust for text length: longer texts naturally have lower unique ratios
        length_adjustment = min(1.0, math.log(total + 1) / math.log(200))
        adjusted_unique_ratio = min(1.0, unique_ratio + length_adjustment * 0.2)

        # Penalize if any single word dominates
        dominance_penalty = max(0.0, max_freq_ratio - 0.1) * 2

        score = max(0.0, min(1.0, adjusted_unique_ratio - dominance_penalty))
        score = round(score, 6)

        return DimensionScore(
            dimension=QualityDimension.CONCISENESS,
            score=score,
            explanation=f"Unique word ratio: {unique}/{total} ({unique_ratio:.2f}). "
                        f"Most frequent word appears {max_freq} times.",
            raw_metrics={
                "total_words": total,
                "unique_words": unique,
                "unique_ratio": round(unique_ratio, 4),
                "max_word_frequency": max_freq,
                "max_freq_ratio": round(max_freq_ratio, 4),
                "length_adjustment": round(length_adjustment, 4),
                "dominance_penalty": round(dominance_penalty, 4),
            },
        )

    def _score_accuracy(self, output: str, context: str) -> DimensionScore:
        """Score accuracy — requires configured evaluation dataset and metrics."""
        raise NotImplementedError("Accuracy scoring requires configured evaluation dataset and metrics")


def analyze_quality(output: str, context: str = "") -> QualityReport:
    """Convenience function to analyze output quality with default settings.

    Args:
        output: The model output text.
        context: Optional context for relevance scoring.

    Returns:
        A QualityReport with scores across all dimensions.
    """
    return QualityAnalyzer().analyze(output, context)


__all__ = [
    "QualityDimension",
    "DimensionScore",
    "QualityReport",
    "QualityAnalyzer",
    "analyze_quality",
]
