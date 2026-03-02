from codomyrmex.nlp.mcp_tools import (
    nlp_extract_entities,
    nlp_summarize,
    nlp_tokenize,
)


def test_nlp_tokenize():
    """Test tokenization of text."""
    result = nlp_tokenize("Hello world this is a test")
    assert result == {"tokens": ["Hello", "world", "this", "is", "a", "test"]}

    result = nlp_tokenize("")
    assert result == {"tokens": []}


def test_nlp_extract_entities():
    """Test extraction of entities."""
    result = nlp_extract_entities("John Doe lives in New York.")
    # Assuming the simple uppercase rule from the dummy implementation
    assert "John" in result["entities"]
    assert "Doe" in result["entities"]
    assert "New" in result["entities"]
    assert "York." in result["entities"]

    result = nlp_extract_entities("no entities here")
    assert result["entities"] == []

    result = nlp_extract_entities("")
    assert result["entities"] == []


def test_nlp_summarize():
    """Test summarization of text."""
    text = (
        "This is a very long text that needs to be summarized. "
        "It has multiple sentences. We will truncate it."
    )
    result = nlp_summarize(text, max_length=20)
    assert result["summary"].endswith("...")
    assert len(result["summary"]) <= 23  # 20 + 3 for "..."

    result = nlp_summarize("Short text", max_length=100)
    assert result["summary"] == "Short text"

    result = nlp_summarize("", max_length=100)
    assert result["summary"] == ""
