"""Zero-mock tests for scrape module core: exceptions, scraper validation,
config, core dataclasses, and MCP tool return shapes.

Targets:
- exceptions.py: full exception hierarchy, classify_http_error utility
- extractors/scraper.py: URL validation paths (no adapter needed)
- config.py: ScrapeConfig from_env, validate, to_dict
- core.py: ScrapeResult.get_format/has_format, ScrapeOptions.to_dict, MapResult auto-total
- mcp_tools.py: scrape_extract_content, scrape_text_similarity

No mocks. No monkeypatch. No MagicMock.
HTTP calls are behind @pytest.mark.skipif(not os.getenv("ALLOW_NETWORK")).
"""

from __future__ import annotations

import os

import pytest

# ---------------------------------------------------------------------------
# Module-level availability guards
# ---------------------------------------------------------------------------

try:
    from codomyrmex.scrape.exceptions import (
        AuthenticationError,
        BlockedError,
        CaptchaError,
        ContentNotFoundError,
        FirecrawlError,
        ParseError,
        RateLimitError,
        RequestError,
        ScrapeConnectionError,
        ScrapeError,
        ScrapeTimeoutError,
        ScrapeValidationError,
        ScrapingError,
        classify_http_error,
    )

    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False

try:
    from codomyrmex.scrape.core import (
        CrawlResult,
        ExtractResult,
        MapResult,
        ScrapeFormat,
        ScrapeOptions,
        ScrapeResult,
    )

    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

try:
    from codomyrmex.scrape.config import (
        ScrapeConfig,
        get_config,
        reset_config,
        set_config,
    )

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from codomyrmex.scrape.mcp_tools import (
        scrape_extract_content,
        scrape_text_similarity,
    )

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


# ---------------------------------------------------------------------------
# ScrapingError base class
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestScrapingErrorBase:
    """Base exception stores all fields correctly."""

    def test_message_stored(self):
        err = ScrapingError("something went wrong")
        assert str(err) == "something went wrong"

    def test_url_stored(self):
        err = ScrapingError("fail", url="https://example.com")
        assert err.url == "https://example.com"

    def test_context_stored(self):
        err = ScrapingError("fail", context={"key": "value"})
        assert err.context["key"] == "value"

    def test_context_merged_into_details(self):
        err = ScrapingError("fail", context={"extra": "info"})
        assert err.details["extra"] == "info"

    def test_error_dict_has_required_keys(self):
        err = ScrapingError("fail", url="https://x.com")
        d = err.error_dict
        assert "error_type" in d
        assert "message" in d
        assert "url" in d
        assert "details" in d

    def test_error_dict_type_is_class_name(self):
        err = ScrapingError("fail")
        assert err.error_dict["error_type"] == "ScrapingError"

    def test_default_url_empty_string(self):
        err = ScrapingError("fail")
        assert err.url == ""

    def test_default_context_empty_dict(self):
        err = ScrapingError("fail")
        assert err.context == {}


# ---------------------------------------------------------------------------
# RequestError
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestRequestError:
    """RequestError stores HTTP-specific fields correctly."""

    def test_status_code_stored(self):
        err = RequestError("bad request", status_code=400)
        assert err.status_code == 400

    def test_response_body_truncated_at_500(self):
        long_body = "x" * 600
        err = RequestError("fail", response_body=long_body)
        assert len(err.response_body) == 500

    def test_response_body_short_not_truncated(self):
        err = RequestError("fail", response_body="short")
        assert err.response_body == "short"

    def test_is_server_error_true_for_5xx(self):
        for code in [500, 502, 503, 504]:
            err = RequestError("err", status_code=code)
            assert err.is_server_error is True

    def test_is_server_error_false_for_4xx(self):
        err = RequestError("err", status_code=404)
        assert err.is_server_error is False

    def test_is_client_error_true_for_4xx(self):
        for code in [400, 401, 403, 404, 422]:
            err = RequestError("err", status_code=code)
            assert err.is_client_error is True

    def test_is_client_error_false_for_5xx(self):
        err = RequestError("err", status_code=500)
        assert err.is_client_error is False

    def test_is_server_error_false_when_no_status(self):
        err = RequestError("err")
        assert err.is_server_error is False

    def test_is_client_error_false_when_no_status(self):
        err = RequestError("err")
        assert err.is_client_error is False

    def test_url_stored(self):
        err = RequestError("fail", url="https://api.example.com")
        assert err.url == "https://api.example.com"


