"""Real-artifact fixtures for release tests."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pytest

from codomyrmex.release import (
    BuildReport,
    PackageBuilder,
    PackageMetadata,
    PublicationBundle,
    PublicationMetadata,
    prepare_publication_bundle,
)


@dataclass(frozen=True)
class RealPackage:
    root: Path
    output_dir: Path
    metadata: PackageMetadata
    report: BuildReport


def _write_minimal_package(root: Path) -> PackageMetadata:
    metadata = PackageMetadata(
        name="release-fixture",
        version="1.2.3",
        description="Real release fixture",
    )
    (root / "src" / "release_fixture").mkdir(parents=True)
    (root / "src" / "release_fixture" / "__init__.py").write_text(
        '"""Release fixture."""\n\nVALUE = 42\n',
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Release fixture\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        """[build-system]
requires = ["uv_build>=0.9,<1"]
build-backend = "uv_build"

[project]
name = "release-fixture"
version = "1.2.3"
description = "Real release fixture"
readme = "README.md"
requires-python = ">=3.11"
""",
        encoding="utf-8",
    )
    return metadata


@pytest.fixture(scope="session")
def real_package(tmp_path_factory: pytest.TempPathFactory) -> RealPackage:
    root = tmp_path_factory.mktemp("real-release-package")
    output_dir = root / "dist"
    metadata = _write_minimal_package(root)
    report = PackageBuilder(
        metadata,
        source_dir=root,
        output_dir=output_dir,
        source_date_epoch=1_700_000_000,
    ).build()
    assert report.success, report.warnings
    return RealPackage(
        root=root,
        output_dir=output_dir,
        metadata=metadata,
        report=report,
    )


def write_searchable_pdf(path: Path, text: str) -> None:
    """Write a tiny valid PDF containing one searchable text line."""
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 10 Tf 40 740 Td ({escaped}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(payload))
        payload.extend(f"{index} 0 obj\n".encode())
        payload.extend(obj)
        payload.extend(b"\nendobj\n")
    xref = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode())
    payload.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode()
    )
    path.write_bytes(bytes(payload))


def content_hash_for_pdf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def publication_bundle(tmp_path: Path) -> PublicationBundle:
    content_pdf = tmp_path / "content.pdf"
    distribution_pdf = tmp_path / "distribution.pdf"
    semantic_html = tmp_path / "report.html"
    reproducibility_input = tmp_path / "parameters.yaml"
    validation_receipt = tmp_path / "qpdf.json"
    write_searchable_pdf(content_pdf, "Unbookended technical report content")
    content_sha256 = content_hash_for_pdf(content_pdf)
    write_searchable_pdf(
        distribution_pdf,
        f"Visible release bookend content SHA-256 {content_sha256}",
    )
    semantic_html.write_text(
        '<!doctype html><html lang="en"><title>Report</title><main>Report</main></html>\n',
        encoding="utf-8",
    )
    reproducibility_input.write_text("seed: 7\n", encoding="utf-8")
    validation_receipt.write_text(
        '{"check": "qpdf", "passed": true}\n',
        encoding="utf-8",
    )
    return prepare_publication_bundle(
        metadata=PublicationMetadata(
            title="Codomyrmex test report",
            subtitle="Publication fixture",
            version="1.2.3",
            authors=("Researcher One",),
            keywords=("release", "verification"),
            repository_url="https://github.com/docxology/codomyrmex",
        ),
        content_pdf=content_pdf,
        distribution_pdf=distribution_pdf,
        semantic_html=semantic_html,
        output_dir=tmp_path / "bundle",
        project_root=Path.cwd(),
        reproducibility_inputs=(reproducibility_input,),
        validation_receipts=(validation_receipt,),
        validation_outcomes=(("qpdf", True, "structure valid"),),
        source_date_epoch=1_700_000_000,
    )
