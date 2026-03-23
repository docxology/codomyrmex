"""Universal Video Transcriber — Codomyrmex integration.

Wraps the ``nativ3ai/universal-video-transcriber`` pipeline:

    URL → yt-dlp fetch → ffmpeg normalize → faster-whisper ASR → JSON

Supports any site resolvable by ``yt-dlp`` (YouTube, X/Twitter, Telegram,
Reddit, Vimeo, and thousands of others).

Two execution modes:

* **CLI mode** (default): calls ``transcribe_url.py`` from a local clone of
  ``universal-video-transcriber``, so no server process is needed.
* **REST mode**: hits the running API server at
  ``http://127.0.0.1:8099/transcribe`` (start with
  ``python3 run_api.py`` inside the skill).

Usage::

    from codomyrmex.video.transcription import VideoTranscriber

    t = VideoTranscriber()

    # Doctor check
    result = t.doctor()
    print(result)

    # Transcribe a URL
    tr = t.transcribe("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(tr.transcript)  # Full text
    for seg in tr.segments:  # Timed segments
        print(seg.start, seg.text)

"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Default locations
# ---------------------------------------------------------------------------

_DEFAULT_SKILL_DIR = (
    Path.home() / ".hermes" / "skills" / "research" / "universal-video-transcriber"
)
_DEFAULT_SCRIPT = (
    _DEFAULT_SKILL_DIR
    / "skill"
    / "video-url-transcriber"
    / "scripts"
    / "transcribe_url.py"
)
_DEFAULT_API_URL = "http://127.0.0.1:8099/transcribe"

# Whisper model size options
WHISPER_MODELS = ("tiny", "base", "small", "medium", "large-v2", "large-v3")


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class TranscriptionWord:
    """A single word with timing information.

    Attributes:
        word: The word text.
        start: Start time in seconds.
        end: End time in seconds.
    """

    word: str
    start: float = 0.0
    end: float = 0.0


@dataclass
class TranscriptionSegment:
    """A timed segment of speech.

    Attributes:
        id: Segment index.
        start: Start time in seconds.
        end: End time in seconds.
        text: Transcript text for this segment.
        speaker: Speaker label (if diarization was run), else None.
        words: Word-level timestamps (if ``word_timestamps=True``).
    """

    id: int = 0
    start: float = 0.0
    end: float = 0.0
    text: str = ""
    speaker: str | None = None
    words: list[TranscriptionWord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to dict."""
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "speaker": self.speaker,
            "words": [
                {"word": w.word, "start": w.start, "end": w.end} for w in self.words
            ],
        }


