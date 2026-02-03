# Audio Module - MCP Tool Specification

## Overview

This document defines Model Context Protocol (MCP) tools for the audio module, enabling AI models to interact with speech-to-text and text-to-speech functionality.

## Tools

### audio_transcribe

Transcribe speech from an audio file to text.

#### Schema

```json
{
  "name": "audio_transcribe",
  "description": "Transcribe speech from an audio file to text using Whisper",
  "inputSchema": {
    "type": "object",
    "properties": {
      "audio_path": {
        "type": "string",
        "description": "Path to the audio file to transcribe"
      },
      "language": {
        "type": "string",
        "description": "ISO 639-1 language code (e.g., 'en', 'es'). Auto-detects if not specified"
      },
      "model_size": {
        "type": "string",
        "enum": ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        "default": "base",
        "description": "Whisper model size. Larger = better quality, slower"
      },
      "output_format": {
        "type": "string",
        "enum": ["text", "srt", "vtt", "json"],
        "default": "text",
        "description": "Output format for transcription"
      },
      "word_timestamps": {
        "type": "boolean",
        "default": true,
        "description": "Include word-level timestamps"
      }
    },
    "required": ["audio_path"]
  }
}
```

#### Example

```json
{
  "name": "audio_transcribe",
  "arguments": {
    "audio_path": "/path/to/meeting.mp3",
    "language": "en",
    "model_size": "base",
    "output_format": "srt"
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "text": "Full transcription text...",
    "language": "en",
    "language_confidence": 0.98,
    "duration": 125.5,
    "segments": [
      {
        "start": 0.0,
        "end": 4.2,
        "text": "Hello and welcome..."
      }
    ],
    "output_file": "/path/to/output.srt"
  }
}
```

---

### audio_detect_language

Detect the language spoken in an audio file.

#### Schema

```json
{
  "name": "audio_detect_language",
  "description": "Detect the language of speech in an audio file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "audio_path": {
        "type": "string",
        "description": "Path to the audio file"
      }
    },
    "required": ["audio_path"]
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "language": "es",
    "language_name": "Spanish",
    "confidence": 0.95
  }
}
```

---

### audio_synthesize

Generate speech audio from text.

#### Schema

```json
{
  "name": "audio_synthesize",
  "description": "Generate speech from text using text-to-speech",
  "inputSchema": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "Text to convert to speech"
      },
      "output_path": {
        "type": "string",
        "description": "Path to save the audio file"
      },
      "provider": {
        "type": "string",
        "enum": ["pyttsx3", "edge-tts"],
        "default": "pyttsx3",
        "description": "TTS provider (pyttsx3=offline, edge-tts=neural)"
      },
      "voice": {
        "type": "string",
        "description": "Voice ID to use (e.g., 'en-US-AriaNeural')"
      },
      "rate": {
        "type": "number",
        "minimum": 0.5,
        "maximum": 2.0,
        "default": 1.0,
        "description": "Speaking rate (1.0 = normal)"
      }
    },
    "required": ["text", "output_path"]
  }
}
```

#### Example

```json
{
  "name": "audio_synthesize",
  "arguments": {
    "text": "Hello, welcome to the demo!",
    "output_path": "/path/to/output.mp3",
    "provider": "edge-tts",
    "voice": "en-US-AriaNeural",
    "rate": 1.0
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "output_path": "/path/to/output.mp3",
    "duration": 2.5,
    "format": "mp3",
    "voice_used": "en-US-AriaNeural",
    "file_size_kb": 45.2
  }
}
```

---

### audio_list_voices

List available TTS voices.

#### Schema

