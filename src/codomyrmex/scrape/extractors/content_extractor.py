"""Content extraction and transformation utilities.

Extracts structured text, metadata, and links from raw HTML content
without requiring network access, enabling offline content processing.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin


@dataclass
class ExtractedContent:
    """Structured content extracted from a page.

    Attributes:
        url: Source URL of the content.
        title: Extracted page title.
        headings: List of (level, text) heading tuples.
        paragraphs: List of paragraph text blocks.
        links: List of (url, anchor_text) tuples.
        images: List of (src, alt_text) tuples.
        meta: Extracted metadata (description, keywords, etc.).
        word_count: Total word count of text content.
        content_hash: SHA-256 hash of the full text.
    """

    url: str = ""
    title: str = ""
    headings: list[tuple[int, str]] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)
    images: list[tuple[str, str]] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)
    word_count: int = 0
    content_hash: str = ""


class ContentExtractor:
    """Extract structured content from raw HTML strings.

    Uses regex-based extraction (no external HTML parser dependency)
    for lightweight content processing.

    Example::

        extractor = ContentExtractor(base_url="https://example.com")
        result = extractor.extract("<html><title>Hi</title>...</html>")
        print(result.title, result.word_count)
    """

    def __init__(self, base_url: str = "") -> None:
        self._base_url = base_url

    def extract(self, html: str, url: str = "") -> ExtractedContent:
        """Extract structured content from an HTML string.

        Args:
            html: Raw HTML content.
            url: URL of the page (for resolving relative links).

        Returns:
            ExtractedContent with all extracted fields.
        """
        effective_url = url or self._base_url
        result = ExtractedContent(url=effective_url)

        result.title = self._extract_title(html)
        result.headings = self._extract_headings(html)
        result.paragraphs = self._extract_paragraphs(html)
        result.links = self._extract_links(html, effective_url)
        result.images = self._extract_images(html, effective_url)
        result.meta = self._extract_meta(html)

        full_text = " ".join(result.paragraphs)
        result.word_count = len(full_text.split()) if full_text.strip() else 0
        result.content_hash = hashlib.sha256(full_text.encode()).hexdigest()

        return result

    def _extract_title(self, html: str) -> str:
        """Extract the <title> content."""
        match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        return self._strip_tags(match.group(1)).strip() if match else ""

    def _extract_headings(self, html: str) -> list[tuple[int, str]]:
        """Extract all heading elements (h1-h6)."""
        headings = []
        for match in re.finditer(r"<h([1-6])[^>]*>(.*?)</h\1>", html, re.IGNORECASE | re.DOTALL):
            level = int(match.group(1))
            text = self._strip_tags(match.group(2)).strip()
            if text:
                headings.append((level, text))
        return headings

    def _extract_paragraphs(self, html: str) -> list[str]:
        """Extract text from <p> elements."""
        paragraphs = []
        for match in re.finditer(r"<p[^>]*>(.*?)</p>", html, re.IGNORECASE | re.DOTALL):
            text = self._strip_tags(match.group(1)).strip()
            if text:
                paragraphs.append(text)
        return paragraphs

    def _extract_links(self, html: str, base_url: str) -> list[tuple[str, str]]:
        """Extract links as (url, anchor_text) tuples."""
        links = []
        for match in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL):
            href = match.group(1)
            text = self._strip_tags(match.group(2)).strip()
            if base_url:
                href = urljoin(base_url, href)
            links.append((href, text))
        return links

    def _extract_images(self, html: str, base_url: str) -> list[tuple[str, str]]:
        """Extract images as (src, alt) tuples."""
        images = []
        for match in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE):
            src = match.group(1)
            alt_match = re.search(r'alt=["\']([^"\']*)["\']', match.group(0), re.IGNORECASE)
            alt = alt_match.group(1) if alt_match else ""
            if base_url:
                src = urljoin(base_url, src)
            images.append((src, alt))
        return images

    def _extract_meta(self, html: str) -> dict[str, str]:
        """Extract <meta> tag name/content pairs."""
        meta = {}
        for match in re.finditer(
            r'<meta[^>]+name=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\']',
            html, re.IGNORECASE,
        ):
            meta[match.group(1).lower()] = match.group(2)
        return meta

    def _strip_tags(self, html: str) -> str:
        """Remove all HTML tags from a string."""
        return re.sub(r"<[^>]+>", "", html)


def text_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two text strings.

    Uses word-level tokenization for comparison.

    Args:
        a: First text.
        b: Second text.

    Returns:
        Similarity score in [0, 1].
    """
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())

    if not words_a and not words_b:
        return 1.0
    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)
