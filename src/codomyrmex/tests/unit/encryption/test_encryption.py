"""Core encryption tests: AES, RSA, digital signatures, key derivation, string/file encryption, hashing."""

import os
import tempfile
import warnings
from pathlib import Path

import pytest

from codomyrmex.encryption import EncryptionError
from codomyrmex.encryption.core.encryptor import Encryptor

# ==============================================================================
# Encryptor (AES) Tests
# ==============================================================================

@pytest.mark.crypto
class TestEncryptorAES:
    """Tests for AES encryption."""

    @pytest.fixture
    def encryptor(self):
        """Create AES encryptor."""
        return Encryptor(algorithm="AES")

    @pytest.fixture
    def key(self):
        """Generate a valid AES key."""
        return os.urandom(32)

    def test_aes_encrypt_decrypt_roundtrip(self, encryptor, key):
        """Test basic AES encrypt/decrypt roundtrip."""
        plaintext = b"Hello, World!"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt(plaintext, key)
            decrypted = encryptor.decrypt(ciphertext, key)
        assert decrypted == plaintext

    def test_aes_encrypt_produces_different_output(self, encryptor, key):
        """Test that encrypting same data twice produces different ciphertext (due to IV)."""
        plaintext = b"Same data"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext1 = encryptor.encrypt(plaintext, key)
            ciphertext2 = encryptor.encrypt(plaintext, key)
        assert ciphertext1 != ciphertext2

    def test_aes_decrypt_with_wrong_key_fails(self, encryptor, key):
        """Test decryption with wrong key fails."""
        plaintext = b"Secret data"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt(plaintext, key)
            wrong_key = os.urandom(32)
            with pytest.raises(EncryptionError):
                encryptor.decrypt(ciphertext, wrong_key)

    def test_aes_encrypt_empty_data(self, encryptor, key):
        """Test encryption of empty data."""
        plaintext = b""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt(plaintext, key)
            decrypted = encryptor.decrypt(ciphertext, key)
        assert decrypted == plaintext

    def test_aes_encrypt_large_data(self, encryptor, key):
        """Test encryption of large data."""
        plaintext = os.urandom(1024 * 1024)  # 1MB
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt(plaintext, key)
            decrypted = encryptor.decrypt(ciphertext, key)
        assert decrypted == plaintext

    def test_aes_key_normalization(self, encryptor):
        """Test that non-32-byte keys are normalized via hashing."""
        short_key = b"shortkey"
        plaintext = b"Test data"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt(plaintext, short_key)
            decrypted = encryptor.decrypt(ciphertext, short_key)
        assert decrypted == plaintext

    def test_generate_aes_key(self, encryptor):
        """Test AES key generation."""
        key = encryptor.generate_key()
        assert len(key) == 32

    def test_generate_aes_key_uniqueness(self, encryptor):
        """Test that generated keys are unique."""
        keys = [encryptor.generate_key() for _ in range(10)]
        assert len(set(keys)) == 10


# ==============================================================================
# Encryptor (RSA) Tests
# ==============================================================================

@pytest.mark.crypto
class TestEncryptorRSA:
    """Tests for RSA encryption."""

    @pytest.fixture
    def encryptor(self):
        """Create RSA encryptor."""
        return Encryptor(algorithm="RSA")

    @pytest.fixture
    def key_pair(self):
        """Generate RSA key pair."""
        encryptor = Encryptor(algorithm="RSA")
        return encryptor.generate_key_pair()

    def test_rsa_encrypt_decrypt_roundtrip(self, encryptor, key_pair):
        """Test basic RSA encrypt/decrypt roundtrip."""
        private_key, public_key = key_pair
        plaintext = b"Hello, RSA!"

        ciphertext = encryptor.encrypt(plaintext, public_key)
        decrypted = encryptor.decrypt(ciphertext, private_key)
        assert decrypted == plaintext

    def test_rsa_encrypt_with_private_key_fails(self, encryptor, key_pair):
        """Test encryption with private key fails."""
        private_key, _ = key_pair
        plaintext = b"Test data"

        with pytest.raises(EncryptionError):
            encryptor.encrypt(plaintext, private_key)

    def test_rsa_decrypt_with_public_key_fails(self, encryptor, key_pair):
        """Test decryption with public key fails."""
        _, public_key = key_pair
        # Create fake ciphertext
        with pytest.raises(EncryptionError):
            encryptor.decrypt(b"fake ciphertext", public_key)

    def test_rsa_key_pair_generation(self, encryptor):
        """Test RSA key pair generation."""
        private_key, public_key = encryptor.generate_key_pair()
        assert b"PRIVATE KEY" in private_key
        assert b"PUBLIC KEY" in public_key

    def test_rsa_different_key_sizes(self):
        """Test RSA with different key sizes."""
        encryptor = Encryptor(algorithm="RSA")
        for key_size in [2048, 4096]:
            private_key, public_key = encryptor.generate_key_pair(key_size)
            plaintext = b"Test"
            ciphertext = encryptor.encrypt(plaintext, public_key)
            decrypted = encryptor.decrypt(ciphertext, private_key)
            assert decrypted == plaintext