```json
{
  "name": "audio_list_voices",
  "description": "List available text-to-speech voices",
  "inputSchema": {
    "type": "object",
    "properties": {
      "provider": {
        "type": "string",
        "enum": ["pyttsx3", "edge-tts"],
        "default": "edge-tts",
        "description": "TTS provider to query"
      },
      "language": {
        "type": "string",
        "description": "Filter by language code (e.g., 'en', 'en-US')"
      },
      "limit": {
        "type": "integer",
        "default": 20,
        "description": "Maximum voices to return"
      }
    }
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "provider": "edge-tts",
    "voices": [
      {
        "id": "en-US-AriaNeural",
        "name": "Microsoft Aria Online (Natural) - English (United States)",
        "language": "en-US",
        "gender": "female",
        "is_neural": true
      },
      {
        "id": "en-US-GuyNeural",
        "name": "Microsoft Guy Online (Natural) - English (United States)",
        "language": "en-US",
        "gender": "male",
        "is_neural": true
      }
    ],
    "total_count": 312
  }
}
```

---

### audio_batch_transcribe

Transcribe multiple audio files.

#### Schema

```json
{
  "name": "audio_batch_transcribe",
  "description": "Transcribe multiple audio files in batch",
  "inputSchema": {
    "type": "object",
    "properties": {
      "audio_paths": {
        "type": "array",
        "items": { "type": "string" },
        "description": "List of audio file paths"
      },
      "language": {
        "type": "string",
        "description": "Language code for all files"
      },
      "model_size": {
        "type": "string",
        "enum": ["tiny", "base", "small", "medium", "large-v3"],
        "default": "base"
      },
      "output_directory": {
        "type": "string",
        "description": "Directory to save transcription files"
      }
    },
    "required": ["audio_paths"]
  }
}
```

#### Response

```json
{
  "success": true,
  "result": {
    "processed": 3,
    "failed": 0,
    "results": [
      {
        "input": "/path/to/audio1.mp3",
        "output": "/path/to/audio1.txt",
        "duration": 120.5,
        "language": "en"
      },
      {
        "input": "/path/to/audio2.mp3",
        "output": "/path/to/audio2.txt",
        "duration": 85.2,
        "language": "en"
      }
    ]
  }
}
```

---

## Error Responses

All tools return errors in this format:

```json
{
  "success": false,
  "error": {
    "type": "TranscriptionError",
    "message": "Audio file not found: /invalid/path.mp3",
    "context": {
      "audio_path": "/invalid/path.mp3"
    }
  }
}
```

### Error Types

| Error Type | Description |
|------------|-------------|
| TranscriptionError | STT processing failed |
| SynthesisError | TTS processing failed |
| AudioFormatError | Unsupported audio format |
| ModelNotLoadedError | Model not available |
| ProviderNotAvailableError | Dependencies missing |
| VoiceNotFoundError | Requested voice not found |

---

## Resource Requirements

### Compute

| Model | VRAM | CPU Fallback |
|-------|------|--------------|
| tiny | ~1GB | Yes |
| base | ~1GB | Yes |
| small | ~2GB | Slow |
| medium | ~5GB | Very slow |
| large-v3 | ~10GB | Not recommended |

### Network

| Provider | Network Required |
|----------|------------------|
| pyttsx3 | No |
| edge-tts | Yes |
| Whisper | No (local) |

---

## Usage Patterns

### Transcribe and Summarize

```json
[
  {
    "name": "audio_transcribe",
    "arguments": {
      "audio_path": "/meeting.mp3",
      "output_format": "text"
    }
  },
  {
    "name": "llm_complete",
    "arguments": {
      "prompt": "Summarize this transcript: {{previous_result.text}}"
    }
  }
]
```

### Voice-to-Voice Translation

```json
[
  {
    "name": "audio_transcribe",
    "arguments": {
      "audio_path": "/spanish.mp3",
      "language": "es"
    }
  },
  {
    "name": "llm_complete",
    "arguments": {
      "prompt": "Translate to English: {{previous_result.text}}"
    }
  },
  {
    "name": "audio_synthesize",
    "arguments": {
      "text": "{{previous_result.content}}",
      "output_path": "/english.mp3",
      "voice": "en-US-AriaNeural"
    }
  }
]
```
