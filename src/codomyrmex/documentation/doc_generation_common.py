"""
Shared helpers for AGENTS.md / README.md generation.

Canonical agent doc sections (bootstrap + docs/modules enrichment):
- Title + path
- Signposting (parent, self, entry artifacts)
- Purpose (one short paragraph)
- Active Components OR Key Capabilities (single inventory — no duplicate Key Files)
- Operating Contracts
- Entry points (README, SPEC, API specs when present) — enrich adds integration URLs
- Dependencies / Development Guidelines (bootstrap) or Integration (enrich)
- Navigation
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

# Relative POSIX prefixes under repo root to skip (vendor-heavy trees; extend as needed)
EXCLUDED_DOC_PREFIXES: tuple[str, ...] = (
    "src/codomyrmex/agents/open_gauss/skills",
    "src/codomyrmex/agents/open_gauss/environments",
)


def path_matches_excluded_prefix(rel_path: Path, prefixes: tuple[str, ...]) -> bool:
    """True if rel_path equals or nests under any excluded prefix."""
    s = rel_path.as_posix()
    for p in prefixes:
        if s == p or s.startswith(f"{p}/"):
            return True
    return False


def extract_init_docstring_first_line(dir_path: Path) -> str:
    """Return first substantive line from dir_path/__init__.py module docstring, or ""."""
    init_py = dir_path / "__init__.py"
    if not init_py.is_file():
        return ""
    try:
        tree = ast.parse(init_py.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return ""
    if not tree.body or not isinstance(tree.body[0], ast.Expr):
        return ""
    val = tree.body[0].value
    if isinstance(val, ast.Constant) and isinstance(val.value, str):
        raw = val.value
    elif isinstance(val, ast.Str):  # pragma: no cover - py<3.8
        raw = val.s
    else:
        return ""
    for line in raw.strip().split("\n"):
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def humanize_slug(name: str) -> str:
    """Turn kebab/snake folder names into short readable labels."""
    cleaned = name.replace("_", " ").replace("-", " ")
    return " ".join(w.capitalize() if w else w for w in cleaned.split())


def _parse_skill_md_front_matter(raw: str) -> dict[str, str]:
    """Extract YAML-like `key: value` from first ---...--- block (minimal parser)."""
    if not raw.startswith("---"):
        return {}
    end = raw.find("\n---", 3)
    if end == -1:
        return {}
    block = raw[3:end].strip()
    out: dict[str, str] = {}
    current_key: str | None = None
    current_val: list[str] = []
    for line in block.split("\n"):
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            if current_key is not None:
                out[current_key] = " ".join(current_val).strip()
            current_key = m.group(1).lower()
            rest = m.group(2).strip()
            if rest in (">", "|"):
                current_val = []
            elif rest:
                current_val = [rest]
            else:
                current_val = []
        elif current_key and line.strip():
            current_val.append(line.strip())
    if current_key is not None:
        out[current_key] = " ".join(current_val).strip()
    return out


def extract_skill_md_purpose(dir_path: Path) -> str:
    """
    If SKILL.md exists in dir_path, return description from front matter or first body line.
    """
    skill_md = dir_path / "SKILL.md"
    if not skill_md.is_file():
        return ""
    try:
        raw = skill_md.read_text(encoding="utf-8")
    except OSError:
        return ""
    fm = _parse_skill_md_front_matter(raw)
    desc = (fm.get("description") or "").strip()
    if desc:
        return desc
    # Body after closing ---
    body = raw
    if raw.startswith("---"):
        close = raw.find("\n---", 3)
        if close != -1:
            body = raw[close + 4 :].lstrip()
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _mission_control_app_segments(rel_parts: tuple[str, ...]) -> list[str] | None:
    """Return path segments under .../mission_control/app/ or None."""
    parts = list(rel_parts)
    try:
        i = parts.index("mission_control")
    except ValueError:
        return None
    if i + 1 >= len(parts) or parts[i + 1] != "app":
        return None
    return parts[i + 2 :]


def infer_mission_control_purpose(dir_path: Path, rel_path: Path) -> str:
    """
    Purpose line for Next.js app under agents/mission_control/app/.
    """
    segs = _mission_control_app_segments(rel_path.parts)
    if segs is None:
        return ""
    route_suffix = "/".join(segs) if segs else "(root)"
    if (dir_path / "route.ts").is_file() or (dir_path / "route.js").is_file():
        scope = "API route handler" if "api" in segs else "Route Handler"
        return f"Mission Control {scope} for `{route_suffix}`."
    if (dir_path / "page.tsx").is_file() or (dir_path / "page.jsx").is_file():
        return (
            f"Mission Control App Router page `{route_suffix}` — "
            "UI route and layout entry."
        )
    if (dir_path / "layout.tsx").is_file() or (dir_path / "layout.jsx").is_file():
        return f"Mission Control App Router layout for `{route_suffix}`."
    if "api" in segs:
        return (
            f"Mission Control App Router API segment `{route_suffix}` — "
            "HTTP handlers and server logic."
        )
    return (
        f"Mission Control frontend subtree `{route_suffix}` — "
        "components, styles, or supporting modules."
    )


def nearest_python_package(start_dir: Path, stop_at: Path) -> Path | None:
    """Walk upward from start_dir inclusive; return nearest directory with __init__.py at or above stop_at."""
    cur = start_dir.resolve()
    stop_resolved = stop_at.resolve()
    while True:
        try:
            cur.relative_to(stop_resolved)
        except ValueError:
            return None
        if (cur / "__init__.py").is_file():
            return cur
        if cur == stop_resolved:
            return None
        parent = cur.parent
        if parent == cur:
            return None
        cur = parent


def infer_purpose_for_directory(dir_path: Path, repo_root: Path) -> str:
    """
    One short purpose paragraph: prefer package docstrings under src/codomyrmex,
    then path-based rules (segment-safe), then generic surface fallback.
    """
    repo_root = repo_root.resolve()
    dir_path = dir_path.resolve()
    rel_path = dir_path.relative_to(repo_root)
    parts = rel_path.parts

    if len(parts) == 1:
        surface = parts[0]
        purposes = {
            "src": "Hosts core source code and agent-enabled services for the Codomyrmex platform.",
            "scripts": "Maintenance and automation utilities for project management.",
            "docs": "Documentation components and guides for the Codomyrmex platform.",
            "config": "Configuration templates and examples.",
            "testing": "Test suites and validation for the Codomyrmex platform.",
            "projects": "Project workspace and templates.",
            "cursorrules": "Coding standards and automation rules.",
            "examples": "Example implementations and demonstrations.",
        }
        return purposes.get(
            surface, f"Contains {surface} components for the Codomyrmex platform."
        )

    # Segment-based (avoid false positives from substrings like "doc" in "mydocument")
    if parts[0] == "docs" and len(parts) > 1 and parts[1] == "modules" and len(parts) > 2:
        mod = parts[2]
        return (
            f"Published documentation mirror for the `{mod}` module "
            f"(see `src/codomyrmex/{mod}/` for source)."
        )
    if parts[0] == "docs":
        return "Documentation files and guides for the Codomyrmex platform."
    if "tests" in parts:
        return "Test files and validation suites."
    if parts[0] == "examples" or "examples" in parts:
        return "Example implementations and demonstrations."
    if parts[0] == "scripts":
        return "Automation and utility scripts for repository maintenance."
    if parts[0] == "config":
        return "Configuration files and templates."

    mc_purpose = infer_mission_control_purpose(dir_path, rel_path)
    if mc_purpose:
        return mc_purpose

    skill_line = extract_skill_md_purpose(dir_path)
    if skill_line:
        return skill_line

    if (
        parts[0] == "src"
        and "skills" in parts
        and "upstream" in parts
        and len(parts) >= 5
    ):
        leaf = parts[-1]
        return (
            f"Upstream skill mirror folder `{leaf}` — {humanize_slug(leaf)} "
            "(child folders may include SKILL.md)."
        )

    codom_root = repo_root / "src" / "codomyrmex"
    try:
        dir_path.relative_to(codom_root)
    except ValueError:
        pass
    else:
        pkg = nearest_python_package(dir_path, codom_root)
        if pkg is not None:
            line = extract_init_docstring_first_line(pkg)
            if line:
                if dir_path == pkg:
                    return line
                # Subdirectory under a package: qualify with folder name
                sub = dir_path.relative_to(pkg)
                sub_s = "/".join(sub.parts) if sub.parts else ""
                if sub_s:
                    return f"{line} — subdirectory `{sub_s}`."
                return line

    rel_s = rel_path.as_posix()
    return (
        f"Repository subtree `{rel_s}` — files and directories under the "
        f"`{parts[0]}` surface."
    )


def describe_inventory_item(item: str) -> str:
    """Short description for an immediate child name in Active Components."""
    if item.endswith("/"):
        name = item.rstrip("/")
        return f"Directory `{name}/`"
    lower = item.lower()
    if lower.endswith(".py"):
        return f"Python source `{item}`"
    if lower.endswith(".md"):
        return f"Markdown `{item}`"
    if lower.endswith((".yaml", ".yml", ".json", ".toml")):
        return f"Config/data `{item}`"
    return f"File `{item}`"


def describe_inventory_item_for_directory(
    dir_path: Path, repo_root: Path, item: str
) -> str:
    """Like describe_inventory_item but adds Mission Control / Next.js-specific labels."""
    rel_path = dir_path.relative_to(repo_root)
    segs = _mission_control_app_segments(rel_path.parts)
    if segs is not None:
        if item.endswith("/"):
            name = item.rstrip("/")
            return f"App route segment `{name}/`"
        lower = item.lower()
        if lower in ("route.ts", "route.js"):
            return f"Next.js Route Handler `{item}`"
        if lower in ("page.tsx", "page.jsx"):
            return f"App Router page `{item}`"
        if lower in ("layout.tsx", "layout.jsx"):
            return f"App Router layout `{item}`"
        if lower.endswith((".tsx", ".ts")):
            return f"TypeScript or React module `{item}`"
    return describe_inventory_item(item)


def relative_link_to_repo_file(from_dir: Path, repo_root: Path, filename: str) -> str:
    """POSIX relative path from from_dir to repo_root/filename."""
    target = (repo_root / filename).resolve()
    return Path(os.path.relpath(target, from_dir.resolve())).as_posix()


def format_signpost_block(rel_path: Path, dir_path: Path, repo_root: Path) -> str:
    """Markdown Signposting section for bootstrapped AGENTS.md."""
    rel_s = rel_path.as_posix()
    agents_href = relative_link_to_repo_file(dir_path, repo_root, "AGENTS.md")
    lines = [
        "## Signposting",
        "",
        f"- **Path**: `{rel_s}`",
        "- **Human overview**: [README.md](README.md)",
    ]
    if (dir_path / "SPEC.md").is_file():
        lines.append("- **Functional spec**: [SPEC.md](SPEC.md)")
    if (dir_path / "API_SPECIFICATION.md").is_file():
        lines.append("- **API spec**: [API_SPECIFICATION.md](API_SPECIFICATION.md)")
    lines.append(
        f"- **Agent coordination** (repo root): [{agents_href}]({agents_href})"
    )
    lines.append("")
    return "\n".join(lines)
