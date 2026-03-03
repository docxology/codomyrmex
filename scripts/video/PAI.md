# PAI.md — Video Generation Scripts

## PAI Phase Mapping

| PAI Phase | Action | Script |
|-----------|--------|--------|
| BUILD | Generate video from text prompt | `orchestrate.py` |
| EXECUTE | Run generation with config params | `orchestrate.py --prompt "..."` |
| OBSERVE | Check outputs in `outputs/videos/` | (filesystem) |

## PAI Tool Invocation

```python
# Via codomyrmex coding module (PAI BUILD phase)
from codomyrmex.coding import code_execute
result = code_execute(
    code_path="scripts/video/orchestrate.py",
    env={"GEMINI_API_KEY": "<key>"}
)

# Via direct Python (recommended for PAI agents)
from codomyrmex.video.generation.video_generator import VideoGenerator
generator = VideoGenerator()
results = generator.generate(prompt="A mountain at dawn", model="veo-2.0-generate-001")
```

## Config Control

PAI agents should modify `config/video/config.yaml` to change generation behaviour without touching script code:

```yaml
generation:
  video:
    model: "veo-2.0-generate-001"
    default_prompt: "Your custom prompt here"
    aspect_ratio: "9:16"   # Change for vertical/portrait
    duration_seconds: 10   # Change for longer clips
```

## Notes

- Veo 2.0 requires an active `GEMINI_API_KEY` with video generation enabled
- Generation is synchronous from the script's perspective but may involve server-side async polling
- Output bytes availability depends on the API response format (may be URI instead of bytes)
