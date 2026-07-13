#!/usr/bin/env python3
"""Compile the codomyrmex manuscript from output/manuscript/ to HTML and PDF.

Usage:
    uv run python scripts/compile_manuscript.py           # HTML only (fast)
    uv run python scripts/compile_manuscript.py --pdf     # HTML + PDF
    uv run python scripts/compile_manuscript.py --check   # verify tokens resolved
    uv run python scripts/compile_manuscript.py --bookends  # include transmission bookends (PDF only)

Workflow:
    1. Run z_generate_manuscript_variables.py to inject tokens
    2. Generate output/manuscript/00_01_contents.md after the cover page
    3. Verify no {{TOKEN}} remain in output/manuscript/*.md
    4. Collect sections in the declared scientific narrative order
       (skips 00_00_transmission_begin.md and 99_zz_transmission_end.md by default —
       those are PDF-only bookends with pending DOI/QR placeholders)
    5. Run pandoc with pandoc-crossref and citeproc to produce output/paper.html
       (always) and output/paper.pdf (--pdf flag)

Bookend files (00_00 / 99_zz) contain:
    - LaTeX raw blocks (```{=latex} ... ```)
    - References to ../figures/transmission_*.png that may not exist
    - Pending DOI / SHA-256 placeholders
    They are excluded by default and only included when --bookends is passed.
"""

# SIZE_OK: Renderer orchestration stays single-file for artifact auditability.

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MANUSCRIPT_SECTIONS_GLOB = "[0-9]*.md"
BOOKEND_NAMES = {"00_00_transmission_begin.md", "99_zz_transmission_end.md"}
GENERATED_CONTENTS_NAME = "00_01_contents.md"
COVER_NAME = "00_00_cover.md"
MANUSCRIPT_SECTION_ORDER = (
    "00_00_transmission_begin.md",
    COVER_NAME,
    "00_abstract.md",
    "01_introduction.md",
    "02_theory.md",
    "02_methodology.md",
    "05_experimental_setup.md",
    "03_results.md",
    "07_scope_and_related_work.md",
    "08_active_inference.md",
    "06_reproducibility.md",
    "04_conclusion.md",
    "90_appendix_design_rationale.md",
    "98_acknowledgements.md",
    "99_references.md",
    "99_zz_transmission_end.md",
)
TOKEN_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
HEADING_PATTERN = re.compile(
    r"^(?P<level>#{1,3})\s+(?P<title>.+?)(?:\s+\{(?P<attrs>[^}]*)\})?\s*$"
)

def _find_project_root() -> Path:
    """Walk up from this script's location to the project root (contains pyproject.toml)."""
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return here.parent


def _extract_latex_from_preamble(preamble_md: Path) -> str:
    """Extract the raw LaTeX inside a ```latex ... ``` fence from preamble.md.

    The preamble.md file is a Markdown document that contains prose plus one
    fenced code block marked ```latex. Only that block's contents should be
    passed verbatim to xelatex via pandoc -H; the surrounding Markdown would
    cause LaTeX to choke on bare # characters from headings.
    """
    text = preamble_md.read_text(encoding="utf-8")
    match = re.search(r"```latex\s*\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1)
    return ""


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
        print(
            f"  WARNING: {script.relative_to(project_root)} not found — skipping variable generation"
        )
        return False
    print("Generating manuscript variables...")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(project_root),
        capture_output=False,
    )
    if result.returncode != 0:
        print(
            f"  WARNING: z_generate_manuscript_variables.py exited with code {result.returncode}"
        )
        return False
    return True


def _collect_sections(
    manuscript_dir: Path, include_bookends: bool = False
) -> list[Path]:
    """Return sections in declared narrative order, then any unknown numbered files."""
    files = list(manuscript_dir.glob(MANUSCRIPT_SECTIONS_GLOB))
    files = [f for f in files if f.name != GENERATED_CONTENTS_NAME]
    if not include_bookends:
        files = [f for f in files if f.name not in BOOKEND_NAMES]
    rank = {name: index for index, name in enumerate(MANUSCRIPT_SECTION_ORDER)}
    files.sort(key=lambda path: (rank.get(path.name, len(rank)), path.name))
    return files


