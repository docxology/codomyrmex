"""Pandoc-aware bibliography inventory and primary-source resolution."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

CROSS_REFERENCE_PREFIXES = frozenset({"eq", "fig", "sec", "tbl"})
CITATION_PATTERN = re.compile(r"(?<![A-Za-z0-9_])@([A-Za-z][A-Za-z0-9_:-]*)")
ENTRY_START_PATTERN = re.compile(r"@([A-Za-z]+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)


@dataclass(frozen=True)
class BibliographyRecord:
    """Parsed BibTeX record."""

    key: str
    entry_type: str
    fields: dict[str, str]


@dataclass(frozen=True)
class CitationInventory:
    """Pandoc citations and cross-references found in manuscript prose."""

    citation_keys: tuple[str, ...]
    cross_references: tuple[str, ...]


def _strip_delimiters(value: str) -> str:
    stripped = value.strip().rstrip(",").strip()
    if len(stripped) >= 2 and (
        (stripped[0] == "{" and stripped[-1] == "}")
        or (stripped[0] == '"' and stripped[-1] == '"')
    ):
        return stripped[1:-1].strip()
    return stripped


def _parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    index = 0
    length = len(body)
    while index < length:
        while index < length and (body[index].isspace() or body[index] == ","):
            index += 1
        match = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=", body[index:])
        if match is None:
            break
        name = match.group(1).lower()
        index += match.end()
        while index < length and body[index].isspace():
            index += 1
        start = index
        brace_depth = 0
        quote = False
        escaped = False
        while index < length:
            character = body[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"' and brace_depth == 0:
                quote = not quote
            elif not quote and character == "{":
                brace_depth += 1
            elif not quote and character == "}":
                brace_depth -= 1
            elif character == "," and brace_depth == 0 and not quote:
                break
            index += 1
        fields[name] = _strip_delimiters(body[start:index])
        index += 1
    return fields


def parse_bibtex(text: str) -> tuple[BibliographyRecord, ...]:
    """Parse ordinary braced BibTeX entries while preserving nested field braces."""
    records: list[BibliographyRecord] = []
    position = 0
    while match := ENTRY_START_PATTERN.search(text, position):
        entry_type, key = match.groups()
        index = match.end()
        body_start = index
        depth = 1
        quote = False
        escaped = False
        while index < len(text) and depth:
            character = text[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quote = not quote
            elif not quote and character == "{":
                depth += 1
            elif not quote and character == "}":
                depth -= 1
            index += 1
        if depth:
            message = f"Unterminated BibTeX entry: {key}"
            raise ValueError(message)
        body = text[body_start : index - 1]
        records.append(
            BibliographyRecord(
                key=key,
                entry_type=entry_type.lower(),
                fields=_parse_fields(body),
            )
        )
        position = index
    return tuple(records)


def _strip_code(markdown: str) -> str:
    without_fences = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", without_fences)


def extract_pandoc_citations(paths: Iterable[Path]) -> CitationInventory:
    """Separate bibliography citations from Pandoc-crossref identifiers."""
    citations: set[str] = set()
    cross_references: set[str] = set()
    for path in paths:
        text = _strip_code(path.read_text(encoding="utf-8"))
        for key in CITATION_PATTERN.findall(text):
            prefix = key.split(":", maxsplit=1)[0]
            if prefix in CROSS_REFERENCE_PREFIXES and ":" in key:
                cross_references.add(key)
            else:
                citations.add(key)
    return CitationInventory(
        citation_keys=tuple(sorted(citations)),
        cross_references=tuple(sorted(cross_references)),
    )


def _locator(record: BibliographyRecord) -> tuple[str, str]:
    fields = record.fields
    doi = fields.get("doi", "").strip()
    if doi:
        return "doi", doi.removeprefix("https://doi.org/")
    eprint = fields.get("eprint", "").strip()
    archive = fields.get("archiveprefix", "").lower()
    if eprint and archive == "arxiv":
        return "arxiv", eprint
    url = fields.get("url", "").strip()
    arxiv_match = re.search(r"arxiv\.org/(?:abs|pdf)/([^/?#]+)", url)
    if arxiv_match:
        return "arxiv", arxiv_match.group(1).removesuffix(".pdf")
    if url:
        return "official-url", url
    isbn = re.sub(r"[^0-9Xx]", "", fields.get("isbn", ""))
    if isbn:
        return "isbn", isbn
    return "missing", ""


def _normalise_title(value: str) -> str:
    value = re.sub(r"[{}\\]", "", value).lower()
    return " ".join(re.findall(r"[a-z0-9]+", value))


def _request_json(url: str, timeout: float) -> tuple[int, dict[str, Any], str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "CodomyrmexBibliographyAudit/1.0 "
                "(https://github.com/docxology/codomyrmex)"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        status = int(response.status)
        payload = json.loads(response.read(2 * 1024 * 1024).decode("utf-8"))
        return status, payload, response.geturl()


def _request_url(url: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "CodomyrmexBibliographyAudit/1.0 "
                "(https://github.com/docxology/codomyrmex)"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read(1024)
        return int(response.status), response.geturl()


def _resolve_record(
    record: BibliographyRecord,
    *,
    timeout: float,
) -> dict[str, Any]:
    kind, locator = _locator(record)
    result: dict[str, Any] = {
        "key": record.key,
        "entry_type": record.entry_type,
        "title": record.fields.get("title", ""),
        "locator_kind": kind,
        "locator": locator,
        "resolved": False,
        "http_status": None,
        "resolved_url": "",
        "registry_title": "",
        "title_similarity": None,
        "title_match": None,
        "access_limited": False,
        "error": "",
    }
    if kind == "missing":
        result["error"] = "no DOI, arXiv identifier, official URL, or ISBN"
        return result
    try:
        if kind == "doi":
            encoded = urllib.parse.quote(locator, safe="")
            status, payload, resolved_url = _request_json(
                (
                    f"https://api.crossref.org/works/{encoded}"
                    "?mailto=daniel%40activeinference.institute"
                ),
                timeout,
            )
            message = payload.get("message", {})
            titles = message.get("title", []) if isinstance(message, dict) else []
            registry_title = str(titles[0]) if titles else ""
            expected = _normalise_title(record.fields.get("title", ""))
            actual = _normalise_title(registry_title)
            similarity = (
                SequenceMatcher(None, expected, actual).ratio()
                if expected and actual
                else 0.0
            )
            title_match = bool(
                expected
                and actual
                and (similarity >= 0.72 or expected in actual or actual in expected)
            )
            result.update(
                {
                    "resolved": status == 200,
                    "http_status": status,
                    "resolved_url": resolved_url,
                    "registry_title": registry_title,
                    "title_similarity": round(similarity, 4),
                    "title_match": title_match,
                }
            )
        else:
            urls = {
                "arxiv": f"https://arxiv.org/abs/{locator}",
                "official-url": locator,
                "isbn": f"https://openlibrary.org/isbn/{locator}.json",
            }
            status, resolved_url = _request_url(urls[kind], timeout)
            result.update(
                {
                    "resolved": 200 <= status < 400,
                    "http_status": status,
                    "resolved_url": resolved_url,
                }
            )
    except (
        OSError,
        TimeoutError,
        ValueError,
        json.JSONDecodeError,
        urllib.error.HTTPError,
        urllib.error.URLError,
    ) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        if isinstance(exc, urllib.error.HTTPError):
            result["http_status"] = exc.code
            result["resolved_url"] = exc.geturl()
            if kind == "official-url" and exc.code in {401, 403}:
                # A repository may reject automated retrieval while still resolving
                # its persistent locator. Preserve that limitation in the receipt.
                result["resolved"] = True
                result["access_limited"] = True
    return result


def audit_bibliography(
    bibliography_path: Path,
    manuscript_paths: Iterable[Path],
    *,
    verify_online: bool = False,
    timeout: float = 15.0,
    workers: int = 8,
) -> dict[str, Any]:
    """Build a citation inventory and optionally resolve primary-source metadata."""
    text = bibliography_path.read_text(encoding="utf-8")
    records = parse_bibtex(text)
    inventory = extract_pandoc_citations(manuscript_paths)
    by_key = {record.key: record for record in records}
    duplicate_keys = sorted(
        key for key in by_key if sum(record.key == key for record in records) > 1
    )
    cited = set(inventory.citation_keys)
    missing = sorted(cited - set(by_key))
    unused = sorted(set(by_key) - cited)

    if verify_online:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            audits = list(
                executor.map(
                    lambda record: _resolve_record(record, timeout=timeout),
                    records,
                )
            )
    else:
        audits = []
        for record in records:
            kind, locator = _locator(record)
            audits.append(
                {
                    "key": record.key,
                    "entry_type": record.entry_type,
                    "title": record.fields.get("title", ""),
                    "locator_kind": kind,
                    "locator": locator,
                    "resolved": None,
                    "http_status": None,
                    "resolved_url": "",
                    "registry_title": "",
                    "title_similarity": None,
                    "title_match": None,
                    "access_limited": False,
                    "error": (
                        "no DOI, arXiv identifier, official URL, or ISBN"
                        if kind == "missing"
                        else ""
                    ),
                }
            )

    for record in audits:
        record["cited"] = record["key"] in cited
    unresolved_locators = sorted(
        record["key"] for record in audits if record["locator_kind"] == "missing"
    )
    online_failures = sorted(
        record["key"] for record in audits if verify_online and not record["resolved"]
    )
    title_mismatches = sorted(
        record["key"]
        for record in audits
        if verify_online and record["title_match"] is False
    )
    return {
        "schema_version": "1",
        "bibliography_path": bibliography_path.name,
        "bibliography_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "online_verification": verify_online,
        "record_count": len(records),
        "cited_count": len(cited),
        "cross_reference_count": len(inventory.cross_references),
        "citation_keys": list(inventory.citation_keys),
        "cross_references": list(inventory.cross_references),
        "missing_citations": missing,
        "unused_bibliography_keys": unused,
        "duplicate_bibliography_keys": duplicate_keys,
        "unresolved_locators": unresolved_locators,
        "online_failures": online_failures,
        "title_mismatches": title_mismatches,
        "records": sorted(audits, key=lambda item: item["key"]),
    }


def write_bibliography_audit(path: Path, audit: dict[str, Any]) -> None:
    """Write a deterministic bibliography audit receipt."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(audit, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "BibliographyRecord",
    "CitationInventory",
    "audit_bibliography",
    "extract_pandoc_citations",
    "parse_bibtex",
    "write_bibliography_audit",
]
