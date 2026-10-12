"""Real offline subprocess controls for validation before model acquisition."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from codomyrmex.audio.exceptions import AudioFormatError, TranscriptionError
from codomyrmex.audio.speech_to_text.validation import validate_audio_path

pytestmark = pytest.mark.unit


def test_capabilities_match_real_backend_metadata_without_native_imports() -> None:
    """Discovery identifies the installed backend while retaining 'whisper'."""
    script = """
import importlib.util,json,sys
from codomyrmex.audio.mcp_tools import audio_get_capabilities
installed = importlib.util.find_spec('faster_whisper') is not None
print(json.dumps({
    'installed': installed,
    'capabilities': audio_get_capabilities(),
    'native_imports': sorted(set(sys.modules) & {'faster_whisper', 'ctranslate2', 'av'}),
}))
"""
    process = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    result = json.loads(process.stdout)
    assert result["capabilities"]["status"] == "success"
    providers = result["capabilities"]["capabilities"]["stt_providers"]
    assert ("whisper" in providers) == result["installed"]
    assert "faster_whisper" not in providers
    assert result["native_imports"] == []


def test_path_validator_rejects_nonfiles_and_unsupported_suffixes(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.wav"
    directory = tmp_path / "directory.wav"
    directory.mkdir()
    text = tmp_path / "input.txt"
    text.write_text("Unsupported input")
    for path in (missing, directory):
        with pytest.raises(TranscriptionError):
            validate_audio_path(path)
    with pytest.raises(AudioFormatError):
        validate_audio_path(text)


def test_invalid_mcp_inputs_do_not_acquire_a_model(tmp_path: Path) -> None:
    """Missing weights cannot mask invalid input or create output/cache state."""
    text = tmp_path / "input.txt"
    text.write_text("Not audio")
    directory = tmp_path / "directory.wav"
    directory.mkdir()
    missing = tmp_path / "missing.wav"
    cache = tmp_path / "empty-hf-cache"
    output = tmp_path / "batch-output"
    environment = dict(os.environ)
    environment.update(
        HF_HOME=str(cache),
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        HF_HUB_DISABLE_IMPLICIT_TOKEN="1",
    )
    script = """
import json,sys
from codomyrmex.audio.mcp_tools import (
    audio_transcribe, audio_detect_language, audio_batch_transcribe,
)
from codomyrmex.audio.speech_to_text.providers import WHISPER_AVAILABLE
bad, missing, directory, output = sys.argv[1:]
print(json.dumps({
    'transcribe': audio_transcribe(bad),
    'missing': audio_transcribe(missing),
    'directory': audio_transcribe(directory),
    'language': audio_detect_language(bad),
    'batch': audio_batch_transcribe([bad, missing, directory], output),
    'empty_batch': audio_batch_transcribe([], output),
    'backend_installed': WHISPER_AVAILABLE,
}))
"""
    process = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(text),
            str(missing),
            str(directory),
            str(output),
        ],
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    result = json.loads(process.stdout)
    for name in ("transcribe", "language"):
        assert result[name]["success"] is False
        assert result[name]["error"]["type"] == "AudioFormatError"
    for name in ("missing", "directory"):
        assert result[name]["success"] is False
        assert result[name]["error"]["type"] == "TranscriptionError"
    if result["backend_installed"]:
        assert result["batch"] == {
            "success": True,
            "result": {"processed": 0, "failed": 3, "results": []},
        }
        assert result["empty_batch"] == {
            "success": True,
            "result": {"processed": 0, "failed": 0, "results": []},
        }
    else:
        assert result["batch"]["error"]["type"] == "ProviderNotAvailableError"
    assert not cache.exists()
    assert not output.exists()
