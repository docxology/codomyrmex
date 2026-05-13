#!/usr/bin/env python3
"""Rewrite Docusaurus module links to point at canonical repo docs.

The generated Docusaurus module mirrors live under
``src/codomyrmex/documentation/docs/modules/<module>/``. Some generated pages
contain local links such as ``SPEC.md`` or ``mcp_tools.py`` even though the
canonical files live elsewhere in the repository. This script rewrites those
links to paths that resolve from the mirrored page location.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_LOCAL_LINK_RE = re.compile(
    r"\]\(("
    r"AGENTS\.md|API_SPECIFICATION\.md|MCP_TOOL_SPECIFICATION\.md|"
    r"PAI\.md|SECURITY\.md|SPEC\.md|mcp_tools\.py"
    r")(#[^)]+)?\)"
)


def prefix_for(parent: Path, repo_root: Path) -> str:
    """Return a relative prefix from *parent* back to *repo_root*."""
    rel = parent.resolve().relative_to(repo_root.resolve())
    if not rel.parts:
        return ""
    return "../" * len(rel.parts)


def href_map_for_module(
    module_name: str, parent: Path, repo_root: Path
) -> dict[str, str | None]:
    """Return canonical hrefs for local module documentation targets."""
    prefix = prefix_for(parent, repo_root)

    module_docs = repo_root / "docs" / "modules" / module_name
    source_module = repo_root / "src" / "codomyrmex" / module_name

    hrefs: dict[str, str | None] = {}

    for filename in (
        "AGENTS.md",
        "API_SPECIFICATION.md",
        "MCP_TOOL_SPECIFICATION.md",
        "SECURITY.md",
        "SPEC.md",
    ):
        docs_target = module_docs / filename
        source_target = source_module / filename
        if docs_target.is_file():
            hrefs[filename] = f"{prefix}docs/modules/{module_name}/{filename}"
        elif source_target.is_file():
            hrefs[filename] = f"{prefix}src/codomyrmex/{module_name}/{filename}"
        else:
            hrefs[filename] = None

    spec_href = None
    if (module_docs / "SPEC.md").is_file():
        spec_href = f"{prefix}docs/modules/{module_name}/SPEC.md"
    elif (source_module / "SPEC.md").is_file():
        spec_href = f"{prefix}src/codomyrmex/{module_name}/SPEC.md"
    hrefs["SPEC.md"] = spec_href

    pai_href = None
    if (module_docs / "PAI.md").is_file():
        pai_href = f"{prefix}docs/modules/{module_name}/PAI.md"
    elif (source_module / "PAI.md").is_file():
        pai_href = f"{prefix}src/codomyrmex/{module_name}/PAI.md"
    elif (repo_root / "docs" / "PAI.md").is_file():
        pai_href = f"{prefix}docs/PAI.md"
    hrefs["PAI.md"] = pai_href

    mcp_href = None
    mcp_path = source_module / "mcp_tools.py"
    if mcp_path.is_file():
        mcp_href = f"{prefix}src/codomyrmex/{module_name}/mcp_tools.py"
    hrefs["mcp_tools.py"] = mcp_href

    return hrefs


def hrefs_for_module(
    module_name: str, parent: Path, repo_root: Path
) -> tuple[str | None, str | None, str | None]:
    """Return canonical SPEC, PAI, and MCP hrefs for *module_name*."""
    hrefs = href_map_for_module(module_name, parent, repo_root)
    return hrefs["SPEC.md"], hrefs["PAI.md"], hrefs["mcp_tools.py"]


def transform_content(
    content: str, module_name: str, parent: Path, repo_root: Path
) -> str:
    """Rewrite bare local module links in *content* when canonical targets exist."""
    replacements = href_map_for_module(module_name, parent, repo_root)

    def replace(match: re.Match[str]) -> str:
        target = match.group(1)
        anchor = match.group(2) or ""
        href = replacements.get(target)
        if href is None:
            return match.group(0)
        return f"]({href}{anchor})"

    return _LOCAL_LINK_RE.sub(replace, content)


def iter_module_pages(repo_root: Path) -> list[Path]:
    """Return Docusaurus mirror markdown pages that may contain module links."""
    modules_root = (
        repo_root / "src" / "codomyrmex" / "documentation" / "docs" / "modules"
    )
    if not modules_root.is_dir():
        return []
    return sorted(modules_root.glob("*/README.md"))


def main(argv: list[str] | None = None) -> int:
    """Rewrite eligible Docusaurus module README links in place."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check", action="store_true", help="Report drift without writing"
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    changed: list[Path] = []
    for page in iter_module_pages(repo_root):
        module_name = page.parent.name
        original = page.read_text(encoding="utf-8")
        updated = transform_content(original, module_name, page.parent, repo_root)
        if updated == original:
            continue
        changed.append(page)
        if not args.check:
            page.write_text(updated, encoding="utf-8")

    if changed:
        for page in changed:
            print(page.relative_to(repo_root))
        return 1 if args.check else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
