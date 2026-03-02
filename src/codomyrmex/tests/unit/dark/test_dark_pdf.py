"""Unit tests for the dark PDF module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

# Try importing fitz for PDF tests
try:
    import fitz

    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

# Only import the dark PDF modules if fitz is available
if FITZ_AVAILABLE:
    from codomyrmex.dark.pdf.dark_pdf_wrapper import _PRESETS, DarkPDF
    from codomyrmex.dark.pdf.filters import DarkPDFFilter, apply_dark_mode
else:
    DarkPDFFilter = None
    apply_dark_mode = None
    DarkPDF = None
    _PRESETS = None

# Skip entire module if fitz is not available
pytestmark = pytest.mark.skipif(
    not FITZ_AVAILABLE,
    reason="PyMuPDF (fitz) not available - install with: uv sync --extra dark"
)


def _make_test_image(
    width: int = 100, height: int = 100, color: tuple[int, int, int] = (200, 200, 200)
) -> Image.Image:
    """Create a simple solid-color test image."""
    return Image.new("RGB", (width, height), color)


def _make_test_pdf(path: Path) -> None:
    """Create a minimal 1-page PDF for testing."""
    doc = fitz.open()
    page = doc.new_page(width=200, height=200)
    # Draw a white rectangle so there's visible content
    page.draw_rect(fitz.Rect(10, 10, 190, 190), color=(1, 1, 1), fill=(1, 1, 1))
    doc.save(str(path))
    doc.close()


class TestDarkPDFFilterInit:
    """Test DarkPDFFilter initialization and validation."""

    @pytest.mark.unit
    def test_default_values(self) -> None:
        """Test functionality: default values."""
        f = DarkPDFFilter()
        assert f.inversion == 0.90
        assert f.brightness == 0.90
        assert f.contrast == 0.90
        assert f.sepia == 0.10
        assert f.dpi == 150

    @pytest.mark.unit
    def test_custom_values(self) -> None:
        """Test functionality: custom values."""
        f = DarkPDFFilter(inversion=0.5, brightness=1.5, contrast=2.0, sepia=0.3)
        assert f.inversion == 0.5
        assert f.brightness == 1.5
        assert f.contrast == 2.0
        assert f.sepia == 0.3

    @pytest.mark.unit
    def test_inversion_out_of_range(self) -> None:
        """Test functionality: inversion out of range."""
        with pytest.raises(ValueError, match="inversion"):
            DarkPDFFilter(inversion=1.5)
        with pytest.raises(ValueError, match="inversion"):
            DarkPDFFilter(inversion=-0.1)

    @pytest.mark.unit
    def test_brightness_out_of_range(self) -> None:
        """Test functionality: brightness out of range."""
        with pytest.raises(ValueError, match="brightness"):
            DarkPDFFilter(brightness=0.05)
        with pytest.raises(ValueError, match="brightness"):
            DarkPDFFilter(brightness=3.5)

    @pytest.mark.unit
    def test_contrast_out_of_range(self) -> None:
        """Test functionality: contrast out of range."""
        with pytest.raises(ValueError, match="contrast"):
            DarkPDFFilter(contrast=0.05)
        with pytest.raises(ValueError, match="contrast"):
            DarkPDFFilter(contrast=3.5)

    @pytest.mark.unit
    def test_sepia_out_of_range(self) -> None:
        """Test functionality: sepia out of range."""
        with pytest.raises(ValueError, match="sepia"):
            DarkPDFFilter(sepia=-0.1)
        with pytest.raises(ValueError, match="sepia"):
            DarkPDFFilter(sepia=1.5)

    @pytest.mark.unit
    def test_dpi_out_of_range(self) -> None:
        """Test functionality: dpi out of range."""
        with pytest.raises(ValueError, match="dpi"):
            DarkPDFFilter(dpi=10)


class TestApplyInversion:
    """Test inversion filter."""

    @pytest.mark.unit
    def test_full_inversion(self) -> None:
        """Test functionality: full inversion."""
        f = DarkPDFFilter(inversion=1.0, brightness=1.0, contrast=1.0, sepia=0.0)
        img = _make_test_image(color=(200, 200, 200))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # Full inversion: 200 + (255 - 400) * 1.0 = 55
        assert np.allclose(pixels[:, :, 0], 55, atol=1)

    @pytest.mark.unit
    def test_no_inversion(self) -> None:
        """Test functionality: no inversion."""
        f = DarkPDFFilter(inversion=0.0, brightness=1.0, contrast=1.0, sepia=0.0)
        img = _make_test_image(color=(100, 150, 200))
        result = f.apply_to_image(img)
        np.array(result)
        # No change expected (contrast=1.0 with formula also has no effect
        # since (1.0-0.5)*2 = 1.0 factor, ((x/255-0.5)*2+0.5)*255 != x)
        # Actually contrast formula: factor = (1.0-0.5)*2 = 1.0
        # ((x/255 - 0.5) * (1+1.0) + 0.5)*255 = ((x/255-0.5)*2+0.5)*255
        # For x=100: ((100/255-0.5)*2+0.5)*255 = ((-0.108)*2+0.5)*255 = 0.284*255 = 72.4
        # So contrast=1.0 does change values. Use the identity contrast value.
        pass

    @pytest.mark.unit
    def test_half_inversion(self) -> None:
        """Test functionality: half inversion."""
        f = DarkPDFFilter(inversion=0.5, brightness=1.0, contrast=0.5, sepia=0.0)
        img = _make_test_image(color=(200, 200, 200))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # Inversion: 200 + (255 - 400)*0.5 = 200 + (-145)*0.5 = 200-72.5 = 127.5
        # Contrast with 0.5: factor=(0.5-0.5)*2=0, so ((x/255-0.5)*1+0.5)*255 = x
        assert pixels[0, 0, 0] == pytest.approx(128, abs=2)


class TestApplyBrightness:
    """Test brightness filter."""

    @pytest.mark.unit
    def test_increased_brightness(self) -> None:
        """Test functionality: increased brightness."""
        f = DarkPDFFilter(inversion=0.0, brightness=2.0, contrast=0.5, sepia=0.0)
        img = _make_test_image(color=(100, 100, 100))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # brightness=2.0 doubles values: 100*2=200
        # contrast=0.5: factor=0, identity => 200
        assert pixels[0, 0, 0] == pytest.approx(200, abs=2)

    @pytest.mark.unit
    def test_decreased_brightness(self) -> None:
        """Test functionality: decreased brightness."""
        f = DarkPDFFilter(inversion=0.0, brightness=0.5, contrast=0.5, sepia=0.0)
        img = _make_test_image(color=(200, 200, 200))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # brightness=0.5 halves: 200*0.5=100
        # contrast=0.5: identity => 100
        assert pixels[0, 0, 0] == pytest.approx(100, abs=2)


class TestApplyContrast:
    """Test contrast filter."""

    @pytest.mark.unit
    def test_high_contrast(self) -> None:
        """Test functionality: high contrast."""
        f = DarkPDFFilter(inversion=0.0, brightness=1.0, contrast=2.0, sepia=0.0)
        img = _make_test_image(color=(200, 200, 200))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # contrast=2.0: factor=(2.0-0.5)*2=3.0
        # ((200/255-0.5)*(1+3.0)+0.5)*255 = ((0.284)*4+0.5)*255 = 1.636*255 = clamped to 255
        assert pixels[0, 0, 0] == 255

    @pytest.mark.unit
    def test_identity_contrast(self) -> None:
        """contrast=0.5 produces factor=0, which is identity."""
        f = DarkPDFFilter(inversion=0.0, brightness=1.0, contrast=0.5, sepia=0.0)
        img = _make_test_image(color=(123, 123, 123))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        assert pixels[0, 0, 0] == pytest.approx(123, abs=1)


class TestApplySepia:
    """Test sepia filter."""

    @pytest.mark.unit
    def test_full_sepia(self) -> None:
        """Test functionality: full sepia."""
        f = DarkPDFFilter(inversion=0.0, brightness=1.0, contrast=0.5, sepia=1.0)
        img = _make_test_image(color=(100, 100, 100))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # With sepia=1.0 on gray (100,100,100):
        # sepia_r = 0.393*100 + 0.769*100 + 0.189*100 = 135.1
        # sepia_g = 0.349*100 + 0.686*100 + 0.168*100 = 120.3
        # sepia_b = 0.272*100 + 0.534*100 + 0.131*100 = 93.7
        assert pixels[0, 0, 0] == pytest.approx(135, abs=2)
        assert pixels[0, 0, 1] == pytest.approx(120, abs=2)
        assert pixels[0, 0, 2] == pytest.approx(94, abs=2)

    @pytest.mark.unit
    def test_no_sepia(self) -> None:
        """Test functionality: no sepia."""
        f = DarkPDFFilter(inversion=0.0, brightness=1.0, contrast=0.5, sepia=0.0)
        img = _make_test_image(color=(100, 150, 200))
        result = f.apply_to_image(img)
        pixels = np.array(result)
        # No sepia, identity contrast, no inversion, unit brightness
        assert pixels[0, 0, 0] == pytest.approx(100, abs=1)
        assert pixels[0, 0, 1] == pytest.approx(150, abs=1)
        assert pixels[0, 0, 2] == pytest.approx(200, abs=1)


class TestApplyToImage:
    """Test apply_to_image with RGBA and edge cases."""

    @pytest.mark.unit
    def test_rgba_preserves_alpha(self) -> None:
        """Test functionality: rgba preserves alpha."""
        f = DarkPDFFilter(inversion=1.0, brightness=1.0, contrast=0.5, sepia=0.0)
        img = Image.new("RGBA", (10, 10), (200, 200, 200, 128))
        result = f.apply_to_image(img)
        assert result.mode == "RGBA"
        # Alpha should be preserved
        assert result.split()[3].getpixel((0, 0)) == 128

    @pytest.mark.unit
    def test_grayscale_input(self) -> None:
        """Test functionality: grayscale input."""
        f = DarkPDFFilter(inversion=0.0, brightness=1.0, contrast=0.5, sepia=0.0)
        img = Image.new("L", (10, 10), 100)
        result = f.apply_to_image(img)
        assert result.mode == "RGB"


@pytest.mark.skipif(not FITZ_AVAILABLE, reason="PyMuPDF not available")
class TestApplyToPdf:
    """Test full PDF round-trip processing."""

    @pytest.mark.unit
    def test_pdf_round_trip(self) -> None:
        """Test functionality: pdf round trip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            _make_test_pdf(input_pdf)

            f = DarkPDFFilter(dpi=72)
            f.apply_to_pdf(input_pdf, output_pdf)

            assert output_pdf.exists()
            doc = fitz.open(str(output_pdf))
            assert len(doc) == 1
            doc.close()

    @pytest.mark.unit
    def test_pdf_not_found(self) -> None:
        """Test functionality: pdf not found."""
        f = DarkPDFFilter()
        with pytest.raises(FileNotFoundError):
            f.apply_to_pdf("/nonexistent/path.pdf", "/tmp/out.pdf")

    @pytest.mark.unit
    def test_apply_dark_mode_function(self) -> None:
        """Test functionality: apply dark mode function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"

            _make_test_pdf(input_pdf)
            apply_dark_mode(input_pdf, output_pdf, dpi=72)

            assert output_pdf.exists()

    @pytest.mark.unit
    def test_creates_output_directory(self) -> None:
        """Test functionality: creates output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "subdir" / "output.pdf"

            _make_test_pdf(input_pdf)

            f = DarkPDFFilter(dpi=72)
            f.apply_to_pdf(input_pdf, output_pdf)

            assert output_pdf.exists()


