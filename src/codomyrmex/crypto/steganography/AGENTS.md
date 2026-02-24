# crypto/steganography -- Agent Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Summary

The `crypto/steganography` submodule provides tools for hiding data within images (LSB embedding) and text (zero-width characters), along with statistical detection methods to identify steganographic content.

## When to Use This Module

- You need to hide a message or payload inside an image using least-significant-bit (LSB) embedding
- You need to hide data in text using zero-width Unicode characters
- You need to extract hidden data from a steganographic image or text
- You need to calculate the maximum data capacity of an image for LSB embedding
- You need to detect whether an image contains LSB steganography via statistical analysis

## Exports

**Image Steganography:**

| Name | Kind | Purpose |
|------|------|---------|
| `embed_in_image` | function | Embed data in image using LSB technique |
| `extract_from_image` | function | Extract hidden data from LSB-encoded image |
| `calculate_capacity` | function | Calculate maximum embedding capacity (bytes) for an image |

**Text Steganography:**

| Name | Kind | Purpose |
|------|------|---------|
| `embed_in_text` | function | Hide data in text using zero-width characters |
| `extract_from_text` | function | Extract hidden data from zero-width encoded text |

**Detection:**

| Name | Kind | Purpose |
|------|------|---------|
| `DetectionResult` | dataclass | Container for detection analysis results |
| `detect_lsb_steganography` | function | Detect LSB steganography in an image |
| `analyze_statistical_anomalies` | function | General statistical anomaly detection for stego analysis |

## Example Agent Usage

```python
from codomyrmex.crypto.steganography import (
    embed_in_image, extract_from_image, calculate_capacity,
    embed_in_text, extract_from_text,
    detect_lsb_steganography,
)

# Image steganography
capacity = calculate_capacity("cover.png")
stego_image = embed_in_image("cover.png", b"hidden message")
recovered = extract_from_image(stego_image)

# Text steganography
stego_text = embed_in_text("Normal looking text.", b"secret")
recovered = extract_from_text(stego_text)

# Detection
result = detect_lsb_steganography("suspect.png")
print(result.detected, result.confidence)
```

## Constraints

- Image LSB embedding requires image files (PNG recommended; JPEG lossy compression destroys LSB data).
- Capacity depends on image dimensions and color channels.
- Zero-width character embedding may be stripped by some text processors or messaging platforms.
- Detection is probabilistic; `confidence` indicates likelihood, not certainty.

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `crypto.analysis` | Entropy and frequency analysis can complement stego detection |
| `crypto.encoding` | Base64/hex encoding for payloads before embedding |
| `encryption.algorithms` | Encrypt payload before embedding for layered security |
