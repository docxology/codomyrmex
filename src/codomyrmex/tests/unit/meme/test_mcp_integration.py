"""Unit tests for Information Dynamics (Meme MCP).

Zero-Mock Policy: Tests naturally evaluate the actual `mcp_tools.py`
endpoints for narrative broadcasting and analysis, utilizing the
real `NarrativeEngine` and mathematical global viral registries.
"""

import pytest

from codomyrmex.meme import mcp_tools


@pytest.fixture(autouse=True)
def reset_viral_registry():
    """Ensure tests run with a clean state."""
    mcp_tools._ACTIVE_VIRAL_MEMES.clear()


@pytest.mark.unit
def test_broadcast_meme_registers_concept():
    """Verify that broadcasting registers a brand new marker context."""
    res = mcp_tools.broadcast_meme(concept="zero-mock dominance", virulence=0.9)
    assert res["status"] == "success"
    assert res["registered"] is True
    assert res["virulence"] == 0.9
    assert res["current_viral_pool_size"] == 1

    # Verify updating a meme's parameters
    res2 = mcp_tools.broadcast_meme(concept="zero-mock dominance", virulence=0.5)
    assert res2["updated"] is True
    assert res2["virulence"] == 0.5
    assert len(mcp_tools._ACTIVE_VIRAL_MEMES) == 1


@pytest.mark.unit
def test_analyze_narrative_detects_viral_markers():
    """Verify that the narrative engine correctly detects cross-pollinated viral concepts."""
    # Seed the registry
    mcp_tools.broadcast_meme("agentic behavior", virulence=0.8)
    mcp_tools.broadcast_meme("synthetic bio", virulence=0.4)

    # Analyze an unaffected text
    corpus_clean = "The hero walked down the quiet path by the river."
    res_clean = mcp_tools.analyze_narrative(corpus_clean)
    assert res_clean["status"] == "success"
    assert len(res_clean["viral_matches"]) == 0

    # Analyze an infected text
    corpus_infected = "The shadow tricked the hero into believing synthetic bio was the path to true agentic behavior!"
    res_infected = mcp_tools.analyze_narrative(corpus_infected)
    assert res_infected["status"] == "success"
    assert "agentic behavior" in res_infected["viral_matches"]
    assert "synthetic bio" in res_infected["viral_matches"]
    assert (
        "Hero" in res_infected["characters"] or "Shadow" in res_infected["characters"]
    )
    assert res_infected["resonance"] > 0.0


@pytest.mark.unit
def test_empty_string_safety():
    """Test safety filters for invalid string usage in MCP interfaces."""
    res_broadcast = mcp_tools.broadcast_meme("   ")
    assert res_broadcast["status"] == "error"

    res_analyze = mcp_tools.analyze_narrative("")
    assert res_analyze["status"] == "error"