@dataclass
class TranscriptionResult:
    """Full transcription output for a URL.

    The response shape matches the ``universal-video-transcriber`` JSON schema
    exactly, so raw API responses can be fed directly to
    :meth:`TranscriptionResult.from_dict`.

    Attributes:
        source_url: Original URL that was transcribed.
        platform: Detected platform (e.g. ``"youtube"``, ``"x"``).
        title: Video title as reported by yt-dlp.
        duration_sec: Duration in seconds.
        language: Detected language code (e.g. ``"en"``).
        transcript: Full concatenated transcript text.
        segments: List of timed :class:`TranscriptionSegment` objects.
        metadata: Raw metadata from yt-dlp and whisper.
        status: ``"completed"``, ``"error"``, or ``"running"``.
        error: Error message if ``status == "error"``.
        elapsed_sec: Wall-clock time taken to transcribe.
    """

    source_url: str = ""
    platform: str = ""
    title: str = ""
    duration_sec: float = 0.0
    language: str = ""
    transcript: str = ""
    segments: list[TranscriptionSegment] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "completed"
    error: str = ""
    elapsed_sec: float = 0.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise to dict (mirrors upstream JSON schema)."""
        return {
            "source_url": self.source_url,
            "platform": self.platform,
            "title": self.title,
            "duration_sec": self.duration_sec,
            "language": self.language,
            "transcript": self.transcript,
            "segments": [s.to_dict() for s in self.segments],
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error,
            "elapsed_sec": self.elapsed_sec,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TranscriptionResult:
        """Build a :class:`TranscriptionResult` from a raw API/CLI JSON dict."""
        segments: list[TranscriptionSegment] = []
        for s in data.get("segments") or []:
            words = [
                TranscriptionWord(w["word"], w.get("start", 0.0), w.get("end", 0.0))
                for w in (s.get("words") or [])
            ]
            segments.append(
                TranscriptionSegment(
                    id=s.get("id", 0),
                    start=s.get("start", 0.0),
                    end=s.get("end", 0.0),
                    text=s.get("text", ""),
                    speaker=s.get("speaker"),
                    words=words,
                )
            )
        return cls(
            source_url=data.get("source_url", ""),
            platform=data.get("platform", ""),
            title=data.get("title", ""),
            duration_sec=float(data.get("duration_sec", 0)),
            language=data.get("language", ""),
            transcript=data.get("transcript", ""),
            segments=segments,
            metadata=data.get("metadata") or {},
            status=data.get("status", "completed"),
            error=data.get("error", ""),
        )

    @property
    def segment_count(self) -> int:
        """Number of timed segments."""
        return len(self.segments)

    @property
    def word_count(self) -> int:
        """Approximate word count of the transcript."""
        return len(self.transcript.split())


# ---------------------------------------------------------------------------
# Main transcriber class
# ---------------------------------------------------------------------------


class VideoTranscriber:
    """Platform-agnostic video URL → transcript pipeline.

    Wraps ``nativ3ai/universal-video-transcriber``:
    ``URL → yt-dlp → ffmpeg → faster-whisper → JSON``.

    Supports any site resolvable by ``yt-dlp``.

    Args:
        skill_dir: Path to the local clone of ``universal-video-transcriber``.
            Defaults to ``~/.hermes/skills/research/universal-video-transcriber``.
        api_url: Base URL for the REST API server (mode ``"rest"``).
        mode: ``"cli"`` (default) or ``"rest"``.  ``"auto"`` picks CLI if the
            script exists, else REST.

    """

    def __init__(
        self,
        skill_dir: str | Path | None = None,
        api_url: str = _DEFAULT_API_URL,
        mode: str = "auto",
    ) -> None:
        self._skill_dir = Path(skill_dir or _DEFAULT_SKILL_DIR).expanduser()
        self._script = (
            self._skill_dir
            / "skill"
            / "video-url-transcriber"
            / "scripts"
            / "transcribe_url.py"
        )
        self._api_url = api_url
        self._venv_python = self._skill_dir / ".venv" / "bin" / "python3"
        self._mode = mode

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def active_mode(self) -> str:
        """Return the resolved execution mode: ``"cli"`` or ``"rest"``."""
        if self._mode == "auto":
            return "cli" if self._script.exists() else "rest"
        return self._mode

    def doctor(self) -> dict[str, Any]:
        """Check that all dependencies are available.

        Returns:
            dict with keys: ``ok``, ``mode``, ``dependencies``, ``message``.

        """
        deps: dict[str, bool] = {}
        deps["yt_dlp"] = bool(shutil.which("yt-dlp"))
        deps["ffmpeg"] = bool(shutil.which("ffmpeg"))
        deps["script_exists"] = self._script.exists()
        deps["venv_python"] = self._venv_python.exists()

        if self.active_mode == "cli":
            # Run --doctor on the script
            if self._script.exists():
                python = (
                    str(self._venv_python)
                    if self._venv_python.exists()
                    else sys.executable
                )
                proc = subprocess.run(
                    [python, str(self._script), "--doctor"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                deps["script_doctor"] = proc.returncode == 0
                doctor_output = proc.stdout.strip() or proc.stderr.strip()
            else:
                deps["script_doctor"] = False
                doctor_output = f"Script not found at {self._script}"
        else:
            # REST mode — ping the API
            try:
                import urllib.request

                req = urllib.request.Request(
                    self._api_url.rstrip("/") + "/health", method="GET"
                )
                urllib.request.urlopen(req, timeout=3)
                deps["api_reachable"] = True
                doctor_output = f"REST API reachable at {self._api_url}"
            except Exception as exc:
                deps["api_reachable"] = False
                doctor_output = f"REST API unreachable: {exc}"

        ok = all(deps.values())
        return {
            "ok": ok,
            "mode": self.active_mode,
            "dependencies": deps,
            "message": doctor_output if not ok else "All checks passed",
        }

    def transcribe(
        self,
        url: str,
        model_size: str = "small",
        language: str | None = None,
        word_timestamps: bool = True,
        persist_media: bool = False,
        cookies_from_browser: str | None = None,
        timeout: int = 600,
    ) -> TranscriptionResult:
        """Transcribe a video URL.

        Args:
            url: Any URL resolvable by yt-dlp.
            model_size: Whisper model size: ``"tiny"``, ``"base"``,
                ``"small"`` (default), ``"medium"``, ``"large-v2"``,
                ``"large-v3"``.
            language: Force language code (e.g. ``"en"``). ``None`` = auto-detect.
            word_timestamps: Include word-level timestamps (default True).
            persist_media: Keep downloaded media after transcription.
            cookies_from_browser: Browser name for cookie extraction
                (e.g. ``"chrome"``, ``"firefox"``, ``"safari"``).
            timeout: Max seconds to wait for the pipeline to complete.

        Returns:
            :class:`TranscriptionResult`

        Raises:
            VideoTranscriberError: On pipeline or parsing failure.

        """
        t0 = time.time()
        if self.active_mode == "cli":
            result = self._transcribe_cli(
                url,
                model_size,
                language,
                word_timestamps,
                persist_media,
                cookies_from_browser,
                timeout,
            )
        else:
            result = self._transcribe_rest(
                url,
                model_size,
                language,
                word_timestamps,
                persist_media,
                timeout,
            )
        result.elapsed_sec = round(time.time() - t0, 2)
        return result

    def transcribe_to_dict(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Transcribe and return a plain dict (MCP-friendly).

        Keyword arguments are forwarded to :meth:`transcribe`.

        Returns:
            dict matching the upstream JSON schema.

        """
        try:
            result = self.transcribe(url, **kwargs)
            return result.to_dict()
        except Exception as exc:
            return {
                "source_url": url,
                "status": "error",
                "error": str(exc),
                "transcript": "",
                "segments": [],
            }

    # ------------------------------------------------------------------
    # CLI backend
    # ------------------------------------------------------------------

    def _transcribe_cli(
        self,
        url: str,
        model_size: str,
        language: str | None,
        word_timestamps: bool,
        persist_media: bool,
        cookies_from_browser: str | None,
        timeout: int,
    ) -> TranscriptionResult:
        """Run the CLI pipeline and parse JSON output."""
        python = (
            str(self._venv_python) if self._venv_python.exists() else sys.executable
        )
        cmd = [
            python,
            str(self._script),
            url,
            "--model-size",
            model_size,
            "--output-format",
            "json",
        ]
        if language:
            cmd += ["--language", language]
        if not word_timestamps:
            cmd.append("--no-word-timestamps")
        if persist_media:
            cmd.append("--persist-media")
        if cookies_from_browser:
            cmd += ["--cookies-from-browser", cookies_from_browser]

        logger.info(
            "VideoTranscriber CLI: %s model=%s url=%.80s",
            " ".join(cmd[:3]),
            model_size,
            url,
        )
        env = dict(os.environ)
        env["NO_COLOR"] = "1"

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return TranscriptionResult(
                source_url=url,
                status="error",
                error=f"Transcription timed out after {timeout}s",
            )

        if proc.returncode != 0:
            return TranscriptionResult(
                source_url=url,
                status="error",
                error=proc.stderr.strip() or proc.stdout.strip(),
            )

        # Parse JSON from stdout (may have leading log lines)
        return self._parse_json_output(proc.stdout, url)

    # ------------------------------------------------------------------
    # REST backend
    # ------------------------------------------------------------------

    def _transcribe_rest(
        self,
        url: str,
        model_size: str,
        language: str | None,
        word_timestamps: bool,
        persist_media: bool,
        timeout: int,
    ) -> TranscriptionResult:
        """Call the REST API and parse the JSON response."""
        import urllib.request

        payload = {
            "url": url,
            "language": language,
            "model_size": model_size,
            "word_timestamps": word_timestamps,
            "persist_media": persist_media,
        }
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            self._api_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        logger.info("VideoTranscriber REST: POST %s url=%.80s", self._api_url, url)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode()
        except Exception as exc:
            return TranscriptionResult(source_url=url, status="error", error=str(exc))
        return self._parse_json_output(raw, url)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json_output(raw: str, url: str) -> TranscriptionResult:
        """Find and parse the first JSON object in *raw* output."""
        # Find the JSON block (may have logging prefix lines)
        start = raw.find("{")
        if start == -1:
            return TranscriptionResult(
                source_url=url,
                status="error",
                error=f"No JSON found in output: {raw[:300]}",
            )
        try:
            data = json.loads(raw[start:])
        except json.JSONDecodeError:
            # Try to find the last complete JSON object
            try:
                last = raw.rfind("}")
                data = json.loads(raw[start : last + 1])
            except Exception as exc:
                return TranscriptionResult(
                    source_url=url, status="error", error=f"JSON parse error: {exc}"
                )
        result = TranscriptionResult.from_dict(data)
        if not result.source_url:
            result.source_url = url
        return result


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class VideoTranscriberError(Exception):
    """Raised on transcription pipeline failures."""


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def transcribe_url(
    url: str,
    model_size: str = "small",
    **kwargs: Any,
) -> TranscriptionResult:
    """Top-level convenience function.

    Creates a :class:`VideoTranscriber` with default settings and transcribes *url*.

    Args:
        url: Video URL to transcribe.
        model_size: Whisper model size (default ``"small"``).
        **kwargs: Forwarded to :meth:`VideoTranscriber.transcribe`.

    Returns:
        :class:`TranscriptionResult`

    """
    return VideoTranscriber().transcribe(url, model_size=model_size, **kwargs)


__all__ = [
    "WHISPER_MODELS",
    "TranscriptionResult",
    "TranscriptionSegment",
    "TranscriptionWord",
    "VideoTranscriber",
    "VideoTranscriberError",
    "transcribe_url",
]
