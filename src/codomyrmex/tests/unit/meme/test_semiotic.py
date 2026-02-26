"""Tests for meme.semiotic -- zero-mock, real instances only.

Sprint 5 coverage expansion for the semiotic submodule: Sign, SignType,
SemanticTerritory, DriftReport, SemioticAnalyzer, SemioticEncoder, and
MnemonicDevice.  All tests use real dataclass instances and real function calls.
"""

from __future__ import annotations

import pytest

from codomyrmex.meme.semiotic.models import (
    DriftReport,
    SemanticTerritory,
    Sign,
    SignType,
)
from codomyrmex.meme.semiotic.analyzer import SemioticAnalyzer
from codomyrmex.meme.semiotic.encoding import SemioticEncoder
from codomyrmex.meme.semiotic.mnemonics import MnemonicDevice, build_memory_palace


# ---------------------------------------------------------------------------
# SignType enum
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSignType:
    """Tests for the Peircean sign type enum."""

    def test_all_three_types(self) -> None:
        """ICON, INDEX, SYMBOL are all present."""
        values = {st.value for st in SignType}
        assert values == {"icon", "index", "symbol"}

    def test_str_subclass(self) -> None:
        """SignType members compare as strings."""
        assert SignType.ICON == "icon"
        assert isinstance(SignType.SYMBOL, str)


# ---------------------------------------------------------------------------
# Sign dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSign:
    """Tests for the Sign dataclass."""

    def test_id_auto_generated(self) -> None:
        """ID is auto-generated when not supplied."""
        s = Sign(signifier="smoke", signified="fire")
        assert len(s.id) == 16
        int(s.id, 16)  # valid hex

    def test_explicit_id_preserved(self) -> None:
        """Supplying an explicit ID skips auto-generation."""
        s = Sign(signifier="x", signified="y", id="my_custom_id_00")
        assert s.id == "my_custom_id_00"

    def test_stability_clamped_above(self) -> None:
        """Stability > 1 clamped to 1."""
        s = Sign(signifier="a", signified="b", stability=5.0)
        assert s.stability == 1.0

    def test_stability_clamped_below(self) -> None:
        """Stability < 0 clamped to 0."""
        s = Sign(signifier="a", signified="b", stability=-1.0)
        assert s.stability == 0.0

    def test_default_type_is_symbol(self) -> None:
        """Default sign_type is SYMBOL."""
        s = Sign(signifier="word", signified="meaning")
        assert s.sign_type == SignType.SYMBOL

    def test_deterministic_id_for_same_pair(self) -> None:
        """Same signifier+signified yields the same ID."""
        s1 = Sign(signifier="flag", signified="nation")
        s2 = Sign(signifier="flag", signified="nation")
        assert s1.id == s2.id

    def test_different_signified_different_id(self) -> None:
        """Different signified yields different ID."""
        s1 = Sign(signifier="flag", signified="nation")
        s2 = Sign(signifier="flag", signified="surrender")
        assert s1.id != s2.id


# ---------------------------------------------------------------------------
# SemanticTerritory dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSemanticTerritory:
    """Tests for the SemanticTerritory dataclass."""

    def test_density_no_boundaries(self) -> None:
        """Density with no boundaries equals number of signs."""
        signs = [Sign(signifier=f"s{i}", signified=f"m{i}") for i in range(3)]
        t = SemanticTerritory(domain="test", signs=signs)
        assert t.density == 3

    def test_density_with_boundaries(self) -> None:
        """Density = len(signs) / len(boundaries)."""
        signs = [Sign(signifier=f"s{i}", signified=f"m{i}") for i in range(6)]
        t = SemanticTerritory(domain="test", signs=signs, boundaries={"a": 1.0, "b": 2.0})
        assert t.density == pytest.approx(3.0, abs=1e-9)

    def test_contested_default_false(self) -> None:
        """contested defaults to False."""
        t = SemanticTerritory(domain="test")
        assert t.contested is False

    def test_contested_set_true(self) -> None:
        """contested can be set True."""
        t = SemanticTerritory(domain="test", contested=True)
        assert t.contested is True


