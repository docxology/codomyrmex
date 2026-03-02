# Codomyrmex Agents — src/codomyrmex/video/analysis

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Video metadata extraction and analysis. Provides `VideoAnalyzer` to query
duration, resolution, FPS, codec, frame count, audio presence, and aspect ratio.
Backends: OpenCV (preferred) and moviepy (fallback). Requires `uv sync --extra video`.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `video_analyzer.py` | `VideoAnalyzer` | Main entry point for video metadata extraction |
| `video_analyzer.py` | `VideoAnalyzer.get_info()` | Return full `VideoInfo` (duration, width, height, fps, frame_count, codec, file_size) |
| `video_analyzer.py` | `VideoAnalyzer.get_duration()` | Video duration in seconds |
| `video_analyzer.py` | `VideoAnalyzer.get_resolution()` | Tuple `(width, height)` |
| `video_analyzer.py` | `VideoAnalyzer.get_fps()` | Frames per second |
| `video_analyzer.py` | `VideoAnalyzer.has_audio()` | True if audio track present (moviepy only; OpenCV returns False) |
| `video_analyzer.py` | `VideoAnalyzer.is_valid_video()` | Validates file exists, format supported, first frame readable |
| `video_analyzer.py` | `VideoAnalyzer.compare_videos()` | Returns `VideoComparison` (resolution/duration/fps/codec match + diffs) |
| `video_analyzer.py` | `SUPPORTED_FORMATS` | `{.mp4, .avi, .mov, .mkv, .webm, .wmv, .flv, .m4v}` |

## Operating Contracts

- Constructor raises `VideoAnalysisError` if neither OpenCV nor moviepy is installed.
- All path arguments accept `str | Path`; invalid paths raise `VideoReadError`; unsupported extensions raise `UnsupportedFormatError`.
- `get_info()` always sets `file_size` from `Path.stat()` after backend call, regardless of which backend ran.
- `has_audio()` requires moviepy — returns `False` silently when only OpenCV is available (not an error).
- `compare_videos()` uses `duration_tolerance=0.5s` (default) and FPS tolerance of `0.1`.
- Errors are logged via module-level `logging.getLogger` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.video.exceptions` (`VideoAnalysisError`, `VideoReadError`, `UnsupportedFormatError`), `codomyrmex.video.models` (`VideoInfo`, `VideoComparison`)
- **External**: `cv2` (OpenCV, optional), `moviepy.editor` (optional)
- **Used by**: `codomyrmex.video` package consumers needing metadata without processing

## Navigation

- **📁 Parent**: [video](../README.md)
- **🏠 Root**: ../../../../README.md
