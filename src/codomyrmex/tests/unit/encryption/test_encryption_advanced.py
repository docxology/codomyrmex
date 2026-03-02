"""Advanced encryption tests: AESGCM, KeyManager, HMAC, HKDF, integration."""

import os
import tempfile
import warnings
from pathlib import Path

import pytest

from codomyrmex.encryption import (
    AESGCMEncryptor,
    EncryptionError,
    SecureDataContainer,
    compute_hmac,
    decrypt,
    decrypt_file,
    derive_key_hkdf,
    encrypt,
    encrypt_file,
    generate_aes_key,
    generate_key,
    get_encryptor,
    hash_data,
    verify_hmac,
)
from codomyrmex.encryption.algorithms.aes_gcm import AESGCMEncryptor
from codomyrmex.encryption.core.encryptor import (
    Encryptor,
    decrypt_data,
    encrypt_data,
)
from codomyrmex.encryption.keys.key_manager import KeyManager
from codomyrmex.exceptions import EncryptionError as ExceptionsEncryptionError

# ==============================================================================
# AES-GCM Tests
# ==============================================================================

@pytest.mark.crypto
class TestAESGCM:
    """Tests for AES-GCM authenticated encryption."""

    def test_aes_gcm_encrypt_decrypt(self):
        """Test AES-GCM encrypt/decrypt roundtrip."""
        key = generate_aes_key()
        encryptor = AESGCMEncryptor(key)
        data = b"secret data"
        ciphertext = encryptor.encrypt(data)
        plaintext = encryptor.decrypt(ciphertext)
        assert data == plaintext

    def test_aes_gcm_with_associated_data(self):
        """Test AES-GCM with associated data (AAD)."""
        key = generate_aes_key()
        encryptor = AESGCMEncryptor(key)
        data = b"secret data"
        aad = b"associated data"
        ciphertext = encryptor.encrypt(data, aad)
        plaintext = encryptor.decrypt(ciphertext, aad)
        assert data == plaintext

    def test_aes_gcm_wrong_aad_fails(self):
        """Test AES-GCM fails with wrong AAD."""
        key = generate_aes_key()
        encryptor = AESGCMEncryptor(key)
        data = b"secret data"
        aad = b"associated data"
        ciphertext = encryptor.encrypt(data, aad)

        with pytest.raises(Exception):  # cryptography raises InvalidTag
            encryptor.decrypt(ciphertext, b"wrong aad")

    def test_aes_gcm_tampered_ciphertext_fails(self):
        """Test AES-GCM detects tampered ciphertext."""
        key = generate_aes_key()
        encryptor = AESGCMEncryptor(key)
        data = b"secret data"
        ciphertext = encryptor.encrypt(data)

        # Tamper with ciphertext
        tampered = bytearray(ciphertext)
        tampered[-1] ^= 0xFF
        tampered = bytes(tampered)

        with pytest.raises(Exception):  # cryptography raises InvalidTag
            encryptor.decrypt(tampered)

    def test_aes_gcm_auto_key_generation(self):
        """Test AES-GCM auto-generates key if not provided."""
        encryptor = AESGCMEncryptor()
        assert len(encryptor.key) == 32

    def test_aes_gcm_invalid_key_size(self):
        """Test AES-GCM rejects invalid key sizes."""
        with pytest.raises(ValueError):
            AESGCMEncryptor(b"short")

    def test_aes_gcm_valid_key_sizes(self):
        """Test AES-GCM accepts valid key sizes (16, 24, 32 bytes)."""
        for size in [16, 24, 32]:
            encryptor = AESGCMEncryptor(os.urandom(size))
            data = b"test"
            ciphertext = encryptor.encrypt(data)
            assert encryptor.decrypt(ciphertext) == data


# ==============================================================================
# Secure Data Container Tests
# ==============================================================================

