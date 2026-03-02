"""Statistical detection of steganographic content.

Provides tools for detecting hidden data in images and arbitrary byte
sequences using statistical analysis of bit-level distributions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from codomyrmex.crypto.exceptions import SteganographyError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class DetectionResult:
    """Result of a steganography detection analysis."""

    detected: bool
    confidence: float  # 0.0 to 1.0
    method: str
    details: dict = field(default_factory=dict)


def detect_lsb_steganography(image_path: str) -> DetectionResult:
    """Detect LSB steganography in a PNG image.

    Performs statistical analysis of the least significant bit plane
    compared to other bit planes. LSB embedding tends to produce a
    more uniform LSB distribution and disrupts the natural correlation
    between bit planes.

    Analysis methods:
    1. Chi-squared test on LSB pairs (sample-pairs analysis)
    2. Comparison of LSB entropy vs higher bit plane entropy
    3. Check for length header pattern in first 32 LSBs

    Args:
        image_path: Path to the PNG image to analyze.

    Returns:
        DetectionResult with detection status, confidence, and details.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise SteganographyError("Pillow is required for image analysis") from e

    try:
        img = Image.open(image_path)
    except Exception as e:
        raise SteganographyError(f"Cannot open image: {e}") from e

    if img.mode != "RGB":
        img = img.convert("RGB")

    width, height = img.size
    pixels = img.load()

    # Extract bit planes
    lsb_values: list[int] = []
    bit1_values: list[int] = []  # second-least significant bit

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            lsb_values.extend([r & 1, g & 1, b & 1])
            bit1_values.extend([(r >> 1) & 1, (g >> 1) & 1, (b >> 1) & 1])

    total_lsbs = len(lsb_values)
    if total_lsbs == 0:
        return DetectionResult(
            detected=False, confidence=0.0,
            method="lsb_analysis", details={"error": "No pixel data"},
        )

    # Test 1: LSB distribution uniformity
    # Natural images have biased LSBs; embedded data makes them ~50/50
    ones_count = sum(lsb_values)
    total_lsbs - ones_count
    lsb_ratio = ones_count / total_lsbs if total_lsbs > 0 else 0.5
    lsb_bias = abs(lsb_ratio - 0.5)

    # Test 2: Chi-squared on LSB pairs
    # Count pairs: (0,0), (0,1), (1,0), (1,1)
    pair_counts = [0, 0, 0, 0]
    for i in range(0, total_lsbs - 1, 2):
        pair_idx = lsb_values[i] * 2 + lsb_values[i + 1]
        pair_counts[pair_idx] += 1

    total_pairs = sum(pair_counts)
    expected_pairs = total_pairs / 4.0

    if expected_pairs > 0:
        chi2_pairs = sum(
            (count - expected_pairs) ** 2 / expected_pairs
            for count in pair_counts
        )
        # Normalize chi-squared by degrees of freedom (3)
        chi2_normalized = chi2_pairs / 3.0
    else:
        chi2_normalized = 0.0

    # Test 3: Compare LSB entropy to bit-1 entropy
    # In natural images, LSBs correlate with higher bits
    # After embedding, LSBs become more random / independent
    ones_count / total_lsbs if total_lsbs > 0 else 0.5
    bit1_ones = sum(bit1_values)
    bit1_ones / len(bit1_values) if bit1_values else 0.5

    # Measure how "random" the LSBs are (closer to 0.5 = more suspicious)
    lsb_randomness = 1.0 - 2.0 * abs(lsb_ratio - 0.5)

    # Test 4: Check for plausible length header in first 32 LSBs
    has_length_header = False
    if total_lsbs >= 32:
        header_bits = lsb_values[:32]
        header_value = 0
        for bit in header_bits:
            header_value = (header_value << 1) | bit
        # Check if header_value is a plausible message length
        max_capacity = (total_lsbs // 8) - 4
        if 0 < header_value <= max_capacity:
            has_length_header = True

    # Combine signals into confidence score
    confidence = 0.0

    # Low LSB bias suggests embedding (natural images are slightly biased)
    if lsb_bias < 0.01:
        confidence += 0.3
    elif lsb_bias < 0.03:
        confidence += 0.15

    # Low chi-squared on pairs suggests uniform (embedded) distribution
    if chi2_normalized < 1.0:
        confidence += 0.2
    elif chi2_normalized < 2.0:
        confidence += 0.1

    # High LSB randomness is suspicious
    if lsb_randomness > 0.95:
        confidence += 0.2
    elif lsb_randomness > 0.90:
        confidence += 0.1

    # Valid length header is strong evidence
    if has_length_header:
        confidence += 0.3

    confidence = min(1.0, confidence)
    detected = confidence >= 0.5

    details = {
        "lsb_ratio": round(lsb_ratio, 6),
        "lsb_bias": round(lsb_bias, 6),
        "chi2_pairs_normalized": round(chi2_normalized, 4),
        "lsb_randomness": round(lsb_randomness, 6),
        "has_length_header": has_length_header,
        "image_size": f"{width}x{height}",
        "total_lsbs": total_lsbs,
    }

    logger.debug(
        "LSB detection: detected=%s, confidence=%.2f, bias=%.4f",
        detected, confidence, lsb_bias,
    )
    return DetectionResult(
        detected=detected, confidence=confidence,
        method="lsb_analysis", details=details,
    )


def analyze_statistical_anomalies(data: bytes) -> DetectionResult:
    """Detect statistical anomalies that may indicate steganographic content.

    Performs general-purpose analysis of byte data looking for patterns
    commonly associated with embedded hidden data.

    Analysis includes:
    1. Byte entropy measurement
    2. Bit-level distribution analysis
    3. Pattern detection for common stego format headers

    Args:
        data: Raw bytes to analyze.

    Returns:
        DetectionResult with anomaly detection status and details.
    """
    if not data:
        return DetectionResult(
            detected=False, confidence=0.0,
            method="statistical_anomaly",
            details={"error": "Empty data"},
        )

    from codomyrmex.crypto.analysis.entropy import byte_entropy, chi_squared_test

    # Test 1: Byte entropy
    entropy = byte_entropy(data)
    # Very high entropy (>7.9) in non-compressed data is suspicious
    # Very low entropy (<1.0) is also unusual

    # Test 2: Bit distribution per position
    bit_counts = [0] * 8
    for byte in data:
        for i in range(8):
            if byte & (1 << i):
                bit_counts[i] += 1

    total_bytes = len(data)
    bit_ratios = [count / total_bytes for count in bit_counts]
    # Check if LSBs are unusually uniform compared to higher bits
    lsb_ratio = bit_ratios[0]
    bit_ratios[7]
    lsb_uniformity = 1.0 - 2.0 * abs(lsb_ratio - 0.5)

    # Test 3: Check for embedded length headers
    # Common stego formats prepend a 4-byte big-endian length
    has_plausible_header = False
    if len(data) >= 4:
        import struct

        potential_length = struct.unpack(">I", data[:4])[0]
        if 0 < potential_length <= len(data) - 4:
            has_plausible_header = True

    # Test 4: Chi-squared uniformity
    try:
        chi_result = chi_squared_test(data)
        is_uniform = chi_result.uniform
    except ValueError:
        is_uniform = False

    # Build confidence
    confidence = 0.0

    if entropy > 7.9:
        confidence += 0.25
    elif entropy > 7.5:
        confidence += 0.1

    if lsb_uniformity > 0.95:
        confidence += 0.2

    if has_plausible_header:
        confidence += 0.3

    if is_uniform:
        confidence += 0.15

    confidence = min(1.0, confidence)
    detected = confidence >= 0.5

    details = {
        "byte_entropy": round(entropy, 4),
        "lsb_ratio": round(lsb_ratio, 6),
        "lsb_uniformity": round(lsb_uniformity, 6),
        "has_plausible_header": has_plausible_header,
        "chi_squared_uniform": is_uniform,
        "data_length": len(data),
    }

    logger.debug(
        "Statistical anomaly: detected=%s, confidence=%.2f, entropy=%.4f",
        detected, confidence, entropy,
    )
    return DetectionResult(
        detected=detected, confidence=confidence,
        method="statistical_anomaly", details=details,
    )
