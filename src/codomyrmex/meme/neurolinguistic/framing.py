"""Framing analysis and construction."""

from __future__ import annotations

from typing import List, Dict

from codomyrmex.meme.neurolinguistic.models import CognitiveFrame


def analyze_frames(text: str, known_frames: List[CognitiveFrame]) -> List[CognitiveFrame]:
    """Identify which frames are active in a text.

    Args:
        text: Input text.
        known_frames: List of Frame definitions to check against.

    Returns:
        List of active Frames sorted by relevance.
    """
    active = []
    text_lower = text.lower()
    
    for frame in known_frames:
        hits = sum(1 for kw in frame.keywords if kw.lower() in text_lower)
        if hits > 0:
            # Clone and calculate dynamic content if needed
            active.append(frame)
            
    return active


def reframe(content: str, source_frame: CognitiveFrame, target_frame: CognitiveFrame) -> str:
    """Translate content from one frame to another.

    Uses keyword mapping to shift the perspective.
    (Heuristic implementation).
    """
    if not source_frame.keywords or not target_frame.keywords:
        return content
        
    result = content
    # Simple direct substitution of primary keywords
    # Real impl would use LLM/embeddings
    src_kw = source_frame.keywords[0]
    tgt_kw = target_frame.keywords[0]
    
    result = result.replace(src_kw, tgt_kw)
    return result
