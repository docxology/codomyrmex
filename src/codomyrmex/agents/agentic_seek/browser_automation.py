"""Browser automation helpers for agenticSeek.

Mirrors the prompt-building and link/form extraction utilities from
``sources.agents.browser_agent.BrowserAgent`` without depending on
Selenium or SearxNG at import time.

Reference: https://github.com/Fosowl/agenticSeek/blob/main/sources/agents/browser_agent.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgenticSeekBrowserConfig:
    """Configuration for agenticSeek browser automation.

    Attributes:
        headless: Run the browser without a visible window.
        stealth_mode: Enable anti-detection measures.
        searxng_url: Base URL of the SearxNG meta-search instance.
    """

    headless: bool = True
    stealth_mode: bool = True
    searxng_url: str = "http://searxng:8080"


# ---------------------------------------------------------------------------
# Link extraction (mirrors BrowserAgent.extract_links)
# ---------------------------------------------------------------------------

_LINK_PATTERN = re.compile(r"(https?://\S+|www\.\S+)")
_TRAILING_PUNCT = set(".,!?;:)")


def extract_links(text: str) -> list[str]:
    """Extract HTTP/HTTPS and ``www.`` URLs from *text*.

    Strips common trailing punctuation that is not part of the URL.

    Args:
        text: Arbitrary text that may contain URLs.

    Returns:
        De-duplicated, order-preserved list of cleaned URLs.
    """
    matches = _LINK_PATTERN.findall(text)
    cleaned = clean_links(matches)
    # Preserve order, remove duplicates
    seen: set[str] = set()
    result: list[str] = []
    for link in cleaned:
        if link not in seen:
            seen.add(link)
            result.append(link)
    return result


def clean_links(links: list[str]) -> list[str]:
    """Remove trailing punctuation from a list of URLs.

    Args:
        links: Raw URL strings.

    Returns:
        Cleaned URL strings.
    """
    cleaned: list[str] = []
    for link in links:
        link = link.strip()
        if not link:
            continue
        while link and link[-1] in _TRAILING_PUNCT:
            link = link[:-1]
        if link:
            cleaned.append(link)
    return cleaned


# ---------------------------------------------------------------------------
# Form field extraction (mirrors BrowserAgent.extract_form)
# ---------------------------------------------------------------------------

_FORM_PATTERN = re.compile(r"\[(\w+)\]\(([^)]+)\)")


def extract_form_fields(text: str) -> list[dict[str, str]]:
    """Extract form field instructions from LLM text.

    The upstream format is ``[input_name](value)``.

    Args:
        text: LLM response that may contain form instructions.

    Returns:
        List of ``{"name": …, "value": …}`` dicts.
    """
    results: list[dict[str, str]] = []
    for match in _FORM_PATTERN.finditer(text):
        results.append({"name": match.group(1), "value": match.group(2)})
    return results


# ---------------------------------------------------------------------------
# Prompt builders (mirrors BrowserAgent.make_*_prompt)
# ---------------------------------------------------------------------------

def build_search_prompt(
    user_query: str,
    search_results: list[dict[str, str]],
) -> str:
    """Build a prompt asking the LLM to select a search result.

    Args:
        user_query: The original user request.
        search_results: List of dicts with ``"title"``, ``"url"``,
            and optionally ``"snippet"`` keys.

    Returns:
        Formatted prompt string.
    """
    formatted = _format_search_results(search_results)
    return (
        f"Based on the search result:\n"
        f"{formatted}\n"
        f"Your goal is to find accurate and complete information "
        f"to satisfy the user's request.\n"
        f"User request: {user_query}\n"
        f'To proceed, choose a relevant link from the search results. '
        f'Announce your choice by saying: "I will navigate to <link>"\n'
        f"Do not explain your choice."
    )


def build_navigation_prompt(
    page_content: str,
    current_url: str = "",
    remaining_links: list[str] | None = None,
    form_inputs: list[str] | None = None,
    notes: list[str] | None = None,
    user_prompt: str = "",
) -> str:
    """Build a navigation prompt for the browser agent.

    Args:
        page_content: Visible text of the current web page.
        current_url: URL of the current page.
        remaining_links: Links not yet visited.
        form_inputs: Form input descriptions on the page.
        notes: Accumulated agent notes.
        user_prompt: Original user request.

    Returns:
        Formatted prompt string.
    """
    links_text = (
        "\n".join(f"[{i}] {link}" for i, link in enumerate(remaining_links))
        if remaining_links
        else "No links remaining, do a new search."
    )
    forms_text = "\n".join(form_inputs) if form_inputs else "None"
    notes_text = "\n".join(notes) if notes else "None"
    today = get_today_date()

    return (
        f"You are navigating the web.\n\n"
        f"**Current Context**\n\n"
        f"Date: {today}\n"
        f"Webpage ({current_url}) content:\n{page_content}\n\n"
        f"Allowed Navigation Links:\n{links_text}\n\n"
        f"Input forms:\n{forms_text}\n\n"
        f"Notes:\n{notes_text}\n\n"
        f"User request: {user_prompt}"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_today_date() -> str:
    """Return today's date as a human-readable string."""
    return date.today().strftime("%B %d, %Y")


def _format_search_results(results: list[dict[str, str]]) -> str:
    """Format search results into a numbered list."""
    lines: list[str] = []
    for i, item in enumerate(results, 1):
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        snippet = item.get("snippet", "")
        lines.append(f"[{i}] {title}\n    URL: {url}")
        if snippet:
            lines.append(f"    {snippet}")
    return "\n".join(lines)