# ---------------------------------------------------------------------------
# ParseError
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestParseError:
    """ParseError stores selector and preview."""

    def test_selector_stored(self):
        err = ParseError("parse fail", selector=".content")
        assert err.selector == ".content"

    def test_content_preview_truncated_at_200(self):
        long_content = "y" * 300
        err = ParseError("fail", content_preview=long_content)
        assert len(err.content_preview) == 200

    def test_content_preview_short_not_truncated(self):
        err = ParseError("fail", content_preview="small")
        assert err.content_preview == "small"

    def test_selector_in_details(self):
        err = ParseError("fail", selector="#main")
        assert err.details["selector"] == "#main"


# ---------------------------------------------------------------------------
# RateLimitError
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestScrapeRateLimitError:
    """RateLimitError stores retry_after."""

    def test_retry_after_stored(self):
        err = RateLimitError("limited", retry_after=120.0)
        assert err.retry_after == 120.0

    def test_retry_after_in_details(self):
        err = RateLimitError("limited", retry_after=60.0)
        assert err.details["retry_after"] == 60.0

    def test_default_message(self):
        err = RateLimitError()
        assert "Rate limited" in str(err)

    def test_url_stored(self):
        err = RateLimitError("rate limit", url="https://api.example.com")
        assert err.url == "https://api.example.com"


# ---------------------------------------------------------------------------
# CaptchaError
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestCaptchaError:
    """CaptchaError stores captcha_type."""

    def test_captcha_type_stored(self):
        err = CaptchaError("captcha", captcha_type="recaptcha")
        assert err.captcha_type == "recaptcha"

    def test_default_captcha_type(self):
        err = CaptchaError()
        assert err.captcha_type == "unknown"

    def test_default_message(self):
        err = CaptchaError()
        assert "CAPTCHA" in str(err)

    def test_in_details(self):
        err = CaptchaError(captcha_type="hcaptcha")
        assert err.details["captcha_type"] == "hcaptcha"


# ---------------------------------------------------------------------------
# BlockedError, ContentNotFoundError, AuthenticationError
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestBlockedAndContentErrors:
    """Test BlockedError, ContentNotFoundError, AuthenticationError."""

    def test_blocked_reason_stored(self):
        err = BlockedError("blocked", reason="IP ban")
        assert err.reason == "IP ban"

    def test_blocked_reason_in_details(self):
        err = BlockedError(reason="rate-IP-ban")
        assert err.details["reason"] == "rate-IP-ban"

    def test_content_not_found_selector(self):
        err = ContentNotFoundError("not found", selector=".article")
        assert err.selector == ".article"

    def test_content_not_found_selector_in_details(self):
        err = ContentNotFoundError(selector="#content")
        assert err.details["selector"] == "#content"

    def test_authentication_error_message(self):
        err = AuthenticationError("invalid token")
        assert "invalid token" in str(err)

    def test_authentication_error_url(self):
        err = AuthenticationError(url="https://secure.example.com")
        assert err.url == "https://secure.example.com"


# ---------------------------------------------------------------------------
# FirecrawlError, ScrapeConnectionError, ScrapeTimeoutError, ScrapeValidationError
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestDerivedExceptions:
    """Derived exception classes store extra fields correctly."""

    def test_firecrawl_error_wraps_original(self):
        original = ValueError("firecrawl sdk error")
        err = FirecrawlError("Firecrawl failed", firecrawl_error=original)
        assert err.firecrawl_error is original

    def test_firecrawl_error_original_in_details(self):
        original = RuntimeError("upstream error")
        err = FirecrawlError("fail", firecrawl_error=original)
        assert "upstream error" in err.details["firecrawl_error"]

    def test_firecrawl_error_without_original(self):
        err = FirecrawlError("basic fail")
        assert err.firecrawl_error is None

    def test_scrape_connection_error_is_request_error(self):
        err = ScrapeConnectionError("connection failed")
        assert isinstance(err, RequestError)

    def test_scrape_timeout_error_stores_timeout(self):
        err = ScrapeTimeoutError("timed out", timeout=30.0)
        assert err.timeout == 30.0

    def test_scrape_timeout_is_request_error(self):
        err = ScrapeTimeoutError()
        assert isinstance(err, RequestError)

    def test_scrape_validation_error_stores_field(self):
        err = ScrapeValidationError("bad input", field="url")
        assert err.field == "url"

    def test_scrape_validation_error_stores_value(self):
        err = ScrapeValidationError("bad value", value="not-a-url")
        assert err.value == "not-a-url"

    def test_scrape_validation_error_fields_in_details(self):
        err = ScrapeValidationError("fail", field="query", value="")
        assert err.details["field"] == "query"

    def test_scrape_error_alias_is_scraping_error(self):
        # ScrapeError = ScrapingError alias
        assert ScrapeError is ScrapingError


