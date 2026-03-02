# Crypto Steganography -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Steganographic embedding and extraction for images (LSB technique) and text (zero-width Unicode characters), plus statistical detection methods to identify hidden data in media.

## Architecture

```
crypto/steganography/
├── __init__.py     # 8 re-exports across 3 submodules
├── image.py        # LSB image steganography (embed, extract, capacity)
├── text.py         # Zero-width character text steganography
└── detection.py    # Statistical detection of hidden data
```

## Key Classes and Functions

### image.py

| Name | Kind | Description |
|------|------|-------------|
| `embed_in_image` | function | Embed secret data into an image using LSB substitution |
| `extract_from_image` | function | Extract hidden data from an LSB-encoded image |
| `calculate_capacity` | function | Calculate the maximum payload size for a given image |

### text.py

| Name | Kind | Description |
|------|------|-------------|
| `embed_in_text` | function | Hide data in text using zero-width Unicode characters |
| `extract_from_text` | function | Extract hidden data from zero-width-encoded text |

### detection.py

| Name | Kind | Description |
|------|------|-------------|
| `DetectionResult` | dataclass | Detection result with confidence score and analysis details |
| `detect_lsb_steganography` | function | Detect LSB steganography in an image via chi-squared analysis |
| `analyze_statistical_anomalies` | function | Analyze media for statistical anomalies indicating hidden data |

## Dependencies

- `Pillow` (PIL) for image manipulation (optional; image functions raise `ImportError` if absent)
- Python standard library for text operations

## Constraints

- Image steganography operates on the least significant bit of each color channel.
- Maximum payload is limited by image dimensions (approximately width * height * 3 / 8 bytes for RGB).
- Text steganography uses Unicode zero-width characters (U+200B, U+200C, U+200D, U+FEFF).

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Payload exceeds image capacity, no hidden data found during extraction |
| `ImportError` | Pillow not installed when calling image functions |

## Navigation

- **Parent**: [crypto/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
