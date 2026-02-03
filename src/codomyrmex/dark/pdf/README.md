# PDF Dark Mode Submodule

Native Python implementation of PDF dark mode filters, inspired by [dark-pdf](https://github.com/benjifriedman/dark-pdf).

## How It Works

1. Each PDF page is rendered to a raster image using PyMuPDF
2. Pixel-level filters (inversion, brightness, contrast, sepia) are applied using NumPy
3. Filtered pages are reassembled into a new PDF

The filter math matches dark-pdf's JavaScript pixel processing pipeline, ensuring visual consistency with the original web application.

## Dependencies

- **PyMuPDF** (`fitz`) - PDF rendering and page extraction
- **Pillow** - Image manipulation
- **NumPy** - Vectorized pixel operations

Install with:
```bash
uv sync --extra dark
```

## Usage

```python
from codomyrmex.dark.pdf import DarkPDF, DarkPDFFilter, apply_dark_mode

# One-liner
DarkPDF("paper.pdf").save("paper_dark.pdf")

# With sepia preset
DarkPDF("paper.pdf", preset="sepia").save("paper_sepia.pdf")

# Full control
f = DarkPDFFilter(inversion=0.95, brightness=0.85, contrast=1.1, sepia=0.0)
f.apply_to_pdf("input.pdf", "output.pdf")

# Process a single image
from PIL import Image
img = Image.open("page.png")
dark_img = f.apply_to_image(img)
dark_img.save("page_dark.png")
```

## Vendor

The original dark-pdf source is included as a git submodule at `vendor/dark-pdf/` for reference. It is a Next.js web application and is not used at runtime by the Python implementation.

To initialize the submodule:
```bash
git submodule update --init --recursive
```

## Filter Pipeline

Filters are applied in this order:

1. **Inversion** - `pixel = pixel + (255 - 2*pixel) * inversion`
2. **Brightness** - `pixel *= brightness`
3. **Contrast** - `pixel = ((pixel/255 - 0.5) * (1 + factor) + 0.5) * 255`
4. **Sepia** - Blends with sepia color matrix (standard ITU coefficients)
5. **Clamp** - Values clamped to [0, 255]
