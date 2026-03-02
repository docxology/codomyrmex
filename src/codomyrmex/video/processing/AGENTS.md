# Codomyrmex Agents — src/codomyrmex/video/processing

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Video manipulation operations: resize, crop, rotate, format conversion, filter
application, time-based trim, and multi-video merge. All operations use moviepy
as the primary backend (OpenCV available as fallback). Requires `uv sync --extra video`.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `video_processor.py` | `VideoProcessor` | Main class for all video manipulation operations |
| `video_processor.py` | `VideoProcessor.resize()` | Scale to target dimensions; `maintain_aspect_ratio=True` preserves ratio, ensures even pixel dimensions |
| `video_processor.py` | `VideoProcessor.crop()` | Extract rectangular region `(x, y, width, height)` |
| `video_processor.py` | `VideoProcessor.rotate()` | Rotate by angle (degrees); `expand=True` grows frame to fit |
| `video_processor.py` | `VideoProcessor.convert()` | Re-encode to different container format with codec/bitrate control |
| `video_processor.py` | `VideoProcessor.apply_filter()` | Apply `FilterType` enum: GRAYSCALE, MIRROR_H/V, INVERT, ROTATE_90/180/270, BRIGHTNESS, CONTRAST, BLUR |
| `video_processor.py` | `VideoProcessor.trim()` | Subclip `[start, end]` seconds; clamps end to video duration |
| `video_processor.py` | `VideoProcessor.merge()` | Concatenate ≥2 videos using `concatenate_videoclips(method="compose")` |
| `video_processor.py` | `SUPPORTED_INPUT_FORMATS` | `.mp4, .avi, .mov, .mkv, .webm, .wmv, .flv, .m4v` |
| `video_processor.py` | `SUPPORTED_OUTPUT_FORMATS` | `.mp4, .avi, .mov, .webm, .mkv` |

## Operating Contracts

- All operations raise `VideoProcessingError` with `operation=` field when moviepy is unavailable — no silent fallbacks.
- Default output path is `{stem}{suffix}{ext}` in the same directory as the input file.
- Output is always written with `codec="libx264"` and `audio_codec="aac"` unless `convert()` overrides them.
- `trim()` raises `VideoProcessingError` if `start >= end` after clamping end to video duration.
- All methods return `ProcessingResult` with `success`, `output_path`, `duration`, `width`, `height`, and `processing_time`.
- `merge()` closes all `VideoFileClip` objects explicitly after writing output.

## Integration Points

- **Depends on**: `codomyrmex.video.config` (`get_config`), `codomyrmex.video.exceptions`, `codomyrmex.video.models` (`FilterType`, `ProcessingResult`)
- **External**: `moviepy.editor` (required for all ops), `cv2`/`numpy` (optional)
- **Used by**: pipeline agents, CLI video commands, any workflow requiring video transformation

## Navigation

- **📁 Parent**: [video](../README.md)
- **🏠 Root**: ../../../../README.md
