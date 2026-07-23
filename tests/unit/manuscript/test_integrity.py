from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

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
            }
        }
    }
    config_path = root / "docs/manuscript/config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    config_hash = hashlib.sha256(config_path.read_bytes()).hexdigest()
    variables = {"CONFIG_HASH": config_hash, "VALUE": "fixture"}
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
                "schema_version": 2,
                "config_hash": config_hash,
                "count": 1,
                "figures": [
                    {
                        "filename": "main.png",
                        "label": "fig:main",
                        "width": "80%",
                        "evidence_class": "schematic",
                        "caption": "A fixture schematic.",
                        "bytes": figure_path.stat().st_size,
                        "sha256": hashlib.sha256(figure_path.read_bytes()).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "output/manuscript/01.md").write_text(
        "![A [bracketed] configured schematic.](figures/main.png)\n", encoding="utf-8"
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


def test_numeric_integrity_guard_flags_drifting_prose_values(tmp_path: Path) -> None:
    manuscript = tmp_path / "docs/manuscript"
    manuscript.mkdir(parents=True)
    path = manuscript / "01_results.md"
    path.write_text("The measured rate was 42 percent.\n", encoding="utf-8")
    findings = hardcoded_numeric_literals(manuscript)
    assert len(findings) == 1
    assert ":1:" in findings[0]