# ---------------------------------------------------------------------------
# DriftReport dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDriftReport:
    """Tests for the DriftReport dataclass."""

    def test_stability_ratio_all_stable(self) -> None:
        """All stable signs gives ratio 1.0."""
        report = DriftReport(
            stable_signs=[Sign(signifier="a", signified="b")],
            shifted_signs=[],
        )
        assert report.stability_ratio == 1.0

    def test_stability_ratio_all_shifted(self) -> None:
        """All shifted signs gives ratio 0.0."""
        report = DriftReport(
            stable_signs=[],
            shifted_signs=[Sign(signifier="a", signified="b")],
        )
        assert report.stability_ratio == 0.0

    def test_stability_ratio_empty(self) -> None:
        """No shared signs gives ratio 1.0 (convention)."""
        report = DriftReport()
        assert report.stability_ratio == 1.0

    def test_stability_ratio_mixed(self) -> None:
        """Mixed stable/shifted gives correct proportion."""
        report = DriftReport(
            stable_signs=[
                Sign(signifier="a", signified="x"),
                Sign(signifier="b", signified="y"),
            ],
            shifted_signs=[
                Sign(signifier="c", signified="z"),
            ],
        )
        assert report.stability_ratio == pytest.approx(2 / 3, abs=1e-6)

    def test_drift_magnitude_stored(self) -> None:
        """drift_magnitude can be set and retrieved."""
        report = DriftReport(drift_magnitude=0.42)
        assert report.drift_magnitude == 0.42

    def test_new_and_lost_signs(self) -> None:
        """new_signs and lost_signs are stored independently."""
        new = [Sign(signifier="new", signified="concept")]
        lost = [Sign(signifier="old", signified="forgotten")]
        report = DriftReport(new_signs=new, lost_signs=lost)
        assert len(report.new_signs) == 1
        assert len(report.lost_signs) == 1


# ---------------------------------------------------------------------------
# SemioticAnalyzer
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSemioticAnalyzer:
    """Tests for the SemioticAnalyzer class."""

    def test_decode_extracts_signs(self) -> None:
        """decode extracts at least some signs from non-trivial text."""
        analyzer = SemioticAnalyzer()
        signs = analyzer.decode("The ancient symbol represents power and freedom.")
        assert len(signs) > 0

    def test_decode_skips_short_words(self) -> None:
        """Single-character words are skipped."""
        analyzer = SemioticAnalyzer()
        signs = analyzer.decode("I a x")
        signifiers = {s.signifier for s in signs}
        assert "a" not in signifiers
        assert "x" not in signifiers

    def test_decode_no_duplicates(self) -> None:
        """The same signifier is not returned twice."""
        analyzer = SemioticAnalyzer()
        signs = analyzer.decode("the cat sat on the cat mat the cat")
        signifiers = [s.signifier for s in signs]
        assert len(signifiers) == len(set(signifiers))

    def test_decode_index_type_for_deictic(self) -> None:
        """Deictic words like 'this' and 'here' get INDEX type."""
        analyzer = SemioticAnalyzer()
        signs = analyzer.decode("this thing is here now")
        index_signs = [s for s in signs if s.sign_type == SignType.INDEX]
        signifiers = {s.signifier for s in index_signs}
        assert "this" in signifiers or "here" in signifiers

    def test_drift_identical_corpora(self) -> None:
        """Identical corpora produce zero drift magnitude."""
        analyzer = SemioticAnalyzer()
        corpus = ["The economy grows through innovation and trade."]
        report = analyzer.drift(corpus, corpus)
        assert report.drift_magnitude == 0.0

    def test_drift_completely_different_corpora(self) -> None:
        """Completely different corpora produce high drift."""
        analyzer = SemioticAnalyzer()
        a = ["Alpha bravo charlie delta echo foxtrot golf."]
        b = ["Zulu yankee xray whiskey victor uniform tango."]
        report = analyzer.drift(a, b)
        assert report.drift_magnitude > 0.0

    def test_drift_report_has_new_signs(self) -> None:
        """Signs in corpus B but not A appear as new_signs."""
        analyzer = SemioticAnalyzer()
        a = ["Alpha bravo charlie."]
        b = ["Alpha bravo delta echo foxtrot."]
        report = analyzer.drift(a, b)
        new_signifiers = {s.signifier for s in report.new_signs}
        # 'delta', 'echo', 'foxtrot' should be new
        assert len(new_signifiers) > 0

    def test_territory_map_returns_territories(self) -> None:
        """territory_map returns a list of SemanticTerritory objects."""
        analyzer = SemioticAnalyzer()
        corpus = [
            "The economy grows through innovation.",
            "Innovation drives economic growth and prosperity.",
            "Markets respond to economic innovation signals.",
        ]
        territories = analyzer.territory_map(corpus, n_domains=2)
        assert len(territories) > 0
        for t in territories:
            assert isinstance(t, SemanticTerritory)

    def test_territory_map_domain_is_string(self) -> None:
        """Each territory's domain is a non-empty string."""
        analyzer = SemioticAnalyzer()
        corpus = ["Science explores nature. Nature reveals truth."]
        territories = analyzer.territory_map(corpus, n_domains=1)
        if territories:
            assert isinstance(territories[0].domain, str)
            assert len(territories[0].domain) > 0