# ==============================================================================
# Digital Signature Tests
# ==============================================================================

@pytest.mark.crypto
@pytest.mark.security
class TestDigitalSignatures:
    """Tests for digital signatures."""

    @pytest.fixture
    def encryptor(self):
        """Create RSA encryptor for signing."""
        return Encryptor(algorithm="RSA")

    @pytest.fixture
    def key_pair(self, encryptor):
        """Generate key pair for signing."""
        return encryptor.generate_key_pair()

    def test_sign_and_verify(self, encryptor, key_pair):
        """Test basic sign and verify roundtrip."""
        private_key, public_key = key_pair
        data = b"Important message"

        signature = encryptor.sign(data, private_key)
        assert encryptor.verify(data, signature, public_key)

    def test_verify_with_wrong_data_fails(self, encryptor, key_pair):
        """Test verification fails with modified data."""
        private_key, public_key = key_pair
        data = b"Original message"

        signature = encryptor.sign(data, private_key)
        assert not encryptor.verify(b"Modified message", signature, public_key)

    def test_verify_with_wrong_signature_fails(self, encryptor, key_pair):
        """Test verification fails with wrong signature."""
        _, public_key = key_pair
        data = b"Test data"

        assert not encryptor.verify(data, b"wrong signature", public_key)

    def test_verify_with_wrong_key_fails(self, encryptor, key_pair):
        """Test verification fails with different key pair."""
        private_key, _ = key_pair
        _, other_public_key = encryptor.generate_key_pair()
        data = b"Test data"

        signature = encryptor.sign(data, private_key)
        assert not encryptor.verify(data, signature, other_public_key)


# ==============================================================================
# Key Derivation Tests
# ==============================================================================

@pytest.mark.crypto
class TestKeyDerivation:
    """Tests for key derivation."""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor for key derivation."""
        return Encryptor()

    def test_derive_key_from_password(self, encryptor):
        """Test key derivation from password."""
        password = "strong_password"
        salt = os.urandom(16)

        key = encryptor.derive_key(password, salt)
        assert len(key) == 32

    def test_derive_key_deterministic(self, encryptor):
        """Test that same password + salt produces same key."""
        password = "test_password"
        salt = b"fixed_salt_1234"

        key1 = encryptor.derive_key(password, salt)
        key2 = encryptor.derive_key(password, salt)
        assert key1 == key2

    def test_derive_key_different_salt(self, encryptor):
        """Test that different salt produces different key."""
        password = "test_password"
        salt1 = b"salt_one______16"
        salt2 = b"salt_two______16"

        key1 = encryptor.derive_key(password, salt1)
        key2 = encryptor.derive_key(password, salt2)
        assert key1 != key2

    def test_derive_key_different_password(self, encryptor):
        """Test that different password produces different key."""
        salt = b"common_salt_____"
        key1 = encryptor.derive_key("password1", salt)
        key2 = encryptor.derive_key("password2", salt)
        assert key1 != key2

    def test_generate_salt(self):
        """Test salt generation."""
        salt = Encryptor.generate_salt()
        assert len(salt) == 16

    def test_generate_salt_custom_length(self):
        """Test salt generation with custom length."""
        salt = Encryptor.generate_salt(32)
        assert len(salt) == 32


# ==============================================================================
# String Encryption Tests
# ==============================================================================

@pytest.mark.crypto
class TestStringEncryption:
    """Tests for string encryption utilities."""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor."""
        return Encryptor()

    @pytest.fixture
    def key(self):
        """Generate key."""
        return os.urandom(32)

    def test_encrypt_decrypt_string(self, encryptor, key):
        """Test string encryption roundtrip."""
        plaintext = "Hello, World!"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt_string(plaintext, key)
            decrypted = encryptor.decrypt_string(ciphertext, key)
        assert decrypted == plaintext

    def test_encrypt_string_unicode(self, encryptor, key):
        """Test encryption of unicode strings."""
        plaintext = "Héllo, 世界! 🌍"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt_string(plaintext, key)
            decrypted = encryptor.decrypt_string(ciphertext, key)
        assert decrypted == plaintext

    def test_encrypt_string_empty(self, encryptor, key):
        """Test encryption of empty string."""
        plaintext = ""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ciphertext = encryptor.encrypt_string(plaintext, key)
            decrypted = encryptor.decrypt_string(ciphertext, key)
        assert decrypted == plaintext