# ---------------------------------------------------------------------------
# Exception inheritance tree
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestExceptionInheritanceTree:
    """All scrape exceptions descend from ScrapingError."""

    def test_request_error_is_scraping_error(self):
        assert issubclass(RequestError, ScrapingError)

    def test_parse_error_is_scraping_error(self):
        assert issubclass(ParseError, ScrapingError)

    def test_rate_limit_error_is_scraping_error(self):
        assert issubclass(RateLimitError, ScrapingError)

    def test_captcha_error_is_scraping_error(self):
        assert issubclass(CaptchaError, ScrapingError)

    def test_auth_error_is_scraping_error(self):
        assert issubclass(AuthenticationError, ScrapingError)

    def test_content_not_found_is_scraping_error(self):
        assert issubclass(ContentNotFoundError, ScrapingError)

    def test_blocked_error_is_scraping_error(self):
        assert issubclass(BlockedError, ScrapingError)

    def test_firecrawl_error_is_scraping_error(self):
        assert issubclass(FirecrawlError, ScrapingError)

    def test_connection_error_is_request_error(self):
        assert issubclass(ScrapeConnectionError, RequestError)

    def test_timeout_error_is_request_error(self):
        assert issubclass(ScrapeTimeoutError, RequestError)

    def test_validation_error_is_scraping_error(self):
        assert issubclass(ScrapeValidationError, ScrapingError)


# ---------------------------------------------------------------------------
# classify_http_error utility
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestClassifyHttpError:
    """classify_http_error returns correct exception types."""

    def test_429_returns_rate_limit_error(self):
        err = classify_http_error(429, url="https://api.example.com")
        assert isinstance(err, RateLimitError)

    def test_401_returns_authentication_error(self):
        err = classify_http_error(401)
        assert isinstance(err, AuthenticationError)

    def test_403_returns_blocked_error(self):
        err = classify_http_error(403)
        assert isinstance(err, BlockedError)

    def test_403_reason_contains_status(self):
        err = classify_http_error(403)
        assert isinstance(err, BlockedError)
        assert "403" in err.reason

    def test_404_returns_content_not_found(self):
        err = classify_http_error(404)
        assert isinstance(err, ContentNotFoundError)

    def test_500_returns_request_error(self):
        err = classify_http_error(500)
        assert isinstance(err, RequestError)

    def test_502_returns_request_error(self):
        err = classify_http_error(502)
        assert isinstance(err, RequestError)

    def test_url_passed_through_to_error(self):
        err = classify_http_error(429, url="https://rate.limited.com")
        assert err.url == "https://rate.limited.com"

    def test_body_passed_to_generic_request_error(self):
        err = classify_http_error(500, body="Internal Server Error")
        assert isinstance(err, RequestError)
        # response_body is stored on RequestError
        assert err.response_body == "Internal Server Error"