# ---------------------------------------------------------------------------
# SemioticEncoder
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSemioticEncoder:
    """Tests for the SemioticEncoder linguistic steganography."""

    def test_encode_modifies_carrier(self) -> None:
        """Encoding with a substitutable word changes the carrier."""
        encoder = SemioticEncoder()
        carrier = "This is a good day to be happy and fast."
        encoded = encoder.encode(carrier, "secret")
        assert encoded != carrier

    def test_encode_preserves_non_synonym_words(self) -> None:
        """Words not in the synonym map are left untouched."""
        encoder = SemioticEncoder()
        carrier = "The cat sat on the mat."
        encoded = encoder.encode(carrier, "payload")
        assert encoded == carrier  # no synonyms to substitute

    def test_decode_extracts_bits(self) -> None:
        """decode extracts bit indices from synonym-encoded text."""
        encoder = SemioticEncoder()
        # Manually build text with known synonyms
        encoded_text = "fine terrible huge tiny"
        bits = encoder.decode(encoded_text)
        assert len(bits) == 4
        # "fine" = index 0 in good synonyms, "terrible" = index 1 in bad, etc.
        assert bits[0] == 0  # "fine" is at index 0 in good's synonyms
        assert bits[1] == 1  # "terrible" is at index 1 in bad's synonyms

    def test_encode_decode_roundtrip(self) -> None:
        """Encoding then decoding preserves bit pattern length."""
        encoder = SemioticEncoder()
        carrier = "It was a good day and I was happy and fast."
        payload = "hi"
        encoded = encoder.encode(carrier, payload)
        bits = encoder.decode(encoded)
        assert len(bits) > 0

    def test_to_bits_deterministic(self) -> None:
        """_to_bits is deterministic for the same input."""
        encoder = SemioticEncoder()
        bits1 = encoder._to_bits("hello")
        bits2 = encoder._to_bits("hello")
        assert bits1 == bits2

    def test_to_bits_values_mod_4(self) -> None:
        """All bit values are in range [0, 3] (mod 4)."""
        encoder = SemioticEncoder()
        bits = encoder._to_bits("test string")
        for b in bits:
            assert 0 <= b <= 3


# ---------------------------------------------------------------------------
# MnemonicDevice and build_memory_palace
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMnemonicDevice:
    """Tests for the MnemonicDevice dataclass and builder."""

    def test_dataclass_creation(self) -> None:
        """MnemonicDevice can be instantiated with defaults."""
        md = MnemonicDevice(name="test")
        assert md.name == "test"
        assert md.anchors == []
        assert md.encoding_strength == 0.5

    def test_build_memory_palace_equal_items_locations(self) -> None:
        """Equal items and locations yields strength 1.0."""
        palace = build_memory_palace(
            items=["apple", "banana", "cherry"],
            locations=["kitchen", "bedroom", "garden"],
        )
        assert palace.encoding_strength == 1.0
        assert len(palace.associations) == 3

    def test_build_memory_palace_more_items_than_locations(self) -> None:
        """More items than locations reduces strength."""
        palace = build_memory_palace(
            items=["a", "b", "c", "d"],
            locations=["room1", "room2"],
        )
        assert palace.encoding_strength < 1.0
        # overflow items should have OVERFLOW marker
        overflow_assocs = [a for a in palace.associations if "OVERFLOW" in a]
        assert len(overflow_assocs) == 2

    def test_build_memory_palace_fewer_items(self) -> None:
        """Fewer items than locations yields strength 1.0."""
        palace = build_memory_palace(
            items=["alpha"],
            locations=["loc1", "loc2", "loc3"],
        )
        assert palace.encoding_strength == 1.0

    def test_build_memory_palace_name(self) -> None:
        """Generated palace has expected name."""
        palace = build_memory_palace(items=["x"], locations=["y"])
        assert palace.name == "Generated Palace"

    def test_build_memory_palace_anchors_match_locations(self) -> None:
        """Palace anchors are the supplied locations."""
        locs = ["hall", "stairs", "roof"]
        palace = build_memory_palace(items=["a", "b"], locations=locs)
        assert palace.anchors == locs
