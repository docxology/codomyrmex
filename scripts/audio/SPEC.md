# SPEC.md — Audio Generation Scripts

## Scope
Thin orchestrator scripts delegating TTS synthesis to `codomyrmex.audio.text_to_speech.Synthesizer`.

## Inputs

| Input | Source | Type |
|-------|--------|------|
| Provider | `config/audio/config.yaml` or `--provider` | "edge-tts" or "pyttsx3" |
| Voice | `config/audio/config.yaml` | string (Edge TTS voice ID) |
| Rate / Pitch / Volume | `config/audio/config.yaml` | float |
| Text | `config/audio/config.yaml` or `--text` CLI arg | string |
| Batch texts | `config/audio/config.yaml` | list[string] |
| Output dir | `config/audio/config.yaml` | path string |

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Single synthesized audio | `outputs/audio/orchestrate_single.mp3` | MP3 (edge-tts) or WAV (pyttsx3) |
| Batch audio files | `outputs/audio/orchestrate_batch_N.mp3` | MP3 or WAV |
| Console logs | stdout | CLI helper format |
| Exit code | process | 0=success/skip, 1=error |

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| Audio extras not installed | `print_warning` + exit 0 |
| Primary provider unavailable | Try fallback provider |
| Both providers fail | `print_error` + exit 1 |
| Synthesis fails | `print_error` + exit 1 |
