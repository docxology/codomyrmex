#!/usr/bin/env python3
"""Rewrite Docusaurus module links to resolvable canonical targets.

The generated Docusaurus module mirror lives under
``src/codomyrmex/documentation/docs/modules/<module>/``. Some generated pages
use local links such as ``SPEC.md`` or ``mcp_tools.py`` even when the canonical
files live in ``docs/modules/<module>/`` or ``src/codomyrmex/<module>/``.
Other pages use uppercase filenames even though the Docusaurus mirror stores
its generated pages as lowercase filenames (for example
``api_specification.md``).

This script rewrites those links in every mirrored module markdown page, not
only README pages, and uses case-sensitive filesystem checks so macOS does not
hide Linux/Docusaurus link failures.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_LINK_TARGET_RE = re.compile(r"\]\(([^)]+)\)")
_LOCAL_DOC_TARGETS = {
    "README.md": "readme.md",
    "API_SPECIFICATION.md": "api_specification.md",
    "MCP_TOOL_SPECIFICATION.md": "mcp_tool_specification.md",
    "SECURITY.md": "security.md",
    "USAGE_EXAMPLES.md": "usage_examples.md",
}
_CANONICAL_DOC_TARGETS = {
    "AGENTS.md",
    "API_SPECIFICATION.md",
    "MCP_TOOL_SPECIFICATION.md",
    "PAI.md",
    "SECURITY.md",
    "SPEC.md",
    "USAGE_EXAMPLES.md",
}
_SPECIAL_TARGETS = {"mcp_tools.py", "AGENT_COMPARISON.md"}
_EXTERNAL_TARGET_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def prefix_for(parent: Path, repo_root: Path) -> str:
    """Return a relative prefix from *parent* back to *repo_root*."""
    rel = parent.resolve().relative_to(repo_root.resolve())
    if not rel.parts:
        return ""
    return "../" * len(rel.parts)


def case_sensitive_exists(path: Path) -> bool:
    """Return True only when every path component matches filesystem casing."""
    path = path.resolve()
    if path.exists() is False:
        return False

    current = path.anchor
    parts = path.parts[1:] if path.is_absolute() else path.parts
    current_path = Path(current) if current else Path(".")
    for part in parts:
        try:
            names = {child.name for child in current_path.iterdir()}
        except OSError:
            return False
        if part not in names:
            return False
        current_path = current_path / part
    return True


def _first_existing(paths: list[Path] | tuple[Path, ...]) -> Path | None:
    for path in paths:
        if case_sensitive_exists(path):
            return path
    return None


def href_map_for_module(
    module_name: str, parent: Path, repo_root: Path
) -> dict[str, str | None]:
    """Return canonical hrefs for module documentation targets."""
    prefix = prefix_for(parent, repo_root)

    module_docs = repo_root / "docs" / "modules" / module_name
    source_module = repo_root / "src" / "codomyrmex" / module_name

    hrefs: dict[str, str | None] = {}
    for filename in _CANONICAL_DOC_TARGETS:
        docs_target = module_docs / filename
        source_target = source_module / filename
        if case_sensitive_exists(docs_target):
            hrefs[filename] = f"{prefix}docs/modules/{module_name}/{filename}"
        elif case_sensitive_exists(source_target):
            hrefs[filename] = f"{prefix}src/codomyrmex/{module_name}/{filename}"
        else:
            hrefs[filename] = None

    pai_target = source_module / "PAI.md"
    if case_sensitive_exists(module_docs / "PAI.md"):
        hrefs["PAI.md"] = f"{prefix}docs/modules/{module_name}/PAI.md"
    elif case_sensitive_exists(pai_target):
        hrefs["PAI.md"] = f"{prefix}src/codomyrmex/{module_name}/PAI.md"
    elif case_sensitive_exists(repo_root / "docs" / "PAI.md"):
        hrefs["PAI.md"] = f"{prefix}docs/PAI.md"

    mcp_path = source_module / "mcp_tools.py"
    hrefs["mcp_tools.py"] = (
        f"{prefix}src/codomyrmex/{module_name}/mcp_tools.py"
        if case_sensitive_exists(mcp_path)
        else None
    )

    agent_comparison = _first_existing(
        [
            repo_root / "docs" / "modules" / "agents" / "AGENT_COMPARISON.md",
            repo_root / "src" / "codomyrmex" / "agents" / "AGENT_COMPARISON.md",
        ]
    )
    if agent_comparison is None:
        hrefs["AGENT_COMPARISON.md"] = None
    else:
        hrefs["AGENT_COMPARISON.md"] = (
            f"{prefix}{agent_comparison.relative_to(repo_root).as_posix()}"
        )

    return hrefs


def hrefs_for_module(
    module_name: str, parent: Path, repo_root: Path
) -> tuple[str | None, str | None, str | None]:
    """Return canonical SPEC, PAI, and MCP hrefs for *module_name*."""
    hrefs = href_map_for_module(module_name, parent, repo_root)
    return hrefs["SPEC.md"], hrefs["PAI.md"], hrefs["mcp_tools.py"]


def _target_parts(target: str) -> tuple[str, str, str]:
    """Split a link target into path, anchor, and query suffixes."""
    path_and_anchor, sep_query, query = target.partition("?")
    path, sep_anchor, anchor = path_and_anchor.partition("#")
    suffix = f"{sep_anchor}{anchor}" if sep_anchor else ""
    suffix += f"{sep_query}{query}" if sep_query else ""
    return path, suffix, sep_anchor


def _is_rewritable_target(target_path: str) -> bool:
    if not target_path or target_path.startswith("#"):
        return False
    return not _EXTERNAL_TARGET_RE.match(target_path)


def _relative_to_repo(path: Path, parent: Path, repo_root: Path) -> str:
    """Return *path* as a markdown target relative to *parent*."""
    try:
        relative = path.relative_to(parent)
        return relative.as_posix()
    except ValueError:
        return (
            f"{prefix_for(parent, repo_root)}{path.relative_to(repo_root).as_posix()}"
        )


def _canonical_for_module_file(
    target_name: str, module_name: str, parent: Path, repo_root: Path
) -> str | None:
    local_lower = _LOCAL_DOC_TARGETS.get(target_name)
    if local_lower is not None and case_sensitive_exists(parent / local_lower):
        return local_lower
    if case_sensitive_exists(parent / target_name):
        return target_name
    return href_map_for_module(module_name, parent, repo_root).get(target_name)


def _rewrite_cross_module_target(
    target_path: str, parent: Path, repo_root: Path
) -> str | None:
    target = (parent / target_path).resolve()
    target_name = Path(target_path).name
    if (
        target_name not in _LOCAL_DOC_TARGETS
        and target_name not in _CANONICAL_DOC_TARGETS
    ):
        return None

    lower_name = _LOCAL_DOC_TARGETS.get(target_name)
    if lower_name is not None:
        lower_target = target.with_name(lower_name)
        if case_sensitive_exists(lower_target):
            return Path(target_path).with_name(lower_name).as_posix()

    # If a sibling module is absent from the Docusaurus mirror, fall back to the
    # repo-level docs/source module file when the relative path reveals a module
    # name (for example ../documentation/API_SPECIFICATION.md).
    parts = Path(target_path).parts
    if len(parts) >= 2 and parts[-1] == target_name:
        module_name = parts[-2]
        href = href_map_for_module(module_name, parent, repo_root).get(target_name)
        if href is not None:
            return href
    return None


def rewrite_target(target: str, module_name: str, parent: Path, repo_root: Path) -> str:
    """Rewrite one markdown link target when a resolvable alternative exists."""
    target_path, suffix, _ = _target_parts(target)
    if not _is_rewritable_target(target_path):
        return target

    target_name = Path(target_path).name
    if target_path in _SPECIAL_TARGETS or target_name in _SPECIAL_TARGETS:
        href = href_map_for_module(module_name, parent, repo_root).get(target_name)
        return f"{href}{suffix}" if href is not None else target

    if target_path in _LOCAL_DOC_TARGETS or target_path in _CANONICAL_DOC_TARGETS:
        href = _canonical_for_module_file(target_path, module_name, parent, repo_root)
        return f"{href}{suffix}" if href is not None else target

    resolved = (parent / target_path).resolve()
    if case_sensitive_exists(resolved):
        return target

    rewritten = _rewrite_cross_module_target(target_path, parent, repo_root)
    return f"{rewritten}{suffix}" if rewritten is not None else target


def transform_content(
    content: str, module_name: str, parent: Path, repo_root: Path
) -> str:
    """Rewrite eligible markdown links in *content* outside fenced code blocks."""
    in_fence = False
    fence_marker = ""
    out: list[str] = []

    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            out.append(line)
            continue

        if in_fence:
            out.append(line)
            continue

        def replace(match: re.Match[str]) -> str:
            old_target = match.group(1)
            new_target = rewrite_target(old_target, module_name, parent, repo_root)
            if new_target == old_target:
                return match.group(0)
            return f"]({new_target})"

        out.append(_LINK_TARGET_RE.sub(replace, line))

    return "".join(out)


def modules_root(repo_root: Path) -> Path:
    """Return the Docusaurus module mirror root."""
    return repo_root / "src" / "codomyrmex" / "documentation" / "docs" / "modules"


def module_name_for_page(page: Path, repo_root: Path) -> str | None:
    """Return the module directory owning a mirrored page."""
    root = modules_root(repo_root)
    try:
        rel = page.relative_to(root)
    except ValueError:
        return None
    return rel.parts[0] if rel.parts else None


def iter_module_pages(repo_root: Path) -> list[Path]:
    """Return Docusaurus mirror markdown pages that may contain module links."""
    root = modules_root(repo_root)
    if not root.is_dir():
        return []
    return sorted(
        path for path in root.rglob("*.md") if module_name_for_page(path, repo_root)
    )


def main(argv: list[str] | None = None) -> int:
    """Rewrite eligible Docusaurus module markdown links in place."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check", action="store_true", help="Report drift without writing"
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    changed: list[Path] = []
    for page in iter_module_pages(repo_root):
        module_name = module_name_for_page(page, repo_root)
        if module_name is None:
            continue
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
