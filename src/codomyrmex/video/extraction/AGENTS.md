# Codomyrmex Agents — src/codomyrmex/video/extraction

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Frame and audio extraction from video files. Provides `FrameExtractor` for
single-frame capture, interval-based batch extraction, specific-timestamp lists,
thumbnail generation, audio track export, and saving frames to disk as image files.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `frame_extractor.py` | `FrameExtractor` | Main class for all extraction operations |
| `frame_extractor.py` | `FrameExtractor.extract_frame()` | Extract single PIL Image at timestamp; prefers OpenCV, falls back to moviepy |
| `frame_extractor.py` | `FrameExtractor.extract_frames()` | Extract frames at regular `interval` seconds between `[start, end]` |
| `frame_extractor.py` | `FrameExtractor.extract_frames_at_timestamps()` | Extract frames at specific timestamps, return `ExtractionResult` |
| `frame_extractor.py` | `FrameExtractor.generate_thumbnail()` | Extract frame at 10% of duration (default), resize to `width` preserving aspect ratio |
| `frame_extractor.py` | `FrameExtractor.extract_audio()` | Write audio track to `mp3`/`wav`/`aac` using moviepy; raises `AudioExtractionError` if no audio |
| `frame_extractor.py` | `FrameExtractor.save_frames()` | Save list of PIL Images to `{prefix}_{i:04d}.{format}` files |

## Operating Contracts

- Constructor raises `FrameExtractionError` if neither OpenCV nor moviepy is installed, OR if PIL/Pillow is missing — both checks run at `__init__` time.
- `extract_frame()` raises `FrameExtractionError` when timestamp exceeds video duration.
- `generate_thumbnail()` uses `Image.Resampling.LANCZOS` for high-quality downscaling.
- `extract_audio()` requires moviepy and raises `AudioExtractionError` if the video has no audio track.
- All path arguments accept `str | Path`; invalid paths raise `VideoReadError`, unsupported formats raise `UnsupportedFormatError`.
- Saved frame filenames are zero-padded to 4 digits: `frame_0000.png`, `frame_0001.png`, etc.

## Integration Points

- **Depends on**: `codomyrmex.video.config` (`get_config`), `codomyrmex.video.exceptions` (`AudioExtractionError`, `FrameExtractionError`, `UnsupportedFormatError`, `VideoReadError`), `codomyrmex.video.models` (`ExtractionResult`)
- **External**: `cv2`/`numpy` (optional), `moviepy.editor` (optional), `PIL.Image` (required)
- **Used by**: thumbnail pipelines, frame analysis workflows, audio transcription pipelines

## Navigation

- **📁 Parent**: [video](../README.md)
- **🏠 Root**: ../../../../README.md
