"""NarrativeEngine — orchestrator for narrative operations."""

from __future__ import annotations

from typing import Dict, List, Optional
from codomyrmex.meme.narrative.models import Narrative, NarrativeArc, NarrativeTemplate

class NarrativeEngine:
    """Engine for analyzing, generating, and transforming narratives."""

    def analyze(self, text: str) -> Narrative:
        """Analyze text to extract narrative structure.

        Uses heuristic sentence-splitting and keyword detection to infer
        arc tension, characters, and thematic content.  No external NLP
        dependency required.
        """
        import re

        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s.strip()]
        num_sentences = len(sentences) or 1

        # Build a simple tension curve based on exclamation / question density
        tension_curve: list[float] = []
        for s in sentences:
            excl = s.count("!")
            quest = s.count("?")
            length_factor = min(1.0, len(s) / 80)
            tension = min(1.0, (excl * 0.3 + quest * 0.2 + length_factor * 0.5))
            tension_curve.append(round(tension, 3))

        arc = NarrativeArc(
            name="Detected Arc",
            tension_curve=tension_curve,
            emotional_valence=[round(t * 2 - 1, 3) for t in tension_curve],
        )

        # Detect characters via archetype keywords
        from codomyrmex.meme.narrative.models import Archetype
        archetype_keywords = {
            "hero": Archetype.HERO,
            "villain": Archetype.SHADOW,
            "mentor": Archetype.MENTOR,
            "trickster": Archetype.TRICKSTER,
            "guardian": Archetype.THRESHOLD_GUARDIAN,
            "ally": Archetype.ALLY,
        }
        characters: Dict[str, "Archetype"] = {}
        text_lower = text.lower()
        for keyword, archetype in archetype_keywords.items():
            if keyword in text_lower:
                characters[keyword.capitalize()] = archetype

        # Detect theme from most common significant words
        words = re.findall(r"[a-z]{4,}", text_lower)
        stopwords = {"that", "this", "with", "from", "have", "been", "were", "they", "their", "once", "upon", "time"}
        significant = [w for w in words if w not in stopwords]
        if significant:
            from collections import Counter
            theme = Counter(significant).most_common(1)[0][0]
        else:
            theme = "unidentified"

        return Narrative(
            title="Analyzed Narrative",
            theme=theme,
            arc=arc,
            characters=characters,
            cultural_resonance=round(sum(tension_curve) / num_sentences, 3),
            content_segments=sentences,
        )

    def generate(self, template: NarrativeTemplate, params: Dict[str, str]) -> str:
        """Generate a story from a template and parameters."""
        story = []
        for stage in template.stages:
            segment = f"[{stage}]: "
            context = params.get("context", "the world")
            protagonist = params.get("protagonist", "Hero")
            segment += f"{protagonist} experiences {stage} in {context}."
            story.append(segment)
        return "\n".join(story)

    def insurgent_counter(self, narrative: Narrative) -> Narrative:
        """Generate a counter-narrative to disrupt an existing one."""
        import copy
        counter = copy.deepcopy(narrative)
        counter.title = f"Counter: {narrative.title}"
        counter.theme = f"Anti-{narrative.theme}"
        counter.content_segments = [
            f"Why {narrative.title} is a lie.",
            f"The true story of {counter.theme}."
        ]
        return counter
