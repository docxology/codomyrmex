"""Narrative structure definitions (Campbell, Freytag, etc.)."""

from __future__ import annotations

from codomyrmex.meme.narrative.models import NarrativeArc

# Standard tension curves (normalized 0-1 duration, 0-1 tension)

def heros_journey_arc() -> NarrativeArc:
    """The Monomyth structure."""
    return NarrativeArc(
        name="Hero's Journey",
        tension_curve=[
            0.1,  # Ordinary World
            0.3,  # Call to Adventure
            0.2,  # Refusal
            0.4,  # Meeting Mentor
            0.5,  # Crossing Threshold
            0.6,  # Tests/Allies
            0.7,  # Approach
            0.9,  # Ordeal (Climax 1)
            0.5,  # Reward
            0.8,  # Road Back
            1.0,  # Resurrection (Climax 2)
            0.2,  # Return with Elixir
        ],
        emotional_valence=[
            0.0, 0.2, -0.2, 0.5, 0.3, 0.1, -0.3, -0.8, 0.8, -0.4, 0.4, 0.9
        ]
    )


def freytag_pyramid_arc() -> NarrativeArc:
    """Classic 5-act dramatic structure."""
    return NarrativeArc(
        name="Freytag's Pyramid",
        tension_curve=[
            0.1,  # Exposition
            0.4,  # Rising Action
            1.0,  # Climax
            0.6,  # Falling Action
            0.2,  # Denouement
        ],
        emotional_valence=[0.0, 0.3, 0.8, -0.2, 0.1]
    )


def fichtean_curve_arc() -> NarrativeArc:
    """Series of crises leading to climax."""
    return NarrativeArc(
        name="Fichtean Curve",
        tension_curve=[
            0.2,  # Setup
            0.5,  # Crisis 1
            0.4,  # Lull
            0.7,  # Crisis 2
            0.6,  # Lull
            0.9,  # Crisis 3
            1.0,  # Climax
            0.1,  # Resolution
        ],
        emotional_valence=[0.0, -0.3, 0.2, -0.5, 0.1, -0.7, 0.5, 0.8]
    )
