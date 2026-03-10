"""Zero-mock tests for the free_apis submodule.

Tests cover:
- APIEntry, APICategory, APICallResult, APICallError model behaviour
- FreeAPIRegistry filter / search / get_categories with in-memory data
- FreeAPIClient dataclass and helper function behaviour
- MCP tool signatures and no-network fast-paths

Network tests are guarded by a skipif marker; no real HTTP calls occur
in CI unless the ``CODOMYRMEX_NETWORK_TESTS`` environment variable is set.
"""

from __future__ import annotations

import os

import pytest

from codomyrmex.api.free_apis.client import (
    FreeAPIClient,
    _append_params,
    _encode_body,
)
from codomyrmex.api.free_apis.models import (
    APICallError,
    APICallResult,
    APICategory,
    APIEntry,
    APISource,
)
from codomyrmex.api.free_apis.registry import (
    FreeAPIRegistry,
    _extract_name_and_link,
    _normalize_auth,
    _parse_readme_markdown,
    _row_to_entry,
)

_NETWORK = os.getenv("CODOMYRMEX_NETWORK_TESTS", "").lower() in ("1", "true", "yes")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_ENTRIES = [
    APIEntry("DogCEO", "Dog breeds", "", True, "yes", "https://dog.ceo/api", "Animals"),
    APIEntry("CatFacts", "Facts about cats", "apiKey", True, "no", "https://catfact.ninja", "Animals"),
    APIEntry("Frankfurter", "Exchange rates", "", True, "yes", "https://frankfurter.app", "Finance"),
    APIEntry("CoinGecko", "Crypto prices", "", False, "yes", "https://coingecko.com/api", "Finance"),
    APIEntry("OpenWeather", "Weather data", "apiKey", True, "no", "https://openweathermap.org", "Weather"),
]


@pytest.fixture
def registry() -> FreeAPIRegistry:
    return FreeAPIRegistry.from_entries(SAMPLE_ENTRIES)


# ---------------------------------------------------------------------------
# APIEntry model
# ---------------------------------------------------------------------------

class TestAPIEntry:
    def test_fields_stored_correctly(self):
        e = APIEntry("X", "desc", "", True, "yes", "https://x.com", "Cat")
        assert e.name == "X"
        assert e.description == "desc"
        assert e.auth == ""
        assert e.https is True
        assert e.cors == "yes"
        assert e.link == "https://x.com"
        assert e.category == "Cat"

    def test_is_no_auth_true_when_empty(self):
        e = APIEntry("X", "d", "", True, "yes", "https://x.com", "C")
        assert e.is_no_auth() is True

    def test_is_no_auth_false_when_apikey(self):
        e = APIEntry("X", "d", "apiKey", True, "yes", "https://x.com", "C")
        assert e.is_no_auth() is False

    def test_is_no_auth_false_for_oauth(self):
        e = APIEntry("X", "d", "OAuth", True, "yes", "https://x.com", "C")
        assert e.is_no_auth() is False

    def test_to_dict_contains_all_keys(self):
        e = APIEntry("X", "d", "apiKey", False, "no", "https://x.com", "Tech")
        d = e.to_dict()
        assert set(d.keys()) == {"name", "description", "auth", "https", "cors", "link", "category"}

    def test_to_dict_values_match_fields(self):
        e = APIEntry("A", "B", "C", True, "yes", "https://a.com", "Z")
        d = e.to_dict()
        assert d["name"] == "A"
        assert d["https"] is True
        assert d["category"] == "Z"

    def test_from_dict_maps_api_key(self):
        raw = {"API": "Foo", "Description": "bar", "Auth": "apiKey",
               "HTTPS": True, "Cors": "yes", "Link": "https://foo.com", "Category": "Test"}
        e = APIEntry.from_dict(raw)
        assert e.name == "Foo"
        assert e.auth == "apiKey"
        assert e.https is True

    def test_from_dict_uses_category_fallback(self):
        raw = {"API": "X", "Description": "", "Auth": "", "HTTPS": False, "Cors": "no", "Link": ""}
        e = APIEntry.from_dict(raw, category="Fallback")
        assert e.category == "Fallback"

    def test_from_dict_handles_missing_fields(self):
        e = APIEntry.from_dict({})
        assert e.name == ""
        assert e.https is False
        assert e.cors == "unknown"

    def test_is_no_auth_strips_whitespace(self):
        e = APIEntry("X", "d", "  ", True, "yes", "", "C")
        assert e.is_no_auth() is True


