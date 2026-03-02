"""
Unit tests for encryption.signing — Zero-Mock compliant.

Covers: SignatureAlgorithm (enum values), SignatureResult (defaults,
to_dict), Signer (sign str/bytes, sha512 branch, verify correct/wrong,
sign_json / verify_json round-trip, tamper detection),
sign_file / verify_file (filesystem, both algorithms).
"""

import tempfile
from pathlib import Path

import pytest

from codomyrmex.encryption.signing import (
    SignatureAlgorithm,
    SignatureResult,
    Signer,
    sign_file,
    verify_file,
)

# ── SignatureAlgorithm ─────────────────────────────────────────────────


@pytest.mark.unit
class TestSignatureAlgorithm:
    def test_hmac_sha256_value(self):
        assert SignatureAlgorithm.HMAC_SHA256.value == "hmac-sha256"

    def test_hmac_sha512_value(self):
        assert SignatureAlgorithm.HMAC_SHA512.value == "hmac-sha512"

    def test_two_members(self):
        assert len(SignatureAlgorithm) == 2


# ── SignatureResult ────────────────────────────────────────────────────


@pytest.mark.unit
class TestSignatureResult:
    def test_signature_stored(self):
        r = SignatureResult(signature="abc123", algorithm=SignatureAlgorithm.HMAC_SHA256)
        assert r.signature == "abc123"
        assert r.algorithm == SignatureAlgorithm.HMAC_SHA256

    def test_timestamp_auto_set(self):
        r = SignatureResult(signature="x", algorithm=SignatureAlgorithm.HMAC_SHA256)
        assert r.timestamp > 0

    def test_key_id_default_empty(self):
        r = SignatureResult(signature="x", algorithm=SignatureAlgorithm.HMAC_SHA256)
        assert r.key_id == ""

    def test_to_dict_keys(self):
        r = SignatureResult(
            signature="sig", algorithm=SignatureAlgorithm.HMAC_SHA256, key_id="k1"
        )
        d = r.to_dict()
        assert d["signature"] == "sig"
        assert d["algorithm"] == "hmac-sha256"
        assert "timestamp" in d
        assert d["key_id"] == "k1"

    def test_to_dict_algorithm_is_string(self):
        r = SignatureResult(signature="s", algorithm=SignatureAlgorithm.HMAC_SHA512)
        assert r.to_dict()["algorithm"] == "hmac-sha512"


