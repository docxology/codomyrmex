<!-- readme: generated -->

# video

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/video/`

## Overview

Video processing module for Codomyrmex.

This module provides video processing capabilities including:
- Video processing (resize, crop, rotate, convert, filter, trim, merge)
- Frame extraction and thumbnail generation
- Audio extraction from video
- Video analysis and metadata extraction
- **URL video transcription** via ``nativ3ai/universal-video-transcriber``
  (yt-dlp → ffmpeg → faster-whisper → JSON)

## Submodules

| Submodule | Description |
|-----------|-------------|
| `processing:` | Video manipulation operations |
| `extraction:` | Frame and audio extraction |
| `analysis:` | Video metadata and comparison |
| `transcription:` | URL video transcription (universal-video-transcriber) |

## Public Exports

`video` exports 34 public symbols via `__all__`:

`ANALYSIS_AVAILABLE`, `EXTRACTION_AVAILABLE`, `MOVIEPY_AVAILABLE`, `OPENCV_AVAILABLE`, `PIL_AVAILABLE`, `PROCESSING_AVAILABLE`, `TRANSCRIPTION_AVAILABLE`, `AudioCodec`, `AudioExtractionError`, `ExtractionResult`, `FilterType`, `FrameExtractionError`, `ProcessingResult`, `TranscriptionResult`, `TranscriptionSegment`, `TranscriptionWord`, `UnsupportedFormatError`, `VideoAnalysisError`, `VideoCodec`, `VideoComparison`, `VideoConfig`, `VideoError`, `VideoInfo`, `VideoProcessingError` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../video/](../../../../video/)
