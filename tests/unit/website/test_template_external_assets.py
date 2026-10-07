"""Third-party assets in the dashboard templates must be pinned and integrity-checked.

Regression: ``docs.html`` loaded ``marked`` with no version at all (so every
upstream release, including a compromised one, executed on the page and the
``marked/marked.min.js`` path disappeared from the package in later majors),
``awareness.html`` floated on ``mermaid@10``, and DOMPurify was pinned to a
release with published sanitizer bypasses. None carried Subresource Integrity.
"""

from __future__ import annotations

import base64
import hashlib
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parents[3] / "src/codomyrmex/website/templates"

# Google Fonts returns user-agent-specific CSS, so its stylesheet cannot carry
# a fixed integrity hash. It loads CSS only, never script.
SRI_EXEMPT_HOSTS = ("https://fonts.googleapis.com/",)

INTEGRITY = re.compile(r"^sha(256|384|512)-[A-Za-z0-9+/]+={0,2}$")
EXACT_VERSION = re.compile(r"@\d+\.\d+\.\d+/")


class _ExternalAssets(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.assets: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script":
            url = attributes.get("src")
        elif tag == "link" and attributes.get("rel") == "stylesheet":
            url = attributes.get("href")
        else:
            return
        if url and url.startswith(("http://", "https://", "//")):
            self.assets.append({"tag": tag, "url": url, **attributes})


def _external_assets() -> list[tuple[str, dict[str, str | None]]]:
    found = []
    for template in sorted(TEMPLATES.glob("*.html")):
        parser = _ExternalAssets()
        parser.feed(template.read_text(encoding="utf-8"))
        found.extend((template.name, asset) for asset in parser.assets)
    return found


ASSETS = _external_assets()
SRI_ASSETS = [
    (name, asset)
    for name, asset in ASSETS
    if not str(asset["url"]).startswith(SRI_EXEMPT_HOSTS)
]


@pytest.mark.unit
def test_templates_load_some_cdn_assets() -> None:
    # Guards the parser: an empty scan would make every other check vacuous.
    assert {name for name, _ in SRI_ASSETS} >= {"docs.html", "awareness.html"}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("template", "asset"), SRI_ASSETS, ids=[str(a["url"]) for _, a in SRI_ASSETS]
)
def test_cdn_asset_is_pinned_with_integrity(template: str, asset: dict) -> None:
    url = asset["url"]
    assert url.startswith("https://"), f"{template}: insecure asset URL {url}"
    assert EXACT_VERSION.search(url), f"{template}: {url} is not pinned to x.y.z"
    assert INTEGRITY.match(asset.get("integrity") or ""), (
        f"{template}: {url} has no valid integrity attribute"
    )
    assert asset.get("crossorigin") == "anonymous", (
        f"{template}: {url} needs crossorigin=anonymous for SRI to apply"
    )


@pytest.mark.network
@pytest.mark.parametrize(
    ("template", "asset"), SRI_ASSETS, ids=[str(a["url"]) for _, a in SRI_ASSETS]
)
def test_cdn_asset_integrity_matches_published_bytes(
    template: str, asset: dict
) -> None:
    integrity = asset.get("integrity") or ""
    if "-" not in integrity:
        pytest.fail(f"{template}: {asset['url']} has no integrity attribute")
    algorithm, expected = integrity.split("-", 1)
    try:
        with urllib.request.urlopen(asset["url"], timeout=30) as response:
            body = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        pytest.skip(f"CDN unreachable: {exc}")
    digest = base64.b64encode(hashlib.new(algorithm, body).digest()).decode()
    assert digest == expected, f"{template}: integrity mismatch for {asset['url']}"
