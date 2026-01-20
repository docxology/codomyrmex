"""Unit tests for the encryption module."""

import unittest
from codomyrmex.encryption import AESGCMEncryptor, SecureDataContainer, generate_aes_key

class TestEncryption(unittest.TestCase):
    def test_aes_gcm_encryption(self):
        key = generate_aes_key()
        encryptor = AESGCMEncryptor(key)
        data = b"secret data"
        aad = b"associated data"
        ciphertext = encryptor.encrypt(data, aad)
        plaintext = encryptor.decrypt(ciphertext, aad)
        self.assertEqual(data, plaintext)

    def test_secure_data_container(self):
        key = generate_aes_key()
        container = SecureDataContainer(key)
        data = {"user": "admin", "id": 123}
        packed = container.pack(data)
        unpacked = container.unpack(packed)
        self.assertEqual(data, unpacked["data"])
