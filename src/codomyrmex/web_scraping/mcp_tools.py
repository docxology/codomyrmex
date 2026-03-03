"""MCP tools for web scraping.

This module provides tools for fetching web pages, extracting links,
and retrieving plain text from HTML documents.
"""

import html
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from codomyrmex.model_context_protocol.tool_decorator import mcp_tool


@mcp_tool(category="web_scraping", description="Fetch and parse a web page")
def scraping_fetch_page(url: str) -> dict:
    """Fetch a web page and return its HTML content and status.

    Args:
        url: The URL to fetch.

    Returns:
        Dictionary containing status, HTML content, and message if failed.
    """
    req = urllib.request.Request(
        url, headers={"User-Agent": "Codomyrmex/1.0 (Web Scraper)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8", errors="replace")
            return {"status": "success", "html": content, "url": response.geturl()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class _LinkExtractor(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    full_url = urllib.parse.urljoin(self.base_url, value)
                    if full_url not in self.links:
                        self.links.append(full_url)


@mcp_tool(category="web_scraping", description="Extract all links from a page")
def scraping_extract_links(url: str, base_url: str = "") -> dict:
    """Extract all hyperlinks from a web page.

    Args:
        url: The URL to fetch and extract links from.
        base_url: Optional base URL for resolving relative links. If empty, uses the fetched URL.

    Returns:
        Dictionary containing status and a list of extracted links.
    """
    fetch_result = scraping_fetch_page(url)
    if fetch_result["status"] != "success":
        return fetch_result

    effective_base = base_url if base_url else fetch_result.get("url", url)
    html_content = fetch_result["html"]

    parser = _LinkExtractor(effective_base)
    try:
        parser.feed(html_content)
        return {"status": "success", "links": parser.links}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.hide_content = False
        self.hidden_tags = {"script", "style", "head", "title", "meta"}

    def handle_starttag(self, tag, attrs):
        if tag in self.hidden_tags:
            self.hide_content = True
        elif tag in {"br", "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"}:
            self.text_chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in self.hidden_tags:
            self.hide_content = False
        elif tag in {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li"}:
            self.text_chunks.append("\n")

    def handle_data(self, data):
        if not self.hide_content:
            text = data.strip()
            if text:
                self.text_chunks.append(text + " ")


@mcp_tool(category="web_scraping", description="Extract clean text content from a URL")
def scraping_get_text(url: str) -> dict:
    """Extract clean text content from a URL, stripping HTML tags.

    Args:
        url: The URL to fetch and extract text from.

    Returns:
        Dictionary containing status and the clean text content.
    """
    fetch_result = scraping_fetch_page(url)
    if fetch_result["status"] != "success":
        return fetch_result

    html_content = fetch_result["html"]

    parser = _TextExtractor()
    try:
        parser.feed(html_content)
        raw_text = "".join(parser.text_chunks)
        # Clean up multiple newlines and spaces
        clean_text = re.sub(r"\n+", "\n", raw_text)
        clean_text = re.sub(r"[ \t]+", " ", clean_text)
        clean_text = html.unescape(clean_text).strip()

        return {"status": "success", "text": clean_text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