# ── Signer ─────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestSigner:
    _KEY = "super-secret-key"

    def test_sign_returns_signature_result(self):
        signer = Signer(self._KEY)
        result = signer.sign("hello")
        assert isinstance(result, SignatureResult)

    def test_sign_signature_is_hex(self):
        signer = Signer(self._KEY)
        result = signer.sign("hello")
        assert all(c in "0123456789abcdef" for c in result.signature)

    def test_sign_sha256_length(self):
        signer = Signer(self._KEY, SignatureAlgorithm.HMAC_SHA256)
        result = signer.sign("data")
        assert len(result.signature) == 64

    def test_sign_sha512_length(self):
        signer = Signer(self._KEY, SignatureAlgorithm.HMAC_SHA512)
        result = signer.sign("data")
        assert len(result.signature) == 128

    def test_sign_algorithm_stored(self):
        signer = Signer(self._KEY, SignatureAlgorithm.HMAC_SHA512)
        result = signer.sign("data")
        assert result.algorithm == SignatureAlgorithm.HMAC_SHA512

    def test_sign_key_id_passed(self):
        signer = Signer(self._KEY)
        result = signer.sign("data", key_id="my-key")
        assert result.key_id == "my-key"

    def test_sign_bytes_input(self):
        signer = Signer(self._KEY)
        result = signer.sign(b"raw bytes")
        assert isinstance(result.signature, str)

    def test_sign_str_and_bytes_same_result(self):
        signer = Signer(self._KEY)
        r_str = signer.sign("hello")
        r_bytes = signer.sign(b"hello")
        assert r_str.signature == r_bytes.signature

    def test_sign_key_as_bytes(self):
        signer = Signer(b"bytes-key")
        result = signer.sign("data")
        assert len(result.signature) == 64

    def test_verify_correct_signature(self):
        signer = Signer(self._KEY)
        result = signer.sign("verify-me")
        assert signer.verify("verify-me", result.signature) is True

    def test_verify_wrong_signature(self):
        signer = Signer(self._KEY)
        assert signer.verify("verify-me", "wrongsignature") is False

    def test_verify_tampered_data(self):
        signer = Signer(self._KEY)
        result = signer.sign("original")
        assert signer.verify("tampered", result.signature) is False

    def test_verify_different_key(self):
        signer1 = Signer("key1")
        signer2 = Signer("key2")
        result = signer1.sign("data")
        assert signer2.verify("data", result.signature) is False

    def test_verify_bytes_input(self):
        signer = Signer(self._KEY)
        result = signer.sign(b"bytes data")
        assert signer.verify(b"bytes data", result.signature) is True

    def test_verify_sha512(self):
        signer = Signer(self._KEY, SignatureAlgorithm.HMAC_SHA512)
        result = signer.sign("hello")
        assert signer.verify("hello", result.signature) is True

    def test_sign_json_embeds_signature(self):
        signer = Signer(self._KEY)
        obj = {"name": "Alice", "score": 100}
        signed = signer.sign_json(obj)
        assert "_signature" in signed
        assert signed["name"] == "Alice"
        assert signed["score"] == 100

    def test_verify_json_valid(self):
        signer = Signer(self._KEY)
        obj = {"key": "value"}
        signed = signer.sign_json(obj)
        assert signer.verify_json(signed) is True

    def test_verify_json_tampered_field(self):
        signer = Signer(self._KEY)
        obj = {"key": "value"}
        signed = signer.sign_json(obj)
        signed["key"] = "tampered"
        assert signer.verify_json(signed) is False

    def test_verify_json_missing_signature(self):
        signer = Signer(self._KEY)
        assert signer.verify_json({"no": "signature"}) is False

    def test_verify_json_empty_signature_field(self):
        signer = Signer(self._KEY)
        assert signer.verify_json({"_signature": {}}) is False

    def test_sign_json_key_id(self):
        signer = Signer(self._KEY)
        signed = signer.sign_json({"a": 1}, key_id="kid-1")
        assert signed["_signature"]["key_id"] == "kid-1"

    def test_sign_json_sort_keys_deterministic(self):
        """Key order in input dict should not affect signature."""
        signer = Signer(self._KEY)
        obj1 = {"b": 2, "a": 1}
        obj2 = {"a": 1, "b": 2}
        s1 = signer.sign_json(obj1)
        s2 = signer.sign_json(obj2)
        assert s1["_signature"]["signature"] == s2["_signature"]["signature"]


# ── sign_file / verify_file ───────────────────────────────────────────


@pytest.mark.unit
class TestSignAndVerifyFile:
    _KEY = "file-signing-key"

    def _write_tmp(self, content: bytes) -> Path:
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
        f.write(content)
        f.close()
        return Path(f.name)

    def test_sign_file_returns_hex(self):
        path = self._write_tmp(b"file content")
        try:
            sig = sign_file(path, self._KEY)
            assert all(c in "0123456789abcdef" for c in sig)
        finally:
            path.unlink()

    def test_verify_file_correct(self):
        path = self._write_tmp(b"verifiable")
        try:
            sig = sign_file(path, self._KEY)
            assert verify_file(path, sig, self._KEY) is True
        finally:
            path.unlink()

    def test_verify_file_wrong_signature(self):
        path = self._write_tmp(b"content")
        try:
            assert verify_file(path, "badsig", self._KEY) is False
        finally:
            path.unlink()

    def test_verify_file_wrong_key(self):
        path = self._write_tmp(b"content")
        try:
            sig = sign_file(path, "key1")
            assert verify_file(path, sig, "key2") is False
        finally:
            path.unlink()

    def test_sign_file_sha512(self):
        path = self._write_tmp(b"data")
        try:
            sig = sign_file(path, self._KEY, SignatureAlgorithm.HMAC_SHA512)
            assert len(sig) == 128
        finally:
            path.unlink()

    def test_verify_file_sha512(self):
        path = self._write_tmp(b"data")
        try:
            sig = sign_file(path, self._KEY, SignatureAlgorithm.HMAC_SHA512)
            assert verify_file(path, sig, self._KEY, SignatureAlgorithm.HMAC_SHA512) is True
        finally:
            path.unlink()
