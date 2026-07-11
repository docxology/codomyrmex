"""Zero-mock tests for wallet encrypted storage module.

Tests EncryptedStore and EncryptedEntry using real in-memory crypto logic.
No external dependencies — pure Python standard library.
"""

from codomyrmex.wallet.security.encrypted_storage import EncryptedEntry, EncryptedStore


class TestEncryptedEntry:
    """Tests for EncryptedEntry dataclass."""

    def test_entry_construction(self):
        entry = EncryptedEntry(
            key="mykey",
            ciphertext="abc123",
            nonce="nonce456",
            tag="tag789",
            created_at=1000.0,
            rotated_at=1001.0,
        )
        assert entry.key == "mykey"
        assert entry.ciphertext == "abc123"
        assert entry.nonce == "nonce456"
        assert entry.tag == "tag789"
        assert entry.created_at == 1000.0
        assert entry.rotated_at == 1001.0

    def test_entry_to_dict(self):
        entry = EncryptedEntry(
            key="apikey",
            ciphertext="enc_data",
            nonce="nonce_val",
            tag="auth_tag",
            created_at=500.0,
            rotated_at=600.0,
        )
        d = entry.to_dict()
        assert d["key"] == "apikey"
        assert d["ciphertext"] == "enc_data"
        assert d["nonce"] == "nonce_val"
        assert d["tag"] == "auth_tag"
        assert d["created_at"] == 500.0
        assert d["rotated_at"] == 600.0

    def test_entry_from_dict_roundtrip(self):
        original = EncryptedEntry(
            key="test_key",
            ciphertext="ct",
            nonce="n",
            tag="t",
            created_at=1.0,
            rotated_at=2.0,
        )
        restored = EncryptedEntry.from_dict(original.to_dict())
        assert restored.key == original.key
        assert restored.ciphertext == original.ciphertext
        assert restored.nonce == original.nonce
        assert restored.tag == original.tag
        assert restored.created_at == original.created_at
        assert restored.rotated_at == original.rotated_at

    def test_entry_default_timestamps(self):
        entry = EncryptedEntry(key="k", ciphertext="c", nonce="n", tag="t")
        assert entry.created_at == 0.0
        assert entry.rotated_at == 0.0


class TestEncryptedStoreInit:
    """Tests for EncryptedStore initialization."""

    def test_init_with_no_key_generates_random_key(self):
        store1 = EncryptedStore()
        store2 = EncryptedStore()
        # Two stores with random keys will produce different ciphertexts
        entry1 = store1.put("k", "v")
        entry2 = store2.put("k", "v")
        # They encrypt the same value but with different keys
        assert entry1.ciphertext != entry2.ciphertext

    def test_init_with_explicit_key(self):
        key = b"a" * 32
        store = EncryptedStore(master_key=key)
        assert store._master_key == key

    def test_initial_store_is_empty(self):
        store = EncryptedStore()
        assert store.size == 0
        assert store.list_keys() == []