# ---------------------------------------------------------------------------
# Scraper URL validation (no adapter needed for validation errors)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
@pytest.mark.skipif(not CORE_AVAILABLE, reason="scrape.core not importable")
class TestScraperUrlValidation:
    """Scraper.scrape/crawl/map/extract raise ScrapeValidationError for bad URLs."""

    def _make_scraper(self):
        """Create a Scraper with a dummy config but no real adapter."""
        from codomyrmex.scrape.config import ScrapeConfig

        # Minimal concrete adapter that satisfies the abstract contract
        from codomyrmex.scrape.core import (
            BaseScraper,
        )
        from codomyrmex.scrape.extractors.scraper import Scraper

        class _StubAdapter(BaseScraper):
            def scrape(self, url, options=None):
                raise NotImplementedError

            def crawl(self, url, options=None):
                raise NotImplementedError

            def map(self, url, search=None):
                raise NotImplementedError

            def search(self, query, options=None):
                raise NotImplementedError

            def extract(self, urls, schema=None, prompt=None):
                raise NotImplementedError

        config = ScrapeConfig(api_key="test-key")
        return Scraper(config=config, adapter=_StubAdapter())

    def test_scrape_empty_url_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.scrape("")

    def test_scrape_non_http_url_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.scrape("ftp://example.com/file")

    def test_scrape_relative_url_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.scrape("/relative/path")

    def test_crawl_empty_url_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.crawl("")

    def test_crawl_non_http_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.crawl("ssh://example.com")

    def test_map_empty_url_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.map("")

    def test_map_invalid_scheme_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.map("file:///etc/passwd")

    def test_search_empty_query_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.search("")

    def test_extract_empty_list_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.extract([])

    def test_extract_invalid_url_in_list_raises_validation_error(self):
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        with pytest.raises(ScrapeValidationError):
            scraper.extract(["not-a-valid-url"])

    def test_http_url_passes_validation_then_raises_scrape_error(self):
        # The stub adapter raises NotImplementedError which Scraper wraps in ScrapeError.
        # This verifies URL validation passed and the call reached the adapter.
        scraper = self._make_scraper()
        from codomyrmex.scrape.exceptions import ScrapingError

        with pytest.raises(ScrapingError):
            scraper.scrape("https://example.com")


# ---------------------------------------------------------------------------
# ScrapeConfig
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="scrape.config not importable")
class TestScrapeConfig:
    """ScrapeConfig field values, validation, and env parsing."""

    def test_default_api_key_none(self):
        cfg = ScrapeConfig()
        assert cfg.api_key is None

    def test_default_base_url(self):
        cfg = ScrapeConfig()
        assert cfg.base_url == "https://api.firecrawl.dev"

    def test_default_timeout(self):
        cfg = ScrapeConfig()
        assert cfg.default_timeout == 30.0

    def test_default_max_retries(self):
        cfg = ScrapeConfig()
        assert cfg.max_retries == 3

    def test_default_respect_robots_txt_true(self):
        cfg = ScrapeConfig()
        assert cfg.respect_robots_txt is True

    def test_validate_raises_on_no_api_key(self):
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        cfg = ScrapeConfig(api_key=None)
        with pytest.raises(ScrapeValidationError):
            cfg.validate()

    def test_validate_raises_on_zero_timeout(self):
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        cfg = ScrapeConfig(api_key="key", default_timeout=0.0)
        with pytest.raises(ScrapeValidationError):
            cfg.validate()

    def test_validate_raises_on_negative_timeout(self):
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        cfg = ScrapeConfig(api_key="key", default_timeout=-5.0)
        with pytest.raises(ScrapeValidationError):
            cfg.validate()

    def test_validate_raises_on_negative_max_retries(self):
        from codomyrmex.scrape.exceptions import ScrapeValidationError

        cfg = ScrapeConfig(api_key="key", max_retries=-1)
        with pytest.raises(ScrapeValidationError):
            cfg.validate()

    def test_validate_passes_with_valid_config(self):
        cfg = ScrapeConfig(api_key="real-key", default_timeout=30.0, max_retries=3)
        cfg.validate()  # must not raise

    def test_to_dict_masks_api_key(self):
        cfg = ScrapeConfig(api_key="super-secret")
        d = cfg.to_dict()
        assert d["api_key"] == "***"

    def test_to_dict_omits_api_key_when_none(self):
        cfg = ScrapeConfig(api_key=None)
        d = cfg.to_dict()
        assert "api_key" not in d

    def test_to_dict_includes_base_url(self):
        cfg = ScrapeConfig()
        d = cfg.to_dict()
        assert "base_url" in d

    def test_to_dict_includes_timeout(self):
        cfg = ScrapeConfig(default_timeout=45.0)
        d = cfg.to_dict()
        assert d["default_timeout"] == 45.0

    def test_from_env_reads_firecrawl_api_key(self):
        import os

        original = os.environ.pop("FIRECRAWL_API_KEY", None)
        try:
            os.environ["FIRECRAWL_API_KEY"] = "env-test-key"
            cfg = ScrapeConfig.from_env()
            assert cfg.api_key == "env-test-key"
        finally:
            os.environ.pop("FIRECRAWL_API_KEY", None)
            if original is not None:
                os.environ["FIRECRAWL_API_KEY"] = original

    def test_from_env_reads_timeout(self):
        import os

        original = os.environ.pop("SCRAPE_TIMEOUT", None)
        try:
            os.environ["SCRAPE_TIMEOUT"] = "60.0"
            cfg = ScrapeConfig.from_env()
            assert cfg.default_timeout == 60.0
        finally:
            os.environ.pop("SCRAPE_TIMEOUT", None)
            if original is not None:
                os.environ["SCRAPE_TIMEOUT"] = original

    def test_from_env_reads_max_retries(self):
        import os

        original = os.environ.pop("SCRAPE_MAX_RETRIES", None)
        try:
            os.environ["SCRAPE_MAX_RETRIES"] = "5"
            cfg = ScrapeConfig.from_env()
            assert cfg.max_retries == 5
        finally:
            os.environ.pop("SCRAPE_MAX_RETRIES", None)
            if original is not None:
                os.environ["SCRAPE_MAX_RETRIES"] = original

    def test_set_and_reset_config(self):
        cfg = ScrapeConfig(api_key="set-test")
        set_config(cfg)
        fetched = get_config()
        assert fetched.api_key == "set-test"
        reset_config()
        # After reset, get_config reads from env (key may or may not be set)
        new_cfg = get_config()
        assert isinstance(new_cfg, ScrapeConfig)
        reset_config()  # cleanup


