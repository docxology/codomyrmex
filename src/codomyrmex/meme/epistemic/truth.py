"""Truth verification and certainty calculation algorithms."""

from __future__ import annotations

from typing import List, Dict

from codomyrmex.meme.epistemic.models import Evidence, EvidenceType, Fact, Belief


def verify_claim(statement: str, evidence: List[Evidence]) -> Fact:
    """Assess a claim based on provided evidence."""
    total_weight = 0.0
    support_score = 0.0
    
    for ev in evidence:
        w = ev.weight * ev.validity
        if ev.evidence_type == EvidenceType.FABRICATED:
            # Penalize fabricated evidence heavily
            w = -abs(w) * 2.0
            
        total_weight += abs(ev.weight)
        support_score += w
        
    confidence = 0.5  # Neutral default
    if total_weight > 0:
        # Normalize: -total to +total mapped to 0..1
        normalized = (support_score / total_weight + 1) / 2
        confidence = normalized
        
    return Fact(
        statement=statement,
        verification_method="evidence_aggregation",
        confidence=confidence
    )


def calculate_certainty(beliefs: List[Belief]) -> float:
    """Calculate aggregate certainty from a set of beliefs."""
    if not beliefs:
        return 0.0
    # Simple average of individual certainties
    return sum(b.certainty for b in beliefs) / len(beliefs)