@pytest.mark.crypto
class TestSecureDataContainer:
    """Tests for SecureDataContainer."""

    @pytest.fixture
    def key(self):
        """Generate key."""
        return generate_aes_key()

    @pytest.fixture
    def container(self, key):
        """Create secure data container."""
        return SecureDataContainer(key)

    def test_pack_unpack_dict(self, container):
        """Test packing and unpacking a dictionary."""
        data = {"user": "admin", "id": 123}
        packed = container.pack(data)
        unpacked = container.unpack(packed)
        assert data == unpacked["data"]

    def test_pack_unpack_with_metadata(self, container):
        """Test packing with metadata."""
        data = {"message": "hello"}
        metadata = {"timestamp": 1234567890, "version": "1.0"}
        packed = container.pack(data, metadata)
        unpacked = container.unpack(packed)
        assert unpacked["data"] == data
        assert unpacked["metadata"] == metadata

    def test_pack_unpack_list(self, container):
        """Test packing a list."""
        data = [1, 2, 3, "a", "b", "c"]
        packed = container.pack(data)
        unpacked = container.unpack(packed)
        assert unpacked["data"] == data

    def test_pack_unpack_nested(self, container):
        """Test packing nested structures."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "config": {"enabled": True}
        }
        packed = container.pack(data)
        unpacked = container.unpack(packed)
        assert unpacked["data"] == data

    def test_different_keys_cannot_decrypt(self):
        """Test that different keys cannot decrypt each other's data."""
        key1 = generate_aes_key()
        key2 = generate_aes_key()

        container1 = SecureDataContainer(key1)
        container2 = SecureDataContainer(key2)

        data = {"secret": "value"}
        packed = container1.pack(data)

        with pytest.raises(Exception):
            container2.unpack(packed)


# ==============================================================================
# Key Manager Tests
# ==============================================================================

