#!/usr/bin/env python3
"""Compile the resolved Codomyrmex manuscript to semantic HTML and PDF.

Usage:
    uv run --locked --group docs python scripts/compile_manuscript.py
    uv run --locked --group docs python scripts/compile_manuscript.py --pdf
    uv run --locked --group docs python scripts/compile_manuscript.py --check
    uv run --locked --group docs python scripts/compile_manuscript.py --pdf --bookends

Workflow:
    1. Run z_generate_manuscript_variables.py to inject tokens
    2. Generate output/manuscript/00_01_contents.md after the cover page
    3. Verify no {{TOKEN}} remain in output/manuscript/*.md
    4. Render semantic HTML from the unbookended report
    5. With ``--pdf --bookends``, render and hash the content PDF, generate
       visible QR/text bookends, then render the final PDF in one Pandoc pass
    6. Require qpdf structural validation and record pdfinfo/veraPDF evidence
"""

# SIZE_OK: Renderer orchestration stays single-file for artifact auditability.

from __future__ import annotations

import argparse
import hashlib
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
    "09_research_roadmap.md",
    "10_formalism_code_crosswalk.md",
    "11_supplemental_notation.md",
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


def _sections_with_contents_at(
    sections: list[Path],
    contents_path: Path,
) -> list[Path]:
    contents_path.parent.mkdir(parents=True, exist_ok=True)
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


