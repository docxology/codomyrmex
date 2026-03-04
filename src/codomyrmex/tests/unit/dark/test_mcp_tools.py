"""Unit tests for dark module MCP tools.

Follows a strict zero-mock policy. All tests use real PDF artifacts.
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.dark.mcp_tools import (
    dark_get_presets,
    dark_pdf_batch,
    dark_pdf_convert,
)


def _make_test_pdf(path: str | Path) -> None:
    """Helper to create a simple PDF for testing.
    Uses PyMuPDF (fitz) to create a valid document."""
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Test PDF for dark mode tools", fontsize=12)
    doc.save(str(path))
    doc.close()


class TestDarkMCPTools:
    """Test suite for dark module MCP tools."""

    @pytest.mark.unit
    def test_dark_pdf_convert_success(self) -> None:
        """Test successful PDF dark mode conversion via MCP tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"
            _make_test_pdf(input_pdf)

            # Test basic preset
            result = dark_pdf_convert(
                input_path=str(input_pdf),
                output_path=str(output_pdf),
                preset="dark",
                dpi=72,
            )

            assert result["success"] is True
            assert result["output_path"] == str(output_pdf)
            assert output_pdf.exists()

            # Test overrides
            output_override = Path(tmpdir) / "output_override.pdf"
            result_override = dark_pdf_convert(
                input_path=str(input_pdf),
                output_path=str(output_override),
                inversion=0.5,
                dpi=72,
            )

            assert result_override["success"] is True
            assert result_override["output_path"] == str(output_override)
            assert output_override.exists()

    @pytest.mark.unit
    def test_dark_pdf_convert_failure(self) -> None:
        """Test failure handling in PDF dark mode conversion tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_pdf = Path(tmpdir) / "output.pdf"

            result = dark_pdf_convert(
                input_path="/nonexistent/input.pdf",
                output_path=str(output_pdf),
                dpi=72,
            )

            assert result["success"] is False
            assert "Input PDF not found" in result["error"]

    @pytest.mark.unit
    def test_dark_pdf_batch_success(self) -> None:
        """Test successful batch PDF dark mode conversion via MCP tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_dir = Path(tmpdir) / "inputs"
            input_dir.mkdir()

            input_pdf1 = input_dir / "doc1.pdf"
            input_pdf2 = input_dir / "doc2.pdf"
            _make_test_pdf(input_pdf1)
            _make_test_pdf(input_pdf2)

            output_dir = Path(tmpdir) / "outputs"

            result = dark_pdf_batch(
                input_paths=[str(input_pdf1), str(input_pdf2)],
                output_dir=str(output_dir),
                preset="sepia",
                suffix="_custom",
                dpi=72,
            )

            assert result["success"] is True
            assert len(result["output_paths"]) == 2

            out1 = output_dir / "doc1_custom.pdf"
            out2 = output_dir / "doc2_custom.pdf"
            assert str(out1) in result["output_paths"]
            assert str(out2) in result["output_paths"]
            assert out1.exists()
            assert out2.exists()

    @pytest.mark.unit
    def test_dark_pdf_batch_failure(self) -> None:
        """Test failure handling in batch conversion tool."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "outputs"

            result = dark_pdf_batch(
                input_paths=["/nonexistent/doc1.pdf"],
                output_dir=str(output_dir),
                dpi=72,
            )

            assert result["success"] is False
            assert "Input PDF not found" in result["error"]

    @pytest.mark.unit
    def test_dark_get_presets(self) -> None:
        """Test retrieval of available presets."""
        presets = dark_get_presets()

        assert isinstance(presets, dict)
        assert "dark" in presets
        assert "sepia" in presets
        assert "high_contrast" in presets
        assert "low_light" in presets

        # Check structure of a preset
        assert "inversion" in presets["dark"]
        assert "brightness" in presets["dark"]
        assert "contrast" in presets["dark"]
        assert "sepia" in presets["dark"]

    @pytest.mark.unit
    def test_tool_metadata(self) -> None:
        """Test that MCP tools have correct metadata registered."""
        # Using the standard codomyrmex way to access mcp tool meta

        # dark_pdf_convert
        meta = dark_pdf_convert._mcp_tool_meta
        assert meta["category"] == "dark"
        assert "Convert a PDF file to dark mode" in meta["description"]
        assert meta["name"] == "codomyrmex.dark_pdf_convert"

        # dark_pdf_batch
        meta = dark_pdf_batch._mcp_tool_meta
        assert meta["category"] == "dark"
        assert "Process multiple PDFs to dark mode in a batch" in meta["description"]
        assert meta["name"] == "codomyrmex.dark_pdf_batch"

        # dark_get_presets
        meta = dark_get_presets._mcp_tool_meta
        assert meta["category"] == "dark"
        assert "Get available dark mode presets" in meta["description"]
        assert meta["name"] == "codomyrmex.dark_get_presets"