@pytest.mark.crypto
class TestKeyManager:
    """Tests for KeyManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_dir):
        """Create key manager."""
        return KeyManager(key_dir=temp_dir)

    def test_store_and_retrieve_key(self, manager):
        """Test storing and retrieving a key."""
        key = os.urandom(32)
        assert manager.store_key("test-key", key)
        retrieved = manager.get_key("test-key")
        assert retrieved == key

    def test_get_nonexistent_key(self, manager):
        """Test retrieving nonexistent key returns None."""
        assert manager.get_key("nonexistent") is None

    def test_delete_key(self, manager):
        """Test key deletion."""
        key = os.urandom(32)
        manager.store_key("delete-me", key)
        assert manager.delete_key("delete-me")
        assert manager.get_key("delete-me") is None

    def test_delete_nonexistent_key(self, manager):
        """Test deleting nonexistent key returns False."""
        assert not manager.delete_key("nonexistent")

    def test_key_file_permissions(self, manager, temp_dir):
        """Test that key files have restrictive permissions."""
        key = os.urandom(32)
        manager.store_key("secure-key", key)
        key_file = temp_dir / "secure-key.key"
        # Check file permissions (owner read/write only)
        mode = key_file.stat().st_mode & 0o777
        assert mode == 0o600

    def test_multiple_keys(self, manager):
        """Test managing multiple keys."""
        keys = {f"key-{i}": os.urandom(32) for i in range(5)}

        for key_id, key in keys.items():
            manager.store_key(key_id, key)

        for key_id, key in keys.items():
            assert manager.get_key(key_id) == key

    def test_list_keys(self, manager):
        """Test listing stored keys."""
        manager.store_key("alpha", os.urandom(32))
        manager.store_key("bravo", os.urandom(32))
        manager.store_key("charlie", os.urandom(32))
        result = manager.list_keys()
        assert result == ["alpha", "bravo", "charlie"]

    def test_list_keys_empty(self, manager):
        """Test listing keys when none are stored."""
        assert manager.list_keys() == []

    def test_key_exists_true(self, manager):
        """Test key_exists returns True for stored key."""
        manager.store_key("existing", os.urandom(32))
        assert manager.key_exists("existing") is True

    def test_key_exists_false(self, manager):
        """Test key_exists returns False for missing key."""
        assert manager.key_exists("missing") is False

    def test_rotate_key(self, manager):
        """Test key rotation returns old key and stores new one."""
        old_key = os.urandom(32)
        new_key = os.urandom(32)
        manager.store_key("rotate-me", old_key)

        returned = manager.rotate_key("rotate-me", new_key)
        assert returned == old_key
        assert manager.get_key("rotate-me") == new_key

    def test_rotate_key_nonexistent(self, manager):
        """Test rotating a nonexistent key returns None and stores new."""
        new_key = os.urandom(32)
        returned = manager.rotate_key("new-id", new_key)
        assert returned is None
        assert manager.get_key("new-id") == new_key


# ==============================================================================
# Convenience Function Tests
# ==============================================================================

@pytest.mark.crypto
class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_generate_aes_key(self):
        """Test generate_aes_key function."""
        key = generate_aes_key()
        assert len(key) == 32

    def test_encrypt_data_aes(self):
        """Test encrypt_data convenience function with AES."""
        key = generate_aes_key()
        data = b"test data"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            encrypted = encrypt_data(data, key, "AES")
            decrypted = decrypt_data(encrypted, key, "AES")
        assert decrypted == data

    def test_encrypt_data_rsa(self):
        """Test encrypt_data convenience function with RSA."""
        encryptor = Encryptor(algorithm="RSA")
        private_key, public_key = encryptor.generate_key_pair()

        data = b"test data"
        encrypted = encrypt_data(data, public_key, "RSA")
        decrypted = decrypt_data(encrypted, private_key, "RSA")
        assert decrypted == data


# ==============================================================================
# __init__.py Convenience Function Tests
# ==============================================================================

@pytest.mark.crypto
class TestInitConvenienceFunctions:
    """Tests for the convenience functions exported by __init__.py."""

    def test_encrypt_decrypt(self):
        """Test encrypt/decrypt from package level."""
        key = generate_aes_key()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ct = encrypt(b"hello", key)
            pt = decrypt(ct, key)
        assert pt == b"hello"

    def test_generate_key(self):
        """Test generate_key from package level."""
        key = generate_key()
        assert len(key) == 32

    def test_get_encryptor(self):
        """Test get_encryptor factory."""
        enc = get_encryptor("AES")
        assert isinstance(enc, Encryptor)
        assert enc.algorithm == "AES"

    def test_encrypt_decrypt_file(self):
        """Test encrypt_file/decrypt_file from package level."""
        key = generate_aes_key()
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src.txt"
            enc_f = Path(tmpdir) / "enc.bin"
            dec_f = Path(tmpdir) / "dec.txt"
            src.write_bytes(b"file content")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                assert encrypt_file(str(src), str(enc_f), key)
                assert decrypt_file(str(enc_f), str(dec_f), key)
            assert dec_f.read_bytes() == b"file content"

    def test_hash_data(self):
        """Test hash_data from package level."""
        h = hash_data(b"data", "sha256")
        assert len(h) == 64


# ==============================================================================
# Error Handling Tests
# ==============================================================================

@pytest.mark.crypto
class TestErrorHandling:
    """Tests for error handling."""

    def test_unknown_algorithm(self):
        """Test that unknown algorithm raises error."""
        encryptor = Encryptor(algorithm="UNKNOWN")
        with pytest.raises(EncryptionError):
            encryptor.encrypt(b"data", b"key")

    def test_encryption_error_has_context(self):
        """Test that EncryptionError includes context."""
        try:
            raise EncryptionError("Test error", file_path="/test/path")
        except EncryptionError as e:
            assert "file_path" in e.context
            assert e.context["file_path"] == "/test/path"

    def test_encryption_error_identity(self):
        """Verify package-level EncryptionError catches encryptor.py raises."""
        from codomyrmex.encryption import EncryptionError as PkgError
        from codomyrmex.encryption.core.encryptor import EncryptionError as EncError

        # Both should be the same class (from codomyrmex.exceptions)
        assert PkgError is ExceptionsEncryptionError
        assert EncError is ExceptionsEncryptionError

        # Verify catching works
        with pytest.raises(PkgError):
            Encryptor("UNKNOWN").encrypt(b"x", b"k")


# ==============================================================================
# HMAC Tests
# ==============================================================================

@pytest.mark.crypto
class TestHMAC:
    """Tests for HMAC utilities."""

    def test_compute_and_verify_sha256(self):
        """Test HMAC roundtrip with sha256."""
        mac = compute_hmac(b"message", b"key")
        assert verify_hmac(b"message", b"key", mac)

    def test_compute_and_verify_sha512(self):
        """Test HMAC roundtrip with sha512."""
        mac = compute_hmac(b"message", b"key", algorithm="sha512")
        assert verify_hmac(b"message", b"key", mac, algorithm="sha512")

    def test_verify_fails_tampered_data(self):
        """Test verification fails with tampered data."""
        mac = compute_hmac(b"original", b"key")
        assert not verify_hmac(b"tampered", b"key", mac)

    def test_verify_fails_wrong_key(self):
        """Test verification fails with wrong key."""
        mac = compute_hmac(b"message", b"key1")
        assert not verify_hmac(b"message", b"key2", mac)

    def test_invalid_algorithm(self):
        """Test that invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            compute_hmac(b"data", b"key", algorithm="md5")

    def test_empty_data(self):
        """Test HMAC of empty data."""
        mac = compute_hmac(b"", b"key")
        assert isinstance(mac, bytes)
        assert len(mac) > 0
        assert verify_hmac(b"", b"key", mac)

    def test_string_inputs(self):
        """Test that str inputs are accepted and encoded."""
        mac_bytes = compute_hmac(b"msg", b"key")
        mac_str = compute_hmac("msg", "key")
        assert mac_bytes == mac_str


