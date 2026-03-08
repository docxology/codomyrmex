"""Zero-mock tests for scrape/exceptions.py.

Tests all exception classes: hierarchy, attribute storage, property behaviors,
error_dict output, and the classify_http_error utility function.
"""

from __future__ import annotations

import pytest

from codomyrmex.scrape.exceptions import (
    AuthenticationError,
    BlockedError,
    CaptchaError,
    ContentNotFoundError,
    FirecrawlError,
    ParseError,
    RateLimitError,
    RequestError,
    ScrapingError,
    ScrapeConnectionError,
    ScrapeTimeoutError,
    ScrapeValidationError,
    classify_http_error,
)


@pytest.mark.unit
class TestScrapingErrorBase:
    """Tests for the ScrapingError base class."""

    def test_is_exception(self):
        err = ScrapingError("base error")
        assert isinstance(err, Exception)

    def test_message_preserved(self):
        err = ScrapingError("something went wrong")
        assert str(err) == "something went wrong"

    def test_url_stored(self):
        err = ScrapingError("error", url="https://example.com")
        assert err.url == "https://example.com"

    def test_url_empty_by_default(self):
        err = ScrapingError("error")
        assert err.url == ""

    def test_details_stored(self):
        err = ScrapingError("error", details={"key": "value"})
        assert err.details["key"] == "value"

    def test_details_empty_by_default(self):
        err = ScrapingError("error")
        assert err.details == {}

    def test_context_merged_into_details(self):
        err = ScrapingError("error", context={"source": "test"})
        assert err.details["source"] == "test"

    def test_error_dict_contains_required_keys(self):
        err = ScrapingError("error", url="https://example.com")
        d = err.error_dict
        assert d["error_type"] == "ScrapingError"
        assert d["message"] == "error"
        assert d["url"] == "https://example.com"
        assert "details" in d

    def test_error_dict_subclass_name(self):
        err = RateLimitError(url="https://example.com")
        d = err.error_dict
        assert d["error_type"] == "RateLimitError"


@pytest.mark.unit
class TestRequestError:
    """Tests for RequestError status code, properties, and truncation."""

    def test_stores_status_code(self):
        err = RequestError("failed", status_code=500)
        assert err.status_code == 500

    def test_status_code_none_by_default(self):
        err = RequestError("failed")
        assert err.status_code is None

    def test_is_server_error_true_for_500(self):
        err = RequestError("failed", status_code=500)
        assert err.is_server_error is True

    def test_is_server_error_true_for_503(self):
        err = RequestError("failed", status_code=503)
        assert err.is_server_error is True

    def test_is_server_error_false_for_404(self):
        err = RequestError("failed", status_code=404)
        assert err.is_server_error is False

    def test_is_server_error_false_when_none(self):
        err = RequestError("failed")
        assert err.is_server_error is False

    def test_is_client_error_true_for_400(self):
        err = RequestError("failed", status_code=400)
        assert err.is_client_error is True

    def test_is_client_error_true_for_429(self):
        err = RequestError("failed", status_code=429)
        assert err.is_client_error is True

    def test_is_client_error_false_for_500(self):
        err = RequestError("failed", status_code=500)
        assert err.is_client_error is False

    def test_is_client_error_false_when_none(self):
        err = RequestError("failed")
        assert err.is_client_error is False

    def test_response_body_stored(self):
        err = RequestError("failed", response_body="error page content")
        assert err.response_body == "error page content"

    def test_response_body_truncated_at_500_chars(self):
        long_body = "x" * 600
        err = RequestError("failed", response_body=long_body)
        assert len(err.response_body) == 500

    def test_response_body_empty_by_default(self):
        err = RequestError("failed")
        assert err.response_body == ""

    def test_url_stored(self):
        err = RequestError("failed", url="https://example.com/page")
        assert err.url == "https://example.com/page"


@pytest.mark.unit
class TestParseError:
    """Tests for ParseError selector and content storage."""

    def test_is_scraping_error(self):
        err = ParseError("parse failed")
        assert isinstance(err, ScrapingError)

    def test_stores_selector(self):
        err = ParseError("parse failed", selector=".article-body")
        assert err.selector == ".article-body"

    def test_stores_content_preview(self):
        err = ParseError("parse failed", content_preview="<div>content</div>")
        assert err.content_preview == "<div>content</div>"

    def test_content_preview_truncated_at_200_chars(self):
        long_content = "x" * 300
        err = ParseError("parse failed", content_preview=long_content)
        assert len(err.content_preview) == 200

    def test_details_contains_selector(self):
        err = ParseError("parse failed", selector="#main", url="https://example.com")
        assert err.details["selector"] == "#main"


@pytest.mark.unit
class TestRateLimitError:
    """Tests for RateLimitError retry_after storage."""

    def test_stores_retry_after(self):
        err = RateLimitError(retry_after=30.0)
        assert err.retry_after == 30.0

    def test_retry_after_none_by_default(self):
        err = RateLimitError()
        assert err.retry_after is None

    def test_stores_url(self):
        err = RateLimitError(url="https://example.com")
        assert err.url == "https://example.com"

    def test_default_message(self):
        err = RateLimitError()
        assert "Rate limited" in str(err)


