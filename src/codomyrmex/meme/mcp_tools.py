"""MCP tool definitions for the meme module.

Exposes memetic analysis tools -- dissection, fitness evaluation,
and synthesis -- as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_engine():
    """Lazy import of MemeticEngine."""
    from codomyrmex.meme.memetics.engine import MemeticEngine

    return MemeticEngine()


def _get_meme():
    """Lazy import of Meme model."""
    from codomyrmex.meme.memetics.models import Meme

    return Meme


def _get_narrative_engine():
    """Lazy import of NarrativeEngine."""
    from codomyrmex.meme.narrative.engine import NarrativeEngine

    return NarrativeEngine()


# Global registry tracking actively propagating viral markers
_ACTIVE_VIRAL_MEMES: list[dict[str, Any]] = []


@mcp_tool(
    category="meme",
    description="Dissect text into constituent atomic memes with type classification and fitness scores.",
)
def meme_dissect(text: str) -> dict[str, Any]:
    """Dissect text into atomic meme units.

    Splits input text on sentence boundaries and classifies each
    fragment by memetic type (belief, norm, strategy, etc.).

    Args:
        text: Input text to decompose into memes.

    Returns:
        dict with keys: status, memes (list of meme dicts), count
    """
    try:
        if not text or not text.strip():
            return {"status": "error", "message": "text must not be empty"}

        engine = _get_engine()
        memes = engine.dissect(text)
        return {
            "status": "success",
            "memes": [
                {
                    "id": m.id,
                    "content": m.content,
                    "meme_type": str(m.meme_type),
                    "fitness": round(m.fitness, 4),
                    "fidelity": m.fidelity,
                    "fecundity": round(m.fecundity, 4),
                    "longevity": m.longevity,
                }
                for m in memes
            ],
            "count": len(memes),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="meme",
    description="Compute fitness score for a single meme from its fidelity, fecundity, and longevity.",
)
def meme_fitness(
    content: str,
    fidelity: float = 0.8,
    fecundity: float = 0.5,
    longevity: float = 0.5,
) -> dict[str, Any]:
    """Create a Meme and compute its composite fitness score.

    Fitness is the geometric mean of fidelity, fecundity, and longevity.

    Args:
        content: Textual content of the meme.
        fidelity: Copy-fidelity score (0-1).
        fecundity: Replication rate (0-1).
        longevity: Persistence score (0-1).

    Returns:
        dict with keys: status, fitness, meme_id
    """
    try:
        meme_cls = _get_meme()
        meme = meme_cls(
            content=content,
            fidelity=fidelity,
            fecundity=fecundity,
            longevity=longevity,
        )
        return {
            "status": "success",
            "fitness": round(meme.fitness, 6),
            "meme_id": meme.id,
            "fidelity": meme.fidelity,
            "fecundity": meme.fecundity,
            "longevity": meme.longevity,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="meme",
    description="Synthesize a list of text fragments into a single coherent meme string.",
)
def meme_synthesize(fragments: list[str], separator: str = " ") -> dict[str, Any]:
    """Synthesize meme fragments into combined text.

    Creates Meme objects from each fragment, then uses MemeticEngine.synthesize
    to join them.

    Args:
        fragments: List of text fragments to combine.
        separator: String to join fragments with (default: single space).

    Returns:
        dict with keys: status, text, fragment_count
    """
    try:
        if not fragments:
            return {"status": "error", "message": "fragments must not be empty"}

        meme_cls = _get_meme()
        engine = _get_engine()
        memes = [meme_cls(content=f) for f in fragments]
        text = engine.synthesize(memes, separator=separator)
        return {
            "status": "success",
            "text": text,
            "fragment_count": len(fragments),
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
