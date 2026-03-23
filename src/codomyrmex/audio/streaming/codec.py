"""Audio codec negotiation for streaming.

Negotiates audio format (opus/wav/pcm/mp3) between client and server
based on available capabilities.

Example::

    client_caps = CodecCapabilities(supported=[AudioCodec.OPUS, AudioCodec.WAV])
    server_caps = CodecCapabilities(supported=[AudioCodec.WAV, AudioCodec.PCM])

    result = CodecNegotiator.negotiate(client_caps, server_caps)
    print(result.codec)  # AudioCodec.WAV
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AudioCodec(Enum):
    """Supported audio codecs."""

    PCM = "pcm"
    WAV = "wav"
    OPUS = "opus"
    MP3 = "mp3"
    OGG_VORBIS = "ogg_vorbis"
    FLAC = "flac"


# Priority order for codec selection (highest quality → most compatible)
_CODEC_PRIORITY: list[AudioCodec] = [
    AudioCodec.OPUS,
    AudioCodec.FLAC,
    AudioCodec.WAV,
    AudioCodec.OGG_VORBIS,
    AudioCodec.MP3,
    AudioCodec.PCM,
]


@dataclass
class CodecCapabilities:
    """Audio capabilities of a client or server.

    Attributes:
        supported: list of supported codecs.
        preferred: Preferred codec (optional).
        sample_rates: Supported sample rates in Hz.
        channels: Supported channel counts.
    """

    supported: list[AudioCodec] = field(
        default_factory=lambda: [AudioCodec.PCM, AudioCodec.WAV]
    )
    preferred: AudioCodec | None = None
    sample_rates: list[int] = field(default_factory=lambda: [16000, 44100, 48000])
    channels: list[int] = field(default_factory=lambda: [1, 2])


@dataclass(frozen=True)
class NegotiationResult:
    """Result of a codec negotiation.

    Attributes:
        codec: The negotiated codec.
        sample_rate: The negotiated sample rate.
        channels: The negotiated channel count.
        success: Whether negotiation succeeded.
        reason: Explanation of negotiation outcome.
    """

    codec: AudioCodec
    sample_rate: int
    channels: int
    success: bool = True
    reason: str = ""


class CodecNegotiator:
    """Negotiates audio format between client and server capabilities.

    Selection strategy:
    1. If both parties have a preferred codec in common, use it.
    2. Otherwise, pick the highest-priority codec supported by both.
    3. For sample rate and channels, pick the highest common value.

    Example::

        result = CodecNegotiator.negotiate(client_caps, server_caps)
        if result.success:
            print(f"Using {result.codec.value} at {result.sample_rate}Hz")
    """

    @staticmethod
    def negotiate(
        client: CodecCapabilities,
        server: CodecCapabilities,
    ) -> NegotiationResult:
        """Negotiate codec, sample rate, and channel count.

        Args:
            client: Client capabilities.
            server: Server capabilities.

        Returns:
            A :class:`NegotiationResult` describing the agreed format.
        """
        # Find common codecs
        client_set = set(client.supported)
        server_set = set(server.supported)
        common_codecs = client_set & server_set

        if not common_codecs:
            return NegotiationResult(
                codec=AudioCodec.PCM,
                sample_rate=16000,
                channels=1,
                success=False,
                reason="No common codec found",
            )

        # Prefer explicit preferences if shared
        if client.preferred and client.preferred in common_codecs:
            selected_codec = client.preferred
        elif server.preferred and server.preferred in common_codecs:
            selected_codec = server.preferred
        else:
            # Use priority order
            selected_codec = AudioCodec.PCM
            for codec in _CODEC_PRIORITY:
                if codec in common_codecs:
                    selected_codec = codec
                    break

        # Negotiate sample rate (highest common)
        common_rates = sorted(
            set(client.sample_rates) & set(server.sample_rates), reverse=True
        )
        selected_rate = common_rates[0] if common_rates else 16000

        # Negotiate channels (highest common)
        common_channels = sorted(
            set(client.channels) & set(server.channels), reverse=True
        )
        selected_channels = common_channels[0] if common_channels else 1

        return NegotiationResult(
            codec=selected_codec,
            sample_rate=selected_rate,
            channels=selected_channels,
            success=True,
            reason=f"Negotiated {selected_codec.value} at {selected_rate}Hz, {selected_channels}ch",
        )


__all__ = [
    "AudioCodec",
    "CodecCapabilities",
    "CodecNegotiator",
    "NegotiationResult",
]
