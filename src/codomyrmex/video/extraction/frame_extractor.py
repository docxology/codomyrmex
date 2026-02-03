"""Frame extraction from video files.

This module provides the FrameExtractor class for extracting frames,
generating thumbnails, and extracting audio from video files.
"""

import time
from pathlib import Path
from typing import Optional, Union

from codomyrmex.video.config import get_config
from codomyrmex.video.exceptions import (
    AudioExtractionError,
    FrameExtractionError,
    UnsupportedFormatError,
    VideoReadError,
)
from codomyrmex.video.models import ExtractionResult

# Check for PIL availability
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore

# Check for OpenCV availability
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None  # type: ignore
    np = None  # type: ignore

# Check for moviepy availability
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None  # type: ignore


SUPPORTED_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv", ".flv", ".m4v"}


class FrameExtractor:
    """Extract frames and audio from video files.

    This class provides methods for extracting individual frames,
    multiple frames at intervals, generating thumbnails, and
    extracting audio tracks.

    Example:
        ```python
        extractor = FrameExtractor()

        # Extract single frame
        frame = extractor.extract_frame("video.mp4", timestamp=5.0)
        frame.save("frame.png")

        # Generate thumbnail
        thumbnail = extractor.generate_thumbnail("video.mp4")
        thumbnail.save("thumb.jpg")

        # Extract audio
        audio_path = extractor.extract_audio("video.mp4", audio_format="mp3")
        ```

    Attributes:
        config: Video configuration
    """

    def __init__(self, config: Optional[object] = None) -> None:
        """Initialize the frame extractor.

        Args:
            config: Optional configuration override
        """
        self.config = config or get_config()
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not OPENCV_AVAILABLE and not MOVIEPY_AVAILABLE:
            raise FrameExtractionError(
                "No video backend available. Install with: uv sync --extra video"
            )
        if not PIL_AVAILABLE:
            raise FrameExtractionError(
                "PIL/Pillow is required. Install with: uv sync --extra video"
            )

    def _validate_input(self, video_path: Union[str, Path]) -> Path:
        """Validate input video path.

        Args:
            video_path: Path to validate

        Returns:
            Validated Path object
        """
        path = Path(video_path)

        if not path.exists():
            raise VideoReadError(f"Video file not found: {path}", video_path=path)

        if path.suffix.lower() not in SUPPORTED_FORMATS:
            raise UnsupportedFormatError(
                f"Unsupported format: {path.suffix}",
                format_type=path.suffix,
                supported_formats=list(SUPPORTED_FORMATS),
            )

        return path

    def extract_frame(
        self,
        video_path: Union[str, Path],
        timestamp: float,
    ) -> "Image.Image":
        """Extract a single frame at specified timestamp.

        Args:
            video_path: Path to video file
            timestamp: Time in seconds to extract frame

        Returns:
            PIL Image of the extracted frame

        Raises:
            FrameExtractionError: If extraction fails
        """
        path = self._validate_input(video_path)

        if OPENCV_AVAILABLE:
            return self._extract_frame_opencv(path, timestamp)
        elif MOVIEPY_AVAILABLE:
            return self._extract_frame_moviepy(path, timestamp)
        else:
            raise FrameExtractionError("No video backend available")

    def _extract_frame_opencv(self, video_path: Path, timestamp: float) -> "Image.Image":
        """Extract frame using OpenCV."""
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path}", video_path=video_path)

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if not ret:
                raise FrameExtractionError(
                    f"Failed to extract frame at {timestamp}s",
                    video_path=video_path,
                    timestamp=timestamp,
                )

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)

        finally:
            cap.release()

    def _extract_frame_moviepy(self, video_path: Path, timestamp: float) -> "Image.Image":
        """Extract frame using moviepy."""
        try:
            with VideoFileClip(str(video_path)) as clip:
                if timestamp > clip.duration:
                    raise FrameExtractionError(
                        f"Timestamp {timestamp}s exceeds video duration {clip.duration}s",
                        video_path=video_path,
                        timestamp=timestamp,
                    )

                frame = clip.get_frame(timestamp)
                return Image.fromarray(frame.astype("uint8"))

        except FrameExtractionError:
            raise
        except Exception as e:
            raise FrameExtractionError(
                f"Frame extraction failed: {e}",
                video_path=video_path,
                timestamp=timestamp,
            ) from e

    def extract_frames(
        self,
        video_path: Union[str, Path],
        interval: float,
        start: float = 0.0,
        end: Optional[float] = None,
    ) -> list["Image.Image"]:
        """Extract frames at regular intervals.

        Args:
            video_path: Path to video file
            interval: Time between frames in seconds
            start: Start time in seconds
            end: End time in seconds (None for video end)

        Returns:
            List of PIL Images
        """
        path = self._validate_input(video_path)
        frames = []

        if OPENCV_AVAILABLE:
            cap = cv2.VideoCapture(str(path))
            if not cap.isOpened():
                raise VideoReadError(f"Cannot open video: {path}")

            try:
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = total_frames / fps

                if end is None:
                    end = duration

                current_time = start
                while current_time <= end:
                    frame_number = int(current_time * fps)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    ret, frame = cap.read()

                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frames.append(Image.fromarray(frame_rgb))

                    current_time += interval

            finally:
                cap.release()

        elif MOVIEPY_AVAILABLE:
            with VideoFileClip(str(path)) as clip:
                if end is None:
                    end = clip.duration

                current_time = start
                while current_time <= end:
                    frame = clip.get_frame(current_time)
                    frames.append(Image.fromarray(frame.astype("uint8")))
                    current_time += interval

        return frames

    def extract_frames_at_timestamps(
        self,
        video_path: Union[str, Path],
        timestamps: list[float],
    ) -> ExtractionResult:
        """Extract frames at specific timestamps.

        Args:
            video_path: Path to video file
            timestamps: List of timestamps in seconds

        Returns:
            ExtractionResult with frames and metadata
        """
        path = self._validate_input(video_path)
        start_time = time.time()

        frames = []
        for ts in timestamps:
            frame = self.extract_frame(path, ts)
            frames.append(frame)

        processing_time = time.time() - start_time

        return ExtractionResult(
            source_path=path,
            frames=frames,
            timestamps=timestamps,
            frame_count=len(frames),
            processing_time=processing_time,
        )

    def generate_thumbnail(
        self,
        video_path: Union[str, Path],
        timestamp: Optional[float] = None,
        width: int = 320,
    ) -> "Image.Image":
        """Generate a thumbnail from a video.

        Args:
            video_path: Path to video file
            timestamp: Time to extract (None for 10% into video)
            width: Thumbnail width (height calculated from aspect ratio)

        Returns:
            PIL Image thumbnail
        """
        path = self._validate_input(video_path)

        # Get video duration to calculate default timestamp
        if timestamp is None:
            if OPENCV_AVAILABLE:
                cap = cv2.VideoCapture(str(path))
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = total_frames / fps
                cap.release()
            elif MOVIEPY_AVAILABLE:
                with VideoFileClip(str(path)) as clip:
                    duration = clip.duration
            else:
                duration = 10.0

            # Default: 10% into the video
            timestamp = duration * 0.1

        frame = self.extract_frame(path, timestamp)

        # Calculate height maintaining aspect ratio
        aspect_ratio = frame.height / frame.width
        height = int(width * aspect_ratio)

        return frame.resize((width, height), Image.Resampling.LANCZOS)

    def extract_audio(
        self,
        video_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        audio_format: str = "mp3",
        bitrate: str = "192k",
    ) -> Path:
        """Extract audio track from video.

        Args:
            video_path: Path to video file
            output_path: Output path for audio file
            audio_format: Audio format (mp3, wav, aac)
            bitrate: Audio bitrate

        Returns:
            Path to extracted audio file

        Raises:
            AudioExtractionError: If extraction fails
        """
        path = self._validate_input(video_path)

        if output_path:
            output = Path(output_path)
        else:
            output = path.parent / f"{path.stem}.{audio_format}"

        if not MOVIEPY_AVAILABLE:
            raise AudioExtractionError(
                "moviepy required for audio extraction",
                video_path=path,
            )

        try:
            with VideoFileClip(str(path)) as clip:
                if clip.audio is None:
                    raise AudioExtractionError(
                        "Video has no audio track",
                        video_path=path,
                    )

                clip.audio.write_audiofile(
                    str(output),
                    bitrate=bitrate,
                    verbose=False,
                    logger=None,
                )

        except AudioExtractionError:
            raise
        except Exception as e:
            raise AudioExtractionError(
                f"Audio extraction failed: {e}",
                video_path=path,
                audio_format=audio_format,
            ) from e

        return output

    def save_frames(
        self,
        frames: list["Image.Image"],
        output_directory: Union[str, Path],
        prefix: str = "frame",
        format: str = "png",
    ) -> list[Path]:
        """Save extracted frames to files.

        Args:
            frames: List of PIL Images
            output_directory: Directory to save frames
            prefix: Filename prefix
            format: Image format (png, jpg)

        Returns:
            List of saved file paths
        """
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []
        for i, frame in enumerate(frames):
            path = output_dir / f"{prefix}_{i:04d}.{format}"
            frame.save(path)
            saved_paths.append(path)

        return saved_paths


__all__ = ["FrameExtractor", "OPENCV_AVAILABLE", "MOVIEPY_AVAILABLE", "PIL_AVAILABLE"]
