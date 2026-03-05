"""Comprehensive unit tests for the encryption module — Zero-Mock compliant.

Covers: Encryptor (AES-CBC, RSA), AESGCMEncryptor, KeyManager, HMAC utils,
HKDF key derivation, Signer (HMAC-based signing), SecureDataContainer,
convenience functions, file encryption, hashing, error handling, and
edge cases. All tests use real cryptographic operations with no mocks,
stubs, or monkeypatching.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import warnings
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Skip guard: the entire module depends on ``cryptography``
# ---------------------------------------------------------------------------
cryptography = pytest.importorskip(
    "cryptography", reason="cryptography library required"
)

from codomyrmex.encryption import (  # noqa: E402
    AESGCMEncryptor,
    EncryptionError,
    Encryptor,
    KeyManager,
    SecureDataContainer,
    Signer,
    compute_hmac,
    decrypt,
    decrypt_data,
    decrypt_file,
    derive_key_hkdf,
    encrypt,
    encrypt_data,
    encrypt_file,
    generate_aes_key,
    generate_key,
    get_encryptor,
    hash_data,
    verify_hmac,
)
from codomyrmex.encryption.signing import (  # noqa: E402
    SignatureAlgorithm,
    SignatureResult,
    sign_file,
    verify_file,
)

# ==============================================================================
# Helpers
# ==============================================================================


def _suppress_cbc_warning():
    """Context manager to suppress the AES-CBC deprecation warning."""
    ctx = warnings.catch_warnings()
    ctx.__enter__()
    warnings.simplefilter("ignore", DeprecationWarning)
    return ctx


# ==============================================================================
# 1. Encryptor — AES-CBC
# ==============================================================================


@pytest.mark.unit
class TestEncryptorAESCBC:
    """AES-CBC encrypt/decrypt via the Encryptor class."""

    @pytest.fixture
    def enc(self):
        return Encryptor(algorithm="AES")

    @pytest.fixture
    def key(self):
        return os.urandom(32)

    def test_roundtrip(self, enc, key):
        plaintext = b"Hello, AES-CBC!"
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(plaintext, key)
            pt = enc.decrypt(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == plaintext

    def test_iv_randomness(self, enc, key):
        """Same plaintext produces different ciphertext due to random IV."""
        data = b"repeat me"
        ctx = _suppress_cbc_warning()
        try:
            c1 = enc.encrypt(data, key)
            c2 = enc.encrypt(data, key)
        finally:
            ctx.__exit__(None, None, None)
        assert c1 != c2

    def test_empty_plaintext(self, enc, key):
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(b"", key)
            pt = enc.decrypt(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == b""

    def test_large_plaintext(self, enc, key):
        data = os.urandom(1024 * 100)  # 100 KB
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(data, key)
            pt = enc.decrypt(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == data

    def test_non_32byte_key_normalized(self, enc):
        """Keys != 32 bytes are SHA-256 hashed to 32 bytes."""
        short_key = b"short"
        data = b"normalize key"
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(data, short_key)
            pt = enc.decrypt(ct, short_key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == data

    def test_wrong_key_raises(self, enc, key):
        data = b"secret"
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(data, key)
            with pytest.raises(EncryptionError):
                enc.decrypt(ct, os.urandom(32))
        finally:
            ctx.__exit__(None, None, None)

    def test_truncated_ciphertext_raises(self, enc, key):
        """Ciphertext shorter than 16 bytes (the IV) should raise."""
        with pytest.raises(EncryptionError):
            enc.decrypt(b"short", key)

    def test_cbc_deprecation_warning(self):
        enc = Encryptor("AES")
        key = os.urandom(32)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            enc.encrypt(b"data", key)
            deprecations = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecations) >= 1
            assert "AES-CBC" in str(deprecations[0].message)

    def test_generate_key_length(self, enc):
        key = enc.generate_key()
        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_generate_key_unique(self, enc):
        keys = {enc.generate_key() for _ in range(20)}
        assert len(keys) == 20

    def test_null_bytes_in_data(self, enc, key):
        data = b"\x00" * 64
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(data, key)
            pt = enc.decrypt(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == data

    def test_binary_with_all_byte_values(self, enc, key):
        data = bytes(range(256))
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt(data, key)
            pt = enc.decrypt(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == data


# ==============================================================================
# 2. Encryptor — RSA
# ==============================================================================


@pytest.mark.unit
class TestEncryptorRSA:
    """RSA encrypt/decrypt and key pair generation."""

    @pytest.fixture
    def enc(self):
        return Encryptor(algorithm="RSA")

    @pytest.fixture
    def keypair(self, enc):
        return enc.generate_key_pair()

    def test_roundtrip(self, enc, keypair):
        priv, pub = keypair
        data = b"Hello, RSA!"
        ct = enc.encrypt(data, pub)
        pt = enc.decrypt(ct, priv)
        assert pt == data

    def test_encrypt_with_private_key_raises(self, enc, keypair):
        priv, _ = keypair
        with pytest.raises(EncryptionError):
            enc.encrypt(b"data", priv)

    def test_decrypt_with_public_key_raises(self, enc, keypair):
        _, pub = keypair
        with pytest.raises(EncryptionError):
            enc.decrypt(b"fake", pub)

    def test_key_pair_pem_format(self, enc, keypair):
        priv, pub = keypair
        assert b"BEGIN PRIVATE KEY" in priv
        assert b"BEGIN PUBLIC KEY" in pub

    def test_different_key_sizes(self, enc):
        for size in (2048, 4096):
            priv, pub = enc.generate_key_pair(size)
            ct = enc.encrypt(b"size test", pub)
            pt = enc.decrypt(ct, priv)
            assert pt == b"size test"

    def test_generate_key_returns_pem(self, enc):
        key = enc.generate_key()
        assert b"BEGIN PRIVATE KEY" in key

    def test_cross_keypair_decryption_fails(self, enc):
        """Ciphertext from one key pair cannot be decrypted by another."""
        _, pub1 = enc.generate_key_pair()
        priv2, _ = enc.generate_key_pair()
        ct = enc.encrypt(b"cross", pub1)
        with pytest.raises(EncryptionError):
            enc.decrypt(ct, priv2)


# ==============================================================================
# 3. RSA Digital Signatures (via Encryptor.sign / .verify)
# ==============================================================================


@pytest.mark.unit
class TestRSASignatures:
    """RSA-PSS digital signatures."""

    @pytest.fixture
    def enc(self):
        return Encryptor(algorithm="RSA")

    @pytest.fixture
    def keypair(self, enc):
        return enc.generate_key_pair()

    def test_sign_and_verify(self, enc, keypair):
        priv, pub = keypair
        data = b"signed document"
        sig = enc.sign(data, priv)
        assert enc.verify(data, sig, pub) is True

    def test_verify_tampered_data_fails(self, enc, keypair):
        priv, pub = keypair
        sig = enc.sign(b"original", priv)
        assert enc.verify(b"modified", sig, pub) is False

    def test_verify_wrong_signature_fails(self, enc, keypair):
        _, pub = keypair
        assert enc.verify(b"data", b"bad_sig", pub) is False

    def test_verify_wrong_key_fails(self, enc, keypair):
        priv, _ = keypair
        _, other_pub = enc.generate_key_pair()
        sig = enc.sign(b"data", priv)
        assert enc.verify(b"data", sig, other_pub) is False

    def test_sign_with_invalid_key_raises(self, enc):
        with pytest.raises(EncryptionError):
            enc.sign(b"data", b"not-a-key")

    def test_sign_empty_data(self, enc, keypair):
        priv, pub = keypair
        sig = enc.sign(b"", priv)
        assert enc.verify(b"", sig, pub) is True


# ==============================================================================
# 4. Key Derivation — PBKDF2
# ==============================================================================


@pytest.mark.unit
class TestPBKDF2:
    """Password-based key derivation via Encryptor.derive_key()."""

    @pytest.fixture
    def enc(self):
        return Encryptor()

    def test_derived_key_length(self, enc):
        key = enc.derive_key("password", os.urandom(16))
        assert len(key) == 32

    def test_deterministic_same_inputs(self, enc):
        salt = b"fixed_salt______"
        k1 = enc.derive_key("pw", salt)
        k2 = enc.derive_key("pw", salt)
        assert k1 == k2

    def test_different_salt_different_key(self, enc):
        k1 = enc.derive_key("pw", b"salt_one________")
        k2 = enc.derive_key("pw", b"salt_two________")
        assert k1 != k2

    def test_different_password_different_key(self, enc):
        salt = b"common_salt_____"
        k1 = enc.derive_key("pass1", salt)
        k2 = enc.derive_key("pass2", salt)
        assert k1 != k2

    def test_custom_iterations(self, enc):
        salt = b"iter_salt________"
        k_low = enc.derive_key("pw", salt, iterations=1000)
        k_high = enc.derive_key("pw", salt, iterations=2000)
        assert k_low != k_high

    def test_derived_key_usable_for_encryption(self, enc):
        """Derived key should work with AES-GCM."""
        salt = os.urandom(16)
        key = enc.derive_key("my-password", salt)
        gcm = AESGCMEncryptor(key)
        ct = gcm.encrypt(b"pbkdf2 test")
        pt = gcm.decrypt(ct)
        assert pt == b"pbkdf2 test"


# ==============================================================================
# 5. Salt Generation
# ==============================================================================


@pytest.mark.unit
class TestSaltGeneration:
    def test_default_length(self):
        salt = Encryptor.generate_salt()
        assert len(salt) == 16

    def test_custom_length(self):
        for length in (8, 32, 64):
            salt = Encryptor.generate_salt(length)
            assert len(salt) == length

    def test_uniqueness(self):
        salts = {Encryptor.generate_salt() for _ in range(50)}
        assert len(salts) == 50


# ==============================================================================
# 6. String Encryption
# ==============================================================================


@pytest.mark.unit
class TestStringEncryption:
    @pytest.fixture
    def enc(self):
        return Encryptor()

    @pytest.fixture
    def key(self):
        return os.urandom(32)

    def test_roundtrip(self, enc, key):
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt_string("hello world", key)
            pt = enc.decrypt_string(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == "hello world"

    def test_unicode(self, enc, key):
        text = "cafe\u0301 \u4e16\u754c"
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt_string(text, key)
            pt = enc.decrypt_string(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == text

    def test_empty_string(self, enc, key):
        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt_string("", key)
            pt = enc.decrypt_string(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == ""

    def test_ciphertext_is_base64(self, enc, key):
        import base64

        ctx = _suppress_cbc_warning()
        try:
            ct = enc.encrypt_string("test", key)
        finally:
            ctx.__exit__(None, None, None)
        # Should not raise
        decoded = base64.b64decode(ct)
        assert len(decoded) > 0


# ==============================================================================
# 7. File Encryption
# ==============================================================================


@pytest.mark.unit
class TestFileEncryption:
    @pytest.fixture
    def enc(self):
        return Encryptor()

    @pytest.fixture
    def key(self):
        return os.urandom(32)

    def test_roundtrip(self, enc, key):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "plain.txt"
            enc_f = td / "cipher.bin"
            dec_f = td / "decrypted.txt"
            src.write_bytes(b"file encryption test")

            ctx = _suppress_cbc_warning()
            try:
                assert enc.encrypt_file(src, enc_f, key) is True
                assert enc_f.exists()
                assert enc.decrypt_file(enc_f, dec_f, key) is True
            finally:
                ctx.__exit__(None, None, None)
            assert dec_f.read_bytes() == b"file encryption test"

    def test_encrypted_content_differs(self, enc, key):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "src.txt"
            enc_f = td / "enc.bin"
            src.write_bytes(b"original content")
            ctx = _suppress_cbc_warning()
            try:
                enc.encrypt_file(src, enc_f, key)
            finally:
                ctx.__exit__(None, None, None)
            assert enc_f.read_bytes() != b"original content"

    def test_nonexistent_input_raises(self, enc, key):
        with tempfile.TemporaryDirectory() as td:
            with pytest.raises(EncryptionError):
                enc.encrypt_file(
                    Path(td) / "missing.txt",
                    Path(td) / "out.bin",
                    key,
                )

    def test_corrupted_file_raises(self, enc, key):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            bad = td / "corrupted.bin"
            bad.write_bytes(b"not encrypted")
            with pytest.raises(EncryptionError):
                enc.decrypt_file(bad, td / "out.txt", key)

    def test_binary_file(self, enc, key):
        """Test encryption of a binary file with all byte values."""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "binary.bin"
            data = bytes(range(256)) * 10
            src.write_bytes(data)
            enc_f = td / "enc.bin"
            dec_f = td / "dec.bin"
            ctx = _suppress_cbc_warning()
            try:
                enc.encrypt_file(src, enc_f, key)
                enc.decrypt_file(enc_f, dec_f, key)
            finally:
                ctx.__exit__(None, None, None)
            assert dec_f.read_bytes() == data

    def test_path_objects_accepted(self, enc, key):
        """Both str and Path should work."""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "pathobj.txt"
            src.write_bytes(b"path test")
            enc_f = td / "enc.bin"
            dec_f = td / "dec.txt"
            ctx = _suppress_cbc_warning()
            try:
                # Test with Path objects
                assert enc.encrypt_file(src, enc_f, key) is True
                # Test with str paths
                assert enc.decrypt_file(str(enc_f), str(dec_f), key) is True
            finally:
                ctx.__exit__(None, None, None)
            assert dec_f.read_bytes() == b"path test"


# ==============================================================================
# 8. Hashing
# ==============================================================================


@pytest.mark.unit
class TestHashing:
    def test_sha256(self):
        h = Encryptor.hash_data(b"test", "sha256")
        assert len(h) == 64
        # Known SHA-256 digest of "test"
        assert h == hashlib.sha256(b"test").hexdigest()

    def test_sha384(self):
        h = Encryptor.hash_data(b"test", "sha384")
        assert len(h) == 96

    def test_sha512(self):
        h = Encryptor.hash_data(b"test", "sha512")
        assert len(h) == 128

    def test_md5(self):
        h = Encryptor.hash_data(b"test", "md5")
        assert len(h) == 32

    def test_deterministic(self):
        assert Encryptor.hash_data(b"abc", "sha256") == Encryptor.hash_data(
            b"abc", "sha256"
        )

    def test_different_data_different_hash(self):
        assert Encryptor.hash_data(b"a", "sha256") != Encryptor.hash_data(
            b"b", "sha256"
        )

    def test_empty_data(self):
        h = Encryptor.hash_data(b"", "sha256")
        assert h == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_invalid_algorithm_raises(self):
        with pytest.raises(ValueError, match="Unknown hash algorithm"):
            Encryptor.hash_data(b"data", "invalid_algo")

    def test_case_insensitive(self):
        assert Encryptor.hash_data(b"x", "SHA256") == Encryptor.hash_data(
            b"x", "sha256"
        )


# ==============================================================================
# 9. AES-GCM Authenticated Encryption
# ==============================================================================


@pytest.mark.unit
class TestAESGCMEncryptor:
    def test_roundtrip(self):
        key = os.urandom(32)
        enc = AESGCMEncryptor(key)
        ct = enc.encrypt(b"hello gcm")
        pt = enc.decrypt(ct)
        assert pt == b"hello gcm"

    def test_associated_data(self):
        key = os.urandom(32)
        enc = AESGCMEncryptor(key)
        aad = b"header"
        ct = enc.encrypt(b"payload", aad)
        pt = enc.decrypt(ct, aad)
        assert pt == b"payload"

    def test_wrong_aad_raises(self):
        key = os.urandom(32)
        enc = AESGCMEncryptor(key)
        ct = enc.encrypt(b"data", b"correct-aad")
        with pytest.raises(EncryptionError):
            enc.decrypt(ct, b"wrong-aad")

    def test_tampered_ciphertext_raises(self):
        enc = AESGCMEncryptor(os.urandom(32))
        ct = enc.encrypt(b"authentic")
        tampered = bytearray(ct)
        tampered[-1] ^= 0xFF
        with pytest.raises(EncryptionError):
            enc.decrypt(bytes(tampered))

    def test_auto_key_generation(self):
        enc = AESGCMEncryptor()
        assert len(enc.key) == 32

    def test_valid_key_sizes(self):
        for size in (16, 24, 32):
            enc = AESGCMEncryptor(os.urandom(size))
            ct = enc.encrypt(b"test")
            assert enc.decrypt(ct) == b"test"

    def test_invalid_key_size_raises(self):
        with pytest.raises(ValueError, match="16, 24, or 32 bytes"):
            AESGCMEncryptor(b"bad_key")

    def test_empty_data(self):
        enc = AESGCMEncryptor()
        ct = enc.encrypt(b"")
        pt = enc.decrypt(ct)
        assert pt == b""

    def test_too_short_data_raises(self):
        enc = AESGCMEncryptor()
        with pytest.raises(EncryptionError, match="too short"):
            enc.decrypt(b"tiny")

    def test_nonce_uniqueness(self):
        """Each encryption should use a different nonce."""
        enc = AESGCMEncryptor(os.urandom(32))
        c1 = enc.encrypt(b"same")
        c2 = enc.encrypt(b"same")
        # Nonce is first 12 bytes
        assert c1[:12] != c2[:12]

    def test_wrong_key_raises(self):
        key1 = os.urandom(32)
        key2 = os.urandom(32)
        ct = AESGCMEncryptor(key1).encrypt(b"secret")
        with pytest.raises(EncryptionError):
            AESGCMEncryptor(key2).decrypt(ct)

    def test_large_payload(self):
        enc = AESGCMEncryptor(os.urandom(32))
        data = os.urandom(1024 * 50)  # 50 KB
        ct = enc.encrypt(data)
        pt = enc.decrypt(ct)
        assert pt == data


# ==============================================================================
# 10. SecureDataContainer
# ==============================================================================


@pytest.mark.unit
class TestSecureDataContainer:
    @pytest.fixture
    def key(self):
        return os.urandom(32)

    @pytest.fixture
    def container(self, key):
        return SecureDataContainer(key)

    def test_pack_unpack_dict(self, container):
        data = {"user": "admin", "level": 5}
        packed = container.pack(data)
        result = container.unpack(packed)
        assert result["data"] == data
        assert result["metadata"] == {}

    def test_pack_unpack_with_metadata(self, container):
        data = {"msg": "hello"}
        meta = {"ts": 12345, "ver": "2.0"}
        packed = container.pack(data, meta)
        result = container.unpack(packed)
        assert result["data"] == data
        assert result["metadata"] == meta

    def test_pack_unpack_list(self, container):
        data = [1, "two", 3.0, None, True]
        packed = container.pack(data)
        result = container.unpack(packed)
        assert result["data"] == data

    def test_pack_unpack_nested(self, container):
        data = {"a": {"b": {"c": [1, 2, 3]}}}
        packed = container.pack(data)
        result = container.unpack(packed)
        assert result["data"] == data

    def test_different_key_cannot_decrypt(self):
        k1 = os.urandom(32)
        k2 = os.urandom(32)
        packed = SecureDataContainer(k1).pack({"secret": True})
        with pytest.raises(EncryptionError):
            SecureDataContainer(k2).unpack(packed)

    def test_non_serializable_raises(self, container):
        with pytest.raises(TypeError):
            container.pack(object())

    def test_tampered_packed_data_raises(self, container):
        packed = container.pack({"val": 1})
        tampered = bytearray(packed)
        tampered[-1] ^= 0xFF
        with pytest.raises(EncryptionError):
            container.unpack(bytes(tampered))

    def test_pack_string(self, container):
        packed = container.pack("just a string")
        result = container.unpack(packed)
        assert result["data"] == "just a string"

    def test_pack_numeric(self, container):
        packed = container.pack(42)
        result = container.unpack(packed)
        assert result["data"] == 42

    def test_pack_null(self, container):
        packed = container.pack(None)
        result = container.unpack(packed)
        assert result["data"] is None


# ==============================================================================
# 11. KeyManager
# ==============================================================================


@pytest.mark.unit
class TestKeyManager:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    @pytest.fixture
    def mgr(self, temp_dir):
        return KeyManager(key_dir=temp_dir)

    def test_store_and_retrieve(self, mgr):
        key = os.urandom(32)
        assert mgr.store_key("k1", key) is True
        assert mgr.get_key("k1") == key

    def test_get_nonexistent_returns_none(self, mgr):
        assert mgr.get_key("no-such-key") is None

    def test_delete_key(self, mgr):
        mgr.store_key("del", os.urandom(16))
        assert mgr.delete_key("del") is True
        assert mgr.get_key("del") is None

    def test_delete_nonexistent_returns_false(self, mgr):
        assert mgr.delete_key("missing") is False

    def test_list_keys_sorted(self, mgr):
        for name in ("charlie", "alpha", "bravo"):
            mgr.store_key(name, os.urandom(16))
        assert mgr.list_keys() == ["alpha", "bravo", "charlie"]

    def test_list_keys_empty(self, mgr):
        assert mgr.list_keys() == []

    def test_key_exists_true(self, mgr):
        mgr.store_key("x", os.urandom(8))
        assert mgr.key_exists("x") is True

    def test_key_exists_false(self, mgr):
        assert mgr.key_exists("nope") is False

    def test_rotate_key(self, mgr):
        old_key = os.urandom(32)
        new_key = os.urandom(32)
        mgr.store_key("rot", old_key)
        returned = mgr.rotate_key("rot", new_key)
        assert returned == old_key
        assert mgr.get_key("rot") == new_key

    def test_rotate_nonexistent(self, mgr):
        new_key = os.urandom(32)
        returned = mgr.rotate_key("fresh", new_key)
        assert returned is None
        assert mgr.get_key("fresh") == new_key

    def test_file_permissions(self, mgr, temp_dir):
        mgr.store_key("perm", os.urandom(16))
        key_file = temp_dir / "perm.key"
        mode = key_file.stat().st_mode & 0o777
        assert mode == 0o600

    def test_overwrite_existing_key(self, mgr):
        k1 = os.urandom(32)
        k2 = os.urandom(32)
        mgr.store_key("ow", k1)
        mgr.store_key("ow", k2)
        assert mgr.get_key("ow") == k2

    def test_multiple_keys(self, mgr):
        keys = {f"key-{i}": os.urandom(32) for i in range(10)}
        for kid, k in keys.items():
            mgr.store_key(kid, k)
        for kid, k in keys.items():
            assert mgr.get_key(kid) == k

    def test_default_key_dir_created(self):
        """KeyManager with no args creates default directory."""
        mgr = KeyManager()
        assert mgr.key_dir.exists()


# ==============================================================================
# 12. HMAC Utilities
# ==============================================================================


@pytest.mark.unit
class TestHMACUtils:
    def test_compute_and_verify_sha256(self):
        mac = compute_hmac(b"msg", b"key")
        assert verify_hmac(b"msg", b"key", mac) is True

    def test_compute_and_verify_sha384(self):
        mac = compute_hmac(b"msg", b"key", algorithm="sha384")
        assert verify_hmac(b"msg", b"key", mac, algorithm="sha384") is True

    def test_compute_and_verify_sha512(self):
        mac = compute_hmac(b"msg", b"key", algorithm="sha512")
        assert verify_hmac(b"msg", b"key", mac, algorithm="sha512") is True

    def test_tampered_data_fails(self):
        mac = compute_hmac(b"original", b"key")
        assert verify_hmac(b"tampered", b"key", mac) is False

    def test_wrong_key_fails(self):
        mac = compute_hmac(b"msg", b"key1")
        assert verify_hmac(b"msg", b"key2", mac) is False

    def test_string_inputs(self):
        mac_b = compute_hmac(b"data", b"secret")
        mac_s = compute_hmac("data", "secret")
        assert mac_b == mac_s

    def test_empty_data(self):
        mac = compute_hmac(b"", b"key")
        assert isinstance(mac, bytes)
        assert len(mac) > 0
        assert verify_hmac(b"", b"key", mac) is True

    def test_invalid_algorithm_raises(self):
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            compute_hmac(b"d", b"k", algorithm="md5")

    def test_hmac_different_algorithms_different_output(self):
        mac256 = compute_hmac(b"data", b"key", "sha256")
        mac512 = compute_hmac(b"data", b"key", "sha512")
        assert mac256 != mac512
        assert len(mac256) == 32  # SHA-256 produces 32-byte digest
        assert len(mac512) == 64  # SHA-512 produces 64-byte digest


# ==============================================================================
# 13. HKDF Key Derivation
# ==============================================================================


@pytest.mark.unit
class TestHKDF:
    def test_basic_length(self):
        key = derive_key_hkdf(b"material")
        assert len(key) == 32

    def test_deterministic(self):
        k1 = derive_key_hkdf(b"m", salt=b"s", info=b"i")
        k2 = derive_key_hkdf(b"m", salt=b"s", info=b"i")
        assert k1 == k2

    def test_different_salt(self):
        k1 = derive_key_hkdf(b"m", salt=b"salt1")
        k2 = derive_key_hkdf(b"m", salt=b"salt2")
        assert k1 != k2

    def test_different_info(self):
        k1 = derive_key_hkdf(b"m", info=b"ctx-a")
        k2 = derive_key_hkdf(b"m", info=b"ctx-b")
        assert k1 != k2

    def test_custom_length(self):
        for length in (16, 48, 64):
            key = derive_key_hkdf(b"m", length=length)
            assert len(key) == length

    def test_string_input(self):
        key = derive_key_hkdf("string-input")
        assert len(key) == 32

    def test_invalid_algorithm_raises(self):
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            derive_key_hkdf(b"m", algorithm="md5")

    def test_sha384_algorithm(self):
        key = derive_key_hkdf(b"m", algorithm="sha384")
        assert len(key) == 32

    def test_sha512_algorithm(self):
        key = derive_key_hkdf(b"m", algorithm="sha512")
        assert len(key) == 32

    def test_no_salt_no_info(self):
        key = derive_key_hkdf(b"ikm", salt=None, info=None)
        assert len(key) == 32


# ==============================================================================
# 14. Signer (HMAC-based signing)
# ==============================================================================


@pytest.mark.unit
class TestSigner:
    _KEY = "signer-test-key"

    def test_sign_returns_result(self):
        signer = Signer(self._KEY)
        result = signer.sign("hello")
        assert isinstance(result, SignatureResult)

    def test_signature_is_hex(self):
        signer = Signer(self._KEY)
        result = signer.sign("test")
        assert all(c in "0123456789abcdef" for c in result.signature)

    def test_sha256_signature_length(self):
        signer = Signer(self._KEY, SignatureAlgorithm.HMAC_SHA256)
        assert len(signer.sign("data").signature) == 64

    def test_sha512_signature_length(self):
        signer = Signer(self._KEY, SignatureAlgorithm.HMAC_SHA512)
        assert len(signer.sign("data").signature) == 128

    def test_verify_correct(self):
        signer = Signer(self._KEY)
        result = signer.sign("msg")
        assert signer.verify("msg", result.signature) is True

    def test_verify_tampered_fails(self):
        signer = Signer(self._KEY)
        result = signer.sign("original")
        assert signer.verify("tampered", result.signature) is False

    def test_verify_wrong_key_fails(self):
        s1 = Signer("key1")
        s2 = Signer("key2")
        result = s1.sign("data")
        assert s2.verify("data", result.signature) is False

    def test_bytes_input(self):
        signer = Signer(self._KEY)
        r_str = signer.sign("abc")
        r_bytes = signer.sign(b"abc")
        assert r_str.signature == r_bytes.signature

    def test_bytes_key(self):
        signer = Signer(b"raw-bytes-key")
        result = signer.sign("data")
        assert signer.verify("data", result.signature)

    def test_key_id_stored(self):
        signer = Signer(self._KEY)
        result = signer.sign("d", key_id="kid-42")
        assert result.key_id == "kid-42"

    def test_sign_json_roundtrip(self):
        signer = Signer(self._KEY)
        obj = {"action": "deploy", "env": "prod"}
        signed = signer.sign_json(obj)
        assert "_signature" in signed
        assert signer.verify_json(signed) is True

    def test_sign_json_tampered(self):
        signer = Signer(self._KEY)
        signed = signer.sign_json({"val": 1})
        signed["val"] = 999
        assert signer.verify_json(signed) is False

    def test_verify_json_no_signature(self):
        signer = Signer(self._KEY)
        assert signer.verify_json({"no_sig": True}) is False

    def test_verify_json_empty_signature_field(self):
        signer = Signer(self._KEY)
        assert signer.verify_json({"_signature": {}}) is False

    def test_sign_json_key_order_irrelevant(self):
        signer = Signer(self._KEY)
        s1 = signer.sign_json({"b": 2, "a": 1})
        s2 = signer.sign_json({"a": 1, "b": 2})
        assert s1["_signature"]["signature"] == s2["_signature"]["signature"]

    def test_sign_json_key_id(self):
        signer = Signer(self._KEY)
        signed = signer.sign_json({"x": 1}, key_id="k99")
        assert signed["_signature"]["key_id"] == "k99"


# ==============================================================================
# 15. SignatureResult
# ==============================================================================


@pytest.mark.unit
class TestSignatureResult:
    def test_to_dict_fields(self):
        sr = SignatureResult(
            signature="abc",
            algorithm=SignatureAlgorithm.HMAC_SHA256,
            key_id="k1",
        )
        d = sr.to_dict()
        assert d["signature"] == "abc"
        assert d["algorithm"] == "hmac-sha256"
        assert d["key_id"] == "k1"
        assert "timestamp" in d

    def test_default_key_id(self):
        sr = SignatureResult(signature="x", algorithm=SignatureAlgorithm.HMAC_SHA256)
        assert sr.key_id == ""

    def test_timestamp_positive(self):
        sr = SignatureResult(signature="x", algorithm=SignatureAlgorithm.HMAC_SHA256)
        assert sr.timestamp > 0

    def test_sha512_algorithm_value(self):
        sr = SignatureResult(signature="x", algorithm=SignatureAlgorithm.HMAC_SHA512)
        assert sr.to_dict()["algorithm"] == "hmac-sha512"


# ==============================================================================
# 16. sign_file / verify_file
# ==============================================================================


@pytest.mark.unit
class TestFileSignVerify:
    def test_sign_and_verify(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "doc.txt"
            f.write_text("important document")
            sig = sign_file(f, "secret")
            assert verify_file(f, sig, "secret") is True

    def test_wrong_secret_fails(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "doc.txt"
            f.write_text("content")
            sig = sign_file(f, "key1")
            assert verify_file(f, sig, "key2") is False

    def test_sha512(self):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "doc.txt"
            f.write_bytes(b"data")
            sig = sign_file(f, "k", SignatureAlgorithm.HMAC_SHA512)
            assert len(sig) == 128
            assert verify_file(f, sig, "k", SignatureAlgorithm.HMAC_SHA512) is True


# ==============================================================================
# 17. SignatureAlgorithm Enum
# ==============================================================================


@pytest.mark.unit
class TestSignatureAlgorithm:
    def test_values(self):
        assert SignatureAlgorithm.HMAC_SHA256.value == "hmac-sha256"
        assert SignatureAlgorithm.HMAC_SHA512.value == "hmac-sha512"

    def test_member_count(self):
        assert len(SignatureAlgorithm) == 2


# ==============================================================================
# 18. Convenience Functions (__init__.py)
# ==============================================================================


@pytest.mark.unit
class TestConvenienceFunctions:
    def test_encrypt_decrypt(self):
        key = generate_aes_key()
        ctx = _suppress_cbc_warning()
        try:
            ct = encrypt(b"hello", key)
            pt = decrypt(ct, key)
        finally:
            ctx.__exit__(None, None, None)
        assert pt == b"hello"

    def test_generate_key_aes(self):
        key = generate_key("AES")
        assert len(key) == 32

    def test_generate_key_rsa(self):
        key = generate_key("RSA")
        assert b"PRIVATE KEY" in key

    def test_get_encryptor_returns_instance(self):
        enc = get_encryptor("AES")
        assert isinstance(enc, Encryptor)
        assert enc.algorithm == "AES"

    def test_generate_aes_key_length(self):
        key = generate_aes_key()
        assert len(key) == 32

    def test_encrypt_data_decrypt_data(self):
        key = generate_aes_key()
        ctx = _suppress_cbc_warning()
        try:
            ct = encrypt_data(b"data", key, "AES")
            pt = decrypt_data(ct, key, "AES")
        finally:
            ctx.__exit__(None, None, None)
        assert pt == b"data"

    def test_encrypt_file_decrypt_file(self):
        key = generate_aes_key()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "src.txt"
            enc_f = td / "enc.bin"
            dec_f = td / "dec.txt"
            src.write_bytes(b"pkg-level test")
            ctx = _suppress_cbc_warning()
            try:
                assert encrypt_file(src, enc_f, key) is True
                assert decrypt_file(enc_f, dec_f, key) is True
            finally:
                ctx.__exit__(None, None, None)
            assert dec_f.read_bytes() == b"pkg-level test"

    def test_hash_data_function(self):
        h = hash_data(b"test", "sha256")
        assert len(h) == 64

    def test_hash_data_default_algorithm(self):
        h = hash_data(b"test")
        assert len(h) == 64  # sha256 is default


# ==============================================================================
# 19. Error Handling
# ==============================================================================


@pytest.mark.unit
class TestErrorHandling:
    def test_unsupported_algorithm_raises(self):
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            Encryptor(algorithm="BLOWFISH")

    def test_encryptor_algorithm_case_insensitive(self):
        enc = Encryptor(algorithm="aes")
        assert enc.algorithm == "AES"

    def test_encryption_error_message(self):
        try:
            raise EncryptionError("context info")
        except EncryptionError as e:
            assert "context info" in str(e)

    def test_encryption_error_is_from_exceptions(self):
        from codomyrmex.exceptions import EncryptionError as ExcErr

        assert EncryptionError is ExcErr


# ==============================================================================
# 20. Integration — Multi-Component Workflows
# ==============================================================================


@pytest.mark.unit
class TestIntegrationWorkflows:
    def test_key_manager_with_gcm(self):
        """Store key in KeyManager, retrieve, use with AES-GCM."""
        with tempfile.TemporaryDirectory() as td:
            mgr = KeyManager(key_dir=Path(td))
            key = generate_aes_key()
            mgr.store_key("app-key", key)
            retrieved = mgr.get_key("app-key")
            enc = AESGCMEncryptor(retrieved)
            ct = enc.encrypt(b"managed key test")
            pt = enc.decrypt(ct)
            assert pt == b"managed key test"

    def test_derived_key_with_container(self):
        """PBKDF2-derived key used with SecureDataContainer."""
        enc = Encryptor()
        salt = Encryptor.generate_salt()
        key = enc.derive_key("passphrase", salt)
        container = SecureDataContainer(key)
        data = {"derived": True}
        packed = container.pack(data)
        result = container.unpack(packed)
        assert result["data"] == data

    def test_hkdf_key_with_gcm(self):
        """HKDF-derived key used for AES-GCM encryption."""
        key = derive_key_hkdf(b"shared-secret", salt=os.urandom(16))
        enc = AESGCMEncryptor(key)
        ct = enc.encrypt(b"hkdf-derived")
        pt = enc.decrypt(ct)
        assert pt == b"hkdf-derived"

    def test_key_rotation_workflow(self):
        """Full key rotation: decrypt with old, re-encrypt with new."""
        with tempfile.TemporaryDirectory() as td:
            mgr = KeyManager(key_dir=Path(td))
            old_key = generate_aes_key()
            mgr.store_key("rotate", old_key)

            # Encrypt with old
            ct_old = AESGCMEncryptor(old_key).encrypt(b"rotate me")

            # Rotate
            new_key = generate_aes_key()
            returned_old = mgr.rotate_key("rotate", new_key)
            assert returned_old == old_key

            # Re-encrypt
            pt = AESGCMEncryptor(returned_old).decrypt(ct_old)
            ct_new = AESGCMEncryptor(new_key).encrypt(pt)
            assert AESGCMEncryptor(new_key).decrypt(ct_new) == b"rotate me"

    def test_hmac_then_encrypt(self):
        """Compute HMAC, then encrypt both message and MAC."""
        msg = b"important message"
        hmac_key = b"hmac-key"
        mac = compute_hmac(msg, hmac_key)

        enc_key = generate_aes_key()
        enc = AESGCMEncryptor(enc_key)
        ct = enc.encrypt(msg + mac)
        pt = enc.decrypt(ct)

        recovered_msg = pt[: len(msg)]
        recovered_mac = pt[len(msg) :]
        assert recovered_msg == msg
        assert verify_hmac(recovered_msg, hmac_key, recovered_mac) is True

    def test_sign_then_encrypt_json(self):
        """Sign JSON, then encrypt the signed payload."""
        signer = Signer("signing-key")
        obj = {"action": "transfer", "amount": 100}
        signed = signer.sign_json(obj)
        assert signer.verify_json(signed) is True

        # Encrypt the signed JSON
        enc_key = generate_aes_key()
        container = SecureDataContainer(enc_key)
        packed = container.pack(signed)
        unpacked = container.unpack(packed)
        assert signer.verify_json(unpacked["data"]) is True
