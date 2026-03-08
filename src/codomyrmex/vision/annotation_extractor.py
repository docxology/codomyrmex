"""Structured annotation extraction from images via VLM.

Uses Vision-Language Models to identify and annotate visual elements
in images with bounding boxes, labels, and confidence scores.

Example::

    client = VLMClient()
    extractor = AnnotationExtractor()
    annotations = extractor.extract_annotations("photo.jpg", client)
    for ann in annotations:
        print(f"{ann.label}: conf={ann.confidence:.2f}")
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from .models import Annotation, BoundingBox, VLMResponse

if TYPE_CHECKING:
    from .vlm_client import VLMClient

logger = logging.getLogger(__name__)


class AnnotationExtractor:
    """Extracts structured annotations from images using VLMs.

    Sends images to a :class:`VLMClient` with structured prompts
    and parses the response into :class:`Annotation` objects.

    Example::

        extractor = AnnotationExtractor()
        annotations = extractor.extract_annotations("image.png", vlm_client)
    """

    def extract_annotations(
        self,
        image_path: str | Path,
        vlm_client: VLMClient,
        categories: list[str] | None = None,
    ) -> list[Annotation]:
        """Extract annotations from an image.

        Args:
            image_path: Path to the image file.
            vlm_client: VLM client for image analysis.
            categories: Optional category filter (e.g. ["text", "logo"]).

        Returns:
            List of :class:`Annotation` objects.
        """
        path = Path(image_path)
        if not path.exists():
            msg = f"Image not found: {path}"
            raise FileNotFoundError(msg)

        prompt = self._build_prompt(categories)
        response = vlm_client.describe_for_annotation(image_path, prompt=prompt)

        return self._parse_annotations(response)

    def extract_text_regions(
        self,
        image_path: str | Path,
        vlm_client: VLMClient,
    ) -> list[Annotation]:
        """Extract only text-containing regions from an image.

        Args:
            image_path: Path to the image.
            vlm_client: VLM client.

        Returns:
            List of text-region annotations.
        """
        return self.extract_annotations(
            image_path, vlm_client, categories=["text", "label", "caption"]
        )

    def _build_prompt(self, categories: list[str] | None = None) -> str:
        """Build the VLM prompt for annotation extraction.

        Args:
            categories: Optional category filter.

        Returns:
            Prompt string.
        """
        base = (
            "Analyze this image and identify all notable visual elements. "
            "For each element, provide a JSON array with objects containing:\n"
            '- "label": string (what the element is)\n'
            '- "confidence": number 0-1\n'
            '- "position": {"x": 0-1, "y": 0-1, "width": 0-1, "height": 0-1}\n'
            '- "attributes": object with notable properties\n'
            "Return ONLY the JSON array, no other text."
        )

        if categories:
            base += f"\nFocus only on these categories: {', '.join(categories)}"

        return base

    def _parse_annotations(self, response: VLMResponse) -> list[Annotation]:
        """Parse VLM response text into Annotation objects.

        Attempts to parse JSON from the response. Falls back to
        a single annotation with the raw text if parsing fails.

        Args:
            response: VLM response.

        Returns:
            List of :class:`Annotation` objects.
        """
        text = response.text.strip()

        # Try to extract JSON from the response
        try:
            # Handle responses wrapped in markdown code blocks
            if "```" in text:
                start = text.find("[")
                end = text.rfind("]") + 1
                if start >= 0 and end > start:
                    text = text[start:end]

            items = json.loads(text)
            if not isinstance(items, list):
                items = [items]

            annotations: list[Annotation] = []
            for item in items:
                if isinstance(item, dict):
                    pos = item.get("position", {})
                    bbox = BoundingBox(
                        x=float(pos.get("x", 0)),
                        y=float(pos.get("y", 0)),
                        width=float(pos.get("width", 0)),
                        height=float(pos.get("height", 0)),
                    )
                    annotations.append(
                        Annotation(
                            label=str(item.get("label", "unknown")),
                            bounding_box=bbox,
                            confidence=float(item.get("confidence", 0)),
                            attributes=item.get("attributes", {}),
                        )
                    )
            return annotations

        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.debug("Failed to parse VLM annotations as JSON: %s", exc)
            # Fallback: return the raw text as a single annotation
            return [
                Annotation(
                    label="raw_description",
                    confidence=0.5,
                    attributes={"raw_text": response.text},
                )
            ]


__all__ = ["AnnotationExtractor"]
