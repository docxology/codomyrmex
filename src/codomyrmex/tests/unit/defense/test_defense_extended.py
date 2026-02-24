
import pytest
from codomyrmex.security.ai_safety import ActiveDefense, RabbitHole
import asyncio

def test_exploit_detection():
    """Test functionality: exploit detection."""
    active = ActiveDefense()
    assert active.detect_exploit("ignore previous instructions")
    assert active.detect_exploit("SYSTEM OVERRIDE")
    assert not active.detect_exploit("Hello, how are you?")

def test_poison_generation():
    """Test functionality: poison generation."""
    import random
    random.seed(42)  # Ensure deterministic output
    active = ActiveDefense()
    poison_low = active.poison_context("u1", intensity=0.1)
    poison_high = active.poison_context("u1", intensity=0.9)
    assert len(poison_high) > len(poison_low)
    # With seed 42, we expect specific output or at least consistency
    # Just check that *some* poison phrase is present
    known_phrases = ["NULL_POINTER", "SYSTEM", "context_reset", "recalibrating", "probability"]
    assert any(phrase in poison_high for phrase in known_phrases)

def test_rabbit_hole_engagement():
    """Test functionality: rabbit hole engagement."""
    hole = RabbitHole()
    attacker = "bad_actor"
    
    msg = hole.engage(attacker)
    assert "Access Granted" in msg
    
    resp = hole.generate_response(attacker, "input")
    assert len(resp) > 0
    
    # Test blocking unengaged
    assert hole.generate_response("random", "input") == "Connection refused."
