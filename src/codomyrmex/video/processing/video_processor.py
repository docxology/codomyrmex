"""Video processing operations.

This module provides the VideoProcessor class for manipulating video files
including resize, crop, rotate, convert, filter, trim, and merge operations.
"""

import importlib.util
import time
from pathlib import Path
from typing import Any

from codomyrmex.video.config import get_config
from codomyrmex.video.exceptions import (
    UnsupportedFormatError,
    VideoProcessingError,
    VideoReadError,
)
from codomyrmex.video.models import (
    FilterType,
    ProcessingResult,
)

# Check for moviepy availability
try:
    from moviepy.editor import (
        VideoFileClip,
        concatenate_videoclips,
        vfx,
    )

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

# OpenCV is optional; avoid importing solely for availability (Ruff F401).
OPENCV_AVAILABLE = importlib.util.find_spec("cv2") is not None


SUPPORTED_INPUT_FORMATS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
    ".wmv",
    ".flv",
    ".m4v",
}
SUPPORTED_OUTPUT_FORMATS = {".mp4", ".avi", ".mov", ".webm", ".mkv"}


def _pil_filter_frame(
    get_frame: Any,
    t: float,
    filter_name: str,
    intensity: float = 1.0,
) -> Any:
    """Apply a PIL-based filter to a single video frame.

    Used as a ``clip.fl`` callback for filters that moviepy's ``vfx`` module
    does not provide natively (blur, sharpen, saturation, sepia).

    Args:
        get_frame: moviepy frame-getter function (called with ``t``).
        t: Timestamp of the frame being processed.
        filter_name: One of ``"blur"``, ``"sharpen"``, ``"saturation"``, ``"sepia"``.
        intensity: Filter intensity (0.0–2.0 scale; semantics vary per filter).

    Returns:
        NumPy array suitable for moviepy (same shape/dtype as input frame).
    """
    import numpy as np

    frame = get_frame(t)
    # Skip processing for non-video frames (e.g., mask)
    if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] < 3:
        return frame

    # Use PIL for per-frame pixel manipulation
    from PIL import Image, ImageFilter

    img = Image.fromarray(frame.astype(np.uint8))

    if filter_name == "blur":
        radius = max(0.1, intensity * 2.0)
        img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    elif filter_name == "sharpen":
        # Unsharp mask: blend sharpened with original based on intensity
        sharpened = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
        if intensity <= 1.0:
            img = Image.blend(img, sharpened, intensity)
        else:
            img = sharpened
    elif filter_name == "saturation":
        # Saturation via HSV: scale the S channel using numpy for precision
        hsv_img = img.convert("HSV")
        hsv_arr = np.array(hsv_img, dtype=np.float32)
        # Scale saturation channel (index 1) and clip
        hsv_arr[:, :, 1] = np.clip(hsv_arr[:, :, 1] * intensity, 0, 255)
        result_img = Image.fromarray(hsv_arr.astype(np.uint8), "HSV")
        img = result_img.convert("RGB")
    elif filter_name == "sepia":
        # Sepia tone: matrix transform per pixel using numpy
        arr = np.array(img, dtype=np.float32)
        # Standard sepia weights
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        new_r = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
        new_g = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
        new_b = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)
        sepia_arr = np.stack([new_r, new_g, new_b], axis=2).astype(np.uint8)
        sepia_img = Image.fromarray(sepia_arr, "RGB")
        if intensity < 1.0:
            img = Image.blend(img, sepia_img, intensity)
        else:
            img = sepia_img

    return np.array(img)


