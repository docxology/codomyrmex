"""NeurolinguisticEngine — orchestrator for NLP operations."""

from __future__ import annotations

from typing import List

from codomyrmex.meme.neurolinguistic.models import CognitiveFrame, LinguisticPattern
from codomyrmex.meme.neurolinguistic.framing import analyze_frames, reframe
from codomyrmex.meme.neurolinguistic.patterns import detect_patterns


class NeurolinguisticEngine:
    """Engine for analyzing and checking text against linguistic models."""

    def __init__(self):
        self.known_frames: List[CognitiveFrame] = []

    def register_frame(self, frame: CognitiveFrame) -> None:
        """Add a frame to the engine's registry."""
        self.known_frames.append(frame)

    def audit(self, text: str) -> dict:
        """Perform a full audit of text.

        Returns:
            Dict containing active frames and detected patterns.
        """
        frames = analyze_frames(text, self.known_frames)
        patterns = detect_patterns(text)
        
        return {
            "frames": frames,
            "patterns": patterns,
            "score": len(frames) + len(patterns)  # Simple impact metric
        }

    def spin(self, text: str, target_frame: str) -> str:
        """Spin content towards a specific frame."""
        # Find target
        tgt = next((f for f in self.known_frames if f.name == target_frame), None)
        if not tgt:
            return text
            
        # Naive approach: just inject frame keywords
        return f"{text} ... which clearly involves {tgt.keywords[0]}."
