"""Unit contracts for the fail-closed manuscript PDF validation gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_compiler():
    root = Path(__file__).resolve().parents[3]
    path = root / "scripts" / "compile_manuscript.py"
    spec = importlib.util.spec_from_file_location("codomyrmex_compile_manuscript", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_integrity_validator():
    root = Path(__file__).resolve().parents[3]
    path = root / "scripts" / "validate_manuscript_integrity.py"
    spec = importlib.util.spec_from_file_location(
        "codomyrmex_validate_manuscript_integrity", path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pdfinfo_parser_normalizes_tagging_fields() -> None:
    compiler = _load_compiler()

    fields = compiler._parse_pdfinfo_fields(
        "Pages: 76\nTagged: yes\nSuspects: no\nCustom field: retained\n"
    )

    assert fields == {
        "pages": "76",
        "tagged": "yes",
        "suspects": "no",
        "custom field": "retained",
    }


def test_verapdf_parser_requires_explicit_compliance() -> None:
    compiler = _load_compiler()
    compliant = json.dumps(
        {
            "report": {
                "jobs": [
                    {"validationResult": [{"compliant": True}]},
                    {"validationResult": [{"compliant": True}]},
                ]
            }
        }
    )
    noncompliant = json.dumps(
        {"report": {"jobs": [{"validationResult": [{"compliant": False}]}]}}
    )

    assert compiler._parse_verapdf_compliance(compliant) is True
    assert compiler._parse_verapdf_compliance(noncompliant) is False
    assert compiler._parse_verapdf_compliance("not-json") is None
    assert compiler._parse_verapdf_compliance(json.dumps({"report": {}})) is False


def test_requested_pdf_standards_have_explicit_verapdf_profiles() -> None:
    compiler = _load_compiler()

    assert compiler.PDF_CONFORMANCE_FLAVOURS == {
        "ua-1": "ua1",
        "ua-2": "ua2",
        "a-2b": "2b",
        "a-3b": "3b",
        "a-4f": "4f",
    }


def test_pdf_validation_receipt_is_bound_to_current_bytes(tmp_path: Path) -> None:
    validator = _load_integrity_validator()
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"first PDF bytes")
    validation_dir = tmp_path / "output" / "validation"
    validation_dir.mkdir(parents=True)
    receipt = {
        "schema_version": "2",
        "artifact": "paper.pdf",
        "size_bytes": pdf_path.stat().st_size,
        "sha256": validator._sha256(pdf_path),
        "passed": True,
        "requirements": {
            "pdf_standard": "ua-2",
            "tagged_required": True,
            "verapdf_flavour": "ua2",
        },
        "qpdf": {"passed": True},
        "pdfinfo": {"passed": True, "tagged": True, "suspects": "no"},
        "verapdf": {"passed": True, "flavour": "ua2", "compliant": True},
    }
    (validation_dir / "paper-pdf-validation.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )

    issues: list[str] = []
    validator._validate_pdf_validation_receipt(tmp_path, pdf_path, issues)
    assert issues == []

    pdf_path.write_bytes(b"replaced PDF bytes")
    issues = []
    validator._validate_pdf_validation_receipt(tmp_path, pdf_path, issues)
    assert any("PDF validation receipt hash is stale" in issue for issue in issues)
    assert any("PDF validation receipt size is stale" in issue for issue in issues)
