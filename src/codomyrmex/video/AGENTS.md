# Video Module - AI Agent Guidelines

## Module Purpose

The video module enables AI agents to:
1. Process and transform video files
2. Extract frames for visual analysis
3. Extract audio for further processing
4. Analyze video metadata

## When to Use This Module

### Use VideoProcessor When:
- Resizing videos for different platforms
- Trimming videos to specific segments
- Applying filters or effects
- Converting between formats
- Merging multiple videos

### Use FrameExtractor When:
- Getting frames for visual AI analysis
- Creating thumbnails for previews
- Extracting specific moments from video
- Getting audio for transcription

### Use VideoAnalyzer When:
- Validating video files
- Getting video metadata
- Comparing video properties
- Checking video compatibility

## Quick Reference

### Video Processing

```python
from codomyrmex.video import VideoProcessor, FilterType

processor = VideoProcessor()

# Resize to 720p
result = processor.resize("video.mp4", width=1280, height=720)

# Trim 10-30 seconds
result = processor.trim("video.mp4", start=10.0, end=30.0)

# Apply grayscale filter
result = processor.apply_filter("video.mp4", FilterType.GRAYSCALE)

# Convert format
result = processor.convert("video.avi", output_format="mp4")
```

### Frame Extraction

```python
from codomyrmex.video import FrameExtractor

extractor = FrameExtractor()

# Single frame
frame = extractor.extract_frame("video.mp4", timestamp=5.0)

# Thumbnail
thumb = extractor.generate_thumbnail("video.mp4", width=320)

# Multiple frames
frames = extractor.extract_frames("video.mp4", interval=1.0)

# Extract audio for transcription
audio_path = extractor.extract_audio("video.mp4", audio_format="mp3")
```

### Video Analysis

```python
from codomyrmex.video import VideoAnalyzer

analyzer = VideoAnalyzer()

# Get full info
info = analyzer.get_info("video.mp4")
print(f"{info.width}x{info.height}, {info.duration}s, {info.fps} fps")

# Quick checks
is_valid = analyzer.is_valid_video("video.mp4")
has_audio = analyzer.has_audio("video.mp4")
```

## Common Patterns

### Extract Frame for Vision AI

```python
from codomyrmex.video import FrameExtractor
import base64

extractor = FrameExtractor()
frame = extractor.extract_frame("video.mp4", timestamp=5.0)

# Save temporarily for vision model
frame.save("/tmp/frame.png")

# Or convert to base64
import io
buffer = io.BytesIO()
frame.save(buffer, format="PNG")
image_base64 = base64.b64encode(buffer.getvalue()).decode()
```

### Extract Audio for Transcription

```python
from codomyrmex.video import FrameExtractor
from codomyrmex.audio import Transcriber

extractor = FrameExtractor()
audio_path = extractor.extract_audio("video.mp4", audio_format="mp3")

transcriber = Transcriber()
result = transcriber.transcribe(audio_path)
print(result.text)
```

### Process Video Pipeline

```python
from codomyrmex.video import VideoProcessor, FilterType

processor = VideoProcessor()

# 1. Trim to relevant section
result = processor.trim("input.mp4", start=60.0, end=120.0)

# 2. Resize for web
result = processor.resize(result.output_path, width=1280, height=720)

# 3. Convert to web format
result = processor.convert(result.output_path, output_format="webm")
```

### Validate Before Processing

```python
from codomyrmex.video import VideoAnalyzer, VideoProcessor

analyzer = VideoAnalyzer()

# Check if valid first
if analyzer.is_valid_video("input.mp4"):
    info = analyzer.get_info("input.mp4")

    # Check if processing needed
    if info.width > 1920:
        processor = VideoProcessor()
        processor.resize("input.mp4", width=1920, height=1080)
```

## Error Handling

```python
from codomyrmex.video import (
    VideoError,
    VideoReadError,
    UnsupportedFormatError,
    VideoProcessingError,
    FrameExtractionError,
)

try:
    processor = VideoProcessor()
    result = processor.resize("video.mp4", 1280, 720)
except VideoReadError as e:
    print(f"Cannot read video: {e.context.get('video_path')}")
except UnsupportedFormatError as e:
    print(f"Format not supported: {e.context.get('format_type')}")
except VideoProcessingError as e:
    print(f"Processing failed: {e.context.get('operation')}")
```

## Integration Examples

### With LLM Vision

```python
from codomyrmex.video import FrameExtractor, VideoAnalyzer
from codomyrmex.llm import get_provider

analyzer = VideoAnalyzer()
extractor = FrameExtractor()
llm = get_provider("openai")

# Get key frames
info = analyzer.get_info("video.mp4")
timestamps = [info.duration * i / 5 for i in range(5)]  # 5 samples

frames = []
for ts in timestamps:
    frame = extractor.extract_frame("video.mp4", ts)
    frames.append(frame)

# Analyze with vision model
# ... send frames to LLM vision API
```

### With Audio Module

```python
from codomyrmex.video import FrameExtractor
from codomyrmex.audio import Transcriber, Synthesizer

extractor = FrameExtractor()
transcriber = Transcriber()

# Extract and transcribe audio
audio_path = extractor.extract_audio("video.mp4")
result = transcriber.transcribe(audio_path)

# Save transcription
result.save_srt("video.srt")
```

## Performance Tips

1. **Use appropriate model/codec**: H264 for compatibility, VP9 for web
2. **Check before processing**: Validate videos before expensive operations
3. **Batch frame extraction**: Use intervals rather than multiple single calls
4. **Clean up**: Delete temporary files after processing
5. **Memory**: Large videos may require significant RAM

## Limitations

- Maximum resolution depends on available memory
- Some codecs may require system dependencies
- Real-time processing not supported
- No direct camera/stream input

## Availability Checking

```python
from codomyrmex.video import (
    PROCESSING_AVAILABLE,
    EXTRACTION_AVAILABLE,
    ANALYSIS_AVAILABLE,
    MOVIEPY_AVAILABLE,
    OPENCV_AVAILABLE,
)

if not PROCESSING_AVAILABLE:
    print("Install: uv sync --extra video")
```
