# SPEC.md — Video Generation Scripts

## Scope
Thin orchestrator scripts that delegate video generation to `codomyrmex.video.generation.VideoGenerator`.

## Inputs

| Input | Source | Type |
|-------|--------|------|
| Generation model | `config/video/config.yaml` | string |
| Prompt | `config/video/config.yaml` or `--prompt` CLI arg | string |
| Number of videos | `config/video/config.yaml` | int (1–4) |
| Aspect ratio | `config/video/config.yaml` | "16:9" or "9:16" |
| Duration | `config/video/config.yaml` | int (seconds) |
| API key | `GEMINI_API_KEY` env var | string |

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Generated videos | `outputs/videos/video_N.mp4` | MP4 |
| Console logs | stdout | CLI helper format |
| Exit code | process | 0=success/skip, 1=error |

## Constraints

- Scripts are **thin** — no business logic beyond config loading and file saving
- All generation logic lives in `src/codomyrmex/video/`
- API key absence is a **soft skip** (exit 0), not a hard error
- Output directory is created automatically; no pre-existing path required

## Error Handling

| Condition | Behaviour |
|-----------|-----------|
| No API key | `print_warning` + exit 0 |
| API call fails | `print_error` + exit 1 |
| Output dir missing | `mkdir(parents=True, exist_ok=True)` |
| Video returned as URI | Print URI, do not save bytes |
