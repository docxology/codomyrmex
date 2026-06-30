#!/usr/bin/env python3
"""Compile the codomyrmex manuscript from output/manuscript/ to HTML and PDF.

Usage:
    uv run python scripts/compile_manuscript.py           # HTML only (fast)
    uv run python scripts/compile_manuscript.py --pdf     # HTML + PDF
    uv run python scripts/compile_manuscript.py --check   # verify tokens resolved
    uv run python scripts/compile_manuscript.py --bookends  # include transmission bookends (PDF only)

Workflow:
    1. Run z_generate_manuscript_variables.py to inject tokens
    2. Verify no {{TOKEN}} remain in output/manuscript/*.md
    3. Collect sections 00_abstract through 99_references in lexicographic order
       (skips 00_00_transmission_begin.md and 99_zz_transmission_end.md by default —
       those are PDF-only bookends with pending DOI/QR placeholders)
    4. Run pandoc to produce output/paper.html (always) and output/paper.pdf (--pdf flag)

Bookend files (00_00 / 99_zz) contain:
    - LaTeX raw blocks (```{=latex} ... ```)
    - References to ../figures/transmission_*.png that may not exist
    - Pending DOI / SHA-256 placeholders
    They are excluded by default and only included when --bookends is passed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MANUSCRIPT_SECTIONS_GLOB = "[0-9]*.md"
BOOKEND_NAMES = {"00_00_transmission_begin.md", "99_zz_transmission_end.md"}
TOKEN_PATTERN = re.compile(r"\{\{[A-Z_]+\}\}")

PAPER_TITLE = "Codomyrmex: An Artificial Ecology for Agentic Software Development"


def _find_project_root() -> Path:
    """Walk up from this script's location to the project root (contains pyproject.toml)."""
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


def _load_variables(project_root: Path) -> dict[str, str]:
    """Load manuscript_variables.json; return empty dict on failure."""
    json_path = project_root / "output" / "data" / "manuscript_variables.json"
    if not json_path.exists():
        return {}
    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _run_generate_variables(project_root: Path) -> bool:
    """Run z_generate_manuscript_variables.py; return True on success."""
    script = project_root / "scripts" / "z_generate_manuscript_variables.py"
    if not script.exists():
        print(f"  WARNING: {script.relative_to(project_root)} not found — skipping variable generation")
        return False
    print("Generating manuscript variables...")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(project_root),
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"  WARNING: z_generate_manuscript_variables.py exited with code {result.returncode}")
        return False
    return True


def _collect_sections(manuscript_dir: Path, include_bookends: bool = False) -> list[Path]:
    """Return section .md files in lexicographic order, excluding bookends unless requested."""
    files = sorted(manuscript_dir.glob(MANUSCRIPT_SECTIONS_GLOB))
    if not include_bookends:
        files = [f for f in files if f.name not in BOOKEND_NAMES]
    return files


def _check_unresolved_tokens(sections: list[Path]) -> list[tuple[Path, list[str]]]:
    """Return list of (file, [token, ...]) for any unresolved {{TOKEN}} patterns.

    Ignores tokens that appear inside backtick-quoted spans (prose examples).
    """
    findings: list[tuple[Path, list[str]]] = []
    for path in sections:
        text = path.read_text(encoding="utf-8")
        # Strip backtick-quoted inline code to avoid false positives from prose examples
        stripped = re.sub(r"`[^`]*`", "", text)
        tokens = TOKEN_PATTERN.findall(stripped)
        if tokens:
            findings.append((path, tokens))
    return findings


def _build_pandoc_metadata_args(variables: dict[str, str]) -> list[str]:
    """Construct -M key=value args from manuscript_variables.json."""
    title = PAPER_TITLE
    author = variables.get("CONFIG_FIRST_AUTHOR", "The Codomyrmex Contributors")
    version = variables.get("CONFIG_VERSION", "")
    keywords = variables.get("CONFIG_KEYWORDS", "")
    timestamp = variables.get("GENERATION_TIMESTAMP", "")
    # Use just the date portion of the ISO timestamp
    date = timestamp[:10] if timestamp else ""

    args: list[str] = [
        "-M", f"title={title}",
        "-M", f"author={author}",
    ]
    if date:
        args += ["-M", f"date={date}"]
    if version:
        args += ["-M", f"version={version}"]
    if keywords:
        args += ["-M", f"keywords={keywords}"]
    args += ["-M", "lang=en"]
    return args


def _run_pandoc_html(
    sections: list[Path],
    output_path: Path,
    bibliography: Path,
    variables: dict[str, str],
    project_root: Path,
) -> bool:
    """Run pandoc to produce HTML output; return True on success."""
    if not shutil.which("pandoc"):
        print("ERROR: pandoc not found on PATH. Install pandoc and retry.", file=sys.stderr)
        return False

    print(f"Compiling HTML → {output_path.relative_to(project_root)} ...")

    cmd: list[str] = ["pandoc"]
    cmd += [str(s) for s in sections]
    # pandoc-crossref MUST come before --citeproc so @fig:, @sec:, @eq: labels
    # are resolved before citeproc sees the remaining citation keys.
    if shutil.which("pandoc-crossref"):
        cmd += ["-F", "pandoc-crossref"]
    else:
        print("  NOTE: pandoc-crossref not found — cross-references will be unresolved")
    cmd += [
        "--standalone",
        "--toc",
        "--toc-depth=3",
        "--citeproc",
        "--from", "markdown+yaml_metadata_block",
        "--bibliography", str(bibliography),
    ]
    cmd += _build_pandoc_metadata_args(variables)
    cmd += ["-o", str(output_path)]

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: pandoc HTML compilation failed (exit {result.returncode})", file=sys.stderr)
        return False
    print(f"  HTML written: {output_path.relative_to(project_root)}")
    return True


