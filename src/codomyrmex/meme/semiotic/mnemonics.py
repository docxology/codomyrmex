"""Mnemotechnical device construction."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MnemonicDevice:
    """A mnemonic device — structured memory aid for robust storage.

    Attributes:
        name: Identifier for the device.
        anchors: List of stable mental anchors (loci).
        associations: Map of anchors to information items.
        encoding_strength: Estimated retention strength (0-1).
    """

    name: str
    anchors: list[str] = field(default_factory=list)
    associations: list[str] = field(default_factory=list)
    encoding_strength: float = 0.5


def build_memory_palace(items: list[str], locations: list[str]) -> MnemonicDevice:
    """Construct a 'Memory Palace' (Method of Loci) device.

    Associates a list of items to be remembered with a list of
    familiar spatial locations.

    Args:
        items: List of information items to store.
        locations: List of spatial anchors (e.g. rooms in a house).

    Returns:
        MnemonicDevice object linking items to locations.
    """
    associations = []
    # Pair items with locations
    for i, item in enumerate(items):
        if i < len(locations):
            loc = locations[i]
            # Create vivid, absurd image association (simulated text)
            associations.append(f"{loc} -> {item} (Vivid Image)")
        else:
            associations.append(f"OVERFLOW -> {item}")

    # Calculate strength based on ratio of items to locations
    ratio = len(items) / len(locations) if locations else float("inf")
    strength = 1.0 if ratio <= 1.0 else 1.0 / ratio

    return MnemonicDevice(
        name="Generated Palace",
        anchors=locations,
        associations=associations,
        encoding_strength=strength,
    )
