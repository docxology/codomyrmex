"""Data models for the free_apis submodule.

Defines structured representations of API entries sourced from the
public-apis project (https://github.com/public-apis/public-apis).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class APISource(Enum):
    """Source used to load the API registry."""

    JSON_API = "json_api"
    GITHUB_README = "github_readme"
    INLINE = "inline"


@dataclass
class APIEntry:
    """A single entry from the public-apis registry.

    Attributes:
        name: Short name of the API.
        description: Brief description of what the API provides.
        auth: Authentication method required ("", "apiKey", "OAuth", etc.).
        https: Whether the API endpoint uses HTTPS.
        cors: CORS support: "yes", "no", or "unknown".
        link: URL to the API documentation or homepage.
        category: Top-level category (e.g. "Animals", "Finance").
    """

    name: str
    description: str
    auth: str
    https: bool
    cors: str
    link: str
    category: str

    def is_no_auth(self) -> bool:
        """Return True when the API requires no authentication."""
        return self.auth.strip() == ""

    def to_dict(self) -> dict[str, Any]:
        """Return a fully serializable dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "auth": self.auth,
            "https": self.https,
            "cors": self.cors,
            "link": self.link,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], category: str = "") -> APIEntry:
        """Construct an APIEntry from a raw public-apis JSON dict.

        Args:
            data: Raw dict with keys "API", "Description", "Auth",
                  "HTTPS", "Cors", "Link", and optionally "Category".
            category: Category name (used when not present in data).

        Returns:
            Populated APIEntry instance.
        """
        return cls(
            name=data.get("API", ""),
            description=data.get("Description", ""),
            auth=data.get("Auth", ""),
            https=bool(data.get("HTTPS", False)),
            cors=data.get("Cors", "unknown"),
            link=data.get("Link", ""),
            category=data.get("Category", category),
        )


@dataclass
class APICategory:
    """Summary of a category in the free API registry.

    Attributes:
        name: Category name (e.g. "Finance").
        count: Number of API entries in this category.
    """

    name: str
    count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Return serializable dict."""
        return {"name": self.name, "count": self.count}


@dataclass
class APICallResult:
    """Result of a call made via FreeAPIClient.

    Attributes:
        url: The URL that was called.
        method: HTTP method used (e.g. "GET").
        status_code: HTTP response status code.
        headers: Response headers as a dict.
        body_text: Raw response body as a string.
    """

    url: str
    method: str
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return serializable dict."""
        return {
            "url": self.url,
            "method": self.method,
            "status_code": self.status_code,
            "headers": self.headers,
            "body_text": self.body_text,
        }


class APICallError(Exception):
    """Raised when FreeAPIClient cannot complete an HTTP call.

    Attributes:
        message: Human-readable error description.
        url: The URL that was targeted.
    """

    def __init__(self, message: str, url: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.url = url


__all__ = [
    "APICallError",
    "APICallResult",
    "APICategory",
    "APIEntry",
    "APISource",
]
