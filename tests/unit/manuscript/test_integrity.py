from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

from codomyrmex.manuscript.bibliography import extract_pandoc_citations

_VALIDATOR_PATH = (
    Path(__file__).resolve().parents[3] / "scripts" / "validate_manuscript_integrity.py"
)
_VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "codomyrmex_manuscript_integrity_validator", _VALIDATOR_PATH
)
if _VALIDATOR_SPEC is None or _VALIDATOR_SPEC.loader is None:
    raise ImportError(f"cannot load manuscript integrity validator: {_VALIDATOR_PATH}")
_VALIDATOR_MODULE = importlib.util.module_from_spec(_VALIDATOR_SPEC)
_VALIDATOR_SPEC.loader.exec_module(_VALIDATOR_MODULE)
validate_manuscript_integrity = _VALIDATOR_MODULE.validate_manuscript_integrity
hardcoded_numeric_literals = _VALIDATOR_MODULE._hardcoded_numeric_literals
normalise_text = _VALIDATOR_MODULE._normalise_text


def _write_minimal_bundle(root: Path) -> None:
    (root / "docs/manuscript").mkdir(parents=True)
    (root / "output/data").mkdir(parents=True)
    (root / "output/figures").mkdir(parents=True)
    (root / "output/manuscript").mkdir(parents=True)
    config = {
        "figures": {
            "main": {
                "filename": "main.png",
                "label": "fig:main",
                "width": "80%",
                "evidence_class": "schematic",
                "caption": "A {{VALUE}} schematic.",
                "alt_text": "A compact schematic of the fixture.",
                "long_description": (
                    "A single fixture schematic demonstrates linked alternative text "
                    "and an extended description without making an empirical claim."
                ),
            }
        }
    }
    config_path = root / "docs/manuscript/config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
    variables = {
        "ARTIFACT_FIGURE_COUNT": "1",
        "CONFIG_HASH": config_hash,
        "VALUE": "fixture",
    }
    variables_path = root / "output/data/manuscript_variables.json"
    variables_path.write_text(json.dumps(variables, sort_keys=True), encoding="utf-8")
    variable_hash = hashlib.sha256(
        json.dumps(variables, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    (root / "output/data/manuscript_variable_manifest.json").write_text(
        json.dumps(
            {
                "status": "valid",
                "config_sha256": config_hash,
                "variable_sha256": variable_hash,
            }
        ),
        encoding="utf-8",
    )
    figure_path = root / "output/figures/main.png"
    figure_path.write_bytes(b"fixture-png-payload")
    (root / "output/figures/figure_registry.json").write_text(
        json.dumps(
            {
                "schema_version": 3,
                "config_hash": config_hash,
                "count": 1,
                "figures": [
                    {
                        "filename": "main.png",
                        "label": "fig:main",
                        "width": "80%",
                        "evidence_class": "schematic",
                        "caption": "A fixture schematic.",
                        "alt_text": "A compact schematic of the fixture.",
                        "long_description": (
                            "A single fixture schematic demonstrates linked alternative "
                            "text and an extended description without making an empirical "
                            "claim."
                        ),
                        "bytes": figure_path.stat().st_size,
                        "sha256": hashlib.sha256(figure_path.read_bytes()).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "output/manuscript/01.md").write_text(
        "![A [bracketed] configured schematic.](figures/main.png)"
        '{#fig:main alt="A compact schematic of the fixture." '
        'aria-describedby="fig:main-description"}\n'
        '<div id="fig:main-description" class="figure-long-description">'
        "A single fixture schematic demonstrates linked alternative text and an "
        "extended description without making an empirical claim.</div>\n",
        encoding="utf-8",
    )
    (root / "docs/manuscript/references.bib").write_text("", encoding="utf-8")
    (root / "docs/manuscript/source.md").write_text("source\n", encoding="utf-8")
    (root / "docs/manuscript/claim_ledger.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "1.0",
                "source_audit": {
                    "covered": [],
                    "excluded": {
                        "docs/manuscript/source.md": "fixture evidence source, not an active manuscript section"
                    },
                },
                "claims": [
                    {
                        "id": "C1",
                        "class": "definition",
                        "status": "supported",
                        "statement": "The fixture is defined.",
                        "source": ["docs/manuscript/source.md"],
                        "evidence": ["docs/manuscript/source.md"],
                        "boundary": "Only a definition.",
                        "citations": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_manuscript_integrity_accepts_a_consistent_bundle(tmp_path: Path) -> None:
    _write_minimal_bundle(tmp_path)
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "valid", report["errors"]
    assert report["figure_count"] == 1
    assert report["claim_count"] == 1
    assert report["claim_source_audit"]["unaccounted"] == []


def test_manuscript_integrity_accepts_embedded_rendered_png(tmp_path: Path) -> None:
    _write_minimal_bundle(tmp_path)
    (tmp_path / "output/paper.html").write_text(
        "<html><body>"
        '<img src="data:image/png;base64,ZmFrZS1wbmc=" '
        'alt="A compact schematic of the fixture." '
        'aria-describedby="fig:main-description">'
        '<div id="fig:main-description" class="figure-long-description">'
        "A single fixture schematic demonstrates linked alternative text and an "
        "extended description without making an empirical claim.</div>"
        "</body></html>",
        encoding="utf-8",
    )
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "valid", report["errors"]
    assert report["html_image_count"] == 1


def test_semantic_text_normalisation_accepts_smart_typography() -> None:
    assert normalise_text("the node\u2019s \u201crole\u201d") == normalise_text(
        'the node\'s "role"'
    )


def test_manuscript_integrity_rejects_stale_figure_hash(tmp_path: Path) -> None:
    _write_minimal_bundle(tmp_path)
    (tmp_path / "output/figures/main.png").write_bytes(b"changed")
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "invalid"
    assert any("SHA-256" in error for error in report["errors"])


def test_manuscript_integrity_rejects_unaccounted_active_section(
    tmp_path: Path,
) -> None:
    _write_minimal_bundle(tmp_path)
    (tmp_path / "docs/manuscript/02_theory.md").write_text(
        "A section requiring explicit claim coverage.\n", encoding="utf-8"
    )
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "invalid"
    assert any("unaccounted" in error for error in report["errors"])


def test_manuscript_integrity_rejects_stale_explicit_alt_text(tmp_path: Path) -> None:
    _write_minimal_bundle(tmp_path)
    manuscript = tmp_path / "output/manuscript/01.md"
    manuscript.write_text(
        manuscript.read_text(encoding="utf-8").replace(
            'alt="A compact schematic of the fixture."',
            'alt="A stale alternative."',
        ),
        encoding="utf-8",
    )
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "invalid"
    assert any("alt text is stale" in error for error in report["errors"])


def test_manuscript_integrity_rejects_missing_extended_description(
    tmp_path: Path,
) -> None:
    _write_minimal_bundle(tmp_path)
    manuscript = tmp_path / "output/manuscript/01.md"
    content = manuscript.read_text(encoding="utf-8")
    manuscript.write_text(content.split("<div", 1)[0], encoding="utf-8")
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "invalid"
    assert any("no linked extended description" in error for error in report["errors"])


def test_numeric_integrity_guard_flags_drifting_prose_values(tmp_path: Path) -> None:
    manuscript = tmp_path / "docs/manuscript"
    manuscript.mkdir(parents=True)
    path = manuscript / "01_results.md"
    path.write_text("The measured rate was 42 percent.\n", encoding="utf-8")
    findings = hardcoded_numeric_literals(manuscript)
    assert len(findings) == 1
    assert ":1:" in findings[0]


def test_pandoc_citation_inventory_excludes_cross_references_and_code(
    tmp_path: Path,
) -> None:
    source = tmp_path / "01_source.md"
    source.write_text(
        "Evidence [@source2026] is shown in @fig:result and @tbl:data. "
        "`@mcp_tool` is code.\\n",
        encoding="utf-8",
    )
    inventory = extract_pandoc_citations([source])
    assert inventory.citation_keys == ("source2026",)
    assert inventory.cross_references == ("fig:result", "tbl:data")


def test_manuscript_integrity_rejects_unused_bibliography_record(
    tmp_path: Path,
) -> None:
    _write_minimal_bundle(tmp_path)
    (tmp_path / "docs/manuscript/references.bib").write_text(
        "@misc{unused, title={Unused}, year={2026}, "
        "url={https://example.invalid/source}}\\n",
        encoding="utf-8",
    )
    report = validate_manuscript_integrity(tmp_path)
    assert report["status"] == "invalid"
    assert any("unused bibliography keys" in error for error in report["errors"])
