# Dark Module API Specification

## Overview

This document provides the complete API reference for the dark module's PDF submodule, including filter configuration, processing, and convenience wrappers.

## PDF Filters API

### DarkPDFFilter

Configurable dark mode filter for PDF pages. Applies pixel-level transformations matching dark-pdf's filter logic.

#### Constructor

```python
DarkPDFFilter(
    inversion: float = 0.90,
    brightness: float = 0.90,
    contrast: float = 0.90,
    sepia: float = 0.10,
    dpi: int = 150,
) -> DarkPDFFilter
```

**Parameters:**
- `inversion`: Inversion amount, 0.0-1.0 (default 0.90)
- `brightness`: Brightness multiplier, 0.1-3.0 (default 0.90)
- `contrast`: Contrast multiplier, 0.1-3.0 (default 0.90)
- `sepia`: Sepia amount, 0.0-1.0 (default 0.10)
- `dpi`: Resolution for rendering PDF pages to images (default 150)

**Raises:** `ValueError` if any parameter is out of range.

#### Methods

##### apply_to_image

```python
def apply_to_image(image: PIL.Image.Image) -> PIL.Image.Image
```

Apply dark mode filters to a PIL Image.

**Parameters:**
- `image`: Input PIL Image (RGB or RGBA)

**Returns:** New PIL Image with filters applied.

##### apply_to_pdf

```python
def apply_to_pdf(
    input_path: str | Path,
    output_path: str | Path,
) -> None
```

Apply dark mode filters to an entire PDF. Renders each page as an image, applies filters, then reassembles into a new PDF.

**Parameters:**
- `input_path`: Path to the input PDF file
- `output_path`: Path for the output PDF file

**Raises:**
- `FileNotFoundError`: If input_path does not exist
- `RuntimeError`: If PDF processing fails

---

### apply_dark_mode

```python
def apply_dark_mode(
    input_path: str | Path,
    output_path: str | Path,
    *,
    inversion: float = 0.90,
    brightness: float = 0.90,
    contrast: float = 0.90,
    sepia: float = 0.10,
    dpi: int = 150,
) -> None
```

Convenience function that creates a DarkPDFFilter and processes the PDF.

**Parameters:**
- `input_path`: Path to the input PDF file
- `output_path`: Path for the output PDF file
- `inversion`: Inversion amount, 0.0-1.0 (default 0.90)
- `brightness`: Brightness multiplier, 0.1-3.0 (default 0.90)
- `contrast`: Contrast multiplier, 0.1-3.0 (default 0.90)
- `sepia`: Sepia amount, 0.0-1.0 (default 0.10)
- `dpi`: Resolution for rendering PDF pages (default 150)

---

### DarkPDF

High-level convenience wrapper with presets and batch processing.

#### Constructor

```python
DarkPDF(
    input_path: str | Path,
    *,
    preset: str | None = None,
    inversion: float | None = None,
    brightness: float | None = None,
    contrast: float | None = None,
    sepia: float | None = None,
    dpi: int = 150,
) -> DarkPDF
```

**Parameters:**
- `input_path`: Path to the input PDF file
- `preset`: Named preset ("dark", "sepia", "high_contrast", "low_light"). Individual parameters override preset values.
- `inversion`, `brightness`, `contrast`, `sepia`: Override individual filter values
- `dpi`: Resolution for rendering (default 150)

**Raises:**
- `ValueError`: If preset name is unknown
- `FileNotFoundError`: If input_path does not exist

#### Methods

##### save

```python
def save(output_path: str | Path) -> Path
```

Apply dark mode and save the result.

**Returns:** Path to the saved output file.

##### dark (classmethod)

```python
@classmethod
def dark(input_path, output_path, **kwargs) -> Path
```

Apply the 'dark' preset and save.

##### sepia (classmethod)

```python
@classmethod
def sepia(input_path, output_path, **kwargs) -> Path
```

Apply the 'sepia' preset and save.

##### batch (classmethod)

```python
@classmethod
def batch(
    input_paths: list[str | Path],
    *,
    output_dir: str | Path,
    preset: str = "dark",
    suffix: str = "_dark",
    **kwargs,
) -> list[Path]
```

Process multiple PDFs with the same settings.

**Parameters:**
- `input_paths`: List of input PDF paths
- `output_dir`: Directory for output files
- `preset`: Preset to use (default "dark")
- `suffix`: Suffix to append to filenames (default "_dark")

**Returns:** List of paths to saved output files.

##### available_presets (staticmethod)

```python
@staticmethod
def available_presets() -> dict[str, dict[str, float]]
```

Return available preset configurations.

## Filter Pipeline

The filter pipeline processes pixels in this order:

1. **Inversion**: `pixel = pixel + (255 - 2 * pixel) * inversion`
2. **Brightness**: `pixel *= brightness`
3. **Contrast**: `pixel = ((pixel/255 - 0.5) * (1 + factor) + 0.5) * 255`
4. **Sepia**: Blends original RGB with sepia transform matrix
5. **Clamp**: All values clamped to 0-255
