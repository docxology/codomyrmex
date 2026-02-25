"""
Multimodal

Multi-modal content handling for images, audio, and text.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from .builder import MultimodalMessageBuilder
from .models import (
    AudioContent,
    AudioFormat,
    ImageContent,
    ImageFormat,
    MediaContent,
    MediaType,
    MultimodalMessage,
)
from .processors import (
    AudioProcessor,
    ImageProcessor,
    MultimodalProcessor,
)


def cli_commands():
    """Return CLI commands for the multimodal module."""
    return {
        "modalities": {
            "help": "List supported modalities",
            "handler": lambda **kwargs: print(
                "Supported Modalities\n"
                f"  Media types: {', '.join(mt.value if hasattr(mt, 'value') else str(mt) for mt in MediaType)}\n"
                f"  Image formats: {', '.join(f.value if hasattr(f, 'value') else str(f) for f in ImageFormat)}\n"
                f"  Audio formats: {', '.join(f.value if hasattr(f, 'value') else str(f) for f in AudioFormat)}\n"
                "  Processors: MultimodalProcessor, ImageProcessor, AudioProcessor"
            ),
        },
        "process": {
            "help": "Process multimodal input",
            "handler": lambda **kwargs: print(
                "Multimodal Processing\n"
                "  Use MultimodalMessageBuilder to compose multimodal messages.\n"
                "  Available processors: ImageProcessor, AudioProcessor\n"
                "  Pipeline: input -> processor -> MultimodalMessage"
            ),
        },
    }


__all__ = [
    # CLI integration
    "cli_commands",
    # Models
    "MediaType",
    "ImageFormat",
    "AudioFormat",
    "MediaContent",
    "ImageContent",
    "AudioContent",
    "MultimodalMessage",
    # Processors
    "MultimodalProcessor",
    "ImageProcessor",
    "AudioProcessor",
    # Builder
    "MultimodalMessageBuilder",
]