# ==============================================================================
# HKDF Tests
# ==============================================================================

@pytest.mark.crypto
class TestHKDF:
    """Tests for HKDF key derivation."""

    def test_basic_derivation(self):
        """Test basic HKDF produces correct length."""
        key = derive_key_hkdf(b"input-material", length=32)
        assert len(key) == 32

    def test_deterministic_with_same_inputs(self):
        """Test same inputs produce same output."""
        k1 = derive_key_hkdf(b"ikm", salt=b"salt", info=b"info")
        k2 = derive_key_hkdf(b"ikm", salt=b"salt", info=b"info")
        assert k1 == k2

    def test_different_salt_different_key(self):
        """Test different salt produces different key."""
        k1 = derive_key_hkdf(b"ikm", salt=b"salt1")
        k2 = derive_key_hkdf(b"ikm", salt=b"salt2")
        assert k1 != k2

    def test_different_info_different_key(self):
        """Test different info produces different key."""
        k1 = derive_key_hkdf(b"ikm", info=b"context-a")
        k2 = derive_key_hkdf(b"ikm", info=b"context-b")
        assert k1 != k2

    def test_custom_length(self):
        """Test custom output length."""
        key = derive_key_hkdf(b"ikm", length=64)
        assert len(key) == 64

    def test_invalid_algorithm(self):
        """Test invalid algorithm raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            derive_key_hkdf(b"ikm", algorithm="md5")

    def test_string_input(self):
        """Test that str input is accepted."""
        key = derive_key_hkdf("string-material")
        assert len(key) == 32


# ==============================================================================
# Edge Case Tests
# ==============================================================================

@pytest.mark.crypto
class TestEdgeCases:
    """Edge case tests."""

    def test_binary_data_with_null_bytes(self):
        """Test encrypting data containing null bytes."""
        key = generate_aes_key()
        data = b"\x00\x01\x02\x00\xff\x00"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ct = Encryptor().encrypt(data, key)
            pt = Encryptor().decrypt(ct, key)
        assert pt == data

    def test_very_long_key_id(self):
        """Test KeyManager with a very long key_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(key_dir=Path(tmpdir))
            long_id = "k" * 200
            key = os.urandom(32)
            assert km.store_key(long_id, key)
            assert km.get_key(long_id) == key

    def test_empty_key_id(self):
        """Test KeyManager with empty key_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(key_dir=Path(tmpdir))
            key = os.urandom(32)
            assert km.store_key("", key)
            assert km.get_key("") == key

    def test_container_non_serializable_data(self):
        """Test SecureDataContainer with non-JSON-serializable data."""
        key = generate_aes_key()
        container = SecureDataContainer(key)
        with pytest.raises(TypeError):
            container.pack(object())

    def test_aes_gcm_empty_data(self):
        """Test AES-GCM with empty data."""
        enc = AESGCMEncryptor()
        ct = enc.encrypt(b"")
        pt = enc.decrypt(ct)
        assert pt == b""

    def test_hash_empty_data(self):
        """Test hashing empty data."""
        h = Encryptor.hash_data(b"", "sha256")
        assert len(h) == 64
        # Well-known SHA-256 of empty string
        assert h == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_aes_cbc_deprecation_warning(self):
        """Test that AES-CBC emits a DeprecationWarning."""
        key = os.urandom(32)
        enc = Encryptor("AES")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            enc.encrypt(b"test", key)
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert "AES-CBC" in str(deprecation_warnings[0].message)


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.crypto
@pytest.mark.integration
class TestEncryptionIntegration:
    """Integration tests combining multiple encryption components."""

    def test_key_manager_with_encryptor(self):
        """Test KeyManager + Encryptor workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(key_dir=Path(tmpdir))
            key = generate_aes_key()
            km.store_key("my-key", key)

            retrieved = km.get_key("my-key")
            enc = AESGCMEncryptor(retrieved)
            ct = enc.encrypt(b"managed key encryption")
            pt = enc.decrypt(ct)
            assert pt == b"managed key encryption"

    def test_file_encryption_with_key_manager(self):
        """Test file encryption using a key from KeyManager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            km = KeyManager(key_dir=tmpdir / "keys")
            key = generate_aes_key()
            km.store_key("file-key", key)

            src = tmpdir / "source.txt"
            enc_f = tmpdir / "encrypted.bin"
            dec_f = tmpdir / "decrypted.txt"
            src.write_bytes(b"integration test data")

            retrieved = km.get_key("file-key")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                assert encrypt_file(str(src), str(enc_f), retrieved)
                assert decrypt_file(str(enc_f), str(dec_f), retrieved)
            assert dec_f.read_bytes() == b"integration test data"

    def test_secure_container_with_derived_key(self):
        """Test SecureDataContainer with a PBKDF2-derived key."""
        enc = Encryptor()
        salt = Encryptor.generate_salt()
        key = enc.derive_key("my-password", salt)
        container = SecureDataContainer(key)
        data = {"secret": "derived-key-test"}
        packed = container.pack(data)
        unpacked = container.unpack(packed)
        assert unpacked["data"] == data

    def test_key_rotation_re_encryption(self):
        """Test full key rotation + re-encryption workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            km = KeyManager(key_dir=Path(tmpdir))
            old_key = generate_aes_key()
            km.store_key("app-key", old_key)

            # Encrypt with old key
            old_enc = AESGCMEncryptor(old_key)
            ct_old = old_enc.encrypt(b"rotate me")

            # Rotate
            new_key = generate_aes_key()
            returned_old = km.rotate_key("app-key", new_key)
            assert returned_old == old_key

            # Re-encrypt
            pt = AESGCMEncryptor(returned_old).decrypt(ct_old)
            ct_new = AESGCMEncryptor(new_key).encrypt(pt)
            assert AESGCMEncryptor(new_key).decrypt(ct_new) == b"rotate me"


