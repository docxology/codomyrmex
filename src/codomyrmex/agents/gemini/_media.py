"""Mixin for Gemini media generation operations (images and video)."""

from typing import Any

from codomyrmex.agents.core.exceptions import GeminiError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GeminiMediaMixin:
    """Image generation, upscaling, editing, and video generation.

    Requires ``client`` and ``default_model`` from the host class.
    """

    def generate_images(
        self, prompt: str, model: str = "imagen-4.0-generate-001", **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Generate images from a text prompt."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs


            result = self.client.models.generate_images(
                model=model, prompt=prompt, config=config
            )
            return [{"image_bytes": img.image_bytes} for img in result.images]
        except Exception as e:
            logger.error("Failed to generate images: %s", e)
            raise GeminiError(f"Failed to generate images: {e}") from e

    def upscale_image(
        self,
        image: Any,
        upscale_factor: str = "x4",
        model: str = "imagen-latest",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Upscale an image."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            result = self.client.models.upscale_image(
                model=model,
                image=image,
                upscale_factor=upscale_factor,
                config=config,
            )
            return [img.model_dump() for img in result.images]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to upscale image: %s", e)
            raise GeminiError(f"Failed to upscale image: {e}") from e

    def edit_image(
        self,
        prompt: str,
        image: Any,
        reference_images: list[Any] | None = None,
        model: str = "imagen-latest",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Edit an image with a text prompt."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            ref_images = reference_images or []
            if image and not ref_images:
                ref_images = [image]

            result = self.client.models.edit_image(
                model=model,
                prompt=prompt,
                reference_images=ref_images,
                config=config,
            )
            return [img.model_dump() for img in result.images]
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            logger.error("Failed to edit image: %s", e)
            raise GeminiError(f"Failed to edit image: {e}") from e

    def generate_videos(
        self, prompt: str, model: str = "veo-2.0-generate-001", **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Generate videos from a text prompt (uses Veo 2.0 long-running operation)."""
        if not self.client:
            raise GeminiError("Gemini Client not initialized")
        try:
            config = kwargs.pop("config", None)
            if config is None and kwargs:
                config = kwargs

            operation = self.client.models.generate_videos(
                model=model, prompt=prompt, config=config
            )

            if hasattr(operation, "done"):
                import time

                while not operation.done:
                    time.sleep(5)
                    operation = self.client.operations.get(operation=operation)

                if operation.error:
                    raise GeminiError(f"Video operation failed: {operation.error}")
                result = operation.result
            else:
                result = operation

            outputs = []
            for video in getattr(result, "videos", []):
                v_bytes = getattr(video, "video_bytes", None) or getattr(
                    video, "video", None
                )
                v_uri = getattr(video, "uri", None)
                if v_bytes:
                    outputs.append({"video_bytes": v_bytes})
                elif v_uri:
                    import urllib.request

                    try:
                        req = urllib.request.urlopen(v_uri)
                        outputs.append({"video_bytes": req.read()})
                    except Exception as e:
                        logger.warning("Failed to download video URI %s: %s", v_uri, e)
                        outputs.append({"uri": v_uri})

            return outputs
        except Exception as e:
            logger.error("Failed to generate videos: %s", e)
            raise GeminiError(f"Failed to generate videos: {e}") from e
