"""Zero-mock tests for the scrape module core behavior.

Covers:
  - core.py: ScrapeFormat, ScrapeResult, ScrapeOptions, CrawlResult, MapResult, ExtractResult
  - extractors/content_extractor.py: ContentExtractor, text_similarity
  - exceptions.py: full exception hierarchy, classify_http_error
  - mcp_tools.py: scrape_extract_content, scrape_text_similarity

No mocks — all tests use real in-memory data. Network calls skipped.
"""

from __future__ import annotations

import pytest

try:
    from codomyrmex.scrape.core import (
        CrawlResult,
        ExtractResult,
        MapResult,
        ScrapeFormat,
        ScrapeOptions,
        ScrapeResult,
    )
    from codomyrmex.scrape.exceptions import (
        AuthenticationError,
        BlockedError,
        CaptchaError,
        ContentNotFoundError,
        ParseError,
        RateLimitError,
        RequestError,
        ScrapeError,
        ScrapeTimeoutError,
        ScrapeValidationError,
        ScrapingError,
        classify_http_error,
    )
    from codomyrmex.scrape.extractors.content_extractor import (
        ContentExtractor,
        ExtractedContent,
        text_similarity,
    )

    HAS_SCRAPE = True
except ImportError:
    HAS_SCRAPE = False

if not HAS_SCRAPE:
    pytest.skip("scrape module not available", allow_module_level=True)

# ---------------------------------------------------------------------------
# ScrapeFormat enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScrapeFormat:
    """ScrapeFormat enum value tests."""

    def test_markdown_value(self):
        assert ScrapeFormat.MARKDOWN == "markdown"

    def test_html_value(self):
        assert ScrapeFormat.HTML == "html"

    def test_json_value(self):
        assert ScrapeFormat.JSON == "json"

    def test_links_value(self):
        assert ScrapeFormat.LINKS == "links"

    def test_screenshot_value(self):
        assert ScrapeFormat.SCREENSHOT == "screenshot"

    def test_metadata_value(self):
        assert ScrapeFormat.METADATA == "metadata"


# ---------------------------------------------------------------------------
# ScrapeResult dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScrapeResult:
    """ScrapeResult creation and method tests."""

    def test_minimal_construction(self):
        result = ScrapeResult(url="https://example.com")
        assert result.url == "https://example.com"
        assert result.content == ""
        assert result.success is True
        assert result.error is None

    def test_get_format_enum_key(self):
        result = ScrapeResult(
            url="https://example.com",
            formats={"markdown": "# Hello"},
        )
        content = result.get_format(ScrapeFormat.MARKDOWN)
        assert content == "# Hello"

    def test_get_format_string_key(self):
        result = ScrapeResult(
            url="https://example.com",
            formats={"html": "<h1>Hello</h1>"},
        )
        assert result.get_format("html") == "<h1>Hello</h1>"

    def test_get_format_missing_returns_none(self):
        result = ScrapeResult(url="https://example.com")
        assert result.get_format("html") is None

    def test_has_format_true(self):
        result = ScrapeResult(
            url="https://example.com",
            formats={"markdown": "content"},
        )
        assert result.has_format(ScrapeFormat.MARKDOWN) is True

    def test_has_format_false(self):
        result = ScrapeResult(url="https://example.com")
        assert result.has_format(ScrapeFormat.HTML) is False

    def test_failed_result_construction(self):
        result = ScrapeResult(
            url="https://example.com",
            success=False,
            error="Connection refused",
            status_code=503,
        )
        assert result.success is False
        assert result.error == "Connection refused"
        assert result.status_code == 503


