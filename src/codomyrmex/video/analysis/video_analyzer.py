"""Video analysis and metadata extraction.

This module provides the VideoAnalyzer class for extracting information
and metadata from video files.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from codomyrmex.video.exceptions import (
    UnsupportedFormatError,
    VideoAnalysisError,
    VideoReadError,
)
from codomyrmex.video.models import VideoComparison, VideoInfo

# Check for OpenCV availability
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None  # type: ignore

# Check for moviepy availability
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None  # type: ignore


SUPPORTED_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".wmv", ".flv", ".m4v"}


class VideoAnalyzer:
    """Analyze video files and extract metadata.

    This class provides methods for extracting video information including
    duration, resolution, codec, frame count, and more.

    Example:
        ```python
        analyzer = VideoAnalyzer()

        # Get complete video info
        info = analyzer.get_info("video.mp4")
        print(f"Duration: {info.duration}s")
        print(f"Resolution: {info.width}x{info.height}")

        # Quick checks
        duration = analyzer.get_duration("video.mp4")
        fps = analyzer.get_fps("video.mp4")
        has_audio = analyzer.has_audio("video.mp4")
        ```
    """

    def __init__(self) -> None:
        """Initialize the video analyzer."""
        self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not OPENCV_AVAILABLE and not MOVIEPY_AVAILABLE:
            raise VideoAnalysisError(
                "No video backend available. Install with: uv sync --extra video"
            )

    def _validate_input(self, video_path: str | Path) -> Path:
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

    def get_info(self, video_path: str | Path) -> VideoInfo:
        """Get complete information about a video file.

        Args:
            video_path: Path to video file

        Returns:
            VideoInfo with all metadata
        """
        path = self._validate_input(video_path)

        if OPENCV_AVAILABLE:
            info = self._get_info_opencv(path)
        elif MOVIEPY_AVAILABLE:
            info = self._get_info_moviepy(path)
        else:
            raise VideoAnalysisError("No video backend available")

        # Add file size
        info.file_size = path.stat().st_size

        return info

    def _get_info_opencv(self, video_path: Path) -> VideoInfo:
        """Get video info using OpenCV."""
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise VideoReadError(f"Cannot open video: {video_path}", video_path=video_path)

        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0.0

            # Get codec
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

            return VideoInfo(
                file_path=video_path,
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                frame_count=frame_count,
                video_codec=codec,
            )

        finally:
            cap.release()

    def _get_info_moviepy(self, video_path: Path) -> VideoInfo:
        """Get video info using moviepy."""
        try:
            with VideoFileClip(str(video_path)) as clip:
                return VideoInfo(
                    file_path=video_path,
                    duration=clip.duration,
                    width=clip.w,
                    height=clip.h,
                    fps=clip.fps,
                    frame_count=int(clip.duration * clip.fps),
                    has_audio=clip.audio is not None,
                )
        except Exception as e:
            raise VideoAnalysisError(
                f"Failed to analyze video: {e}",
                video_path=video_path,
            ) from e

    def get_duration(self, video_path: str | Path) -> float:
        """Get video duration in seconds.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds
        """
        info = self.get_info(video_path)
        return info.duration

    def get_resolution(self, video_path: str | Path) -> tuple[int, int]:
        """Get video resolution.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (width, height)
        """
        info = self.get_info(video_path)
        return (info.width, info.height)

    def get_codec(self, video_path: str | Path) -> str:
        """Get video codec.

        Args:
            video_path: Path to video file

        Returns:
            Codec name/identifier
        """
        info = self.get_info(video_path)
        return info.video_codec

    def get_fps(self, video_path: str | Path) -> float:
        """Get video frames per second.

        Args:
            video_path: Path to video file

        Returns:
            FPS value
        """
        info = self.get_info(video_path)
        return info.fps

    def get_frame_count(self, video_path: str | Path) -> int:
        """Get total number of frames.

        Args:
            video_path: Path to video file

        Returns:
            Frame count
        """
        info = self.get_info(video_path)
        return info.frame_count

    def has_audio(self, video_path: str | Path) -> bool:
        """Check if video has an audio track.

        Args:
            video_path: Path to video file

        Returns:
            True if video has audio
        """
        path = self._validate_input(video_path)

        if MOVIEPY_AVAILABLE:
            try:
                with VideoFileClip(str(path)) as clip:
                    return clip.audio is not None
            except Exception as e:
                logger.warning("Failed to check audio presence in %s: %s", path, e)
                return False
        else:
            # OpenCV doesn't have reliable audio detection
            # Return False as we can't determine
            return False

    def is_valid_video(self, video_path: str | Path) -> bool:
        """Check if file is a valid, readable video.

        Args:
            video_path: Path to video file

        Returns:
            True if video is valid and readable
        """
        try:
            path = Path(video_path)
            if not path.exists():
                return False

            if path.suffix.lower() not in SUPPORTED_FORMATS:
                return False

            # Try to open and read basic properties
            if OPENCV_AVAILABLE:
                cap = cv2.VideoCapture(str(path))
                if not cap.isOpened():
                    return False

                # Try to read a frame
                ret, _ = cap.read()
                cap.release()
                return ret

            elif MOVIEPY_AVAILABLE:
                with VideoFileClip(str(path)) as clip:
                    return clip.duration > 0

        except Exception as e:
            logger.warning("Failed to validate video file %s: %s", video_path, e)
            return False

        return False

    def compare_videos(
        self,
        video_path1: str | Path,
        video_path2: str | Path,
        duration_tolerance: float = 0.5,
    ) -> VideoComparison:
        """Compare two videos and report differences.

        Args:
            video_path1: Path to first video
            video_path2: Path to second video
            duration_tolerance: Tolerance for duration comparison (seconds)

        Returns:
            VideoComparison with comparison results
        """
        path1 = self._validate_input(video_path1)
        path2 = self._validate_input(video_path2)

        info1 = self.get_info(path1)
        info2 = self.get_info(path2)

        duration_diff = abs(info1.duration - info2.duration)

        return VideoComparison(
            video1_path=path1,
            video2_path=path2,
            same_resolution=(info1.width == info2.width and info1.height == info2.height),
            same_duration=(duration_diff <= duration_tolerance),
            same_fps=(abs(info1.fps - info2.fps) < 0.1),
            same_codec=(info1.video_codec == info2.video_codec),
            duration_diff=duration_diff,
            size_diff=info1.file_size - info2.file_size,
            details={
                "video1": info1.to_dict(),
                "video2": info2.to_dict(),
            },
        )

    def get_aspect_ratio(self, video_path: str | Path) -> float:
        """Get video aspect ratio.

        Args:
            video_path: Path to video file

        Returns:
            Aspect ratio (width/height)
        """
        info = self.get_info(video_path)
        return info.aspect_ratio


__all__ = ["VideoAnalyzer", "OPENCV_AVAILABLE", "MOVIEPY_AVAILABLE"]
