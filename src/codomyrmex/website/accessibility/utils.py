"""Accessibility utility functions."""


def calculate_contrast_ratio(fg: str, bg: str) -> float:
    """Calculate WCAG contrast ratio between two colors."""
    def hex_to_luminance(hex_color: str) -> float:
        """Execute Hex To Luminance operations natively."""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]

        def adjust(c):
            """Execute Adjust operations natively."""
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    try:
        l1 = hex_to_luminance(fg)
        l2 = hex_to_luminance(bg)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
    except (ValueError, IndexError):
        return 0.0


def check_heading_hierarchy(headings: list[int]) -> list[str]:
    """Check heading level hierarchy."""
    issues = []
    prev_level = 0

    for level in headings:
        if level > prev_level + 1:
            issues.append(f"Skipped heading level: h{prev_level} to h{level}")
        prev_level = level

    if headings and headings[0] != 1:
        issues.append("Document should start with h1")

    return issues