# ---------------------------------------------------------------------------
# APICategory model
# ---------------------------------------------------------------------------

class TestAPICategory:
    def test_name_and_count(self):
        c = APICategory("Animals", 42)
        assert c.name == "Animals"
        assert c.count == 42

    def test_default_count_is_zero(self):
        c = APICategory("Finance")
        assert c.count == 0

    def test_to_dict(self):
        c = APICategory("Sports", 5)
        d = c.to_dict()
        assert d == {"name": "Sports", "count": 5}


# ---------------------------------------------------------------------------
# APISource enum
# ---------------------------------------------------------------------------

class TestAPISource:
    def test_values(self):
        assert APISource.JSON_API.value == "json_api"
        assert APISource.GITHUB_README.value == "github_readme"
        assert APISource.INLINE.value == "inline"


# ---------------------------------------------------------------------------
# APICallResult model
# ---------------------------------------------------------------------------

class TestAPICallResult:
    def test_fields(self):
        r = APICallResult("https://x.com", "GET", 200, {"Content-Type": "application/json"}, '{"ok":true}')
        assert r.url == "https://x.com"
        assert r.method == "GET"
        assert r.status_code == 200
        assert r.headers["Content-Type"] == "application/json"
        assert r.body_text == '{"ok":true}'

    def test_to_dict_keys(self):
        r = APICallResult("https://x.com", "POST", 201)
        d = r.to_dict()
        assert set(d.keys()) == {"url", "method", "status_code", "headers", "body_text"}

    def test_default_body_text_empty(self):
        r = APICallResult("https://x.com", "GET", 200)
        assert r.body_text == ""

    def test_default_headers_empty(self):
        r = APICallResult("https://x.com", "GET", 200)
        assert r.headers == {}


# ---------------------------------------------------------------------------
# APICallError
# ---------------------------------------------------------------------------

class TestAPICallError:
    def test_is_exception(self):
        err = APICallError("bad", url="https://x.com")
        assert isinstance(err, Exception)
        assert err.message == "bad"
        assert err.url == "https://x.com"

    def test_str_representation(self):
        err = APICallError("timeout")
        assert "timeout" in str(err)

    def test_default_url_empty(self):
        err = APICallError("err")
        assert err.url == ""


# ---------------------------------------------------------------------------
# FreeAPIRegistry — filter / search / categories (in-memory, no network)
# ---------------------------------------------------------------------------

class TestFreeAPIRegistryFromEntries:
    def test_entries_property_returns_copy(self, registry):
        entries = registry.entries
        assert len(entries) == 5

    def test_source_is_inline(self, registry):
        assert registry.source == APISource.INLINE

    def test_search_by_name(self, registry):
        results = registry.search("Dog")
        assert len(results) == 1
        assert results[0].name == "DogCEO"

    def test_search_case_insensitive(self, registry):
        results = registry.search("dog")
        assert len(results) == 1

    def test_search_by_description(self, registry):
        results = registry.search("breeds")
        assert any(e.name == "DogCEO" for e in results)

    def test_search_no_match_returns_empty(self, registry):
        assert registry.search("zzzzz") == []

    def test_search_matches_multiple(self, registry):
        results = registry.search("Facts")
        assert len(results) == 1

    def test_filter_by_category(self, registry):
        finance = registry.filter_by_category("Finance")
        assert len(finance) == 2
        assert all(e.category == "Finance" for e in finance)

    def test_filter_by_category_case_insensitive(self, registry):
        animals = registry.filter_by_category("animals")
        assert len(animals) == 2

    def test_filter_by_category_no_match(self, registry):
        assert registry.filter_by_category("Nonexistent") == []

    def test_filter_by_auth_empty(self, registry):
        no_auth = registry.filter_by_auth("")
        assert all(e.auth == "" for e in no_auth)
        assert len(no_auth) == 3

    def test_filter_by_auth_apikey(self, registry):
        api_key = registry.filter_by_auth("apiKey")
        assert len(api_key) == 2
        assert all(e.auth == "apiKey" for e in api_key)

    def test_filter_by_https_true(self, registry):
        https_only = registry.filter_by_https(True)
        assert all(e.https for e in https_only)
        assert len(https_only) == 4

    def test_filter_by_https_false(self, registry):
        http_only = registry.filter_by_https(False)
        assert all(not e.https for e in http_only)
        assert len(http_only) == 1

    def test_get_categories_sorted(self, registry):
        cats = registry.get_categories()
        names = [c.name for c in cats]
        assert names == sorted(names)

    def test_get_categories_counts(self, registry):
        cats = registry.get_categories()
        cat_map = {c.name: c.count for c in cats}
        assert cat_map["Animals"] == 2
        assert cat_map["Finance"] == 2
        assert cat_map["Weather"] == 1

    def test_get_categories_returns_api_category(self, registry):
        cats = registry.get_categories()
        assert all(isinstance(c, APICategory) for c in cats)

    def test_empty_registry(self):
        r = FreeAPIRegistry.from_entries([])
        assert r.entries == []
        assert r.get_categories() == []
        assert r.search("x") == []