def _heading_id(title: str, attrs: str | None) -> str:
    if attrs:
        match = re.search(r"#([A-Za-z0-9_.:-]+)", attrs)
        if match:
            return match.group(1)
    slug = re.sub(r"`([^`]*)`", r"\1", title)
    slug = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", slug)
    slug = re.sub(r"[^A-Za-z0-9 _.-]+", "", slug).strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug or "section"


def _heading_title(title: str) -> str:
    cleaned = re.sub(r"`([^`]*)`", r"\1", title)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"[*_~]", "", cleaned)
    return cleaned.strip()


def _toc_entries(sections: list[Path]) -> list[tuple[int, str, str]]:
    entries: list[tuple[int, str, str]] = []
    for section in sections:
        if section.name in {COVER_NAME, GENERATED_CONTENTS_NAME, *BOOKEND_NAMES}:
            continue
        for line in section.read_text(encoding="utf-8").splitlines():
            match = HEADING_PATTERN.match(line)
            if not match:
                continue
            level = len(match.group("level"))
            title = _heading_title(match.group("title"))
            identifier = _heading_id(match.group("title"), match.group("attrs"))
            entries.append((level, title, identifier))
    return entries


def _build_html_toc(entries: list[tuple[int, str, str]]) -> str:
    lines = [
        '<nav id="TOC" role="doc-toc" aria-label="Table of contents">',
        "<h1>Contents</h1>",
        "<ul>",
    ]
    for level, title, identifier in entries:
        safe_title = html_lib.escape(title)
        safe_identifier = html_lib.escape(identifier, quote=True)
        lines.append(
            f'  <li class="toc-level-{level}"><a href="#{safe_identifier}">{safe_title}</a></li>'
        )
    lines += ["</ul>", "</nav>"]
    return "\n".join(lines)


def _write_generated_contents_section(
    contents_path: Path, entries: list[tuple[int, str, str]]
) -> None:
    html_toc = _build_html_toc(entries)
    contents_path.write_text(
        f"""```{{=latex}}
\\clearpage
\\phantomsection
\\tableofcontents
\\clearpage
```

```{{=html}}
{html_toc}
```
""",
        encoding="utf-8",
    )


def _sections_with_generated_contents(
    sections: list[Path], manuscript_dir: Path
) -> list[Path]:
    contents_path = manuscript_dir / GENERATED_CONTENTS_NAME
    _write_generated_contents_section(contents_path, _toc_entries(sections))
    with_contents: list[Path] = []
    inserted = False
    for section in sections:
        with_contents.append(section)
        if section.name == COVER_NAME:
            with_contents.append(contents_path)
            inserted = True
    if not inserted:
        with_contents.insert(0, contents_path)
    return with_contents


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


def _strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines())
    if text.endswith("\n"):
        cleaned += "\n"
    path.write_text(cleaned, encoding="utf-8")


def _build_pandoc_metadata_args(
    variables: dict[str, str], project_root: Path
) -> list[str]:
    """Construct -M key=value args from manuscript_variables.json."""
    for required in (
        "CONFIG_TITLE",
        "CONFIG_FIRST_AUTHOR",
        "CONFIG_PUBLICATION_DATE",
    ):
        if not variables.get(required):
            raise RuntimeError(f"Required manuscript variable is missing: {required}")
    title = variables["CONFIG_TITLE"]
    author = variables["CONFIG_FIRST_AUTHOR"]
    version = variables.get("CONFIG_VERSION", "")
    keywords = variables.get("CONFIG_KEYWORDS", "")
    publication_date = variables["CONFIG_PUBLICATION_DATE"]

    args: list[str] = [
        "-M",
        f"pagetitle={title}",
        "-M",
        f"title-meta={title}",
        "-M",
        f"author-meta={author}",
    ]
    args += ["-M", f"date={publication_date}"]
    if version:
        args += ["-M", f"version={version}"]
    if keywords:
        args += ["-M", f"keywords={keywords}"]
    args += ["-M", "lang=en"]
    return args


def _require_executable(name: str) -> bool:
    if shutil.which(name):
        return True
    print(
        f"ERROR: {name} not found on PATH. Install {name} and retry.", file=sys.stderr
    )
    return False


