"""Free API registry — fetch, cache, filter, and search public API entries.

Data is sourced from the public-apis project:
  JSON API:      https://api.publicapis.org/entries
  GitHub README: https://raw.githubusercontent.com/public-apis/public-apis/master/README.md

The registry caches fetched entries in memory and only re-fetches after
``cache_ttl_seconds`` has elapsed. For offline/test use, build the registry
from a list of ``APIEntry`` objects via :meth:`FreeAPIRegistry.from_entries`.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any

from .models import APICategory, APIEntry, APISource

_JSON_API_URL = "https://api.publicapis.org/entries"
_GITHUB_README_URL = (
    "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
)
_DEFAULT_TIMEOUT = 15


class FreeAPIRegistry:
    """Registry of free public APIs sourced from public-apis.

    Args:
        cache_ttl_seconds: How long (seconds) to keep fetched data before
            re-fetching. set to 0 to always re-fetch. Default: 3600.
        timeout: HTTP request timeout in seconds. Default: 15.
    """

    def __init__(
        self,
        cache_ttl_seconds: int = 3600,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        self._entries: list[APIEntry] = []
        self._fetched_at: float = 0.0
        self._source: APISource | None = None
        self.cache_ttl_seconds = cache_ttl_seconds
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_entries(cls, entries: list[APIEntry]) -> FreeAPIRegistry:
        """Create a registry pre-loaded from a list (no network required).

        Args:
            entries: list of :class:`APIEntry` objects.

        Returns:
            FreeAPIRegistry populated with the given entries.
        """
        registry = cls()
        registry._entries = list(entries)
        registry._fetched_at = time.monotonic()
        registry._source = APISource.INLINE
        return registry

    # ------------------------------------------------------------------
    # Fetching
    # ------------------------------------------------------------------

    def fetch(self, force: bool = False) -> list[APIEntry]:
        """Ensure entries are loaded, using cache when still fresh.

        Tries the JSON API first; falls back to parsing the GitHub README.

        Args:
            force: If True, bypass the cache and always re-fetch.

        Returns:
            list of all loaded :class:`APIEntry` objects.

        Raises:
            RuntimeError: If both fetch strategies fail.
        """
        if not force and self._is_cache_fresh():
            return self._entries

        try:
            entries = self._fetch_from_json_api()
            self._entries = entries
            self._source = APISource.JSON_API
        except Exception:
            try:
                entries = self._fetch_from_github_readme()
                self._entries = entries
                self._source = APISource.GITHUB_README
            except Exception as exc:
                raise RuntimeError(
                    "Failed to fetch API entries from both JSON API and GitHub README"
                ) from exc

        self._fetched_at = time.monotonic()
        return self._entries

    def _is_cache_fresh(self) -> bool:
        if not self._entries:
            return False
        if self.cache_ttl_seconds == 0:
            return False
        age = time.monotonic() - self._fetched_at
        return age < self.cache_ttl_seconds

    def _fetch_from_json_api(self) -> list[APIEntry]:
        """Fetch entries from https://api.publicapis.org/entries.

        Returns:
            list of APIEntry objects parsed from the JSON response.

        Raises:
            urllib.error.URLError: On network failure.
            ValueError: If response JSON is not in expected shape.
        """
        req = urllib.request.Request(
            _JSON_API_URL,
            headers={
                "Accept": "application/json",
                "User-Agent": "codomyrmex/free_apis",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            raw = response.read().decode("utf-8")

        data: dict[str, Any] = json.loads(raw)
        raw_entries = data.get("entries")
        if not isinstance(raw_entries, list):
            raise ValueError(
                "Unexpected JSON shape: 'entries' key missing or not a list"
            )

        return [APIEntry.from_dict(e) for e in raw_entries]

    def _fetch_from_github_readme(self) -> list[APIEntry]:
        """Fetch and parse the public-apis README markdown table.

        The README contains sections like:

            ## Category Name
            | API | Description | Auth | HTTPS | CORS |
            |-----|-------------|------|-------|------|
            | Name | Desc | apiKey | Yes | Yes |

        Returns:
            list of APIEntry objects parsed from the README.

        Raises:
            urllib.error.URLError: On network failure.
            ValueError: If no entries could be parsed.
        """
        req = urllib.request.Request(
            _GITHUB_README_URL,
            headers={"User-Agent": "codomyrmex/free_apis"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            content = response.read().decode("utf-8")

        return _parse_readme_markdown(content)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def search(self, query: str) -> list[APIEntry]:
        """Search entries by name and description (case-insensitive substring).

        Args:
            query: Search string to match against name and description.

        Returns:
            list of matching :class:`APIEntry` objects.
        """
        q = query.lower()
        return [
            e
            for e in self._entries
            if q in e.name.lower() or q in e.description.lower()
        ]

    def filter_by_category(self, category: str) -> list[APIEntry]:
        """Return all entries belonging to a category.

        Args:
            category: Category name (case-insensitive).

        Returns:
            Matching entries.
        """
        cat = category.lower()
        return [e for e in self._entries if e.category.lower() == cat]

    def filter_by_auth(self, auth: str) -> list[APIEntry]:
        """Return entries matching an auth requirement.

        Args:
            auth: Auth type string to match exactly, e.g. "apiKey", "OAuth",
                  or "" for no-auth APIs.

        Returns:
            Matching entries.
        """
        return [e for e in self._entries if e.auth == auth]

    def filter_by_https(self, https_only: bool = True) -> list[APIEntry]:
        """Filter entries by HTTPS support.

        Args:
            https_only: If True, return only HTTPS entries; if False, only HTTP.

        Returns:
            Matching entries.
        """
        return [e for e in self._entries if e.https == https_only]

    def get_categories(self) -> list[APICategory]:
        """Return a sorted list of unique categories with entry counts.

        Returns:
            Sorted list of :class:`APICategory` objects.
        """
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.category] = counts.get(entry.category, 0) + 1
        return [APICategory(name=k, count=v) for k, v in sorted(counts.items())]

    @property
    def entries(self) -> list[APIEntry]:
        """All currently loaded entries (may be empty before :meth:`fetch`)."""
        return list(self._entries)

    @property
    def source(self) -> APISource | None:
        """The source used for the most recent successful fetch."""
        return self._source


# ---------------------------------------------------------------------------
# Internal README parser
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(r"^#{1,3}\s+(.+)$")
_TABLE_ROW_RE = re.compile(
    r"^\|\s*\[?([^\]|]+)\]?\(?[^)]*\)?\s*\|"
    r"\s*([^|]+)\|"
    r"\s*([^|]*)\|"
    r"\s*(yes|no|true|false)\s*\|"
    r"\s*(yes|no|unknown)\s*\|",
    re.IGNORECASE,
)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _normalize_auth(auth_raw: str) -> str:
    """Normalise an auth column value from the README to a canonical form.

    The public-apis README wraps auth types in backticks (e.g. ``apiKey``)
    and uses the literal string ``No`` for no-auth APIs.  This function
    strips backticks and converts ``"No"`` → ``""`` so callers can use
    ``filter_by_auth("")`` uniformly regardless of data source.
    """
    stripped = auth_raw.strip().strip("`")
    return "" if stripped.lower() == "no" else stripped


def _extract_name_and_link(name_raw: str) -> tuple[str, str]:
    """Extract plain name and URL from a markdown link or plain text."""
    m = _LINK_RE.search(name_raw)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return name_raw.strip(), ""


def _row_to_entry(parts: list[str], category: str) -> APIEntry | None:
    """Convert a split table row into an APIEntry, or None if invalid."""
    if len(parts) < 6:
        return None
    name_raw, desc, auth, https_raw, cors = (
        parts[1],
        parts[2],
        parts[3],
        parts[4],
        parts[5],
    )
    if name_raw.lower() in ("api", "name") or "---" in name_raw:
        return None
    name, link = _extract_name_and_link(name_raw)
    if not name:
        return None
    https_bool = https_raw.strip().lower() in ("yes", "true")
    cors_lower = cors.strip().lower()
    cors_val = cors_lower if cors_lower in ("yes", "no") else "unknown"
    return APIEntry(
        name=name,
        description=desc.strip(),
        auth=_normalize_auth(auth),
        https=https_bool,
        cors=cors_val,
        link=link,
        category=category,
    )


def _parse_readme_markdown(content: str) -> list[APIEntry]:
    """Parse API entries from the public-apis README markdown.

    Args:
        content: Full text content of the README.md file.

    Returns:
        list of parsed :class:`APIEntry` objects.

    Raises:
        ValueError: If no entries at all could be parsed.
    """
    entries: list[APIEntry] = []
    current_category = ""
    _skip_headings = {"index", "table of contents", "contents"}

    for line in content.splitlines():
        line = line.strip()
        m = _HEADER_RE.match(line)
        if m:
            heading = m.group(1).strip()
            if heading.lower() not in _skip_headings:
                current_category = heading
            continue
        if not line.startswith("|") or "---" in line[:10]:
            continue
        parts = [p.strip() for p in line.split("|")]
        entry = _row_to_entry(parts, current_category)
        if entry:
            entries.append(entry)

    if not entries:
        raise ValueError("Could not parse any API entries from README markdown")
    return entries


__all__ = [
    "FreeAPIRegistry",
]
