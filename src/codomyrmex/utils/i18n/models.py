"""Internationalization models and data types."""

from dataclasses import dataclass


@dataclass
class Locale:
    """A locale specification."""
    language: str  # ISO 639-1 (e.g., "en", "es")
    region: str = ""  # ISO 3166-1 (e.g., "US", "MX")

    @property
    def code(self) -> str:
        """Execute Code operations natively."""
        if self.region:
            return f"{self.language}_{self.region}"
        return self.language

    @classmethod
    def from_string(cls, code: str) -> "Locale":
        """Execute From String operations natively."""
        parts = code.replace("-", "_").split("_")
        language = parts[0].lower()
        region = parts[1].upper() if len(parts) > 1 else ""
        return cls(language=language, region=region)

    def __str__(self) -> str:
        """Execute   Str   operations natively."""
        return self.code