class VideoProcessor:
    """Video processing class for manipulating video files.

    This class provides methods for common video processing operations
    using moviepy and OpenCV backends.

    Example:
        ```python
        processor = VideoProcessor()

        # Resize video
        result = processor.resize("input.mp4", width=1280, height=720)

        # Apply filter
        result = processor.apply_filter("input.mp4", FilterType.GRAYSCALE)

        # Trim video
        result = processor.trim("input.mp4", start=10.0, end=30.0)
        ```

    Attributes:
        config: Video processing configuration
    """

    def __init__(self, config: object | None = None) -> None:
        """Initialize the video processor.

        Args:
            config: Optional configuration override
        """
        self.config = config or get_config()
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not MOVIEPY_AVAILABLE and not OPENCV_AVAILABLE:
            raise VideoProcessingError(
                "No video processing backend available. "
                "Install with: uv sync --extra video"
            )

    def _validate_input(self, video_path: str | Path) -> Path:
        """Validate input video path.

        Args:
            video_path: Path to validate

        Returns:
            Validated Path object

        Raises:
            VideoReadError: If file doesn't exist
            UnsupportedFormatError: If format not supported
        """
        path = Path(video_path)

        if not path.exists():
            raise VideoReadError(f"Video file not found: {path}", video_path=path)

        if path.suffix.lower() not in SUPPORTED_INPUT_FORMATS:
            raise UnsupportedFormatError(
                f"Unsupported input format: {path.suffix}",
                format_type=path.suffix,
                supported_formats=list(SUPPORTED_INPUT_FORMATS),
            )

        return path

    def _get_output_path(
        self,
        input_path: Path,
        output_path: str | Path | None = None,
        suffix: str = "_processed",
    ) -> Path:
        """Generate output path if not provided.

        Args:
            input_path: Input video path
            output_path: Optional output path
            suffix: Suffix to add to filename

        Returns:
            Output Path object
        """
        if output_path:
            return Path(output_path)

        return input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"

    def resize(
        self,
        video_path: str | Path,
        width: int,
        height: int,
        output_path: str | Path | None = None,
        maintain_aspect_ratio: bool = True,
    ) -> ProcessingResult:
        """Resize a video to specified dimensions.

        Args:
            video_path: Path to input video
            width: Target width in pixels
            height: Target height in pixels
            output_path: Optional output path
            maintain_aspect_ratio: If True, scale to fit within dimensions

        Returns:
            ProcessingResult with output details
        """
        input_path = self._validate_input(video_path)
        output = self._get_output_path(input_path, output_path, "_resized")
        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for resize operation",
                operation="resize",
            )

        try:
            with VideoFileClip(str(input_path)) as clip:
                if maintain_aspect_ratio:
                    # Calculate scale factor to fit within dimensions
                    scale_w = width / clip.w
                    scale_h = height / clip.h
                    scale = min(scale_w, scale_h)
                    new_width = int(clip.w * scale)
                    new_height = int(clip.h * scale)
                    # Ensure even dimensions for codec compatibility
                    new_width = new_width - (new_width % 2)
                    new_height = new_height - (new_height % 2)
                    resized = clip.resize(newsize=(new_width, new_height))
                else:
                    resized = clip.resize(newsize=(width, height))

                resized.write_videofile(
                    str(output),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None,
                )

                final_width = resized.w
                final_height = resized.h
                duration = clip.duration

        except Exception as e:
            raise VideoProcessingError(
                f"Resize failed: {e}",
                video_path=input_path,
                operation="resize",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=final_width,
            height=final_height,
            operation="resize",
            processing_time=processing_time,
            success=True,
        )

    def crop(
        self,
        video_path: str | Path,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str | Path | None = None,
    ) -> ProcessingResult:
        """Crop a video to specified region.

        Args:
            video_path: Path to input video
            x: Left edge of crop region
            y: Top edge of crop region
            width: Width of crop region
            height: Height of crop region
            output_path: Optional output path

        Returns:
            ProcessingResult with output details
        """
        input_path = self._validate_input(video_path)
        output = self._get_output_path(input_path, output_path, "_cropped")
        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for crop operation",
                operation="crop",
            )

        try:
            with VideoFileClip(str(input_path)) as clip:
                cropped = clip.crop(x1=x, y1=y, x2=x + width, y2=y + height)

                cropped.write_videofile(
                    str(output),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None,
                )

                duration = clip.duration

        except Exception as e:
            raise VideoProcessingError(
                f"Crop failed: {e}",
                video_path=input_path,
                operation="crop",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=width,
            height=height,
            operation="crop",
            processing_time=processing_time,
            success=True,
        )

    def rotate(
        self,
        video_path: str | Path,
        angle: float,
        output_path: str | Path | None = None,
        expand: bool = True,
    ) -> ProcessingResult:
        """Rotate a video by specified angle.

        Args:
            video_path: Path to input video
            angle: Rotation angle in degrees (clockwise)
            output_path: Optional output path
            expand: If True, expand frame to fit rotated video

        Returns:
            ProcessingResult with output details
        """
        input_path = self._validate_input(video_path)
        output = self._get_output_path(input_path, output_path, "_rotated")
        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for rotate operation",
                operation="rotate",
            )

        try:
            with VideoFileClip(str(input_path)) as clip:
                rotated = clip.rotate(angle, expand=expand)

                rotated.write_videofile(
                    str(output),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None,
                )

                duration = clip.duration
                final_width = rotated.w
                final_height = rotated.h

        except Exception as e:
            raise VideoProcessingError(
                f"Rotate failed: {e}",
                video_path=input_path,
                operation="rotate",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=final_width,
            height=final_height,
            operation="rotate",
            processing_time=processing_time,
            success=True,
        )

    def convert(
        self,
        video_path: str | Path,
        output_format: str,
        output_path: str | Path | None = None,
        video_codec: str | None = None,
        audio_codec: str | None = None,
        bitrate: str | None = None,
    ) -> ProcessingResult:
        """Convert video to a different format.

        Args:
            video_path: Path to input video
            output_format: Target format (e.g., "mp4", "avi")
            output_path: Optional output path
            video_codec: Video codec to use
            audio_codec: Audio codec to use
            bitrate: Target bitrate (e.g., "5000k")

        Returns:
            ProcessingResult with output details
        """
        input_path = self._validate_input(video_path)

        # Ensure format has dot prefix
        if not output_format.startswith("."):
            output_format = f".{output_format}"

        if output_format.lower() not in SUPPORTED_OUTPUT_FORMATS:
            raise UnsupportedFormatError(
                f"Unsupported output format: {output_format}",
                format_type=output_format,
                supported_formats=list(SUPPORTED_OUTPUT_FORMATS),
            )

        if output_path:
            output = Path(output_path)
        else:
            output = input_path.parent / f"{input_path.stem}_converted{output_format}"

        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for convert operation",
                operation="convert",
            )

        try:
            with VideoFileClip(str(input_path)) as clip:
                write_params: dict[str, Any] = {
                    "verbose": False,
                    "logger": None,
                }

                if video_codec:
                    write_params["codec"] = video_codec
                else:
                    write_params["codec"] = "libx264"

                if audio_codec:
                    write_params["audio_codec"] = audio_codec
                else:
                    write_params["audio_codec"] = "aac"

                if bitrate:
                    write_params["bitrate"] = bitrate

                clip.write_videofile(str(output), **write_params)

                duration = clip.duration
                final_width = clip.w
                final_height = clip.h

        except Exception as e:
            raise VideoProcessingError(
                f"Convert failed: {e}",
                video_path=input_path,
                operation="convert",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=final_width,
            height=final_height,
            operation="convert",
            processing_time=processing_time,
            success=True,
        )

    def apply_filter(
        self,
        video_path: str | Path,
        filter_type: FilterType,
        intensity: float = 1.0,
        output_path: str | Path | None = None,
    ) -> ProcessingResult:
        """Apply a filter to a video.

        Args:
            video_path: Path to input video
            filter_type: Type of filter to apply
            intensity: Filter intensity (0.0-1.0, where applicable)
            output_path: Optional output path

        Returns:
            ProcessingResult with output details
        """
        input_path = self._validate_input(video_path)
        output = self._get_output_path(input_path, output_path, f"_{filter_type.value}")
        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for filter operation",
                operation="filter",
            )

        try:
            with VideoFileClip(str(input_path)) as clip:
                # Apply filter based on type
                if filter_type == FilterType.GRAYSCALE:
                    filtered = clip.fx(vfx.blackwhite)
                elif filter_type == FilterType.MIRROR_HORIZONTAL:
                    filtered = clip.fx(vfx.mirror_x)
                elif filter_type == FilterType.MIRROR_VERTICAL:
                    filtered = clip.fx(vfx.mirror_y)
                elif filter_type == FilterType.INVERT:
                    filtered = clip.fx(vfx.invert_colors)
                elif filter_type == FilterType.ROTATE_90:
                    filtered = clip.rotate(90)
                elif filter_type == FilterType.ROTATE_180:
                    filtered = clip.rotate(180)
                elif filter_type == FilterType.ROTATE_270:
                    filtered = clip.rotate(270)
                elif filter_type == FilterType.BRIGHTNESS:
                    # Adjust brightness using colorx
                    filtered = clip.fx(vfx.colorx, intensity)
                elif filter_type == FilterType.CONTRAST:
                    filtered = clip.fx(vfx.lum_contrast, contrast=intensity)
                elif filter_type == FilterType.BLUR:
                    # Real Gaussian blur via per-frame PIL processing
                    blurred = clip.fl(
                        lambda gf, t: _pil_filter_frame(gf, t, "blur", intensity),
                        apply_to=["mask", "video"],
                    )
                    filtered = blurred
                elif filter_type == FilterType.SHARPEN:
                    # Sharpen via PIL ImageFilter
                    filtered = clip.fl(
                        lambda gf, t: _pil_filter_frame(gf, t, "sharpen", intensity),
                        apply_to=["mask", "video"],
                    )
                elif filter_type == FilterType.SATURATION:
                    # Saturation boost/reduce via HSV manipulation
                    filtered = clip.fl(
                        lambda gf, t: _pil_filter_frame(gf, t, "saturation", intensity),
                        apply_to=["mask", "video"],
                    )
                elif filter_type == FilterType.SEPIA:
                    # Sepia tone via per-frame matrix transform
                    filtered = clip.fl(
                        lambda gf, t: _pil_filter_frame(gf, t, "sepia", intensity),
                        apply_to=["mask", "video"],
                    )
                else:
                    # Default: no filter
                    filtered = clip

                filtered.write_videofile(
                    str(output),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None,
                )

                duration = clip.duration
                final_width = filtered.w
                final_height = filtered.h

        except Exception as e:
            raise VideoProcessingError(
                f"Filter application failed: {e}",
                video_path=input_path,
                operation="filter",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=final_width,
            height=final_height,
            operation=f"filter_{filter_type.value}",
            processing_time=processing_time,
            success=True,
        )

    def trim(
        self,
        video_path: str | Path,
        start: float,
        end: float,
        output_path: str | Path | None = None,
    ) -> ProcessingResult:
        """Trim video to specified time range.

        Args:
            video_path: Path to input video
            start: Start time in seconds
            end: End time in seconds
            output_path: Optional output path

        Returns:
            ProcessingResult with output details
        """
        input_path = self._validate_input(video_path)
        output = self._get_output_path(input_path, output_path, "_trimmed")
        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for trim operation",
                operation="trim",
            )

        try:
            with VideoFileClip(str(input_path)) as clip:
                end = min(end, clip.duration)

                if start >= end:
                    raise VideoProcessingError(
                        f"Invalid trim range: start ({start}) >= end ({end})",
                        operation="trim",
                    )

                trimmed = clip.subclip(start, end)

                trimmed.write_videofile(
                    str(output),
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None,
                )

                duration = end - start
                final_width = clip.w
                final_height = clip.h

        except VideoProcessingError:
            raise
        except Exception as e:
            raise VideoProcessingError(
                f"Trim failed: {e}",
                video_path=input_path,
                operation="trim",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=final_width,
            height=final_height,
            operation="trim",
            processing_time=processing_time,
            success=True,
        )

    def merge(
        self,
        video_paths: list[str | Path],
        output_path: str | Path,
        transition: str | None = None,
        transition_duration: float = 1.0,
    ) -> ProcessingResult:
        """Merge multiple videos into one.

        Args:
            video_paths: list of video paths to merge
            output_path: Output path for merged video
            transition: Transition type (currently unused)
            transition_duration: Duration of transitions

        Returns:
            ProcessingResult with output details
        """
        if len(video_paths) < 2:
            raise VideoProcessingError(
                "At least 2 videos required for merge",
                operation="merge",
            )

        # Validate all input videos
        validated_paths = [self._validate_input(p) for p in video_paths]
        output = Path(output_path)
        start_time = time.time()

        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError(
                "moviepy required for merge operation",
                operation="merge",
            )

        try:
            clips = [VideoFileClip(str(p)) for p in validated_paths]

            # Concatenate all clips
            merged = concatenate_videoclips(clips, method="compose")

            merged.write_videofile(
                str(output),
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )

            duration = merged.duration
            final_width = merged.w
            final_height = merged.h

            # Clean up clips
            for clip in clips:
                clip.close()
            merged.close()

        except Exception as e:
            raise VideoProcessingError(
                f"Merge failed: {e}",
                operation="merge",
            ) from e

        processing_time = time.time() - start_time

        return ProcessingResult(
            output_path=output,
            duration=duration,
            file_size=output.stat().st_size if output.exists() else 0,
            width=final_width,
            height=final_height,
            operation="merge",
            processing_time=processing_time,
            success=True,
        )


__all__ = ["MOVIEPY_AVAILABLE", "OPENCV_AVAILABLE", "VideoProcessor"]
