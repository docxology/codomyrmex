# Video Module - MCP Tool Specification

## Overview

This document defines Model Context Protocol (MCP) tools for the video module.

## Tools

### video_process

Process a video with various operations.

#### Schema

```json
{
  "name": "video_process",
  "description": "Process a video file with operations like resize, crop, trim, filter",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the input video file"
      },
      "operation": {
        "type": "string",
        "enum": ["resize", "crop", "rotate", "trim", "filter", "convert"],
        "description": "Processing operation to perform"
      },
      "output_path": {
        "type": "string",
        "description": "Path for output video (auto-generated if not provided)"
      },
      "width": {
        "type": "integer",
        "description": "Target width for resize/crop"
      },
      "height": {
        "type": "integer",
        "description": "Target height for resize/crop"
      },
      "x": {
        "type": "integer",
        "description": "X position for crop"
      },
      "y": {
        "type": "integer",
        "description": "Y position for crop"
      },
      "angle": {
        "type": "number",
        "description": "Rotation angle in degrees"
      },
      "start": {
        "type": "number",
        "description": "Start time in seconds for trim"
      },
      "end": {
        "type": "number",
        "description": "End time in seconds for trim"
      },
      "filter_type": {
        "type": "string",
        "enum": ["grayscale", "blur", "sharpen", "brightness", "contrast", "sepia", "invert", "mirror_horizontal", "mirror_vertical"],
        "description": "Filter to apply"
      },
      "output_format": {
        "type": "string",
        "enum": ["mp4", "avi", "mov", "webm"],
        "description": "Output format for convert"
      }
    },
    "required": ["video_path", "operation"]
  }
}
```

#### Examples

**Resize:**
```json
{
  "name": "video_process",
  "arguments": {
    "video_path": "/path/to/input.mp4",
    "operation": "resize",
    "width": 1280,
    "height": 720
  }
}
```

**Trim:**
```json
{
  "name": "video_process",
  "arguments": {
    "video_path": "/path/to/input.mp4",
    "operation": "trim",
    "start": 10.0,
    "end": 30.0
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "output_path": "/path/to/output_resized.mp4",
    "duration": 125.5,
    "width": 1280,
    "height": 720,
    "file_size_mb": 45.2,
    "processing_time": 12.5
  }
}
```

---

### video_extract_frame

Extract a frame from a video.

#### Schema

```json
{
  "name": "video_extract_frame",
  "description": "Extract a single frame from a video at specified timestamp",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the video file"
      },
      "timestamp": {
        "type": "number",
        "description": "Time in seconds to extract frame"
      },
      "output_path": {
        "type": "string",
        "description": "Path to save the frame image"
      },
      "format": {
        "type": "string",
        "enum": ["png", "jpg", "webp"],
        "default": "png",
        "description": "Output image format"
      }
    },
    "required": ["video_path", "timestamp", "output_path"]
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "output_path": "/path/to/frame.png",
    "timestamp": 5.0,
    "width": 1920,
    "height": 1080
  }
}
```

---

### video_extract_frames

Extract multiple frames at intervals.

#### Schema

```json
{
  "name": "video_extract_frames",
  "description": "Extract multiple frames from a video at regular intervals",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the video file"
      },
      "interval": {
        "type": "number",
        "description": "Time between frames in seconds"
      },
      "start": {
        "type": "number",
        "default": 0,
        "description": "Start time in seconds"
      },
      "end": {
        "type": "number",
        "description": "End time in seconds (null for video end)"
      },
      "output_directory": {
        "type": "string",
        "description": "Directory to save frames"
      },
      "format": {
        "type": "string",
        "enum": ["png", "jpg"],
        "default": "png"
      }
    },
    "required": ["video_path", "interval", "output_directory"]
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "frame_count": 30,
    "output_paths": [
      "/path/to/frame_0000.png",
      "/path/to/frame_0001.png"
    ],
    "timestamps": [0.0, 1.0, 2.0]
  }
}
```