def _hash_file(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _repository_url(value: str) -> str:
    repository = value.strip()
    if repository and not repository.startswith(("http://", "https://")):
        return f"https://github.com/{repository}"
    return repository


def _write_release_bookends(
    *,
    output_dir: Path,
    variables: dict[str, str],
    content_sha256: str,
) -> tuple[Path, Path] | None:
    """Generate visible bookend Markdown and a QR code from verified inputs."""
    required = {
        "CONFIG_TITLE": variables.get("CONFIG_TITLE", ""),
        "CONFIG_VERSION": variables.get("CONFIG_VERSION", ""),
        "CONFIG_FIRST_AUTHOR": variables.get("CONFIG_FIRST_AUTHOR", ""),
        "CONFIG_GITHUB_REPOSITORY": variables.get("CONFIG_GITHUB_REPOSITORY", ""),
        "CONFIG_RELEASE_TAG": variables.get("CONFIG_RELEASE_TAG", ""),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        print(
            f"ERROR: bookend metadata is missing: {', '.join(missing)}",
            file=sys.stderr,
        )
        return None
    try:
        import qrcode
    except ImportError:
        print(
            "ERROR: qrcode is required for --bookends; "
            "run with `uv run --locked --group docs`.",
            file=sys.stderr,
        )
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    repository_url = _repository_url(required["CONFIG_GITHUB_REPOSITORY"])
    release_url = (
        f"{repository_url}/releases/tag/{required['CONFIG_RELEASE_TAG']}"
        if repository_url
        else ""
    )
    qr_target = f"{release_url}#content-sha256={content_sha256}"
    qr_path = output_dir / "release-identity-qr.png"
    qr = qrcode.make(qr_target)
    qr.save(qr_path)

    doi = variables.get("CONFIG_DOI", "").strip()
    doi_line = doi if doi and doi.lower() != "not assigned" else "not assigned"
    commit = variables.get("REPRO_GIT_COMMIT", "not recorded")
    dirty = variables.get("REPRO_WORKTREE_DIRTY", "not recorded")
    identity_lines = [
        f"**Report:** {required['CONFIG_TITLE']}",
        f"**Release:** {required['CONFIG_VERSION']}",
        f"**Author:** {required['CONFIG_FIRST_AUTHOR']}",
        f"**DOI:** {doi_line}",
        f"**Source commit:** `{commit}`",
        f"**Source worktree dirty:** `{dirty}`",
        f"**Content SHA-256:** `{content_sha256}`",
        f"**Repository release link:** [{release_url}]({release_url})",
    ]
    qr_markdown = (
        f"![QR code for the visible repository release link]({qr_path.as_posix()})"
        "{width=1.25in}"
    )
    front = output_dir / "00_00_transmission_begin.md"
    back = output_dir / "99_zz_transmission_end.md"
    front.write_text(
        "\n".join(
            [
                "```{=latex}",
                "\\clearpage",
                "\\thispagestyle{empty}",
                "```",
                "",
                "# Release identity {.unnumbered}",
                "",
                *identity_lines,
                "",
                qr_markdown,
                "",
                (
                    "This visible page identifies the unbookended report content. "
                    "The final distribution PDF has its own detached hashes in "
                    "`publication_manifest.json`, `SHA256SUMS`, and `SHA512SUMS`."
                ),
                "",
                "```{=latex}",
                "\\clearpage",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    back.write_text(
        "\n".join(
            [
                "```{=latex}",
                "\\clearpage",
                "\\thispagestyle{empty}",
                "```",
                "",
                "# End of distribution copy {.unnumbered}",
                "",
                *identity_lines,
                "",
                qr_markdown,
                "",
                (
                    "Verification boundary: this hash identifies the locally rendered "
                    "content PDF. It does not attest external actuation, deployment "
                    "safety, or remote publication."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return front, back


def _validate_pdf(
    pdf_path: Path,
    *,
    receipt_dir: Path,
) -> bool:
    """Require qpdf structural validity and record optional conformance evidence."""
    receipt_dir.mkdir(parents=True, exist_ok=True)
    qpdf = shutil.which("qpdf")
    if qpdf is None:
        print("ERROR: qpdf is required for PDF validation.", file=sys.stderr)
        return False
    qpdf_result = subprocess.run(
        [qpdf, "--check", pdf_path.name],
        cwd=pdf_path.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    receipt: dict[str, object] = {
        "schema_version": "1",
        "artifact": pdf_path.name,
        "qpdf": {
            "command": ["qpdf", "--check", pdf_path.name],
            "exit_code": qpdf_result.returncode,
            "passed": qpdf_result.returncode == 0,
            "stdout": qpdf_result.stdout,
            "stderr": qpdf_result.stderr,
        },
    }

    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        info_result = subprocess.run(
            [pdfinfo, pdf_path.name],
            cwd=pdf_path.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        receipt["pdfinfo"] = {
            "exit_code": info_result.returncode,
            "output": info_result.stdout,
        }
    else:
        receipt["pdfinfo"] = {"status": "not-installed"}

    verapdf = shutil.which("verapdf")
    if verapdf:
        vera_result = subprocess.run(
            [verapdf, "--format", "json", pdf_path.name],
            cwd=pdf_path.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        receipt["verapdf"] = {
            "exit_code": vera_result.returncode,
            "passed": vera_result.returncode == 0,
            "stdout": vera_result.stdout,
            "stderr": vera_result.stderr,
        }
    else:
        receipt["verapdf"] = {
            "status": "not-installed",
            "conformance": "not-claimed",
        }

    receipt_path = receipt_dir / f"{pdf_path.stem}-pdf-validation.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if qpdf_result.returncode != 0:
        print(
            f"ERROR: qpdf rejected {_display_path(pdf_path, pdf_path.parent)}",
            file=sys.stderr,
        )
        return False
    return True


def _validate_bookend_placement(pdf_path: Path, content_sha256: str) -> bool:
    """Require the content hash on both the first and last PDF pages."""
    pdftotext = shutil.which("pdftotext")
    pdfinfo = shutil.which("pdfinfo")
    if pdftotext is None or pdfinfo is None:
        print(
            "ERROR: pdftotext and pdfinfo are required to verify bookend placement.",
            file=sys.stderr,
        )
        return False
    info = subprocess.run(
        [pdfinfo, str(pdf_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    match = re.search(r"^Pages:\s+(\d+)\s*$", info.stdout, re.MULTILINE)
    if info.returncode != 0 or match is None:
        print("ERROR: could not determine PDF page count.", file=sys.stderr)
        return False
    page_count = int(match.group(1))
    for page in (1, page_count):
        result = subprocess.run(
            [
                pdftotext,
                "-f",
                str(page),
                "-l",
                str(page),
                str(pdf_path),
                "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or content_sha256 not in "".join(
            result.stdout.split()
        ):
            print(
                f"ERROR: content SHA-256 is absent from bookend page {page}.",
                file=sys.stderr,
            )
            return False
    return True


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

    print(f"Compiling HTML → {_display_path(output_path, project_root)} ...")

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
    print(f"  HTML written: {_display_path(output_path, project_root)}")
    return True


def _run_pandoc_pdf(
    sections: list[Path],
    output_path: Path,
    bibliography: Path,
    preamble: Path | None,
    variables: dict[str, str],
    project_root: Path,
    pdf_engine: str,
    pdf_standard: str,
) -> bool:
    """Run pandoc to produce PDF output; return True on success."""
    if not _require_executable("pandoc") or not _require_executable("pandoc-crossref"):
        return False

    if pdf_standard != "none" and pdf_engine != "lualatex":
        print(
            "ERROR: PDF standards require --pdf-engine lualatex.",
            file=sys.stderr,
        )
        return False

    print(f"Compiling PDF → {_display_path(output_path, project_root)} ...")

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
        f"--pdf-engine={pdf_engine}",
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
    if pdf_standard != "none":
        cmd += ["-V", f"pdfstandard={pdf_standard}"]
    temp_header: Path | None = None
    if preamble and preamble.exists():
        latex_src = _extract_latex_from_preamble(preamble)
        if latex_src:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".tex", delete=False, encoding="utf-8"
            )
            tmp.write(latex_src)
            tmp.flush()
            tmp.close()
            temp_header = Path(tmp.name)
            cmd += ["-H", tmp.name]
        else:
            cmd += ["-H", str(preamble)]
    cmd += _build_pandoc_metadata_args(variables, project_root)
    cmd += ["-o", str(output_path)]

    try:
        result = subprocess.run(cmd, cwd=str(project_root), capture_output=False)
    finally:
        if temp_header is not None:
            temp_header.unlink(missing_ok=True)
    if result.returncode != 0:
        print(
            f"ERROR: pandoc PDF compilation failed (exit {result.returncode})",
            file=sys.stderr,
        )
        return False
    print(f"  PDF written: {_display_path(output_path, project_root)}")
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
        help="Also produce a structurally validated PDF.",
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
            "Run the two-pass release render: hash the content PDF, generate "
            "visible bookends, and render the final distribution PDF."
        ),
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Use existing resolved manuscript files.",
    )
    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        help="Resolved manuscript input directory (default: output/manuscript).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Artifact destination directory (default: output).",
    )
    parser.add_argument(
        "--pdf-engine",
        choices=("lualatex", "xelatex"),
        default="lualatex",
        help="Pandoc PDF engine (default: lualatex).",
    )
    parser.add_argument(
        "--pdf-standard",
        choices=("none", "ua-1", "ua-2", "a-2b", "a-3b", "a-4f"),
        default="ua-2",
        help="Requested Pandoc PDF standard (default: ua-2; use none explicitly).",
    )
    args = parser.parse_args()

    project_root = _find_project_root()
    if args.bookends and not args.pdf:
        print("ERROR: --bookends requires --pdf.", file=sys.stderr)
        return 1

    # Step 1: Regenerate tokens unless skipped
    if not args.skip_generate:
        if not _run_generate_variables(project_root):
            return 1
    else:
        print("Skipping variable generation (--skip-generate).")

    # Step 2: Locate manuscript files
    manuscript_dir = (
        args.manuscript_dir.resolve()
        if args.manuscript_dir is not None
        else project_root / "output" / "manuscript"
    )
    if not manuscript_dir.exists():
        print(
            f"ERROR: manuscript input directory does not exist: {manuscript_dir}",
            file=sys.stderr,
        )
        print(
            "  Run without --skip-generate to generate manuscript files first.",
            file=sys.stderr,
        )
        return 1

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else project_root / "output"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    sections = _collect_sections(manuscript_dir, include_bookends=False)
    if not sections:
        print(f"ERROR: no section files found in {manuscript_dir}", file=sys.stderr)
        return 1
    sections = _sections_with_contents_at(
        sections,
        output_dir / "generated-manuscript" / GENERATED_CONTENTS_NAME,
    )

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
        return 1
    print("  No unresolved tokens found.")

    if args.check:
        print("--check passed: no unresolved tokens.")
        return 0

    # Locate supporting files
    bibliography = manuscript_dir / "references.bib"
    if not bibliography.exists():
        print(f"ERROR: references.bib not found at {bibliography}", file=sys.stderr)
        return 1

    preamble = manuscript_dir / "preamble.md"

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
        validation_dir = output_dir / "validation"
        if args.bookends:
            content_out = output_dir / "paper-content.pdf"
            content_ok = _run_pandoc_pdf(
                sections=sections,
                output_path=content_out,
                bibliography=bibliography,
                preamble=preamble,
                variables=variables,
                project_root=project_root,
                pdf_engine=args.pdf_engine,
                pdf_standard=args.pdf_standard,
            )
            if not content_ok or not content_out.is_file():
                print(
                    "ERROR: required content PDF was not generated.",
                    file=sys.stderr,
                )
                return 1
            if not _validate_pdf(content_out, receipt_dir=validation_dir):
                return 1
            content_sha256 = _hash_file(content_out)
            content_receipt = {
                "schema_version": "1",
                "artifact": content_out.name,
                "role": "unbookended-content",
                "sha256": content_sha256,
                "sha512": _hash_file(content_out, "sha512"),
                "size_bytes": content_out.stat().st_size,
            }
            (validation_dir / "content-identity.json").write_text(
                json.dumps(content_receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            bookends = _write_release_bookends(
                output_dir=output_dir / "generated-bookends",
                variables=variables,
                content_sha256=content_sha256,
            )
            if bookends is None:
                return 1
            front, back = bookends
            distribution_out = output_dir / "paper.pdf"
            distribution_ok = _run_pandoc_pdf(
                sections=[front, *sections, back],
                output_path=distribution_out,
                bibliography=bibliography,
                preamble=preamble,
                variables=variables,
                project_root=project_root,
                pdf_engine=args.pdf_engine,
                pdf_standard=args.pdf_standard,
            )
            if not distribution_ok or not distribution_out.is_file():
                return 1
            if not _validate_pdf(distribution_out, receipt_dir=validation_dir):
                return 1
            if not _validate_bookend_placement(distribution_out, content_sha256):
                return 1
        else:
            pdf_out = output_dir / "paper.pdf"
            pdf_ok = _run_pandoc_pdf(
                sections=sections,
                output_path=pdf_out,
                bibliography=bibliography,
                preamble=preamble,
                variables=variables,
                project_root=project_root,
                pdf_engine=args.pdf_engine,
                pdf_standard=args.pdf_standard,
            )
            if not pdf_ok or not _validate_pdf(
                pdf_out,
                receipt_dir=validation_dir,
            ):
                return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
