"""Shared data models for the vision module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VLMConfig:
    """Configuration for a Vision-Language Model client.

    Attributes:
        model_name: Ollama model name (e.g. ``"llava"``, ``"bakllava"``).
        host: Ollama server host.
        port: Ollama server port.
        temperature: Sampling temperature.
        max_tokens: Maximum response tokens.
        timeout: Request timeout in seconds.
    """

    model_name: str = "llava"
    host: str = "localhost"
    port: int = 11434
    temperature: float = 0.2
    max_tokens: int = 2048
    timeout: float = 60.0


@dataclass
class VLMResponse:
    """Response from a VLM analysis.

    Attributes:
        text: Generated text response.
        model: Model that generated the response.
        confidence: Response confidence (if available).
        metadata: Additional response metadata.
    """

    text: str
    model: str = ""
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BoundingBox:
    """A bounding box for spatial annotation.

    Attributes:
        x: Left coordinate (0–1 normalized).
        y: Top coordinate (0–1 normalized).
        width: Width (0–1 normalized).
        height: Height (0–1 normalized).
    """

    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def area(self) -> float:
        """Calculate bounding box area."""
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        """Return the center point."""
        return (self.x + self.width / 2, self.y + self.height / 2)


@dataclass
class Annotation:
    """A structured annotation extracted from an image.

    Attributes:
        label: Annotation label/class.
        bounding_box: Spatial location.
        confidence: Detection confidence.
        attributes: Additional key-value attributes.
    """

    label: str
    bounding_box: BoundingBox = field(default_factory=BoundingBox)
    confidence: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class PageContent:
    """Extracted content from a single page.

    Attributes:
        page_number: 1-indexed page number.
        text: Extracted text content.
        images: list of image descriptions on the page.
        annotations: Structured annotations found.
        metadata: Additional page metadata.
    """

    page_number: int = 1
    text: str = ""
    images: list[str] = field(default_factory=list)
    annotations: list[Annotation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "Annotation",
    "BoundingBox",
    "PageContent",
    "VLMConfig",
    "VLMResponse",
]
