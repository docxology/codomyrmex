"""Simulation assessment and generation logic."""

from __future__ import annotations

import random
from typing import Dict, Any

from codomyrmex.meme.hyperreality.models import (
    Simulacrum,
    SimulationLevel,
    OntologicalStatus,
)


def assess_reality_level(object_data: Dict[str, Any]) -> SimulationLevel:
    """Determine the simulation level of an object/concept.

    Heuristic assessment based on metadata fields.
    """
    history = str(object_data.get("history", ""))
    provenance = object_data.get("provenance", [])
    
    # If no provenance, likely pure simulacrum (Level 4)
    if not provenance:
        return SimulationLevel.PURE
        
    # If explicitly marked as copy of copy
    if "copy" in history.lower() and "original" not in history.lower():
        # Masking absence of basic reality
        return SimulationLevel.ABSENCE
        
    # Check for distortion metadata
    distortion = float(object_data.get("distortion", 0.0))
    if distortion > 0.8:
        return SimulationLevel.ABSENCE
    elif distortion > 0.4:
        return SimulationLevel.MASK
        
    # Default: reflection of a basic reality
    return SimulationLevel.REFLECTION


def generate_simulacrum(
    referent: str, level: SimulationLevel
) -> Simulacrum:
    """Create a new simulacrum based on a referent."""
    fidelity = 1.0
    autonomy = 0.0
    
    if level == SimulationLevel.REFLECTION:
        fidelity = 0.95
        autonomy = 0.1
    elif level == SimulationLevel.MASK:
        fidelity = 0.8
        autonomy = 0.3
    elif level == SimulationLevel.ABSENCE:
        fidelity = 0.5
        autonomy = 0.6
    elif level == SimulationLevel.PURE:
        # Hyperreal is 'more real than real'
        fidelity = 1.0 
        autonomy = 1.0
        
    return Simulacrum(
        referent=referent,
        level=level,
        fidelity=fidelity,
        autonomy=autonomy
    )