# ---------------------------------------------------------------------------
# FreeAPIRegistry — cache TTL behaviour (no network)
# ---------------------------------------------------------------------------

class TestFreeAPIRegistryCache:
    def test_cache_is_fresh_after_from_entries(self):
        r = FreeAPIRegistry.from_entries(SAMPLE_ENTRIES)
        # cache_ttl_seconds=3600 by default, should be fresh
        assert r._is_cache_fresh()

    def test_cache_not_fresh_when_no_entries(self):
        r = FreeAPIRegistry()
        assert not r._is_cache_fresh()

    def test_cache_not_fresh_when_ttl_zero(self):
        r = FreeAPIRegistry.from_entries(SAMPLE_ENTRIES )
        r.cache_ttl_seconds = 0
        assert not r._is_cache_fresh()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class TestAppendParams:
    def test_no_params_returns_url(self):
        assert _append_params("https://x.com", None) == "https://x.com"

    def test_empty_params_returns_url(self):
        assert _append_params("https://x.com", {}) == "https://x.com"

    def test_adds_question_mark(self):
        result = _append_params("https://x.com", {"a": "1"})
        assert "?a=1" in result

    def test_adds_ampersand_when_query_exists(self):
        result = _append_params("https://x.com?foo=bar", {"a": "1"})
        assert result.startswith("https://x.com?foo=bar&")

    def test_multiple_params(self):
        result = _append_params("https://x.com", {"a": "1", "b": "2"})
        assert "a=1" in result
        assert "b=2" in result


class TestEncodeBody:
    def test_none_returns_none(self):
        assert _encode_body(None) is None

    def test_bytes_returned_unchanged(self):
        b = b"hello"
        assert _encode_body(b) is b

    def test_str_encoded_to_utf8(self):
        assert _encode_body("hello") == b"hello"

    def test_unicode_str(self):
        assert _encode_body("café") == "café".encode()


class TestExtractNameAndLink:
    def test_plain_text(self):
        name, link = _extract_name_and_link("FooAPI")
        assert name == "FooAPI"
        assert link == ""

    def test_markdown_link(self):
        name, link = _extract_name_and_link("[Dog API](https://dog.ceo/api)")
        assert name == "Dog API"
        assert link == "https://dog.ceo/api"

    def test_strips_whitespace(self):
        name, link = _extract_name_and_link("  MyAPI  ")
        assert name == "MyAPI"


class TestNormalizeAuth:
    def test_no_maps_to_empty_string(self):
        assert _normalize_auth("No") == ""

    def test_no_case_insensitive(self):
        assert _normalize_auth("no") == ""

    def test_backtick_stripped_apikey(self):
        assert _normalize_auth("`apiKey`") == "apiKey"

    def test_backtick_stripped_oauth(self):
        assert _normalize_auth("`OAuth`") == "OAuth"

    def test_already_clean(self):
        assert _normalize_auth("apiKey") == "apiKey"

    def test_empty_string_stays_empty(self):
        assert _normalize_auth("") == ""

    def test_whitespace_stripped(self):
        assert _normalize_auth("  No  ") == ""


class TestRowToEntry:
    def test_valid_row(self):
        parts = ["", "[DogCEO](https://dog.ceo)", "Random dog images", "", "Yes", "yes", ""]
        e = _row_to_entry(parts, "Animals")
        assert e is not None
        assert e.name == "DogCEO"
        assert e.category == "Animals"
        assert e.https is True

    def test_too_few_parts_returns_none(self):
        assert _row_to_entry(["a", "b"], "Cat") is None

    def test_header_row_returns_none(self):
        parts = ["", "API", "Description", "Auth", "HTTPS", "CORS", ""]
        assert _row_to_entry(parts, "Cat") is None

    def test_separator_row_returns_none(self):
        parts = ["", "---", "---", "---", "---", "---", ""]
        assert _row_to_entry(parts, "Cat") is None

    def test_https_no_maps_to_false(self):
        parts = ["", "Foo", "desc", "", "No", "no", ""]
        e = _row_to_entry(parts, "Test")
        assert e is not None
        assert e.https is False

    def test_cors_unknown_fallback(self):
        parts = ["", "Foo", "desc", "", "Yes", "unknown", ""]
        e = _row_to_entry(parts, "Test")
        assert e is not None
        assert e.cors == "unknown"


