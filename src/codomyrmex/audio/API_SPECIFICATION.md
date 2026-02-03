# Audio Module API Specification

## Overview

This document provides the complete API reference for the audio module, including speech-to-text and text-to-speech functionality.

## Speech-to-Text API

### Transcriber

The main interface for speech-to-text transcription.

#### Constructor

```python
Transcriber(
    provider: str = "whisper",
    model_size: WhisperModelSize = WhisperModelSize.BASE,
    device: str = "auto",
    compute_type: str = "auto",
    **kwargs
) -> Transcriber
```

**Parameters:**
- `provider`: STT provider name (currently "whisper")
- `model_size`: Whisper model size enum
- `device`: Compute device ("auto", "cpu", "cuda")
- `compute_type`: Precision ("auto", "float16", "int8", "float32")

#### Methods

##### transcribe

```python
def transcribe(
    audio_path: str | Path,
    language: Optional[str] = None,
    task: str = "transcribe",
    word_timestamps: bool = True,
    vad_filter: bool = True,
    **kwargs
) -> TranscriptionResult
```

Transcribe an audio file synchronously.

**Parameters:**
- `audio_path`: Path to audio file
- `language`: ISO 639-1 language code (None for auto-detect)
- `task`: "transcribe" or "translate" (to English)
- `word_timestamps`: Include word-level timing
- `vad_filter`: Skip non-speech segments

**Returns:** `TranscriptionResult`

**Raises:**
- `TranscriptionError`: If transcription fails
- `AudioFormatError`: If format not supported

##### transcribe_async

```python
async def transcribe_async(
    audio_path: str | Path,
    language: Optional[str] = None,
    **kwargs
) -> TranscriptionResult
```

Transcribe asynchronously (runs in thread pool).

##### transcribe_stream

```python
async def transcribe_stream(
    audio_path: str | Path,
    language: Optional[str] = None,
    **kwargs
) -> AsyncIterator[TranscriptionResult]
```

Stream partial results as segments complete.

##### detect_language

```python
def detect_language(
    audio_path: str | Path
) -> tuple[str, float]
```

Detect the language of an audio file.

**Returns:** Tuple of (language_code, confidence)

##### transcribe_batch

```python
def transcribe_batch(
    audio_paths: list[str | Path],
    language: Optional[str] = None,
    **kwargs
) -> list[TranscriptionResult]
```

Transcribe multiple files sequentially.

##### transcribe_batch_async

```python
async def transcribe_batch_async(
    audio_paths: list[str | Path],
    language: Optional[str] = None,
    max_concurrent: int = 3,
    **kwargs
) -> list[TranscriptionResult]
```

Transcribe multiple files concurrently.

##### get_supported_languages

```python
def get_supported_languages() -> list[str]
```

Get list of supported language codes.

##### unload

```python
def unload() -> None
```

Unload model to free memory.

### TranscriptionResult

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| text | str | Full transcription text |
| segments | list[Segment] | Timed segments |
| language | str | Detected/specified language |
| language_probability | float | Detection confidence |
| duration | float | Audio duration (seconds) |
| processing_time | float | Processing time (seconds) |
| model_size | WhisperModelSize | Model used |
| source_path | Path | Source audio file |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| word_count | int | Total word count |
| segment_count | int | Number of segments |

#### Methods

```python
def to_srt() -> str        # Export as SRT subtitle format
def to_vtt() -> str        # Export as WebVTT format
def to_txt() -> str        # Export as plain text
def to_json() -> dict      # Export as JSON dictionary
def save_srt(path) -> Path # Save to SRT file
def save_vtt(path) -> Path # Save to VTT file
```

### Segment

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| id | int | Segment index |
| start | float | Start time (seconds) |
| end | float | End time (seconds) |
| text | str | Segment text |
| words | list[Word] | Word-level timing |
| avg_logprob | float | Average log probability |
| no_speech_prob | float | No-speech probability |

### Word

| Attribute | Type | Description |
|-----------|------|-------------|
| word | str | Word text |
| start | float | Start time |
| end | float | End time |
| probability | float | Confidence |

### WhisperModelSize

```python
class WhisperModelSize(Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"
```

---

## Text-to-Speech API

### Synthesizer

The main interface for text-to-speech synthesis.

#### Constructor

```python
Synthesizer(
    provider: str = "pyttsx3",
    config: Optional[TTSConfig] = None,
    **kwargs
) -> Synthesizer
```

**Parameters:**
- `provider`: TTS provider ("pyttsx3" or "edge-tts")
- `config`: Default synthesis configuration