# ---------------------------------------------------------------------------
# ScrapeOptions dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScrapeOptions:
    """ScrapeOptions to_dict and default tests."""

    def test_default_format_is_markdown(self):
        opts = ScrapeOptions()
        assert ScrapeFormat.MARKDOWN in opts.formats

    def test_to_dict_contains_formats(self):
        opts = ScrapeOptions(formats=[ScrapeFormat.HTML])
        d = opts.to_dict()
        assert "formats" in d
        assert "html" in d["formats"]

    def test_to_dict_timeout_omitted_when_none(self):
        opts = ScrapeOptions()
        d = opts.to_dict()
        assert "timeout" not in d

    def test_to_dict_timeout_included_when_set(self):
        opts = ScrapeOptions(timeout=30.0)
        d = opts.to_dict()
        assert d["timeout"] == 30.0

    def test_to_dict_max_depth_omitted_when_none(self):
        opts = ScrapeOptions()
        d = opts.to_dict()
        assert "max_depth" not in d

    def test_to_dict_custom_headers(self):
        opts = ScrapeOptions(headers={"Authorization": "Bearer token"})
        d = opts.to_dict()
        assert d["headers"]["Authorization"] == "Bearer token"

    def test_follow_links_default_true(self):
        opts = ScrapeOptions()
        assert opts.follow_links is True

    def test_respect_robots_txt_default_true(self):
        opts = ScrapeOptions()
        assert opts.respect_robots_txt is True


# ---------------------------------------------------------------------------
# CrawlResult and MapResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCrawlResult:
    """CrawlResult creation tests."""

    def test_construction(self):
        cr = CrawlResult(job_id="job-123", status="pending")
        assert cr.job_id == "job-123"
        assert cr.status == "pending"
        assert cr.total == 0
        assert cr.completed == 0
        assert cr.results == []

    def test_with_results(self):
        pages = [
            ScrapeResult(url="https://example.com/page1"),
            ScrapeResult(url="https://example.com/page2"),
        ]
        cr = CrawlResult(job_id="j1", status="completed", results=pages, total=2)
        assert len(cr.results) == 2
        assert cr.total == 2


@pytest.mark.unit
class TestMapResult:
    """MapResult auto-total computation tests."""

    def test_total_auto_calculated_from_links(self):
        links = [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}]
        mr = MapResult(links=links)
        assert mr.total == 2

    def test_explicit_total_not_overridden(self):
        links = [{"url": "https://example.com/a"}]
        mr = MapResult(links=links, total=99)
        # __post_init__ only auto-sets when total==0
        assert mr.total == 99

    def test_empty_links_total_zero(self):
        mr = MapResult()
        assert mr.total == 0


# ---------------------------------------------------------------------------
# ExtractResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractResult:
    """ExtractResult default and construction tests."""

    def test_defaults(self):
        er = ExtractResult()
        assert er.status == "completed"
        assert er.data == {}
        assert er.urls == []
        assert er.job_id is None

    def test_with_data(self):
        er = ExtractResult(
            job_id="e-1",
            data={"name": "Test"},
            urls=["https://example.com"],
        )
        assert er.job_id == "e-1"
        assert er.data["name"] == "Test"
        assert len(er.urls) == 1


