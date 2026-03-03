# PAI.md — Audio Generation Scripts

## PAI Phase Mapping

| PAI Phase | Action | Script |
|-----------|--------|--------|
| BUILD | Synthesize speech from text | `orchestrate.py` |
| EXECUTE | Run synthesis with config params | `orchestrate.py --text "..."` |
| OBSERVE | Check outputs in `outputs/audio/` | (filesystem) |

## PAI Tool Invocation

```python
# Via direct Python (recommended for PAI agents)
from codomyrmex.audio import Synthesizer

# Neural TTS (edge-tts)
synth = Synthesizer(provider="edge-tts")
result = synth.synthesize("Hello, world!", voice="en-US-AriaNeural")
result.save("outputs/audio/output.mp3")

# Offline TTS (pyttsx3)
synth_offline = Synthesizer(provider="pyttsx3")
result = synth_offline.synthesize("Hello, world!")
result.save("outputs/audio/output.wav")

# To file directly
synth.synthesize_to_file("Text here", "outputs/audio/output.mp3")
```

## Config Control

PAI agents modify `config/audio/config.yaml` to control synthesis:

```yaml
generation:
  tts:
    default_provider: "edge-tts"
    default_voice: "en-GB-SoniaNeural"   # UK female voice
    rate: 0.9                             # Slightly slower
    default_text: "Your custom text"
```

## Voice Reference (edge-tts)

Common voices: `en-US-AriaNeural`, `en-US-GuyNeural`, `en-GB-SoniaNeural`,
`en-AU-NatashaNeural`, `es-ES-AlvaroNeural`, `fr-FR-DeniseNeural`

Full list: `synth.list_voices(language="en-US")`