#### Methods

##### synthesize

```python
def synthesize(
    text: str,
    voice: Optional[str] = None,
    rate: float = 1.0,
    pitch: float = 1.0,
    volume: float = 1.0,
    **kwargs
) -> SynthesisResult
```

Synthesize speech from text.

**Parameters:**
- `text`: Text to synthesize
- `voice`: Voice ID (None for default)
- `rate`: Speaking rate (0.5 = half speed, 2.0 = double)
- `pitch`: Pitch adjustment
- `volume`: Output volume (0.0-1.0)

**Returns:** `SynthesisResult`

**Raises:**
- `SynthesisError`: If synthesis fails
- `VoiceNotFoundError`: If voice not available

##### synthesize_async

```python
async def synthesize_async(
    text: str,
    voice: Optional[str] = None,
    **kwargs
) -> SynthesisResult
```

Synthesize asynchronously.

##### synthesize_to_file

```python
def synthesize_to_file(
    text: str,
    output_path: str | Path,
    voice: Optional[str] = None,
    **kwargs
) -> Path
```

Synthesize and save directly to file.

##### synthesize_batch

```python
def synthesize_batch(
    texts: list[str],
    voice: Optional[str] = None,
    **kwargs
) -> list[SynthesisResult]
```

Synthesize multiple texts.

##### synthesize_batch_async

```python
async def synthesize_batch_async(
    texts: list[str],
    voice: Optional[str] = None,
    max_concurrent: int = 5,
    **kwargs
) -> list[SynthesisResult]
```

Synthesize multiple texts concurrently.

##### list_voices

```python
def list_voices(
    language: Optional[str] = None
) -> list[VoiceInfo]
```

List available voices, optionally filtered by language.

##### get_voice

```python
def get_voice(voice_id: str) -> Optional[VoiceInfo]
```

Get information about a specific voice.

##### get_supported_languages

```python
def get_supported_languages() -> list[str]
```

Get list of supported language codes.

##### set_default_voice

```python
def set_default_voice(voice_id: str) -> None
```

Set the default voice for synthesis.

### SynthesisResult

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| audio_data | bytes | Raw audio bytes |
| format | AudioFormat | WAV or MP3 |
| duration | float | Duration (seconds) |
| sample_rate | int | Sample rate (Hz) |
| voice_id | str | Voice used |
| text | str | Original text |
| provider | str | Provider name |
| processing_time | float | Processing time |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| size_bytes | int | Audio data size |
| size_kb | float | Size in KB |

#### Methods

```python
def save(path: Path | str) -> Path  # Save to file
def to_dict() -> dict               # Metadata dictionary
```

### VoiceInfo

| Attribute | Type | Description |
|-----------|------|-------------|
| id | str | Unique voice ID |
| name | str | Display name |
| language | str | Language code |
| gender | VoiceGender | Voice gender |
| is_neural | bool | Neural voice flag |
| provider | str | Provider name |
| sample_rate | int | Native sample rate |
| styles | list[str] | Available styles |

### AudioFormat

```python
class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
```

### VoiceGender

```python
class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"
```

---

## Exceptions

### AudioError

Base exception for all audio errors.

```python
AudioError(message: str, audio_path: Optional[Path] = None, **kwargs)
```

### TranscriptionError

Raised when transcription fails.

```python
TranscriptionError(
    message: str,
    audio_path: Optional[Path] = None,
    language: Optional[str] = None,
    model_size: Optional[str] = None
)
```

### SynthesisError

Raised when synthesis fails.

```python
SynthesisError(
    message: str,
    text: Optional[str] = None,
    voice_id: Optional[str] = None
)
```

### AudioFormatError

Raised for unsupported formats.

```python
AudioFormatError(
    message: str,
    format_type: Optional[str] = None,
    supported_formats: Optional[list[str]] = None
)
```

### ModelNotLoadedError

Raised when model is not loaded.

```python
ModelNotLoadedError(
    message: str,
    model_name: Optional[str] = None,
    model_size: Optional[str] = None
)
```

### ProviderNotAvailableError

Raised when provider dependencies are missing.

```python
ProviderNotAvailableError(
    message: str,
    provider_name: Optional[str] = None,
    missing_packages: Optional[list[str]] = None
)
```

### VoiceNotFoundError

Raised when requested voice is unavailable.

```python
VoiceNotFoundError(
    message: str,
    voice_id: Optional[str] = None,
    available_voices: Optional[list[str]] = None
)
```