# From test_coverage_boost.py
class TestSigner:
    """Tests for HMAC Signer."""

    def test_sign_and_verify(self):
        from codomyrmex.encryption.signing import Signer

        signer = Signer("my-secret-key")
        result = signer.sign("hello world")
        assert result.signature
        assert signer.verify("hello world", result.signature)

    def test_verify_fails_with_wrong_data(self):
        from codomyrmex.encryption.signing import Signer

        signer = Signer("key")
        result = signer.sign("original")
        assert not signer.verify("tampered", result.signature)

    def test_sha512_algorithm(self):
        from codomyrmex.encryption.signing import SignatureAlgorithm, Signer

        signer = Signer("key", SignatureAlgorithm.HMAC_SHA512)
        result = signer.sign("data")
        assert result.algorithm == SignatureAlgorithm.HMAC_SHA512
        assert signer.verify("data", result.signature)

    def test_sign_json_roundtrip(self):
        from codomyrmex.encryption.signing import Signer

        signer = Signer("json-key")
        obj = {"user": "alice", "action": "deploy"}
        signed = signer.sign_json(obj, key_id="k1")
        assert "_signature" in signed
        assert signer.verify_json(signed)

    def test_verify_json_tampered(self):
        from codomyrmex.encryption.signing import Signer

        signer = Signer("json-key")
        signed = signer.sign_json({"val": 1})
        signed["val"] = 999  # Tamper
        assert not signer.verify_json(signed)

    def test_verify_json_no_signature(self):
        from codomyrmex.encryption.signing import Signer

        signer = Signer("key")
        assert not signer.verify_json({"no_sig": True})


# From test_coverage_boost.py
class TestSignatureResult:
    """Tests for SignatureResult.to_dict."""

    def test_to_dict(self):
        from codomyrmex.encryption.signing import SignatureAlgorithm, SignatureResult

        sr = SignatureResult(
            signature="abc123",
            algorithm=SignatureAlgorithm.HMAC_SHA256,
            key_id="k1",
        )
        d = sr.to_dict()
        assert d["signature"] == "abc123"
        assert d["algorithm"] == "hmac-sha256"
        assert d["key_id"] == "k1"


# From test_coverage_boost.py
class TestFileSignature:
    """Tests for sign_file / verify_file."""

    def test_file_sign_verify(self, tmp_path):
        from codomyrmex.encryption.signing import sign_file, verify_file

        p = tmp_path / "doc.txt"
        p.write_text("important document")

        sig = sign_file(p, "file-secret")
        assert verify_file(p, sig, "file-secret")
        assert not verify_file(p, sig, "wrong-secret")
