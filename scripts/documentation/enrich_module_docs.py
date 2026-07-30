#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Enrich module documentation by reading source code structure.

Reads each src/codomyrmex/<module>/ directory and generates enriched
README.md, AGENTS.md, and SPEC.md files in docs/modules/<module>/.

This command is deliberately fail-closed: use ``--dry-run`` to inspect a
change plan and ``--apply`` to write it. Existing hand-authored files are
preserved unless a matching ``--force-*`` option is supplied, and curated
README/AGENTS markers are never overwritten.
"""

import argparse
import ast
import logging
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "codomyrmex"
DOCS_ROOT = REPO_ROOT / "docs" / "modules"

CURATED_MARKERS = {
    "README.md": "<!-- readme: curated -->",
    "AGENTS.md": "<!-- agents: curated -->",
}
GENERATED_MARKERS = {
    "README.md": "<!-- readme: generated -->",
    "AGENTS.md": "<!-- agents: generated -->",
    "SPEC.md": "<!-- spec: generated -->",
}

# Human-readable display names for modules
DISPLAY_NAMES = {
    "accessibility": "Accessibility",
    "agentic_memory": "Agentic Memory",
    "agents": "AI Agents",
    "api": "API",
    "audio": "Audio Processing",
    "auth": "Authentication",
    "build_synthesis": "Build Synthesis",
    "cache": "Cache",
    "cerebrum": "Cerebrum",
    "chaos_engineering": "Chaos Engineering",
    "ci_cd_automation": "CI/CD Automation",
    "cli": "CLI",
    "cloud": "Cloud",
    "coding": "Coding",
    "collaboration": "Collaboration",
    "compression": "Compression",
    "concurrency": "Concurrency",
    "config_management": "Config Management",
    "containerization": "Containerization",
    "cost_management": "Cost Management",
    "dark": "Dark",
    "data_lineage": "Data Lineage",
    "data_visualization": "Data Visualization",
    "database_management": "Database Management",
    "defense": "Defense",
    "deployment": "Deployment",
    "documentation": "Documentation",
    "documents": "Documents",
    "edge_computing": "Edge Computing",
    "embodiment": "Embodiment",
    "encryption": "Encryption",
    "environment_setup": "Environment Setup",
    "events": "Events",
    "evolutionary_ai": "Evolutionary AI",
    "examples": "Examples",
    "feature_flags": "Feature Flags",
    "feature_store": "Feature Store",
    "fpf": "FPF (Filesystem Processing Framework)",
    "git_operations": "Git Operations",
    "graph_rag": "Graph RAG",
    "i18n": "Internationalization (i18n)",
    "ide": "IDE Integration",
    "identity": "Identity",
    "inference_optimization": "Inference Optimization",
    "llm": "LLM",
    "logging_monitoring": "Logging & Monitoring",
    "logistics": "Logistics",
    "market": "Market",
    "metrics": "Metrics",
    "migration": "Migration",
    "model_context_protocol": "Model Context Protocol",
    "model_ops": "Model Ops",
    "model_registry": "Model Registry",
    "module_template": "Module Template",
    "multimodal": "Multimodal",
    "networking": "Networking",
    "notification": "Notification",
    "observability_dashboard": "Observability Dashboard",
    "orchestrator": "Orchestrator",
    "pattern_matching": "Pattern Matching",
    "performance": "Performance",
    "physical_management": "Physical Management",
    "plugin_system": "Plugin System",
    "privacy": "Privacy",
    "prompt_testing": "Prompt Testing",
    "quantum": "Quantum",
    "rate_limiting": "Rate Limiting",
    "scheduler": "Scheduler",
    "scrape": "Scrape",
    "search": "Search",
    "security": "Security",
    "serialization": "Serialization",
    "service_mesh": "Service Mesh",
    "skills": "Skills",
    "smart_contracts": "Smart Contracts",
    "spatial": "Spatial",
    "static_analysis": "Static Analysis",
    "streaming": "Streaming",
    "system_discovery": "System Discovery",
    "telemetry": "Telemetry",
    "templating": "Templating",
    "terminal_interface": "Terminal Interface",
    "testing": "Testing",
    "tests": "Tests",
    "tools": "Tools",
    "tree_sitter": "Tree-sitter",
    "utils": "Utilities",
    "validation": "Validation",
    "vector_store": "Vector Store",
    "video": "Video",
    "wallet": "Wallet",
    "website": "Website",
    "workflow_testing": "Workflow Testing",
}


def extract_module_info(module_dir: Path) -> dict[str, Any]:
    """Extract information from a source module directory."""
    info: dict[str, Any] = {
        "name": module_dir.name,
        "display_name": DISPLAY_NAMES.get(
            module_dir.name, module_dir.name.replace("_", " ").title()
        ),
        "docstring": "",
        "classes": [],
        "functions": [],
        "submodules": [],
        "py_files": [],
        "has_tests": False,
        "version": "",
    }

    init_file = module_dir / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        try:
            tree = ast.parse(content)
            # Extract module docstring
            if (
                tree.body
                and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)
            ):
                info["docstring"] = tree.body[0].value.value.strip()

            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    doc = ast.get_docstring(node) or ""
                    info["classes"].append(
                        {
                            "name": node.name,
                            "doc": doc.split("\n")[0] if doc else "",
                        }
                    )
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):
                        doc = ast.get_docstring(node) or ""
                        info["functions"].append(
                            {
                                "name": node.name,
                                "doc": doc.split("\n")[0] if doc else "",
                            }
                        )

            # Extract version
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__version__":
                            if isinstance(node.value, ast.Constant):
                                info["version"] = str(node.value.value)

        except SyntaxError as e:
            logger.debug("Syntax error parsing __init__.py: %s", e)

    # Find submodules (subdirectories with __init__.py)
    for child in sorted(module_dir.iterdir()):
        if child.is_dir() and (child / "__init__.py").exists():
            sub_doc = ""
            sub_init = child / "__init__.py"
            try:
                sub_tree = ast.parse(sub_init.read_text())
                if (
                    sub_tree.body
                    and isinstance(sub_tree.body[0], ast.Expr)
                    and isinstance(sub_tree.body[0].value, ast.Constant)
                    and isinstance(sub_tree.body[0].value.value, str)
                ):
                    sub_doc = sub_tree.body[0].value.value.strip().split("\n")[0]
            except (SyntaxError, Exception) as e:
                logger.debug(
                    "Could not parse submodule __init__.py for %s: %s", child.name, e
                )
            info["submodules"].append({"name": child.name, "doc": sub_doc})

    # Find all .py files
    for py_file in sorted(module_dir.glob("*.py")):
        if py_file.name != "__init__.py":
            info["py_files"].append(py_file.name)

    return info


def get_module_description(info: dict) -> str:
    """Get a one-line description from the docstring."""
    ds = info["docstring"]
    if ds:
        # Get the first non-empty line after the title
        lines = ds.split("\n")
        for line in lines:
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("Submodule")
                and stripped != info["display_name"]
                and stripped != info["name"]
            ):
                # Skip title-like lines
                if stripped.lower().replace("_", " ") == info["name"].replace("_", " "):
                    continue
                if stripped.endswith(("Module", "module")):
                    continue
                return stripped
    return f"Provides {info['display_name'].lower()} functionality for the Codomyrmex ecosystem."


def generate_readme(info: dict, docs_root: Path = DOCS_ROOT) -> str:
    """Generate enriched README.md content."""
    desc = get_module_description(info)

    lines = [
        GENERATED_MARKERS["README.md"],
        "",
        f"# {info['display_name']} Module Documentation",
        "",
        f"**Package version**: v{info['version']} | **Status**: Generated reference",
        "",
        "## Overview",
        "",
        f"{desc}",
        "",
    ]

    # Key Features
    features = []
    for cls in info["classes"][:6]:
        if cls["doc"]:
            features.append(f"- **{cls['name']}** — {cls['doc']}")
        else:
            features.append(f"- **{cls['name']}** — {cls['name'].replace('_', ' ')}")
    for fn in info["functions"][:4]:
        if fn["doc"]:
            features.append(f"- `{fn['name']}()` — {fn['doc']}")
        else:
            features.append(f"- `{fn['name']}()` — {fn['name'].replace('_', ' ')}")

    if features:
        lines.append("## Key Features")
        lines.append("")
        lines.extend(features)
        lines.append("")

    # Submodules
    if info["submodules"]:
        lines.append("## Submodules")
        lines.append("")
        lines.append("| Submodule | Description |")
        lines.append("|-----------|-------------|")
        for sub in info["submodules"]:
            doc = sub["doc"] or sub["name"].replace("_", " ").title()
            lines.append(f"| `{sub['name']}` | {doc} |")
        lines.append("")

    # Quick Start
    lines.append("## Quick Start")
    lines.append("")
    lines.append("```python")
    lines.append(f"import codomyrmex.{info['name']} as {info['name']}")
    lines.append("")
    lines.append(f"print({info['name']}.__all__)  # Authoritative public exports")
    lines.append("```")
    lines.append("")

    # API Reference (if enough classes/functions)
    if len(info["classes"]) > 2 or len(info["functions"]) > 2:
        lines.append("## API Reference")
        lines.append("")
        if info["classes"]:
            lines.append("### Classes")
            lines.append("")
            lines.append("| Class | Description |")
            lines.append("|-------|-------------|")
            for cls in info["classes"]:
                doc = cls["doc"] or cls["name"].replace("_", " ")
                lines.append(f"| `{cls['name']}` | {doc} |")
            lines.append("")
        if info["functions"]:
            lines.append("### Functions")
            lines.append("")
            lines.append("| Function | Description |")
            lines.append("|----------|-------------|")
            for fn in info["functions"]:
                doc = fn["doc"] or fn["name"].replace("_", " ")
                lines.append(f"| `{fn['name']}()` | {doc} |")
            lines.append("")

    # Directory Contents
    lines.append("## Directory Contents")
    lines.append("")
    lines.append("| File | Description |")
    lines.append("|------|-------------|")
    lines.append("| `README.md` | This documentation |")
    lines.append("| `AGENTS.md` | Agent coordination guide |")
    lines.append("| `SPEC.md` | Technical specification |")

    # Check for extra files in docs dir
    docs_dir = docs_root / info["name"]
    if docs_dir.exists():
        for child in sorted(docs_dir.iterdir()):
            if child.is_dir():
                lines.append(
                    f"| `{child.name}/` | {child.name.replace('_', ' ').title()} |"
                )
    lines.append("")

    # Navigation
    lines.append("## Navigation")
    lines.append("")
    lines.append(
        f"- **Source**: [src/codomyrmex/{info['name']}/](../../../src/codomyrmex/{info['name']}/)"
    )
    lines.append("- **Parent**: [Modules](../README.md)")
    lines.append("")

    return "\n".join(lines)


def generate_agents(info: dict) -> str:
    """Generate enriched AGENTS.md content."""
    desc = get_module_description(info)

    lines = [
        GENERATED_MARKERS["AGENTS.md"],
        "",
        f"# {info['display_name']} Module — Agent Coordination",
        "",
        "## Purpose",
        "",
        f"{desc}",
        "",
        "## Key Capabilities",
        "",
    ]

    # Capabilities from classes + functions
    caps = []
    for cls in info["classes"][:5]:
        doc = cls["doc"] or cls["name"].replace("_", " ")
        caps.append(f"- **{cls['name']}**: {doc}")
    for fn in info["functions"][:3]:
        doc = fn["doc"] or fn["name"].replace("_", " ")
        caps.append(f"- `{fn['name']}()`: {doc}")

    if caps:
        lines.extend(caps)
    else:
        lines.append(f"- {info['display_name']} operations and management")
    lines.append("")

    # Agent Usage
    lines.append("## Agent Usage Patterns")
    lines.append("")
    lines.append("```python")
    lines.append(f"import codomyrmex.{info['name']} as {info['name']}")
    lines.append("")
    lines.append(f"print({info['name']}.__all__)  # Inspect supported public exports")
    lines.append("```")
    lines.append("")

    # Integration
    lines.append("## Integration Points")
    lines.append("")
    lines.append(
        f"- **Source**: [src/codomyrmex/{info['name']}/](../../../src/codomyrmex/{info['name']}/)"
    )
    lines.append("- **Docs**: [Module Documentation](README.md)")
    lines.append("- **Spec**: [Technical Specification](SPEC.md)")
    lines.append("")

    return "\n".join(lines)


def generate_spec(info: dict) -> str:
    """Generate enriched SPEC.md content."""
    desc = get_module_description(info)

    lines = [
        GENERATED_MARKERS["SPEC.md"],
        "",
        f"# {info['display_name']} — Functional Specification",
        "",
        f"**Module**: `codomyrmex.{info['name']}`  ",
        f"**Version**: v{info['version']}  ",
        "**Status**: Active",
        "",
        "## 1. Overview",
        "",
        f"{desc}",
        "",
        "## 2. Architecture",
        "",
    ]

    # Architecture table
    if info["classes"] or info["py_files"]:
        lines.append("### Components")
        lines.append("")
        lines.append("| Component | Type | Description |")
        lines.append("|-----------|------|-------------|")
        for cls in info["classes"][:10]:
            doc = cls["doc"] or cls["name"].replace("_", " ")
            lines.append(f"| `{cls['name']}` | Class | {doc} |")
        for fn in info["functions"][:5]:
            doc = fn["doc"] or fn["name"].replace("_", " ")
            lines.append(f"| `{fn['name']}()` | Function | {doc} |")
        lines.append("")

    # Submodules
    if info["submodules"]:
        lines.append("### Submodule Structure")
        lines.append("")
        for sub in info["submodules"]:
            doc = sub["doc"] or sub["name"].replace("_", " ").title()
            lines.append(f"- `{sub['name']}/` — {doc}")
        lines.append("")

    # Source files
    if info["py_files"]:
        lines.append("### Source Files")
        lines.append("")
        for f in info["py_files"][:10]:
            lines.append(f"- `{f}`")
        if len(info["py_files"]) > 10:
            lines.append(f"- ...and {len(info['py_files']) - 10} more")
        lines.append("")

    # Dependencies
    lines.append("## 3. Dependencies")
    lines.append("")
    lines.append(
        f"See `src/codomyrmex/{info['name']}/__init__.py` for import dependencies."
    )
    lines.append("")

    # API
    lines.append("## 4. Public API")
    lines.append("")
    if info["classes"]:
        imports = ", ".join(c["name"] for c in info["classes"][:5])
        lines.append("```python")
        lines.append(f"from codomyrmex.{info['name']} import {imports}")
        lines.append("```")
    elif info["functions"]:
        imports = ", ".join(f["name"] for f in info["functions"][:5])
        lines.append("```python")
        lines.append(f"from codomyrmex.{info['name']} import {imports}")
        lines.append("```")
    else:
        lines.append("See source module for available exports.")
    lines.append("")

    # Testing
    lines.append("## 5. Testing")
    lines.append("")
    lines.append("```bash")
    lines.append(f"uv run python -m pytest tests/ -k {info['name']} -v")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def should_enrich(
    module_name: str,
    doc_file: Path,
    info: dict,
    *,
    force: bool = False,
) -> bool:
    """Return whether a documentation file may be regenerated safely.

    Missing files and files carrying an explicit generated marker are safe to
    refresh. Other existing files require a matching force flag. Curated
    README/AGENTS files remain protected even under force.
    """
    if not doc_file.exists():
        return True
    head = doc_file.read_text(encoding="utf-8", errors="replace")[:800]
    curated_marker = CURATED_MARKERS.get(doc_file.name)
    if curated_marker and curated_marker in head:
        return False
    generated_marker = GENERATED_MARKERS.get(doc_file.name)
    return bool(force or (generated_marker and generated_marker in head))


def package_version(repo_root: Path) -> str:
    """Read the repository package version from pyproject.toml."""
    pyproject = repo_root / "pyproject.toml"
    with pyproject.open("rb") as handle:
        data = tomllib.load(handle)
    version = data.get("project", {}).get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"Missing [project].version in {pyproject}")
    return version.strip()


def enrich_modules(
    repo_root: Path,
    *,
    apply_changes: bool,
    module_names: Sequence[str] = (),
    force_readmes: bool = False,
    force_agents: bool = False,
    force_specs: bool = False,
) -> dict[str, Any]:
    """Plan or apply source-derived module documentation changes."""
    repo_root = repo_root.resolve()
    src_root = repo_root / "src" / "codomyrmex"
    docs_root = repo_root / "docs" / "modules"
    if not src_root.is_dir() or not docs_root.is_dir():
        raise ValueError(f"Expected src/codomyrmex and docs/modules under {repo_root}")

    version = package_version(repo_root)
    enriched_count = 0
    skipped_count = 0
    planned: list[str] = []
    available_modules = sorted(
        [
            d.name
            for d in src_root.iterdir()
            if d.is_dir() and d.name != "__pycache__" and (d / "__init__.py").exists()
        ]
    )
    requested = sorted(set(module_names))
    unknown = sorted(set(requested) - set(available_modules))
    if unknown:
        raise ValueError(f"Unknown source module(s): {', '.join(unknown)}")
    modules = requested or available_modules

    print(f"Found {len(available_modules)} source modules; selected {len(modules)}")

    for mod_name in modules:
        src_dir = src_root / mod_name
        docs_dir = docs_root / mod_name

        if not docs_dir.exists():
            print(f"  ⚠️ No docs dir for {mod_name}, skipping")
            continue

        info = extract_module_info(src_dir)
        info["version"] = version

        candidates = (
            (
                docs_dir / "README.md",
                generate_readme(info, docs_root),
                force_readmes,
            ),
            (docs_dir / "AGENTS.md", generate_agents(info), force_agents),
            (docs_dir / "SPEC.md", generate_spec(info), force_specs),
        )
        for path, content, force in candidates:
            if not should_enrich(mod_name, path, info, force=force):
                skipped_count += 1
                continue
            relative = path.relative_to(repo_root).as_posix()
            planned.append(relative)
            enriched_count += 1
            action = "Enriched" if apply_changes else "Would enrich"
            if apply_changes:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content + "\n", encoding="utf-8")
            print(f"  {'✅' if apply_changes else '•'} {action} {relative}")

    print(f"\n{'=' * 50}")
    print(f"{'✅ Enriched' if apply_changes else 'Planned'}: {enriched_count} files")
    print(f"⏭️ Skipped (already rich): {skipped_count} files")
    print(f"📊 Total processed: {enriched_count + skipped_count} files")
    return {
        "applied": apply_changes,
        "planned": planned,
        "planned_count": enriched_count,
        "skipped_count": skipped_count,
        "selected_module_count": len(modules),
        "source_module_count": len(available_modules),
    }


def build_parser() -> argparse.ArgumentParser:
    """Construct the fail-closed command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Plan or apply source-derived docs/modules README, AGENTS, and SPEC "
            "updates. Existing curated README/AGENTS files are always preserved."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: inferred from this script)",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the exact change plan without writing files",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Write the reviewed change plan",
    )
    parser.add_argument(
        "--module",
        action="append",
        default=[],
        help="Limit work to one module; repeat for multiple modules",
    )
    parser.add_argument(
        "--force-readmes",
        action="store_true",
        help="Regenerate non-curated README.md files even without a generated marker",
    )
    parser.add_argument(
        "--force-agents",
        action="store_true",
        help="Regenerate non-curated AGENTS.md files even without a generated marker",
    )
    parser.add_argument(
        "--force-specs",
        action="store_true",
        help="Regenerate SPEC.md files even without a generated marker",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the module documentation enrichment CLI."""
    args = build_parser().parse_args(argv)
    try:
        enrich_modules(
            args.repo_root,
            apply_changes=args.apply,
            module_names=args.module,
            force_readmes=args.force_readmes,
            force_agents=args.force_agents,
            force_specs=args.force_specs,
        )
    except ValueError as exc:
        print(f"error: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
