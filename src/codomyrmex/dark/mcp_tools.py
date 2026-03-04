"""MCP tools for the dark module.

Exposes PDF dark mode conversion and preset retrieval as
auto-discovered MCP tools.
"""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="dark",
    description=(
        "Convert a PDF file to dark mode. Provide 'input_path' (string path to input PDF) "
        "and 'output_path' (string path to save output PDF). Optionally provide "
        "'preset' (string, e.g., 'dark', 'sepia', 'high_contrast', 'low_light'), "
        "and numerical overrides: 'inversion', 'brightness', 'contrast', 'sepia', 'dpi'."
    ),
)
def dark_pdf_convert(
    input_path: str,
    output_path: str,
    preset: str | None = None,
    inversion: float | None = None,
    brightness: float | None = None,
    contrast: float | None = None,
    sepia: float | None = None,
    dpi: int = 150,
) -> dict:
    """Convert a PDF file to dark mode.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path for the output PDF file.
        preset: Named preset ("dark", "sepia", "high_contrast", "low_light").
        inversion: Inversion amount, 0.0-1.0.
        brightness: Brightness multiplier, 0.1-3.0.
        contrast: Contrast multiplier, 0.1-3.0.
        sepia: Sepia amount, 0.0-1.0.
        dpi: Resolution for rendering PDF pages (default 150).

    Returns:
        Dictionary indicating success or failure.
    """
    from codomyrmex.dark.pdf import apply_dark_mode

    kwargs: dict = {"dpi": dpi}
    if preset is not None:
        kwargs["preset"] = preset
    if inversion is not None:
        kwargs["inversion"] = inversion
    if brightness is not None:
        kwargs["brightness"] = brightness
    if contrast is not None:
        kwargs["contrast"] = contrast
    if sepia is not None:
        kwargs["sepia"] = sepia

    try:
        apply_dark_mode(input_path, output_path, **kwargs)
        return {"success": True, "output_path": output_path}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp_tool(
    category="dark",
    description=(
        "Process multiple PDFs to dark mode in a batch. Provide 'input_paths' "
        "(list of string paths) and 'output_dir' (directory string). Optionally provide "
        "'preset' (string, default 'dark') and 'suffix' (string, default '_dark')."
    ),
)
def dark_pdf_batch(
    input_paths: list[str],
    output_dir: str,
    preset: str = "dark",
    suffix: str = "_dark",
    dpi: int = 150,
) -> dict:
    """Process multiple PDFs with the same settings.

    Args:
        input_paths: List of input PDF paths.
        output_dir: Directory for output files.
        preset: Preset to use (default "dark").
        suffix: Suffix to append to filenames (default "_dark").
        dpi: Resolution for rendering PDF pages (default 150).

    Returns:
        Dictionary with list of saved outputs or error.
    """
    from codomyrmex.dark.pdf import DarkPDF

    try:
        results = DarkPDF.batch(
            input_paths,
            output_dir=output_dir,
            preset=preset,
            suffix=suffix,
            dpi=dpi,
        )
        return {"success": True, "output_paths": [str(p) for p in results]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


@mcp_tool(
    category="dark",
    description=(
        "Get available dark mode presets and their configuration values. "
        "Returns a dictionary of preset names mapped to their settings."
    ),
)
def dark_get_presets() -> dict:
    """Return available preset configurations.

    Returns:
        Dictionary mapping preset names to their filter parameters.
    """
    from codomyrmex.dark.pdf import DarkPDF

    return DarkPDF.available_presets()