---

### video_thumbnail

Generate a thumbnail from a video.

#### Schema

```json
{
  "name": "video_thumbnail",
  "description": "Generate a thumbnail image from a video",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the video file"
      },
      "output_path": {
        "type": "string",
        "description": "Path to save the thumbnail"
      },
      "timestamp": {
        "type": "number",
        "description": "Time to capture (null for auto)"
      },
      "width": {
        "type": "integer",
        "default": 320,
        "description": "Thumbnail width in pixels"
      }
    },
    "required": ["video_path", "output_path"]
  }
}
```

---

### video_extract_audio

Extract audio track from a video.

#### Schema

```json
{
  "name": "video_extract_audio",
  "description": "Extract audio track from a video file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the video file"
      },
      "output_path": {
        "type": "string",
        "description": "Path for extracted audio"
      },
      "audio_format": {
        "type": "string",
        "enum": ["mp3", "wav", "aac"],
        "default": "mp3"
      },
      "bitrate": {
        "type": "string",
        "default": "192k",
        "description": "Audio bitrate"
      }
    },
    "required": ["video_path", "output_path"]
  }
}
```

---

### video_info

Get video file information.

#### Schema

```json
{
  "name": "video_info",
  "description": "Get metadata and information about a video file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the video file"
      }
    },
    "required": ["video_path"]
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "duration": 125.5,
    "width": 1920,
    "height": 1080,
    "fps": 29.97,
    "frame_count": 3762,
    "video_codec": "h264",
    "audio_codec": "aac",
    "has_audio": true,
    "file_size_mb": 156.4
  }
}
```

---

### video_merge

Merge multiple videos into one.

#### Schema

```json
{
  "name": "video_merge",
  "description": "Merge multiple video files into a single video",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_paths": {
        "type": "array",
        "items": { "type": "string" },
        "description": "List of video file paths to merge"
      },
      "output_path": {
        "type": "string",
        "description": "Path for merged output video"
      }
    },
    "required": ["video_paths", "output_path"]
  }
}
```

---

### video_validate

Validate a video file.

#### Schema

```json
{
  "name": "video_validate",
  "description": "Check if a file is a valid, readable video",
  "inputSchema": {
    "type": "object",
    "properties": {
      "video_path": {
        "type": "string",
        "description": "Path to the video file"
      }
    },
    "required": ["video_path"]
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "is_valid": true,
    "has_audio": true,
    "format": "mp4",
    "codec": "h264"
  }
}
```

---

## Error Responses

```json
{
  "success": false,
  "error": {
    "type": "VideoProcessingError",
    "message": "Failed to process video: codec not supported",
    "context": {
      "video_path": "/path/to/video.mp4",
      "operation": "convert"
    }
  }
}
```

### Error Types

| Error Type | Description |
|------------|-------------|
| VideoReadError | Cannot read video file |
| VideoWriteError | Cannot write output file |
| VideoProcessingError | Processing operation failed |
| FrameExtractionError | Frame extraction failed |
| AudioExtractionError | Audio extraction failed |
| UnsupportedFormatError | Format not supported |

---

## Usage Patterns

### Extract Frames for Vision Analysis

```json
[
  {
    "name": "video_extract_frames",
    "arguments": {
      "video_path": "/video.mp4",
      "interval": 5.0,
      "output_directory": "/frames"
    }
  },
  {
    "name": "vision_analyze",
    "arguments": {
      "image_paths": "{{previous_result.output_paths}}"
    }
  }
]
```

### Extract and Transcribe Audio

```json
[
  {
    "name": "video_extract_audio",
    "arguments": {
      "video_path": "/video.mp4",
      "output_path": "/audio.mp3"
    }
  },
  {
    "name": "audio_transcribe",
    "arguments": {
      "audio_path": "/audio.mp3"
    }
  }
]
```