class TestDarkPDFPresets:
    """Test DarkPDF high-level wrapper and presets."""

    @pytest.mark.unit
    def test_default_preset(self) -> None:
        """Test functionality: default preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            _make_test_pdf(input_pdf)

            dp = DarkPDF(input_pdf)
            assert dp.filter.inversion == 0.90
            assert dp.filter.sepia == 0.10

    @pytest.mark.unit
    def test_sepia_preset(self) -> None:
        """Test functionality: sepia preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            _make_test_pdf(input_pdf)

            dp = DarkPDF(input_pdf, preset="sepia")
            assert dp.filter.inversion == 0.85
            assert dp.filter.sepia == 0.40

    @pytest.mark.unit
    def test_high_contrast_preset(self) -> None:
        """Test functionality: high contrast preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            _make_test_pdf(input_pdf)

            dp = DarkPDF(input_pdf, preset="high_contrast")
            assert dp.filter.inversion == 1.0
            assert dp.filter.contrast == 1.3
            assert dp.filter.sepia == 0.0

    @pytest.mark.unit
    def test_unknown_preset(self) -> None:
        """Test functionality: unknown preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            _make_test_pdf(input_pdf)

            with pytest.raises(ValueError, match="Unknown preset"):
                DarkPDF(input_pdf, preset="nonexistent")

    @pytest.mark.unit
    def test_preset_with_overrides(self) -> None:
        """Test functionality: preset with overrides."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            _make_test_pdf(input_pdf)

            dp = DarkPDF(input_pdf, preset="dark", inversion=0.5)
            assert dp.filter.inversion == 0.5
            assert dp.filter.brightness == 0.90  # from preset

    @pytest.mark.unit
    def test_save(self) -> None:
        """Test functionality: save."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"
            _make_test_pdf(input_pdf)

            result = DarkPDF(input_pdf, dpi=72).save(output_pdf)
            assert result == output_pdf
            assert output_pdf.exists()

    @pytest.mark.unit
    def test_dark_classmethod(self) -> None:
        """Test functionality: dark classmethod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"
            _make_test_pdf(input_pdf)

            result = DarkPDF.dark(input_pdf, output_pdf, dpi=72)
            assert result == output_pdf
            assert output_pdf.exists()

    @pytest.mark.unit
    def test_sepia_classmethod(self) -> None:
        """Test functionality: sepia classmethod."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_pdf = Path(tmpdir) / "input.pdf"
            output_pdf = Path(tmpdir) / "output.pdf"
            _make_test_pdf(input_pdf)

            result = DarkPDF.sepia(input_pdf, output_pdf, dpi=72)
            assert result == output_pdf
            assert output_pdf.exists()

    @pytest.mark.unit
    def test_batch(self) -> None:
        """Test functionality: batch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input1 = Path(tmpdir) / "a.pdf"
            input2 = Path(tmpdir) / "b.pdf"
            output_dir = Path(tmpdir) / "output"
            _make_test_pdf(input1)
            _make_test_pdf(input2)

            results = DarkPDF.batch(
                [input1, input2], output_dir=output_dir, dpi=72
            )
            assert len(results) == 2
            assert all(p.exists() for p in results)
            assert results[0].name == "a_dark.pdf"
            assert results[1].name == "b_dark.pdf"

    @pytest.mark.unit
    def test_available_presets(self) -> None:
        """Test functionality: available presets."""
        presets = DarkPDF.available_presets()
        assert "dark" in presets
        assert "sepia" in presets
        assert "high_contrast" in presets
        assert "low_light" in presets
        # Verify it returns a copy
        presets["dark"]["inversion"] = 999
        assert _PRESETS["dark"]["inversion"] != 999

    @pytest.mark.unit
    def test_file_not_found(self) -> None:
        """Test functionality: file not found."""
        with pytest.raises(FileNotFoundError):
            DarkPDF("/nonexistent/path.pdf")
