from __future__ import annotations

from codomyrmex.manuscript.bibliography import (
    _google_books_feed_title,
    _isbn_search_title,
)


def test_isbn_search_title_requires_the_requested_identifier() -> None:
    payload = {
        "docs": [
            {
                "title": "Principles of constraint programming",
                "isbn": ["0521825830", "9780521825832"],
            }
        ]
    }

    assert _isbn_search_title(payload, "978-0-521-82583-2") == (
        "Principles of constraint programming"
    )


def test_isbn_search_title_rejects_unrelated_search_results() -> None:
    payload = {
        "docs": [
            {
                "title": "Swarm Intelligence",
                "isbn": ["0195131584"],
            }
        ]
    }

    assert _isbn_search_title(payload, "9780195131598") is None


def test_google_books_feed_title_requires_the_requested_identifier() -> None:
    feed = """<?xml version='1.0'?>
    <feed xmlns='http://www.w3.org/2005/Atom'
          xmlns:dc='http://purl.org/dc/terms/'>
      <entry>
        <title>Probabilistic Reasoning in Intelligent Systems</title>
        <dc:identifier>ISBN:1558604790</dc:identifier>
      </entry>
    </feed>
    """

    assert _google_books_feed_title(feed, "1558604790") == (
        "Probabilistic Reasoning in Intelligent Systems"
    )