@pytest.mark.unit
class TestCaptchaError:
    """Tests for CaptchaError captcha_type storage."""

    def test_stores_captcha_type(self):
        err = CaptchaError(captcha_type="recaptcha")
        assert err.captcha_type == "recaptcha"

    def test_default_captcha_type_unknown(self):
        err = CaptchaError()
        assert err.captcha_type == "unknown"

    def test_default_message(self):
        err = CaptchaError()
        assert "CAPTCHA" in str(err)


@pytest.mark.unit
class TestAuthenticationError:
    """Tests for AuthenticationError basic functionality."""

    def test_is_scraping_error(self):
        err = AuthenticationError()
        assert isinstance(err, ScrapingError)

    def test_default_message(self):
        err = AuthenticationError()
        assert "Authentication failed" in str(err)

    def test_custom_message(self):
        err = AuthenticationError("session expired", url="https://example.com")
        assert "session expired" in str(err)


@pytest.mark.unit
class TestContentNotFoundError:
    """Tests for ContentNotFoundError selector storage."""

    def test_stores_selector(self):
        err = ContentNotFoundError(selector=".price")
        assert err.selector == ".price"

    def test_selector_in_details(self):
        err = ContentNotFoundError(selector=".main", url="https://example.com")
        assert err.details["selector"] == ".main"

    def test_default_message(self):
        err = ContentNotFoundError()
        assert "Content not found" in str(err)


@pytest.mark.unit
class TestBlockedError:
    """Tests for BlockedError reason storage."""

    def test_stores_reason(self):
        err = BlockedError(reason="user-agent blacklisted")
        assert err.reason == "user-agent blacklisted"

    def test_reason_in_details(self):
        err = BlockedError(reason="IP banned", url="https://example.com")
        assert err.details["reason"] == "IP banned"

    def test_default_message(self):
        err = BlockedError()
        assert "Blocked" in str(err)


@pytest.mark.unit
class TestClassifyHttpError:
    """Tests for the classify_http_error utility function."""

    def test_429_returns_rate_limit_error(self):
        err = classify_http_error(429, url="https://example.com")
        assert isinstance(err, RateLimitError)

    def test_401_returns_authentication_error(self):
        err = classify_http_error(401, url="https://example.com")
        assert isinstance(err, AuthenticationError)

    def test_403_returns_blocked_error(self):
        err = classify_http_error(403, url="https://example.com")
        assert isinstance(err, BlockedError)
        assert "HTTP 403" in err.reason

    def test_404_returns_content_not_found_error(self):
        err = classify_http_error(404, url="https://example.com")
        assert isinstance(err, ContentNotFoundError)

    def test_500_returns_request_error(self):
        err = classify_http_error(500, url="https://example.com")
        assert isinstance(err, RequestError)
        assert err.status_code == 500

    def test_503_returns_request_error(self):
        err = classify_http_error(503, url="https://example.com")
        assert isinstance(err, RequestError)

    def test_url_propagated(self):
        err = classify_http_error(500, url="https://example.com/api")
        assert err.url == "https://example.com/api"

    def test_body_propagated_for_generic_error(self):
        err = classify_http_error(502, body="Bad Gateway")
        assert isinstance(err, RequestError)


@pytest.mark.unit
class TestFirecrawlError:
    """Tests for FirecrawlError firecrawl_error storage."""

    def test_is_scraping_error(self):
        err = FirecrawlError("firecrawl failed")
        assert isinstance(err, ScrapingError)

    def test_stores_firecrawl_error(self):
        original = ValueError("upstream error")
        err = FirecrawlError("failed", firecrawl_error=original)
        assert err.firecrawl_error is original

    def test_firecrawl_error_string_in_details(self):
        original = ValueError("upstream error")
        err = FirecrawlError("failed", firecrawl_error=original)
        assert "upstream error" in err.details["firecrawl_error"]

    def test_no_firecrawl_error_clean_details(self):
        err = FirecrawlError("failed")
        assert "firecrawl_error" not in err.details


@pytest.mark.unit
class TestScrapeSubclasses:
    """Tests for ScrapeConnectionError, ScrapeTimeoutError, ScrapeValidationError."""

    def test_scrape_connection_error_is_request_error(self):
        err = ScrapeConnectionError("connection refused", url="https://example.com")
        assert isinstance(err, RequestError)

    def test_scrape_timeout_error_is_request_error(self):
        err = ScrapeTimeoutError(url="https://example.com", timeout=10.0)
        assert isinstance(err, RequestError)

    def test_scrape_timeout_stores_timeout(self):
        err = ScrapeTimeoutError(url="https://example.com", timeout=30.5)
        assert err.timeout == 30.5

    def test_scrape_timeout_default_message(self):
        err = ScrapeTimeoutError()
        assert "timed out" in str(err)

    def test_scrape_validation_is_scraping_error(self):
        err = ScrapeValidationError("invalid input")
        assert isinstance(err, ScrapingError)

    def test_scrape_validation_stores_field(self):
        err = ScrapeValidationError("invalid", field="url", value="not-a-url")
        assert err.field == "url"
        assert err.value == "not-a-url"

    def test_scrape_validation_field_in_details(self):
        err = ScrapeValidationError("invalid", field="url", value="bad")
        assert err.details["field"] == "url"