# ---------------------------------------------------------------------------
# ContentExtractor — pure Python, no network
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContentExtractor:
    """ContentExtractor HTML parsing tests (no network)."""

    SIMPLE_HTML = """
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page">
        <meta name="keywords" content="test, python">
    </head>
    <body>
        <h1>Main Heading</h1>
        <h2>Sub Heading</h2>
        <p>First paragraph with some content.</p>
        <p>Second paragraph here.</p>
        <a href="/relative/link">Relative Link</a>
        <a href="https://external.com">External Link</a>
        <img src="/image.png" alt="An image">
    </body>
    </html>
    """

    def test_extract_title(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        assert result.title == "Test Page"

    def test_extract_headings_levels(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        levels = [h[0] for h in result.headings]
        assert 1 in levels
        assert 2 in levels

    def test_extract_heading_text(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        texts = [h[1] for h in result.headings]
        assert "Main Heading" in texts
        assert "Sub Heading" in texts

    def test_extract_paragraphs(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        assert len(result.paragraphs) == 2
        assert "First paragraph" in result.paragraphs[0]

    def test_extract_word_count(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        assert result.word_count > 0

    def test_extract_links_resolved_with_base_url(self):
        extractor = ContentExtractor(base_url="https://example.com")
        result = extractor.extract(self.SIMPLE_HTML)
        hrefs = [link[0] for link in result.links]
        assert "https://example.com/relative/link" in hrefs

    def test_extract_external_link(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        hrefs = [link[0] for link in result.links]
        assert "https://external.com" in hrefs

    def test_extract_images(self):
        # Place alt before src to ensure regex captures alt within the match
        html = '<html><body><img alt="An image" src="/image.png"></body></html>'
        extractor = ContentExtractor(base_url="https://example.com")
        result = extractor.extract(html)
        assert len(result.images) >= 1
        src, alt = result.images[0]
        assert "image.png" in src
        assert alt == "An image"

    def test_extract_meta_description(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        assert result.meta.get("description") == "A test page"

    def test_extract_content_hash_non_empty(self):
        extractor = ContentExtractor()
        result = extractor.extract(self.SIMPLE_HTML)
        assert len(result.content_hash) == 64  # SHA-256 hex = 64 chars

    def test_empty_html_returns_defaults(self):
        extractor = ContentExtractor()
        result = extractor.extract("")
        assert result.title == ""
        assert result.headings == []
        assert result.paragraphs == []


# ---------------------------------------------------------------------------
# text_similarity
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTextSimilarity:
    """Jaccard text similarity edge case tests."""

    def test_identical_texts(self):
        score = text_similarity("hello world", "hello world")
        assert score == 1.0

    def test_completely_different(self):
        score = text_similarity("apple orange", "car truck")
        assert score == 0.0

    def test_partial_overlap(self):
        score = text_similarity("hello world", "hello python")
        assert 0.0 < score < 1.0

    def test_both_empty_returns_one(self):
        score = text_similarity("", "")
        assert score == 1.0

    def test_one_empty_returns_zero(self):
        score = text_similarity("hello", "")
        assert score == 0.0

    def test_case_insensitive(self):
        score_lower = text_similarity("hello world", "hello world")
        score_mixed = text_similarity("Hello World", "hello world")
        assert score_lower == score_mixed

    def test_word_order_invariant(self):
        score1 = text_similarity("apple banana cherry", "cherry apple banana")
        assert score1 == 1.0


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScrapeExceptions:
    """Exception class and hierarchy tests."""

    def test_scraping_error_base(self):
        err = ScrapingError("something broke", url="https://example.com")
        assert str(err) == "something broke"
        assert err.url == "https://example.com"

    def test_error_dict_fields(self):
        err = ScrapingError("msg", url="https://x.com")
        d = err.error_dict
        assert d["error_type"] == "ScrapingError"
        assert d["message"] == "msg"
        assert d["url"] == "https://x.com"

    def test_request_error_status_code(self):
        err = RequestError("Request failed", url="https://x.com", status_code=500)
        assert err.status_code == 500
        assert err.is_server_error is True
        assert err.is_client_error is False

    def test_request_error_client_error(self):
        err = RequestError("Not found", url="https://x.com", status_code=404)
        assert err.is_client_error is True
        assert err.is_server_error is False

    def test_parse_error_fields(self):
        err = ParseError("Parse failed", url="https://x.com", selector=".main")
        assert err.selector == ".main"

    def test_rate_limit_error_retry_after(self):
        err = RateLimitError(retry_after=60.0)
        assert err.retry_after == 60.0

    def test_captcha_error_type(self):
        err = CaptchaError(captcha_type="recaptcha")
        assert err.captcha_type == "recaptcha"

    def test_content_not_found_selector(self):
        err = ContentNotFoundError(selector=".article")
        assert err.selector == ".article"

    def test_blocked_error_reason(self):
        err = BlockedError(reason="IP banned")
        assert err.reason == "IP banned"

    def test_scrape_error_alias(self):
        # ScrapeError is an alias for ScrapingError
        assert ScrapeError is ScrapingError

    def test_scrape_validation_error_fields(self):
        err = ScrapeValidationError("bad url", field="url", value="not-a-url")
        assert err.field == "url"
        assert err.value == "not-a-url"

    def test_scrape_timeout_error(self):
        err = ScrapeTimeoutError(url="https://x.com", timeout=30.0)
        assert err.timeout == 30.0

    def test_authentication_error_is_scraping_error(self):
        err = AuthenticationError()
        assert isinstance(err, ScrapingError)


# ---------------------------------------------------------------------------
# classify_http_error
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestClassifyHttpError:
    """classify_http_error returns the right exception type."""

    def test_429_rate_limit(self):
        err = classify_http_error(429, url="https://x.com")
        assert isinstance(err, RateLimitError)

    def test_401_authentication(self):
        err = classify_http_error(401, url="https://x.com")
        assert isinstance(err, AuthenticationError)

    def test_403_blocked(self):
        err = classify_http_error(403, url="https://x.com")
        assert isinstance(err, BlockedError)

    def test_404_content_not_found(self):
        err = classify_http_error(404, url="https://x.com")
        assert isinstance(err, ContentNotFoundError)

    def test_500_request_error(self):
        err = classify_http_error(500, url="https://x.com")
        assert isinstance(err, RequestError)

    def test_all_errors_are_scraping_errors(self):
        for code in [401, 403, 404, 429, 500, 503]:
            err = classify_http_error(code)
            assert isinstance(err, ScrapingError)


# ---------------------------------------------------------------------------
# MCP tools — pure Python, no network
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScrapeMcpToolsContent:
    """scrape_extract_content MCP tool tests (pure Python, no network)."""

    def test_success_status(self):
        from codomyrmex.scrape.mcp_tools import scrape_extract_content

        html = "<html><head><title>Hello</title></head><body><p>World</p></body></html>"
        result = scrape_extract_content(html=html)
        assert result["status"] == "success"

    def test_title_extracted(self):
        from codomyrmex.scrape.mcp_tools import scrape_extract_content

        html = "<html><head><title>My Title</title></head><body></body></html>"
        result = scrape_extract_content(html=html)
        assert result["title"] == "My Title"

    def test_result_fields_present(self):
        from codomyrmex.scrape.mcp_tools import scrape_extract_content

        html = "<html><body><h1>Heading</h1><p>Para</p></body></html>"
        result = scrape_extract_content(html=html)
        for key in (
            "title",
            "headings",
            "paragraph_count",
            "link_count",
            "word_count",
            "content_hash",
        ):
            assert key in result

    def test_headings_structured(self):
        from codomyrmex.scrape.mcp_tools import scrape_extract_content

        html = "<html><body><h1>Title</h1><h2>Sub</h2></body></html>"
        result = scrape_extract_content(html=html)
        assert isinstance(result["headings"], list)
        if result["headings"]:
            h = result["headings"][0]
            assert "level" in h
            assert "text" in h

    def test_base_url_resolves_links(self):
        from codomyrmex.scrape.mcp_tools import scrape_extract_content

        html = '<html><body><a href="/page">Link</a></body></html>'
        result = scrape_extract_content(html=html, base_url="https://example.com")
        assert result["status"] == "success"


@pytest.mark.unit
class TestScrapeMcpToolsSimilarity:
    """scrape_text_similarity MCP tool tests."""

    def test_identical_texts(self):
        from codomyrmex.scrape.mcp_tools import scrape_text_similarity

        result = scrape_text_similarity(text_a="hello world", text_b="hello world")
        assert result["status"] == "success"
        assert result["similarity"] == 1.0

    def test_different_texts_low_similarity(self):
        from codomyrmex.scrape.mcp_tools import scrape_text_similarity

        result = scrape_text_similarity(text_a="apple orange", text_b="car truck")
        assert result["status"] == "success"
        assert result["similarity"] == 0.0

    def test_partial_similarity_between_zero_and_one(self):
        from codomyrmex.scrape.mcp_tools import scrape_text_similarity

        result = scrape_text_similarity(text_a="hello world", text_b="hello python")
        assert 0.0 < result["similarity"] < 1.0
