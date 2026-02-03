# Audio Module - AI Agent Guidelines

## Module Purpose

The audio module enables AI agents to:
1. Transcribe speech from audio files to text
2. Generate speech from text for audio output
3. Process audio for multimodal applications

## When to Use This Module

### Use Speech-to-Text When:
- Processing voice recordings, interviews, or meetings
- Creating subtitles or captions
- Enabling voice input for applications
- Analyzing spoken content
- Transcribing podcasts or videos

### Use Text-to-Speech When:
- Creating audio content from text
- Building voice assistants
- Generating narration
- Accessibility features (screen readers)
- Creating audio previews

## Quick Reference

### Speech-to-Text

```python
from codomyrmex.audio import Transcriber, WhisperModelSize

# Create transcriber with appropriate model size
transcriber = Transcriber(model_size=WhisperModelSize.BASE)

# Transcribe audio
result = transcriber.transcribe("audio.mp3")

# Access results
print(result.text)           # Full transcription
print(result.language)       # Detected language
print(result.segments)       # Timed segments

# Export subtitles
result.save_srt("output.srt")
```

### Text-to-Speech

```python
from codomyrmex.audio import Synthesizer

# Offline synthesis (fast, no internet)
synth = Synthesizer(provider="pyttsx3")
result = synth.synthesize("Hello world!")
result.save("output.wav")

# Neural synthesis (high quality, needs internet)
synth = Synthesizer(provider="edge-tts")
result = synth.synthesize("Hello!", voice="en-US-AriaNeural")
result.save("output.mp3")
```

## Model Selection Guidelines

### Whisper Model Sizes

| Model | Use Case | Quality | Speed |
|-------|----------|---------|-------|
| tiny | Quick previews, low-resource | Basic | Fastest |
| base | General use, balanced | Good | Fast |
| small | Better accuracy needed | Better | Medium |
| medium | High accuracy required | Great | Slow |
| large-v3 | Best quality needed | Best | Slowest |

**Recommendation**: Start with `base` for most tasks, upgrade if quality is insufficient.

### TTS Provider Selection

| Provider | When to Use |
|----------|-------------|
| pyttsx3 | Offline required, speed priority |
| edge-tts | Quality priority, internet available |

## Common Patterns

### Batch Processing

```python
# Transcribe multiple files
results = transcriber.transcribe_batch([
    "audio1.mp3",
    "audio2.mp3",
    "audio3.mp3"
])

# Synthesize multiple texts
results = synth.synthesize_batch([
    "First message",
    "Second message"
])
```

### Async Processing

```python
# Async transcription
result = await transcriber.transcribe_async("audio.mp3")

# Streaming transcription (yields partial results)
async for partial in transcriber.transcribe_stream("audio.mp3"):
    print(partial.text)  # Shows progress
```

### Language Detection

```python
# Detect language before transcription
language, confidence = transcriber.detect_language("audio.mp3")
print(f"Language: {language} ({confidence:.1%} confident)")

# Then transcribe with detected language
result = transcriber.transcribe("audio.mp3", language=language)
```

### Voice Selection

```python
# List available voices
voices = synth.list_voices(language="en")
for v in voices:
    print(f"{v.id}: {v.name} ({v.gender.value})")

# Use specific voice
result = synth.synthesize("Hello", voice="en-US-AriaNeural")
```

## Error Handling

```python
from codomyrmex.audio import (
    AudioError,
    TranscriptionError,
    SynthesisError,
    ProviderNotAvailableError,
    VoiceNotFoundError,
)

try:
    result = transcriber.transcribe("audio.mp3")
except ProviderNotAvailableError:
    print("Install: uv sync --extra audio")
except TranscriptionError as e:
    print(f"Transcription failed: {e}")

try:
    result = synth.synthesize("Hello", voice="invalid-voice")
except VoiceNotFoundError as e:
    print(f"Voice not found: {e.context.get('voice_id')}")
```

## Integration Patterns

### With Document Processing

```python
# Transcribe audio and save as document
from codomyrmex.audio import Transcriber
from codomyrmex.documents import write_text

transcriber = Transcriber()
result = transcriber.transcribe("meeting.mp3")

# Save as plain text
write_text("meeting_transcript.txt", result.text)

# Save as SRT
result.save_srt("meeting_captions.srt")
```

### With LLM Processing

```python
# Transcribe and summarize
from codomyrmex.audio import Transcriber
from codomyrmex.llm import get_provider

transcriber = Transcriber()
result = transcriber.transcribe("lecture.mp3")

# Summarize with LLM
llm = get_provider("openai")
summary = llm.complete([
    {"role": "user", "content": f"Summarize: {result.text}"}
])
```

## Performance Tips

1. **Model Loading**: Load model once, reuse for multiple transcriptions
2. **Batch Processing**: Use batch methods for multiple files
3. **VAD Filtering**: Enable VAD to skip silence (default on)
4. **Memory**: Unload models when done: `transcriber.unload()`

## Limitations

- STT requires audio files (no direct microphone input)
- TTS pyttsx3 quality varies by OS
- Edge TTS requires internet connection
- Large models require significant VRAM

## Availability Checking

```python
from codomyrmex.audio import (
    STT_AVAILABLE,
    TTS_AVAILABLE,
    WHISPER_AVAILABLE,
    PYTTSX3_AVAILABLE,
    EDGE_TTS_AVAILABLE,
)

if not STT_AVAILABLE:
    print("Install audio deps: uv sync --extra audio")
```