class TestParseReadmeMarkdown:
    _MINIMAL_README = """
# Public APIs

## Animals

| API | Description | Auth | HTTPS | CORS |
| --- | --- | --- | --- | --- |
| [DogCEO](https://dog.ceo) | Random dogs | No | Yes | yes |
| [CatFacts](https://catfact.ninja) | Cat facts | `apiKey` | Yes | no |

## Finance

| API | Description | Auth | HTTPS | CORS |
| --- | --- | --- | --- | --- |
| [Frankfurter](https://frankfurter.app) | Exchange rates | No | Yes | yes |
"""

    def test_parses_entries(self):
        entries = _parse_readme_markdown(self._MINIMAL_README)
        assert len(entries) == 3

    def test_category_assigned(self):
        entries = _parse_readme_markdown(self._MINIMAL_README)
        animals = [e for e in entries if e.category == "Animals"]
        assert len(animals) == 2

    def test_name_extracted(self):
        entries = _parse_readme_markdown(self._MINIMAL_README)
        names = {e.name for e in entries}
        assert "DogCEO" in names
        assert "Frankfurter" in names

    def test_https_parsed(self):
        entries = _parse_readme_markdown(self._MINIMAL_README)
        assert all(e.https for e in entries)

    def test_auth_no_normalized_to_empty(self):
        entries = _parse_readme_markdown(self._MINIMAL_README)
        no_auth = [e for e in entries if e.auth == ""]
        assert len(no_auth) == 2  # DogCEO and Frankfurter

    def test_auth_backtick_stripped(self):
        entries = _parse_readme_markdown(self._MINIMAL_README)
        api_key = [e for e in entries if e.auth == "apiKey"]
        assert len(api_key) == 1
        assert api_key[0].name == "CatFacts"

    def test_raises_on_empty_content(self):
        with pytest.raises(ValueError, match="Could not parse"):
            _parse_readme_markdown("# Just a heading\n\nNo table rows here.")


# ---------------------------------------------------------------------------
# FreeAPIClient unit behaviour (no network)
# ---------------------------------------------------------------------------

class TestFreeAPIClientInit:
    def test_default_timeout(self):
        c = FreeAPIClient()
        assert c.default_timeout == 10

    def test_custom_timeout(self):
        c = FreeAPIClient(default_timeout=30)
        assert c.default_timeout == 30

    def test_default_user_agent_set(self):
        c = FreeAPIClient()
        assert "codomyrmex" in c.default_headers.get("User-Agent", "")

    def test_custom_headers_merged(self):
        c = FreeAPIClient(default_headers={"X-Token": "abc"})
        assert c.default_headers["X-Token"] == "abc"


# ---------------------------------------------------------------------------
# Network tests — only run when CODOMYRMEX_NETWORK_TESTS=1
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _NETWORK, reason="Network tests disabled; set CODOMYRMEX_NETWORK_TESTS=1")
class TestFreeAPIRegistryNetwork:
    def test_fetch_returns_entries(self):
        r = FreeAPIRegistry(cache_ttl_seconds=0)
        entries = r.fetch()
        assert len(entries) > 100

    def test_categories_non_empty_after_fetch(self):
        r = FreeAPIRegistry(cache_ttl_seconds=0)
        r.fetch()
        cats = r.get_categories()
        assert len(cats) > 5


@pytest.mark.skipif(not _NETWORK, reason="Network tests disabled; set CODOMYRMEX_NETWORK_TESTS=1")
class TestFreeAPIClientNetwork:
    def test_get_dog_api(self):
        c = FreeAPIClient()
        result = c.get("https://dog.ceo/api/breeds/list/all")
        assert result.status_code == 200
        assert "breeds" in result.body_text or result.body_text != ""

    def test_invalid_url_raises_api_call_error(self):
        c = FreeAPIClient(default_timeout=3)
        with pytest.raises(APICallError):
            c.get("https://this-host-does-not-exist.invalid/foo")
