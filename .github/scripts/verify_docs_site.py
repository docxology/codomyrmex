"""Assert that the page under the base path is the artifact that was built.

Two published numbers came out of this harness before these checks existed:

* the build declares an absolute ``baseUrl`` (``/codomyrmex/``), so serving
  ``build/`` at the server root made every asset request 404 and Lighthouse
  scored a page that shipped no CSS or JavaScript;
* the local server did not compress, so the emulated link measured
  compressibility (1.76 MB) instead of the site GitHub Pages sends (337 KB).

Three checks close both holes, and each prints the value it measured: a gate
whose green state cannot show what it verified is only half a gate.

1. the document at the base path is byte-identical to ``build/index.html``;
2. every JS/CSS asset the page references resolves with HTTP 200 under the
   base path;
3. a JS asset comes back gzip-encoded when the client accepts gzip.

Exit status is 0 when all three hold, 1 otherwise, and the failure line names
the check and the values it compared, so a red run says what went wrong.

Used by ``serve_docs_site.sh`` for both the server LHCI starts and the workflow
step that prints these lines, so the two cannot drift apart.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE_URL = "http://127.0.0.1:4173/codomyrmex/"
DEFAULT_BUILD_DIR = "src/codomyrmex/documentation/build"
REQUEST_TIMEOUT_SECONDS = 30
ASSET_PATTERN = re.compile(r'(?:src|href)="(/[^"]*assets/(?:js|css)/[^"]+)"')


def fetch(url: str, *, accept_gzip: bool = False) -> tuple[int, dict, bytes]:
    request = urllib.request.Request(url)
    if accept_gzip:
        request.add_header("Accept-Encoding", "gzip")
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return response.status, dict(response.headers), response.read()


def header(headers: dict, name: str) -> str:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def fail(message: str) -> int:
    print(f"verify_docs_site: FAIL {message}", file=sys.stderr)
    return 1


def status_of(url: str) -> object:
    try:
        code, _headers, _body = fetch(url)
        return code
    except urllib.error.HTTPError as error:
        return error.code
    except (urllib.error.URLError, OSError) as error:
        return f"unreachable ({error})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--build-dir", default=DEFAULT_BUILD_DIR)
    args = parser.parse_args()

    base_url = args.base_url if args.base_url.endswith("/") else f"{args.base_url}/"
    parts = urllib.parse.urlsplit(base_url)
    origin = f"{parts.scheme}://{parts.netloc}"
    built_path = os.path.join(args.build_dir, "index.html")

    # 1. The document at the base path is the build's own index.html.
    try:
        status, _headers, served = fetch(base_url)
    except (urllib.error.URLError, OSError) as error:
        return fail(f"{base_url} did not answer ({error})")
    if status != 200:
        return fail(f"{base_url} returned HTTP {status}")
    try:
        with open(built_path, "rb") as handle:
            built = handle.read()
    except OSError as error:
        return fail(f"cannot read {built_path} ({error})")
    if served != built:
        return fail(
            f"the served HTML is not {built_path}: served {len(served)} B "
            f"sha256 {digest(served)}, built {len(built)} B sha256 {digest(built)}"
        )
    print(
        f"verify_docs_site: served HTML is byte-identical to {built_path} "
        f"({len(built)} B, sha256 {digest(built)})"
    )

    # 2. Every asset the page references resolves under the base path.
    assets = sorted(
        set(ASSET_PATTERN.findall(served.decode("utf-8", errors="replace")))
    )
    if not assets:
        return fail(
            "the served HTML references no JS/CSS asset under the base path; "
            "a page with no assets is not the deployed site"
        )
    unresolved = []
    for asset in assets:
        status = status_of(origin + asset)
        if status != 200:
            unresolved.append(f"{asset} -> HTTP {status}")
    if unresolved:
        return fail(
            "assets do not resolve under the base path: " + "; ".join(unresolved)
        )
    print(
        f"verify_docs_site: {len(assets)}/{len(assets)} referenced assets resolve under "
        f"the base path (e.g. {assets[0]})"
    )

    # 3. Text responses are compressed, as GitHub Pages compresses them.
    js_assets = [asset for asset in assets if "/assets/js/" in asset]
    if not js_assets:
        return fail("the served HTML references no JS asset, so gzip cannot be checked")
    probe = next((asset for asset in js_assets if "/main." in asset), js_assets[0])
    try:
        status, headers, body = fetch(origin + probe, accept_gzip=True)
    except (urllib.error.URLError, OSError) as error:
        return fail(
            f"{probe} could not be fetched with Accept-Encoding: gzip ({error})"
        )
    encoding = header(headers, "Content-Encoding")
    if status != 200 or "gzip" not in encoding.lower():
        return fail(
            f"{probe} was served without gzip "
            f"(HTTP {status}, Content-Encoding: {encoding or 'absent'})"
        )
    print(
        f"verify_docs_site: {probe} is gzip-encoded "
        f"(Content-Encoding: {encoding}, {len(body)} B on the wire)"
    )

    print(
        "verify_docs_site: artifact verified "
        "(index.html byte-identical, assets resolve, gzip on)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