# ---------------------------------------------------------------------------
# ScrapeResult, ScrapeOptions, ScrapeFormat core dataclasses
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not CORE_AVAILABLE, reason="scrape.core not importable")
class TestCoreDataclasses:
    """Test ScrapeResult, ScrapeOptions, and format helpers."""

    def test_scrape_result_defaults(self):
        r = ScrapeResult(url="https://example.com")
        assert r.content == ""
        assert r.success is True
        assert r.error is None
        assert r.status_code is None

    def test_scrape_result_get_format_enum(self):
        r = ScrapeResult(url="https://ex.com", formats={"markdown": "# Hello"})
        assert r.get_format(ScrapeFormat.MARKDOWN) == "# Hello"

    def test_scrape_result_get_format_string(self):
        r = ScrapeResult(url="https://ex.com", formats={"html": "<p>Hi</p>"})
        assert r.get_format("html") == "<p>Hi</p>"

    def test_scrape_result_get_format_missing_returns_none(self):
        r = ScrapeResult(url="https://ex.com", formats={})
        assert r.get_format(ScrapeFormat.JSON) is None

    def test_scrape_result_has_format_true(self):
        r = ScrapeResult(url="https://ex.com", formats={"markdown": "data"})
        assert r.has_format(ScrapeFormat.MARKDOWN) is True

    def test_scrape_result_has_format_false(self):
        r = ScrapeResult(url="https://ex.com", formats={})
        assert r.has_format(ScrapeFormat.HTML) is False

    def test_scrape_format_enum_values(self):
        assert ScrapeFormat.MARKDOWN.value == "markdown"
        assert ScrapeFormat.HTML.value == "html"
        assert ScrapeFormat.JSON.value == "json"
        assert ScrapeFormat.LINKS.value == "links"
        assert ScrapeFormat.SCREENSHOT.value == "screenshot"
        assert ScrapeFormat.METADATA.value == "metadata"

    def test_scrape_options_defaults(self):
        opts = ScrapeOptions()
        assert opts.formats == [ScrapeFormat.MARKDOWN]
        assert opts.timeout is None
        assert opts.follow_links is True
        assert opts.respect_robots_txt is True
        assert opts.headers == {}
        assert opts.max_depth is None
        assert opts.limit is None

    def test_scrape_options_to_dict_formats_as_strings(self):
        opts = ScrapeOptions(formats=[ScrapeFormat.MARKDOWN, ScrapeFormat.HTML])
        d = opts.to_dict()
        assert d["formats"] == ["markdown", "html"]

    def test_scrape_options_to_dict_timeout_present_when_set(self):
        opts = ScrapeOptions(timeout=45.0)
        d = opts.to_dict()
        assert d["timeout"] == 45.0

    def test_scrape_options_to_dict_timeout_absent_when_none(self):
        opts = ScrapeOptions(timeout=None)
        d = opts.to_dict()
        assert "timeout" not in d

    def test_scrape_options_to_dict_max_depth_present_when_set(self):
        opts = ScrapeOptions(max_depth=3)
        d = opts.to_dict()
        assert d["max_depth"] == 3

    def test_crawl_result_defaults(self):
        cr = CrawlResult(job_id="j1", status="pending")
        assert cr.total == 0
        assert cr.completed == 0
        assert cr.results == []
        assert cr.credits_used == 0
        assert cr.expires_at is None

    def test_map_result_auto_calculates_total_from_links(self):
        links = [{"url": "https://a.com"}, {"url": "https://b.com"}]
        mr = MapResult(links=links)
        assert mr.total == 2

    def test_map_result_explicit_total_zero_triggers_auto(self):
        links = [{"url": "https://a.com"}]
        mr = MapResult(links=links, total=0)
        assert mr.total == 1

    def test_map_result_no_links_total_stays_zero(self):
        mr = MapResult(links=[])
        assert mr.total == 0

    def test_extract_result_defaults(self):
        er = ExtractResult()
        assert er.status == "completed"
        assert er.data == {}
        assert er.urls == []
        assert er.job_id is None

    def test_extract_result_with_data(self):
        er = ExtractResult(data={"title": "Page"}, urls=["https://x.com"])
        assert er.data["title"] == "Page"
        assert "https://x.com" in er.urls