def _run_pandoc_pdf(
    sections: list[Path],
    output_path: Path,
    bibliography: Path,
    preamble: Path | None,
    variables: dict[str, str],
    project_root: Path,
) -> bool:
    """Run pandoc to produce PDF output; return True on success."""
    if not shutil.which("pandoc"):
        print("ERROR: pandoc not found on PATH. Install pandoc and retry.", file=sys.stderr)
        return False

    print(f"Compiling PDF → {output_path.relative_to(project_root)} ...")

    cmd: list[str] = ["pandoc"]
    cmd += [str(s) for s in sections]
    # pandoc-crossref MUST come before --citeproc so @fig:, @sec:, @eq: labels
    # are resolved before citeproc sees the remaining citation keys.
    if shutil.which("pandoc-crossref"):
        cmd += ["-F", "pandoc-crossref"]
    else:
        print("  NOTE: pandoc-crossref not found — cross-references will be unresolved")
    cmd += [
        "--standalone",
        "--toc",
        "--toc-depth=3",
        "--citeproc",
        "--from", "markdown+yaml_metadata_block",
        "--bibliography", str(bibliography),
        "--pdf-engine=xelatex",
    ]
    if preamble and preamble.exists():
        cmd += ["-H", str(preamble)]
    cmd += _build_pandoc_metadata_args(variables)
    cmd += ["-o", str(output_path)]

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: pandoc PDF compilation failed (exit {result.returncode})", file=sys.stderr)
        return False
    print(f"  PDF written: {output_path.relative_to(project_root)}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile the codomyrmex manuscript to HTML (and optionally PDF)."
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also produce output/paper.pdf via xelatex",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for unresolved {{TOKEN}} patterns and exit (exit 1 if any found)",
    )
    parser.add_argument(
        "--bookends",
        action="store_true",
        help=(
            "Include transmission bookend pages (00_00 / 99_zz). "
            "These contain LaTeX-only content and pending DOI placeholders — "
            "only useful for a full PDF production run."
        ),
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Skip running z_generate_manuscript_variables.py (use existing output/manuscript/)",
    )
    args = parser.parse_args()

    project_root = _find_project_root()

    # Step 1: Regenerate tokens unless skipped
    if not args.skip_generate:
        _run_generate_variables(project_root)
    else:
        print("Skipping variable generation (--skip-generate).")

    # Step 2: Locate manuscript files
    manuscript_dir = project_root / "output" / "manuscript"
    if not manuscript_dir.exists():
        print(f"ERROR: output/manuscript/ does not exist: {manuscript_dir}", file=sys.stderr)
        print("  Run without --skip-generate to generate manuscript files first.", file=sys.stderr)
        return 1

    sections = _collect_sections(manuscript_dir, include_bookends=args.bookends)
    if not sections:
        print("ERROR: no section files found in output/manuscript/", file=sys.stderr)
        return 1

    print(f"Sections ({len(sections)}):")
    for s in sections:
        print(f"  {s.name}")

    # Step 3: Check for unresolved tokens
    print("Checking for unresolved {{TOKEN}} patterns...")
    token_findings = _check_unresolved_tokens(sections)
    if token_findings:
        print("UNRESOLVED TOKENS FOUND:", file=sys.stderr)
        for path, tokens in token_findings:
            print(f"  {path.name}: {', '.join(sorted(set(tokens)))}", file=sys.stderr)
        if args.check:
            return 1
        print("  WARNING: proceeding with unresolved tokens in output.")
    else:
        print("  No unresolved tokens found.")

    if args.check:
        print("--check passed: no unresolved tokens.")
        return 0

    # Locate supporting files
    bibliography = manuscript_dir / "references.bib"
    if not bibliography.exists():
        print(f"ERROR: references.bib not found at {bibliography}", file=sys.stderr)
        return 1

    preamble = manuscript_dir / "preamble.md"  # LaTeX header inclusions

    # Ensure output directory exists
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load variables for metadata
    variables = _load_variables(project_root)

    # Step 4: Compile HTML
    html_out = output_dir / "paper.html"
    html_ok = _run_pandoc_html(
        sections=sections,
        output_path=html_out,
        bibliography=bibliography,
        variables=variables,
        project_root=project_root,
    )
    if not html_ok:
        return 1

    # Step 5: Optionally compile PDF
    if args.pdf:
        pdf_out = output_dir / "paper.pdf"
        pdf_ok = _run_pandoc_pdf(
            sections=sections,
            output_path=pdf_out,
            bibliography=bibliography,
            preamble=preamble,
            variables=variables,
            project_root=project_root,
        )
        if not pdf_ok:
            return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
