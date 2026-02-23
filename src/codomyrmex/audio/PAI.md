# Audio Module - Programmable AI Interface (PAI)

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Identity

- **Name**: audio
- - **Category**: Media Processing
- **Dependencies**: logging_monitoring, environment_setup

## Capabilities

### Primary Functions

1. **Speech-to-Text Transcription**
   - Input: Audio files (WAV, MP3, FLAC, OGG, M4A, WEBM)
   - Output: TranscriptionResult with text, segments, timing
   - Provider: Whisper via faster-whisper

2. **Text-to-Speech Synthesis**
   - Input: Text string
   - Output: SynthesisResult with audio data
   - Providers: pyttsx3 (offline), edge-tts (neural)

3. **Language Detection**
   - Input: Audio file
   - Output: Language code and confidence score

### Availability Flags

```python
STT_AVAILABLE      # Speech-to-text functionality
TTS_AVAILABLE      # Text-to-speech functionality
WHISPER_AVAILABLE  # Whisper provider available
PYTTSX3_AVAILABLE  # Offline TTS available
EDGE_TTS_AVAILABLE # Neural TTS available
```

## Interface Contracts

### Transcriber Interface

```python
class Transcriber:
    def transcribe(audio_path, language=None, **kwargs) -> TranscriptionResult
    async def transcribe_async(audio_path, **kwargs) -> TranscriptionResult
    async def transcribe_stream(audio_path, **kwargs) -> AsyncIterator[TranscriptionResult]
    def detect_language(audio_path) -> tuple[str, float]
    def transcribe_batch(audio_paths, **kwargs) -> list[TranscriptionResult]
    def get_supported_languages() -> list[str]
    def unload() -> None
```

### Synthesizer Interface

```python
class Synthesizer:
    def synthesize(text, voice=None, rate=1.0, **kwargs) -> SynthesisResult
    async def synthesize_async(text, **kwargs) -> SynthesisResult
    def synthesize_to_file(text, output_path, **kwargs) -> Path
    def synthesize_batch(texts, **kwargs) -> list[SynthesisResult]
    def list_voices(language=None) -> list[VoiceInfo]
    def get_voice(voice_id) -> Optional[VoiceInfo]
    def get_supported_languages() -> list[str]
```

## Data Models

### TranscriptionResult

```python
TranscriptionResult:
    text: str                    # Full transcription
    segments: list[Segment]      # Timed segments
    language: str                # ISO 639-1 code
    language_probability: float  # 0.0-1.0
    duration: float              # Seconds
    processing_time: float       # Seconds
    model_size: WhisperModelSize
    source_path: Optional[Path]

    # Methods
    to_srt() -> str
    to_vtt() -> str
    to_json() -> dict
    save_srt(path) -> Path
    save_vtt(path) -> Path
```

### SynthesisResult

```python
SynthesisResult:
    audio_data: bytes
    format: AudioFormat          # WAV or MP3
    duration: float
    sample_rate: int
    voice_id: str
    text: str
    provider: str
    processing_time: float

    # Methods
    save(path) -> Path
    size_bytes: int
    size_kb: float
```

### VoiceInfo

```python
VoiceInfo:
    id: str                      # Unique identifier
    name: str                    # Display name
    language: str                # e.g., "en-US"
    gender: VoiceGender          # MALE, FEMALE, NEUTRAL
    is_neural: bool
    provider: str
    sample_rate: int
    styles: list[str]
```

## Error Handling

### Exception Hierarchy

```
AudioError (base)
├── TranscriptionError     # STT failures
├── SynthesisError         # TTS failures
├── AudioFormatError       # Invalid format
├── ModelNotLoadedError    # Model not ready
├── ProviderNotAvailableError  # Missing deps
└── VoiceNotFoundError     # Invalid voice
```

### Error Context

All exceptions include context:
```python
except TranscriptionError as e:
    e.context.get("audio_path")
    e.context.get("language")
    e.context.get("model_size")
```

## Configuration

### Transcriber Config

```python
TranscriptionConfig:
    language: Optional[str]      # None = auto-detect
    task: str                    # "transcribe" or "translate"
    beam_size: int = 5
    word_timestamps: bool = True
    vad_filter: bool = True
```

### TTS Config

```python
TTSConfig:
    voice: Optional[str]
    language: str = "en-US"
    rate: float = 1.0            # 0.5-2.0
    pitch: float = 1.0
    volume: float = 1.0          # 0.0-1.0
    format: AudioFormat = WAV
```

## Integration Points

### Upstream Dependencies
- `logging_monitoring` - Logging infrastructure
- `environment_setup` - Dependency validation

### Downstream Consumers
- `documents` - Save transcriptions
- `llm` - Process transcribed text
- `coding` - Voice-to-code workflows

## Resource Management

### Memory
- Whisper models: 1-10GB VRAM depending on size
- Call `transcriber.unload()` when done

### Network
- pyttsx3: No network required
- edge-tts: Requires internet

### Thread Safety
- Create separate instances per thread
- Use async methods for concurrent processing

## Versioning

- Follows semantic versioning
- Breaking changes in major versions only
- Provider additions are minor versions
