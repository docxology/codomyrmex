"""High-level convenience wrapper for PDF dark mode processing.

Provides a fluent API with preset configurations for common dark mode
use cases, plus batch processing support.
"""

from __future__ import annotations

from pathlib import Path

from .filters import DarkPDFFilter

# Preset configurations matching common use cases
_PRESETS: dict[str, dict[str, float]] = {
    "dark": {
        "inversion": 0.90,
        "brightness": 0.90,
        "contrast": 0.90,
        "sepia": 0.10,
    },
    "sepia": {
        "inversion": 0.85,
        "brightness": 0.95,
        "contrast": 0.90,
        "sepia": 0.40,
    },
    "high_contrast": {
        "inversion": 1.0,
        "brightness": 1.0,
        "contrast": 1.3,
        "sepia": 0.0,
    },
    "low_light": {
        "inversion": 0.80,
        "brightness": 0.70,
        "contrast": 0.85,
        "sepia": 0.05,
    },
}


class DarkPDF:
    """High-level API for applying dark mode to PDFs.

    Supports preset configurations, custom filter parameters, and batch
    processing.

    Examples:
        Simple one-call usage:
            >>> DarkPDF("input.pdf").save("output.pdf")

        With a preset:
            >>> DarkPDF("input.pdf", preset="sepia").save("output.pdf")

        Custom parameters:
            >>> DarkPDF("input.pdf", inversion=0.85, contrast=1.2).save("output.pdf")

        Class method shortcuts:
            >>> DarkPDF.dark("input.pdf", "output.pdf")
            >>> DarkPDF.sepia("input.pdf", "output.pdf")

        Batch processing:
            >>> DarkPDF.batch(["a.pdf", "b.pdf"], output_dir="dark_pdfs/")
    """

    def __init__(
        self,
        input_path: str | Path,
        *,
        preset: str | None = None,
        inversion: float | None = None,
        brightness: float | None = None,
        contrast: float | None = None,
        sepia: float | None = None,
        dpi: int = 150,
    ) -> None:
        """Initialize with an input PDF and filter configuration.

        Args:
            input_path: Path to the input PDF file.
            preset: Named preset ("dark", "sepia", "high_contrast", "low_light").
                If provided, individual parameters override the preset values.
            inversion: Inversion amount, 0.0-1.0.
            brightness: Brightness multiplier, 0.1-3.0.
            contrast: Contrast multiplier, 0.1-3.0.
            sepia: Sepia amount, 0.0-1.0.
            dpi: Resolution for rendering PDF pages (default 150).

        Raises:
            ValueError: If preset name is unknown.
            FileNotFoundError: If input_path does not exist.
        """
        self.input_path = Path(input_path)

        if not self.input_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {self.input_path}")

        # Start with preset defaults or standard defaults
        if preset is not None:
            if preset not in _PRESETS:
                raise ValueError(
                    f"Unknown preset '{preset}'. Available: {list(_PRESETS.keys())}"
                )
            params = dict(_PRESETS[preset])
        else:
            params = dict(_PRESETS["dark"])

        # Override with explicit parameters
        if inversion is not None:
            params["inversion"] = inversion
        if brightness is not None:
            params["brightness"] = brightness
        if contrast is not None:
            params["contrast"] = contrast
        if sepia is not None:
            params["sepia"] = sepia

        self.filter = DarkPDFFilter(
            inversion=params["inversion"],
            brightness=params["brightness"],
            contrast=params["contrast"],
            sepia=params["sepia"],
            dpi=dpi,
        )

    @property
    def current_filter(self) -> DarkPDFFilter:
        """Return the current filter configuration."""
        return self.filter

    @property
    def page_count(self) -> int:
        """Return the number of pages in the input PDF."""
        import fitz

        doc = fitz.open(str(self.input_path))
        count = len(doc)
        doc.close()
        return count

    def set_filter(self, preset: str | DarkPDFFilter) -> DarkPDF:
        """set the filter to a preset or a custom DarkPDFFilter.

        Args:
            preset: Preset name or DarkPDFFilter instance.

        Returns:
            self for chaining.
        """
        if isinstance(preset, DarkPDFFilter):
            self.filter = preset
        elif preset in _PRESETS:
            params = _PRESETS[preset]
            self.filter = DarkPDFFilter(
                inversion=params["inversion"],
                brightness=params["brightness"],
                contrast=params["contrast"],
                sepia=params["sepia"],
                dpi=self.filter.dpi,
            )
        else:
            raise ValueError(
                f"Unknown preset '{preset}'. Available: {list(_PRESETS.keys())}"
            )
        return self

    def set_brightness(self, value: float) -> DarkPDF:
        """set brightness multiplier.

        Args:
            value: Brightness multiplier, 0.1-3.0.

        Returns:
            self for chaining.
        """
        self.filter.brightness = value
        self.filter.validate()
        return self

    def set_contrast(self, value: float) -> DarkPDF:
        """set contrast multiplier.

        Args:
            value: Contrast multiplier, 0.1-3.0.

        Returns:
            self for chaining.
        """
        self.filter.contrast = value
        self.filter.validate()
        return self

    def set_inversion(self, value: float) -> DarkPDF:
        """set inversion amount.

        Args:
            value: Inversion amount, 0.0-1.0.

        Returns:
            self for chaining.
        """
        self.filter.inversion = value
        self.filter.validate()
        return self

    def set_sepia(self, value: float) -> DarkPDF:
        """set sepia amount.

        Args:
            value: Sepia amount, 0.0-1.0.

        Returns:
            self for chaining.
        """
        self.filter.sepia = value
        self.filter.validate()
        return self

    def process(self) -> DarkPDF:
        """Process the PDF. (Placeholder for internal consistency)

        In this implementation, processing happens during save().
        This method is provided for API compatibility with AGENTS.md patterns.

        Returns:
            self for chaining.
        """
        return self

    def save(self, output_path: str | Path) -> Path:
        """Apply dark mode and save the result.

        Args:
            output_path: Path for the output PDF file.

        Returns:
            Path to the saved output file.
        """
        output_path = Path(output_path)
        self.filter.apply_to_pdf(self.input_path, output_path)
        return output_path

    @classmethod
    def dark(
        cls,
        input_path: str | Path,
        output_path: str | Path,
        **kwargs: float,
    ) -> Path:
        """Apply the 'dark' preset and save.

        Args:
            input_path: Path to the input PDF.
            output_path: Path for the output PDF.
            **kwargs: Override individual filter parameters.

        Returns:
            Path to the saved output file.
        """
        return cls(input_path, preset="dark", **kwargs).save(output_path)

    @classmethod
    def sepia(
        cls,
        input_path: str | Path,
        output_path: str | Path,
        **kwargs: float,
    ) -> Path:
        """Apply the 'sepia' preset and save.

        Args:
            input_path: Path to the input PDF.
            output_path: Path for the output PDF.
            **kwargs: Override individual filter parameters.

        Returns:
            Path to the saved output file.
        """
        return cls(input_path, preset="sepia", **kwargs).save(output_path)

    @classmethod
    def batch(
        cls,
        input_paths: list[str | Path],
        *,
        output_dir: str | Path,
        preset: str = "dark",
        suffix: str = "_dark",
        **kwargs: float,
    ) -> list[Path]:
        """Process multiple PDFs with the same settings.

        Args:
            input_paths: list of input PDF paths.
            output_dir: Directory for output files.
            preset: Preset to use (default "dark").
            suffix: Suffix to append to filenames (default "_dark").
            **kwargs: Override individual filter parameters.

        Returns:
            list of paths to saved output files.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for input_path in input_paths:
            input_path = Path(input_path)
            output_path = output_dir / f"{input_path.stem}{suffix}.pdf"
            result = cls(input_path, preset=preset, **kwargs).save(output_path)
            results.append(result)

        return results

    @staticmethod
    def available_presets() -> dict[str, dict[str, float]]:
        """Return a copy of available preset configurations.

        Returns:
            Dictionary mapping preset names to their filter parameters.
        """
        return {k: dict(v) for k, v in _PRESETS.items()}
