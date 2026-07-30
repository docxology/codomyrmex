"""Fail-closed MkDocs hooks for Codomyrmex documentation.

The documentation tree intentionally links to source and configuration files
outside ``docs/``. MkDocs cannot copy those files into the site, so this hook
rewrites only *existing* repository targets to stable GitHub blob/tree URLs.
Missing targets are deliberately left untouched so ``mkdocs build --strict``
still reports them.

The generated technical report is treated as a build input rather than a
second Markdown source. Its semantic HTML is validated before the site build
and copied into the final site after MkDocs has written static files.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from mkdocs.exceptions import BuildError

LOGGER = logging.getLogger("codomyrmex.documentation.mkdocs")

_INLINE_LINK_RE = re.compile(
    r"(?P<prefix>!?\[[^\]\n]*\]\()"
    r"(?P<destination><[^>\n]+>|[^)\s]+)"
    r"(?P<suffix>(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\))"
)
_REFERENCE_LINK_RE = re.compile(
    r"^(?P<prefix>[ \t]{0,3}\[[^\]\n]+\]:[ \t]*)"
    r"(?P<destination><[^>\n]+>|\S+)"
    r"(?P<suffix>.*)$"
)
_FENCE_RE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
_REPORT_ROUTE = Path("manuscript/technical-report.html")
_REPORT_MARKERS = (
    "<!DOCTYPE html>",
    "<title>Codomyrmex:",
    'aria-describedby="fig:',
)


def _absolute(path: str | os.PathLike[str]) -> Path:
    """Return a normalized absolute path without requiring it to exist."""

    return Path(path).expanduser().resolve(strict=False)


def _is_within(path: Path, parent: Path) -> bool:
    """Return whether *path* is inside *parent*, including the parent itself."""

    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _canonical_docs_target(target: Path) -> Path:
    """Resolve directory and README/index ambiguity within ``docs/``."""

    if target.is_dir():
        for name in ("index.md", "README.md", "index.html"):
            candidate = target / name
            if candidate.is_file():
                return candidate

    if target.name == "README.md":
        index = target.with_name("index.md")
        if index.is_file():
            return index

    return target


def _github_url(
    target: Path,
    *,
    repo_root: Path,
    repo_url: str,
    source_branch: str,
) -> str:
    """Create a GitHub blob/tree URL for an existing repository target."""

    relative = target.relative_to(repo_root).as_posix()
    kind = "tree" if target.is_dir() else "blob"
    encoded = quote(relative, safe="/")
    return f"{repo_url.rstrip('/')}/{kind}/{quote(source_branch, safe='')}/{encoded}"


def _rewrite_destination(
    destination: str,
    *,
    source_path: Path,
    docs_dir: Path,
    repo_root: Path,
    repo_url: str,
    source_branch: str,
) -> str:
    """Rewrite one Markdown link destination when its local target exists."""

    wrapped = destination.startswith("<") and destination.endswith(">")
    raw = destination[1:-1] if wrapped else destination
    parsed = urlsplit(raw)

    if (
        not parsed.path
        or parsed.scheme
        or parsed.netloc
        or raw.startswith(("#", "/", "mailto:", "tel:", "data:"))
    ):
        return destination

    decoded_path = unquote(parsed.path)
    source_candidate = _absolute(source_path.parent / decoded_path)
    root_candidate = _absolute(repo_root / decoded_path)

    target: Path | None = None
    for candidate in (source_candidate, root_candidate):
        if candidate.exists() and _is_within(candidate, repo_root):
            target = candidate
            break

    if target is None:
        return destination

    if _is_within(target, docs_dir):
        canonical = _canonical_docs_target(target)
        relative = os.path.relpath(canonical, source_path.parent)
        rewritten_path = Path(relative).as_posix()
        rewritten = urlunsplit(("", "", rewritten_path, parsed.query, parsed.fragment))
    else:
        rewritten = _github_url(
            target,
            repo_root=repo_root,
            repo_url=repo_url,
            source_branch=source_branch,
        )
        if parsed.query:
            rewritten = f"{rewritten}?{parsed.query}"
        if parsed.fragment:
            rewritten = f"{rewritten}#{parsed.fragment}"

    return f"<{rewritten}>" if wrapped else rewritten


def rewrite_markdown_links(
    markdown: str,
    *,
    source_path: str | os.PathLike[str],
    docs_dir: str | os.PathLike[str],
    repo_root: str | os.PathLike[str],
    repo_url: str,
    source_branch: str = "main",
) -> str:
    """Rewrite repository-valid Markdown links while preserving code fences."""

    source = _absolute(source_path)
    docs = _absolute(docs_dir)
    root = _absolute(repo_root)
    active_fence: str | None = None
    rewritten_lines: list[str] = []

    def replace(match: re.Match[str]) -> str:
        destination = _rewrite_destination(
            match.group("destination"),
            source_path=source,
            docs_dir=docs,
            repo_root=root,
            repo_url=repo_url,
            source_branch=source_branch,
        )
        return f"{match.group('prefix')}{destination}{match.group('suffix')}"

    for line in markdown.splitlines(keepends=True):
        fence_match = _FENCE_RE.match(line)
        if fence_match:
            fence = fence_match.group("fence")
            if active_fence is None:
                active_fence = fence[0]
            elif fence.startswith(active_fence):
                active_fence = None
            rewritten_lines.append(line)
            continue

        if active_fence is not None:
            rewritten_lines.append(line)
            continue

        line = _INLINE_LINK_RE.sub(replace, line)
        line = _REFERENCE_LINK_RE.sub(replace, line)
        rewritten_lines.append(line)

    return "".join(rewritten_lines)


def _report_source(config: Any) -> Path:
    repo_root = _absolute(Path(config["config_file_path"]).parent)
    configured = config.get("extra", {}).get(
        "technical_report_source", "output/paper.html"
    )
    return _absolute(repo_root / configured)


def _validate_semantic_report(path: Path) -> None:
    if not path.is_file():
        raise BuildError(
            "Generated semantic report is required before the MkDocs build: "
            f"{path}. Run the documented manuscript compilation command."
        )

    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in _REPORT_MARKERS if marker not in text]
    if missing:
        raise BuildError(
            f"Generated semantic report {path} is missing required markers: "
            + ", ".join(missing)
        )


def on_pre_build(*, config: Any, **_: Any) -> None:
    """Require a current-looking semantic report before building the site."""

    report = _report_source(config)
    _validate_semantic_report(report)
    LOGGER.info("Validated semantic technical report: %s", report)


def on_page_markdown(
    markdown: str,
    *,
    page: Any,
    config: Any,
    files: Any,
) -> str:
    """Rewrite resolvable repository links before MkDocs validates them."""

    del files
    source_path = Path(page.file.abs_src_path)
    repo_root = _absolute(Path(config["config_file_path"]).parent)
    source_branch = str(config.get("extra", {}).get("source_branch", "main"))
    return rewrite_markdown_links(
        markdown,
        source_path=source_path,
        docs_dir=config["docs_dir"],
        repo_root=repo_root,
        repo_url=str(config["repo_url"]),
        source_branch=source_branch,
    )


def on_post_build(*, config: Any, **_: Any) -> None:
    """Copy the validated report over the placeholder site artifact."""

    report = _report_source(config)
    _validate_semantic_report(report)
    destination = _absolute(config["site_dir"]) / _REPORT_ROUTE
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(report, destination)
    LOGGER.info("Installed semantic technical report at %s", destination)