# ==============================================================================
# File Encryption Tests
# ==============================================================================

@pytest.mark.crypto
class TestFileEncryption:
    """Tests for file encryption."""

    @pytest.fixture
    def encryptor(self):
        """Create encryptor."""
        return Encryptor()

    @pytest.fixture
    def key(self):
        """Generate key."""
        return os.urandom(32)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_encrypt_decrypt_file(self, encryptor, key, temp_dir):
        """Test file encryption roundtrip."""
        # Create input file
        input_file = temp_dir / "plaintext.txt"
        input_file.write_bytes(b"Secret file content")

        encrypted_file = temp_dir / "encrypted.enc"
        decrypted_file = temp_dir / "decrypted.txt"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            # Encrypt
            assert encryptor.encrypt_file(str(input_file), str(encrypted_file), key)
            assert encrypted_file.exists()

            # Decrypt
            assert encryptor.decrypt_file(str(encrypted_file), str(decrypted_file), key)
        assert decrypted_file.read_bytes() == input_file.read_bytes()

    def test_encrypt_file_not_found(self, encryptor, key, temp_dir):
        """Test encryption of nonexistent file raises error."""
        with pytest.raises(EncryptionError):
            encryptor.encrypt_file(
                str(temp_dir / "nonexistent.txt"),
                str(temp_dir / "output.enc"),
                key
            )

    def test_decrypt_file_corrupted(self, encryptor, key, temp_dir):
        """Test decryption of corrupted file raises error."""
        corrupted_file = temp_dir / "corrupted.enc"
        corrupted_file.write_bytes(b"corrupted data")

        with pytest.raises(EncryptionError):
            encryptor.decrypt_file(
                str(corrupted_file),
                str(temp_dir / "output.txt"),
                key
            )


# ==============================================================================
# Hashing Tests
# ==============================================================================

@pytest.mark.crypto
class TestHashing:
    """Tests for hashing functions."""

    def test_hash_sha256(self):
        """Test SHA-256 hashing."""
        data = b"test data"
        hash_value = Encryptor.hash_data(data, "sha256")
        assert len(hash_value) == 64
        # Verify deterministic
        assert Encryptor.hash_data(data, "sha256") == hash_value

    def test_hash_sha512(self):
        """Test SHA-512 hashing."""
        data = b"test data"
        hash_value = Encryptor.hash_data(data, "sha512")
        assert len(hash_value) == 128

    def test_hash_sha384(self):
        """Test SHA-384 hashing."""
        data = b"test data"
        hash_value = Encryptor.hash_data(data, "sha384")
        assert len(hash_value) == 96

    def test_hash_md5(self):
        """Test MD5 hashing."""
        data = b"test data"
        hash_value = Encryptor.hash_data(data, "md5")
        assert len(hash_value) == 32

    def test_hash_invalid_algorithm(self):
        """Test hashing with invalid algorithm raises error."""
        with pytest.raises(ValueError):
            Encryptor.hash_data(b"data", "invalid")

    def test_hash_different_data(self):
        """Test that different data produces different hashes."""
        hash1 = Encryptor.hash_data(b"data1", "sha256")
        hash2 = Encryptor.hash_data(b"data2", "sha256")
        assert hash1 != hash2
