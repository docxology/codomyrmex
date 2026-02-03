# Audio Module Technical Specification

## Overview

The audio module provides speech-to-text (STT) and text-to-speech (TTS) capabilities through a provider-based architecture that allows flexibility between offline and online processing.

## Architecture

### Provider Pattern

Both STT and TTS follow a provider pattern:

```
audio/
├── speech_to_text/
│   ├── transcriber.py      # High-level interface
│   ├── models.py           # Data models
│   └── providers/
│       ├── base.py         # Abstract STTProvider
│       └── whisper_provider.py
└── text_to_speech/
    ├── synthesizer.py      # High-level interface
    ├── models.py           # Data models
    └── providers/
        ├── base.py         # Abstract TTSProvider
        ├── pyttsx3_provider.py
        └── edge_tts_provider.py
```

### Class Hierarchy

```
STTProvider (ABC)
└── WhisperProvider

TTSProvider (ABC)
├── Pyttsx3Provider
└── EdgeTTSProvider
```

## Speech-to-Text Specification

### WhisperProvider

**Backend**: faster-whisper (CTranslate2)

**Features**:
- Local processing (no internet required)
- GPU acceleration with CUDA
- VAD filtering for improved accuracy
- Word-level timestamps
- 99+ languages

**Model Loading**:
```python
WhisperModel(
    model_size,
    device="auto",      # auto, cpu, cuda
    compute_type="auto" # auto, float16, int8, float32
)
```

**Transcription Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| language | str | None | Language code (auto-detect if None) |
| task | str | "transcribe" | "transcribe" or "translate" |
| beam_size | int | 5 | Beam search size |
| word_timestamps | bool | True | Enable word timing |
| vad_filter | bool | True | Enable VAD filtering |

### TranscriptionResult

```python
@dataclass
class TranscriptionResult:
    text: str                    # Full transcription
    segments: list[Segment]      # Timed segments
    language: str                # Detected language
    language_probability: float  # Detection confidence
    duration: float              # Audio duration (seconds)
    processing_time: float       # Processing time
    model_size: WhisperModelSize
    source_path: Path
```

### Segment

```python
@dataclass
class Segment:
    id: int
    start: float              # Start time (seconds)
    end: float                # End time (seconds)
    text: str                 # Segment text
    words: list[Word]         # Word-level timing
    avg_logprob: float        # Average log probability
    no_speech_prob: float     # No-speech probability
```

## Text-to-Speech Specification

### Pyttsx3Provider

**Backend**: System TTS engines
- Windows: SAPI5
- macOS: NSSpeechSynthesizer
- Linux: espeak

**Features**:
- Completely offline
- Uses system-installed voices
- Fast synthesis

**Output**: WAV format, 22050 Hz

### EdgeTTSProvider

**Backend**: Microsoft Edge TTS (online)

**Features**:
- 300+ neural voices
- 40+ languages
- Free (no API key)
- SSML support

**Output**: MP3 format, 24000 Hz

### SynthesisResult

```python
@dataclass
class SynthesisResult:
    audio_data: bytes         # Raw audio bytes
    format: AudioFormat       # WAV or MP3
    duration: float           # Duration (seconds)
    sample_rate: int          # Sample rate (Hz)
    voice_id: str             # Voice used
    text: str                 # Original text
    provider: str             # Provider name
    processing_time: float    # Processing time
```

### VoiceInfo

```python
@dataclass
class VoiceInfo:
    id: str                   # Unique voice ID
    name: str                 # Display name
    language: str             # Language code (e.g., "en-US")
    gender: VoiceGender       # MALE, FEMALE, NEUTRAL
    is_neural: bool           # Neural/AI voice
    provider: str             # Provider name
    sample_rate: int          # Native sample rate
    styles: list[str]         # Available styles
```

## Exception Hierarchy

```
CodomyrmexError
└── AudioError
    ├── TranscriptionError
    ├── SynthesisError
    ├── AudioFormatError
    ├── ModelNotLoadedError
    ├── ProviderNotAvailableError
    └── VoiceNotFoundError
```

## Dependencies

```toml
[project.optional-dependencies]
audio = [
    "faster-whisper>=1.0.0",
    "pyttsx3>=2.90",
    "edge-tts>=6.1.0",
    "pydub>=0.25.0",
    "soundfile>=0.12.0",
]
```

## Performance Considerations

### Memory Usage

| Whisper Model | VRAM Required |
|---------------|---------------|
| tiny | ~1 GB |
| base | ~1 GB |
| small | ~2 GB |
| medium | ~5 GB |
| large-v3 | ~10 GB |

### Processing Speed

- STT: ~10x realtime for base model on GPU
- TTS (pyttsx3): Near-realtime
- TTS (edge-tts): Depends on network latency

## Thread Safety

- **Transcriber**: Not thread-safe, use separate instances per thread
- **Synthesizer (pyttsx3)**: Not thread-safe
- **Synthesizer (edge-tts)**: Thread-safe (async)

## Async Support

Both STT and TTS provide async methods:
- `transcribe_async()`
- `transcribe_stream()` (yields partial results)
- `synthesize_async()`