class TestEncryptedStorePut:
    """Tests for EncryptedStore.put method."""

    def test_put_returns_encrypted_entry(self):
        store = EncryptedStore(master_key=b"k" * 32)
        entry = store.put("api_key", "secret_value")
        assert isinstance(entry, EncryptedEntry)
        assert entry.key == "api_key"
        assert entry.ciphertext != "secret_value"
        assert entry.nonce != ""
        assert entry.tag != ""

    def test_put_increases_size(self):
        store = EncryptedStore(master_key=b"k" * 32)
        assert store.size == 0
        store.put("k1", "v1")
        assert store.size == 1
        store.put("k2", "v2")
        assert store.size == 2

    def test_put_creates_timestamps(self):
        store = EncryptedStore(master_key=b"k" * 32)
        entry = store.put("key", "value")
        assert entry.created_at > 0
        assert entry.rotated_at > 0

    def test_put_overwrites_existing_key(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("key", "first_value")
        store.put("key", "second_value")
        # Size stays at 1 since same key
        assert store.size == 1
        # But we can decrypt the latest value
        assert store.get("key") == "second_value"

    def test_put_empty_string(self):
        store = EncryptedStore(master_key=b"k" * 32)
        entry = store.put("empty", "")
        assert entry.key == "empty"
        retrieved = store.get("empty")
        assert retrieved == ""

    def test_put_unicode_value(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("unicode", "Hello 世界 🌍")
        result = store.get("unicode")
        assert result == "Hello 世界 🌍"


class TestEncryptedStoreGet:
    """Tests for EncryptedStore.get method."""

    def test_get_decrypts_value_correctly(self):
        store = EncryptedStore(master_key=b"testkey" * 5)
        store.put("password", "my-secret-password-123")
        result = store.get("password")
        assert result == "my-secret-password-123"

    def test_get_returns_none_for_missing_key(self):
        store = EncryptedStore(master_key=b"k" * 32)
        result = store.get("nonexistent_key")
        assert result is None

    def test_get_multiple_values_independently(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("key1", "value1")
        store.put("key2", "value2")
        store.put("key3", "value3")
        assert store.get("key1") == "value1"
        assert store.get("key2") == "value2"
        assert store.get("key3") == "value3"

    def test_get_after_multiple_puts_same_key(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("mykey", "original")
        store.put("mykey", "updated")
        assert store.get("mykey") == "updated"

    def test_get_long_value(self):
        store = EncryptedStore(master_key=b"k" * 32)
        long_value = "x" * 1000
        store.put("long", long_value)
        result = store.get("long")
        assert result == long_value


class TestEncryptedStoreDelete:
    """Tests for EncryptedStore.delete method."""

    def test_delete_existing_key_returns_true(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("to_delete", "val")
        result = store.delete("to_delete")
        assert result is True

    def test_delete_removes_from_store(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("to_delete", "val")
        store.delete("to_delete")
        assert store.size == 0
        assert store.get("to_delete") is None

    def test_delete_nonexistent_key_returns_false(self):
        store = EncryptedStore(master_key=b"k" * 32)
        result = store.delete("does_not_exist")
        assert result is False

    def test_delete_does_not_affect_other_keys(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("keep", "keep_val")
        store.put("remove", "remove_val")
        store.delete("remove")
        assert store.get("keep") == "keep_val"
        assert store.size == 1


class TestEncryptedStoreHas:
    """Tests for EncryptedStore.has method."""

    def test_has_returns_true_for_existing_key(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("existing", "value")
        assert store.has("existing") is True

    def test_has_returns_false_for_missing_key(self):
        store = EncryptedStore(master_key=b"k" * 32)
        assert store.has("missing") is False

    def test_has_returns_false_after_delete(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("key", "val")
        store.delete("key")
        assert store.has("key") is False


class TestEncryptedStoreListKeys:
    """Tests for EncryptedStore.list_keys method."""

    def test_list_keys_empty_store(self):
        store = EncryptedStore(master_key=b"k" * 32)
        assert store.list_keys() == []

    def test_list_keys_returns_sorted_keys(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("charlie", "v")
        store.put("alpha", "v")
        store.put("beta", "v")
        keys = store.list_keys()
        assert keys == ["alpha", "beta", "charlie"]

    def test_list_keys_excludes_deleted(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("a", "va")
        store.put("b", "vb")
        store.delete("a")
        assert store.list_keys() == ["b"]


class TestEncryptedStoreMasterKeyRotation:
    """Tests for EncryptedStore.rotate_master_key method."""

    def test_rotate_master_key_reencrypts_all(self):
        old_key = b"old_key_" * 4
        new_key = b"new_key_" * 4
        store = EncryptedStore(master_key=old_key)
        store.put("cred1", "password1")
        store.put("cred2", "password2")
        count = store.rotate_master_key(new_key)
        assert count == 2
        # Values still accessible after rotation
        assert store.get("cred1") == "password1"
        assert store.get("cred2") == "password2"

    def test_rotate_master_key_empty_store(self):
        store = EncryptedStore(master_key=b"k" * 32)
        count = store.rotate_master_key(b"new" * 11)
        assert count == 0

    def test_rotate_master_key_updates_master_key(self):
        old_key = b"old" * 11
        new_key = b"new" * 11
        store = EncryptedStore(master_key=old_key)
        store.rotate_master_key(new_key)
        assert store._master_key == new_key

    def test_rotate_master_key_old_entries_replaced(self):
        old_key = b"old_key_" * 4
        new_key = b"new_key_" * 4
        store = EncryptedStore(master_key=old_key)
        store.put("secret", "my_value")
        old_entry = store._entries.get("secret")
        old_ciphertext = old_entry.ciphertext if old_entry else None
        store.rotate_master_key(new_key)
        new_entry = store._entries.get("secret")
        # The ciphertext should differ since the key changed
        assert new_entry is not None
        assert new_entry.ciphertext != old_ciphertext


class TestEncryptedStoreIntegrity:
    """Tests for tamper detection."""

    def test_tampered_ciphertext_returns_none(self):
        store = EncryptedStore(master_key=b"k" * 32)
        store.put("key", "original_value")
        # Tamper with the ciphertext directly
        entry = store._entries["key"]
        import base64

        original_bytes = base64.b64decode(entry.ciphertext)
        tampered = bytes([original_bytes[0] ^ 0xFF]) + original_bytes[1:]
        entry.ciphertext = base64.b64encode(tampered).decode()
        # Integrity check should fail
        result = store.get("key")
        assert result is None

    def test_different_keys_produce_different_ciphertexts(self):
        store = EncryptedStore(master_key=b"k" * 32)
        entry1 = store.put("key1", "same_value")
        entry2 = store.put("key2", "same_value")
        # Different credential keys produce different ciphertexts (nonce differs)
        assert entry1.ciphertext != entry2.ciphertext