# ---------------------------------------------------------------------------
# MCP tool shape tests (no network)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not MCP_AVAILABLE, reason="scrape.mcp_tools not importable")
class TestScrapeMcpTools:
    """scrape MCP tools return correct shape without network calls."""

    def test_extract_content_success_on_simple_html(self):
        result = scrape_extract_content("<html><title>Test</title><p>Hello</p></html>")
        assert result["status"] == "success"
        assert result["title"] == "Test"

    def test_extract_content_has_required_fields(self):
        result = scrape_extract_content("<html><h1>Heading</h1></html>")
        for key in (
            "status",
            "title",
            "headings",
            "paragraph_count",
            "link_count",
            "word_count",
        ):
            assert key in result

    def test_extract_content_headings_list(self):
        result = scrape_extract_content("<h1>Main</h1><h2>Sub</h2>")
        assert isinstance(result["headings"], list)

    def test_extract_content_heading_has_level_and_text(self):
        result = scrape_extract_content("<h1>Main Heading</h1>")
        if result["headings"]:
            h = result["headings"][0]
            assert "level" in h
            assert "text" in h

    def test_extract_content_with_base_url(self):
        html = '<a href="/page">Link</a>'
        result = scrape_extract_content(html, base_url="https://example.com")
        assert result["status"] == "success"
        assert result["link_count"] >= 1

    def test_extract_content_empty_html_succeeds(self):
        result = scrape_extract_content("")
        assert result["status"] == "success"

    def test_text_similarity_identical_strings(self):
        result = scrape_text_similarity("hello world", "hello world")
        assert result["status"] == "success"
        assert result["similarity"] == 1.0

    def test_text_similarity_completely_different(self):
        result = scrape_text_similarity("apple orange banana", "xyz abc def")
        assert result["status"] == "success"
        assert result["similarity"] == 0.0

    def test_text_similarity_partial_overlap(self):
        result = scrape_text_similarity("hello world", "hello planet")
        assert result["status"] == "success"
        assert 0.0 < result["similarity"] < 1.0

    def test_text_similarity_returns_float(self):
        result = scrape_text_similarity("foo", "bar")
        assert isinstance(result["similarity"], float)

    def test_text_similarity_empty_strings(self):
        result = scrape_text_similarity("", "")
        assert result["status"] == "success"


# ---------------------------------------------------------------------------
# Network-gated tests (real HTTP calls)
# ---------------------------------------------------------------------------

_ALLOW_NETWORK = os.getenv("ALLOW_NETWORK") == "1"


@pytest.mark.skipif(not _ALLOW_NETWORK, reason="ALLOW_NETWORK=1 not set")
@pytest.mark.skipif(not EXCEPTIONS_AVAILABLE, reason="scrape.exceptions not importable")
class TestScraperNetworkPaths:
    """Real network tests — only run when ALLOW_NETWORK=1."""

    def test_scrape_real_url_returns_scrape_result(self):
        from codomyrmex.scrape.extractors.scraper import Scraper

        scraper = Scraper()
        result = scraper.scrape("https://httpbin.org/get")
        assert result is not None