def _pandoc_crossref_args() -> list[str]:
    return [
        "-F",
        "pandoc-crossref",
        "--number-sections",
        "-M",
        "link-citations=true",
        "-M",
        "linkReferences=true",
        "-M",
        "nameInLink=true",
        "-M",
        "chapters=false",
        "-M",
        "secPrefix=Section",
        "-M",
        "figPrefix=Figure",
        "-M",
        "tblPrefix=Table",
        "-M",
        "eqnPrefix=Equation",
        "-M",
        "reference-section-title=References",
    ]


def _run_pandoc_html(
    sections: list[Path],
    output_path: Path,
    bibliography: Path,
    variables: dict[str, str],
    project_root: Path,
) -> bool:
    """Run pandoc to produce HTML output; return True on success."""
    if not _require_executable("pandoc") or not _require_executable("pandoc-crossref"):
        return False

    print(f"Compiling HTML → {output_path.relative_to(project_root)} ...")

    cmd: list[str] = ["pandoc"]
    cmd += [str(s) for s in sections]
    cmd += _pandoc_crossref_args()
    cmd += [
        "--standalone",
        "--embed-resources",
        "--mathml",
        "--css",
        str(project_root / "docs" / "manuscript" / "manuscript.css"),
        "--citeproc",
        "--from",
        "markdown+yaml_metadata_block",
        "--bibliography",
        str(bibliography),
        "--resource-path",
        f"{project_root / 'output'}:{project_root / 'output' / 'manuscript'}:{project_root}",
    ]
    cmd += _build_pandoc_metadata_args(variables, project_root)
    cmd += ["-o", str(output_path)]

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=False)
    if result.returncode != 0:
        print(
            f"ERROR: pandoc HTML compilation failed (exit {result.returncode})",
            file=sys.stderr,
        )
        return False
    _strip_trailing_whitespace(output_path)
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
    if not _require_executable("pandoc") or not _require_executable("pandoc-crossref"):
        return False

    print(f"Compiling PDF → {output_path.relative_to(project_root)} ...")

    cmd: list[str] = ["pandoc"]
    cmd += [str(s) for s in sections]
    cmd += _pandoc_crossref_args()
    cmd += [
        "--standalone",
        "--citeproc",
        "--from",
        "markdown+yaml_metadata_block",
        "--bibliography",
        str(bibliography),
        "--pdf-engine=xelatex",
        "--resource-path",
        f"{project_root / 'output'}:{project_root / 'output' / 'manuscript'}:{project_root}",
        "-V",
        "colorlinks=true",
        "-V",
        "linkcolor=red",
        "-V",
        "urlcolor=red",
        "-V",
        "citecolor=red",
        "-V",
        "filecolor=red",
        "-V",
        "toccolor=red",
    ]
    if preamble and preamble.exists():
        latex_src = _extract_latex_from_preamble(preamble)
        if latex_src:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".tex", delete=False, encoding="utf-8"
            )
            tmp.write(latex_src)
            tmp.flush()
            cmd += ["-H", tmp.name]
        else:
            cmd += ["-H", str(preamble)]
    cmd += _build_pandoc_metadata_args(variables, project_root)
    cmd += ["-o", str(output_path)]

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=False)
    if result.returncode != 0:
        print(
            f"ERROR: pandoc PDF compilation failed (exit {result.returncode})",
            file=sys.stderr,
        )
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
        if not _run_generate_variables(project_root):
            return 1
    else:
        print("Skipping variable generation (--skip-generate).")

    # Step 2: Locate manuscript files
    manuscript_dir = project_root / "output" / "manuscript"
    if not manuscript_dir.exists():
        print(
            f"ERROR: output/manuscript/ does not exist: {manuscript_dir}",
            file=sys.stderr,
        )
        print(
            "  Run without --skip-generate to generate manuscript files first.",
            file=sys.stderr,
        )
        return 1

    sections = _collect_sections(manuscript_dir, include_bookends=args.bookends)
    if not sections:
        print("ERROR: no section files found in output/manuscript/", file=sys.stderr)
        return 1
    sections = _sections_with_generated_contents(sections, manuscript_dir)

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
