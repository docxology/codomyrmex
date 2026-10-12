# providers

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module implementation, resources, and local coordination for Providers.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `base.py` – File
- `edge_tts_provider.py` – File
- `py.typed` – File
- `pyttsx3_provider.py` – File

## Navigation

- **Parent Directory**: [text_to_speech](../README.md)
- **Project Root**: ../../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Edge stream transport ownership

For in-memory and direct-file synthesis, the installed `edge-tts` library owns
one connector per stream session. The provider does not supply a shared connector:
individual text chunks and the library's existing HTTP 403 recovery may each open
a new session, and the previous session closes its owned connector. Socket
connect/read timeouts remain 10/60 seconds. The voice-inventory request retains its
explicit IPv4 connector and awaited cleanup. No provider retry policy was added.

```bash
uv run --locked pytest -q tests/unit/audio/test_edge_tts_lifecycle.py
```

The local regression uses the actual Edge `Communicate` configuration and actual
aiohttp sessions across successive lifetimes. Live Edge synthesis requires the
remote service; HTTP 403 is an unavailable service observation, not successful
synthesis acceptance.

Both Edge synthesis paths use the same supported-prosody conversion. Speaking
rate is a multiplier mapped to `int((rate - 1) * 100)` percent; pitch preserves the
existing neutral-at-one mapping `int((pitch - 1) * 50)` Hz. Volume is a gain in
[0, 1], mapped to `int((volume - 1) * 100)` percent (1 is +0%, 0.5 is -50%, and
0 is -100%). Edge's integer setting resolution truncates toward zero. Nonfinite
settings, nonpositive speaking rate, and out-of-range volume raise `SynthesisError`.
Direct-file synthesis now honors pitch and volume, and rejects empty/whitespace
text before the Edge library opens the output file. Local tests construct real
Edge request configurations and exercise direct-file rejection with real temporary
paths; they do not establish the acoustic result of a live remote synthesis.
