# mypy: ignore-errors
"""Unit tests for scrape module MCP tools.

Enforces strictly zero-mock policy. All tests must execute real code paths
and trigger native exceptions by passing invalid inputs.
"""

import pytest

from codomyrmex.scrape.mcp_tools import scrape_extract_content, scrape_text_similarity


@pytest.mark.unit
class TestScrapeMCPTools:
    """Test suite for scrape MCP tools."""

    def test_scrape_extract_content_success(self) -> None:
        """Test successful content extraction from valid HTML."""
        html = """
        <html>
            <head><title>Test Title</title></head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a paragraph.</p>
                <a href="/link1">Link 1</a>
                <img src="/img1.png" alt="Image 1">
            </body>
        </html>
        """
        result = scrape_extract_content(html, base_url="https://example.com")

        assert result["status"] == "ok"
        assert result["title"] == "Test Title"
        assert len(result["headings"]) == 1
        assert result["headings"][0]["text"] == "Main Heading"
        assert result["paragraph_count"] == 1
        assert result["link_count"] == 1
        assert result["image_count"] == 1
        assert result["word_count"] > 0
        assert "content_hash" in result

    def test_scrape_extract_content_invalid_html(self) -> None:
        """Test content extraction with invalid type triggers natural error."""
        # Pass an integer instead of string to trigger natural exception in extraction
        result = scrape_extract_content(12345)  # type: ignore

        assert result["status"] == "error"
        assert "error" in result
        assert isinstance(result["error"], str)

    def test_scrape_text_similarity_success(self) -> None:
        """Test successful text similarity computation."""
        text_a = "The quick brown fox jumps over the lazy dog"
        text_b = "The fast brown fox jumps over the lazy dog"

        result = scrape_text_similarity(text_a, text_b)

        assert result["status"] == "ok"
        assert "similarity" in result
        assert 0.0 < result["similarity"] < 1.0

    def test_scrape_text_similarity_identical(self) -> None:
        """Test similarity computation for identical texts."""
        text = "identical text"
        result = scrape_text_similarity(text, text)

        assert result["status"] == "ok"
        assert result["similarity"] == 1.0

    def test_scrape_text_similarity_invalid_type(self) -> None:
        """Test similarity computation with invalid types triggers natural error."""
        # Pass a list instead of a string to trigger native AttributeError (split)
        result = scrape_text_similarity(["a", "b", "c"], "b")  # type: ignore

        assert result["status"] == "error"
        assert "error" in result
        assert isinstance(result["error"], str)
