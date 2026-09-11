"""Unit tests for language detection MCP tools."""

from codomyrmex.language_detection.mcp_tools import (
    language_detection_detect,
    language_detection_detect_probs,
)


def test_language_detection_detect_english():
    """Test detecting English text."""
    res = language_detection_detect("Hello, this is a test.")
    assert res["status"] == "success"
    assert res["language"] == "en"


def test_language_detection_detect_french():
    """Test detecting French text."""
    res = language_detection_detect("Bonjour, c'est un test.")
    assert res["status"] == "success"
    assert res["language"] == "fr"


def test_language_detection_detect_empty():
    """Test detecting empty text."""
    res = language_detection_detect("")
    assert res["status"] == "success"
    assert res["language"] == "unknown"


def test_language_detection_detect_gibberish():
    """Test detecting gibberish/numbers without language."""
    res = language_detection_detect("12345 67890")
    assert res["status"] == "success"
    assert res["language"] == "unknown"


def test_language_detection_detect_probs():
    """Test detecting multiple languages with probabilities."""
    res = language_detection_detect_probs("Hello world. Bonjour le monde.")
    assert res["status"] == "success"
    assert "results" in res
    assert isinstance(res["results"], list)
    if res["results"]:
        assert "lang" in res["results"][0]
        assert "prob" in res["results"][0]


def test_language_detection_detect_probs_empty():
    """Test detecting multiple languages with probabilities for empty text."""
    res = language_detection_detect_probs("")
    assert res["status"] == "success"
    assert res["results"] == []
