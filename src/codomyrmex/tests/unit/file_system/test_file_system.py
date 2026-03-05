"""Comprehensive unit tests for the file_system module — Zero-Mock compliant.

Covers: FileSystemManager CRUD operations (create_file, read_file, append_to_file,
delete), directory management (create_directory, list_dir), metadata (get_info),
search (find_files, find_duplicates), hashing (get_hash), disk usage
(get_disk_usage), convenience factory (create_file_system_manager), and
edge cases. All tests use tempfile.TemporaryDirectory for isolation.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from codomyrmex.file_system import FileSystemManager, create_file_system_manager

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def fs():
    """Provide a FileSystemManager instance."""
    return FileSystemManager()


@pytest.fixture
def td():
    """Provide an isolated temporary directory that is cleaned up after."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ==============================================================================
# 1. create_file
# ==============================================================================


@pytest.mark.unit
class TestCreateFile:
    def test_creates_file_with_content(self, fs, td):
        path = td / "hello.txt"
        result = fs.create_file(path, "hello world")
        assert result == path
        assert path.exists()
        assert path.is_file()
        assert path.read_text(encoding="utf-8") == "hello world"

    def test_creates_empty_file(self, fs, td):
        path = td / "empty.txt"
        fs.create_file(path)
        assert path.exists()
        assert path.read_text(encoding="utf-8") == ""

    def test_creates_parent_directories(self, fs, td):
        path = td / "a" / "b" / "c" / "deep.txt"
        fs.create_file(path, "deep")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "deep"

    def test_overwrite_true_replaces_content(self, fs, td):
        path = td / "overwrite.txt"
        fs.create_file(path, "original")
        fs.create_file(path, "replaced", overwrite=True)
        assert path.read_text(encoding="utf-8") == "replaced"

    def test_overwrite_false_raises_if_exists(self, fs, td):
        path = td / "exists.txt"
        fs.create_file(path, "first")
        with pytest.raises(FileExistsError):
            fs.create_file(path, "second", overwrite=False)

    def test_unicode_content(self, fs, td):
        path = td / "unicode.txt"
        text = "cafe\u0301 \u4e16\u754c \U0001f30d"
        fs.create_file(path, text)
        assert fs.read_file(path) == text

    def test_multiline_content(self, fs, td):
        path = td / "multiline.txt"
        text = "line1\nline2\nline3\n"
        fs.create_file(path, text)
        assert fs.read_file(path) == text

    def test_returns_path_object(self, fs, td):
        result = fs.create_file(td / "ret.txt", "x")
        assert isinstance(result, Path)

    def test_string_path_accepted(self, fs, td):
        path = str(td / "strpath.txt")
        result = fs.create_file(path, "str path test")
        assert isinstance(result, Path)
        assert result.read_text(encoding="utf-8") == "str path test"


# ==============================================================================
# 2. read_file
# ==============================================================================


@pytest.mark.unit
class TestReadFile:
    def test_reads_content(self, fs, td):
        path = td / "read.txt"
        path.write_text("content here", encoding="utf-8")
        assert fs.read_file(path) == "content here"

    def test_nonexistent_raises(self, fs, td):
        with pytest.raises(FileNotFoundError):
            fs.read_file(td / "nonexistent.txt")

    def test_directory_raises(self, fs, td):
        subdir = td / "adir"
        subdir.mkdir()
        with pytest.raises(FileNotFoundError):
            fs.read_file(subdir)

    def test_empty_file(self, fs, td):
        path = td / "empty.txt"
        path.write_text("", encoding="utf-8")
        assert fs.read_file(path) == ""

    def test_string_path_accepted(self, fs, td):
        path = td / "strread.txt"
        path.write_text("str test", encoding="utf-8")
        assert fs.read_file(str(path)) == "str test"


# ==============================================================================
# 3. append_to_file
# ==============================================================================


@pytest.mark.unit
class TestAppendToFile:
    def test_appends_content(self, fs, td):
        path = td / "append.txt"
        fs.create_file(path, "base ")
        fs.append_to_file(path, "appended")
        assert fs.read_file(path) == "base appended"

    def test_multiple_appends(self, fs, td):
        path = td / "multi.txt"
        fs.create_file(path, "")
        for i in range(5):
            fs.append_to_file(path, f"{i}")
        assert fs.read_file(path) == "01234"

    def test_returns_path(self, fs, td):
        path = td / "ret.txt"
        fs.create_file(path, "")
        result = fs.append_to_file(path, "data")
        assert isinstance(result, Path)

    def test_append_newlines(self, fs, td):
        path = td / "newlines.txt"
        fs.create_file(path, "line1\n")
        fs.append_to_file(path, "line2\n")
        content = fs.read_file(path)
        assert content == "line1\nline2\n"
        assert content.count("\n") == 2


# ==============================================================================
# 4. delete
# ==============================================================================


@pytest.mark.unit
class TestDelete:
    def test_delete_file(self, fs, td):
        path = td / "del.txt"
        fs.create_file(path, "delete me")
        assert fs.delete(path) is True
        assert not path.exists()

    def test_delete_nonexistent_returns_false(self, fs, td):
        assert fs.delete(td / "nonexistent.txt") is False

    def test_delete_empty_dir(self, fs, td):
        subdir = td / "emptydir"
        subdir.mkdir()
        assert fs.delete(subdir) is True
        assert not subdir.exists()

    def test_delete_nonempty_dir_non_recursive_raises(self, fs, td):
        subdir = td / "nonempty"
        subdir.mkdir()
        (subdir / "file.txt").write_text("x", encoding="utf-8")
        with pytest.raises(OSError):
            fs.delete(subdir, recursive=False)

    def test_delete_nonempty_dir_recursive(self, fs, td):
        subdir = td / "rec"
        subdir.mkdir()
        (subdir / "nested").mkdir()
        (subdir / "nested" / "deep.txt").write_text("deep", encoding="utf-8")
        assert fs.delete(subdir, recursive=True) is True
        assert not subdir.exists()

    def test_delete_returns_true_on_success(self, fs, td):
        path = td / "check.txt"
        fs.create_file(path, "x")
        assert fs.delete(path) is True


# ==============================================================================
# 5. create_directory
# ==============================================================================


@pytest.mark.unit
class TestCreateDirectory:
    def test_creates_directory(self, fs, td):
        path = td / "newdir"
        result = fs.create_directory(path)
        assert result == path
        assert path.is_dir()

    def test_creates_nested_directories(self, fs, td):
        path = td / "a" / "b" / "c"
        fs.create_directory(path)
        assert path.is_dir()

    def test_exist_ok_true_no_error(self, fs, td):
        path = td / "existing"
        path.mkdir()
        result = fs.create_directory(path, exist_ok=True)
        assert result == path

    def test_exist_ok_false_raises(self, fs, td):
        path = td / "exists"
        path.mkdir()
        with pytest.raises(FileExistsError):
            fs.create_directory(path, exist_ok=False)

    def test_returns_path_object(self, fs, td):
        result = fs.create_directory(td / "retdir")
        assert isinstance(result, Path)


# ==============================================================================
# 6. list_dir
# ==============================================================================


@pytest.mark.unit
class TestListDir:
    def test_non_recursive(self, fs, td):
        fs.create_file(td / "a.txt", "a")
        fs.create_file(td / "b.txt", "b")
        fs.create_directory(td / "sub")
        items = fs.list_dir(td, recursive=False)
        names = {p.name for p in items}
        assert "a.txt" in names
        assert "b.txt" in names
        assert "sub" in names
        assert len(items) == 3

    def test_recursive(self, fs, td):
        fs.create_file(td / "top.txt", "t")
        fs.create_directory(td / "sub")
        fs.create_file(td / "sub" / "nested.txt", "n")
        items = fs.list_dir(td, recursive=True)
        names = {p.name for p in items}
        assert "top.txt" in names
        assert "sub" in names
        assert "nested.txt" in names

    def test_empty_directory(self, fs, td):
        subdir = td / "empty"
        subdir.mkdir()
        items = fs.list_dir(subdir)
        assert items == []

    def test_returns_list_of_paths(self, fs, td):
        fs.create_file(td / "item.txt", "")
        items = fs.list_dir(td)
        assert isinstance(items, list)
        assert all(isinstance(p, Path) for p in items)

    def test_string_path_accepted(self, fs, td):
        fs.create_file(td / "x.txt", "")
        items = fs.list_dir(str(td))
        assert len(items) >= 1


# ==============================================================================
# 7. get_info
# ==============================================================================


@pytest.mark.unit
class TestGetInfo:
    def test_file_info(self, fs, td):
        path = td / "info.txt"
        content = "some content"
        fs.create_file(path, content)
        info = fs.get_info(path)
        assert info["name"] == "info.txt"
        assert info["size"] == len(content.encode("utf-8"))
        assert info["is_dir"] is False
        assert info["extension"] == ".txt"
        assert isinstance(info["created_at"], datetime)
        assert isinstance(info["modified_at"], datetime)
        assert "permissions" in info

    def test_directory_info(self, fs, td):
        subdir = td / "mydir"
        subdir.mkdir()
        info = fs.get_info(subdir)
        assert info["name"] == "mydir"
        assert info["is_dir"] is True
        assert info["extension"] == ""

    def test_nonexistent_raises(self, fs, td):
        with pytest.raises(FileNotFoundError):
            fs.get_info(td / "nonexistent")

    def test_absolute_path_in_info(self, fs, td):
        path = td / "abs.txt"
        fs.create_file(path, "x")
        info = fs.get_info(path)
        assert os.path.isabs(info["path"])

    def test_no_extension_file(self, fs, td):
        path = td / "Makefile"
        fs.create_file(path, "all: build")
        info = fs.get_info(path)
        assert info["extension"] == ""

    def test_dotfile(self, fs, td):
        path = td / ".hidden"
        fs.create_file(path, "secret")
        info = fs.get_info(path)
        assert info["name"] == ".hidden"

    def test_permissions_is_string(self, fs, td):
        path = td / "perms.txt"
        fs.create_file(path, "x")
        info = fs.get_info(path)
        assert isinstance(info["permissions"], str)
        assert len(info["permissions"]) == 3


# ==============================================================================
# 8. find_files
# ==============================================================================


@pytest.mark.unit
class TestFindFiles:
    def test_find_by_extension(self, fs, td):
        fs.create_file(td / "a.py", "")
        fs.create_file(td / "b.txt", "")
        fs.create_directory(td / "sub")
        fs.create_file(td / "sub" / "c.py", "")
        results = fs.find_files("*.py", td)
        assert len(results) == 2
        assert all(p.suffix == ".py" for p in results)

    def test_find_no_matches(self, fs, td):
        fs.create_file(td / "a.txt", "")
        results = fs.find_files("*.xyz", td)
        assert results == []

    def test_find_all_files(self, fs, td):
        fs.create_file(td / "x.txt", "")
        fs.create_file(td / "y.log", "")
        results = fs.find_files("*", td)
        # Should find at least the 2 files
        assert len(results) >= 2

    def test_find_specific_name(self, fs, td):
        fs.create_file(td / "target.txt", "found")
        fs.create_file(td / "other.txt", "not this")
        results = fs.find_files("target.txt", td)
        assert len(results) == 1
        assert results[0].name == "target.txt"

    def test_returns_list_of_paths(self, fs, td):
        fs.create_file(td / "f.txt", "")
        results = fs.find_files("*.txt", td)
        assert isinstance(results, list)
        assert all(isinstance(p, Path) for p in results)


# ==============================================================================
# 9. get_hash
# ==============================================================================


@pytest.mark.unit
class TestGetHash:
    def test_sha256_default(self, fs, td):
        path = td / "hash.txt"
        path.write_bytes(b"test data")
        h = fs.get_hash(path)
        import hashlib

        expected = hashlib.sha256(b"test data").hexdigest()
        assert h == expected

    def test_sha512(self, fs, td):
        path = td / "hash512.txt"
        path.write_bytes(b"data")
        h = fs.get_hash(path, algorithm="sha512")
        import hashlib

        expected = hashlib.sha512(b"data").hexdigest()
        assert h == expected

    def test_md5(self, fs, td):
        path = td / "hashmd5.txt"
        path.write_bytes(b"data")
        h = fs.get_hash(path, algorithm="md5")
        import hashlib

        expected = hashlib.md5(b"data").hexdigest()
        assert h == expected

    def test_deterministic(self, fs, td):
        path = td / "det.txt"
        path.write_bytes(b"consistent")
        h1 = fs.get_hash(path)
        h2 = fs.get_hash(path)
        assert h1 == h2

    def test_different_content_different_hash(self, fs, td):
        p1 = td / "f1.txt"
        p2 = td / "f2.txt"
        p1.write_bytes(b"content A")
        p2.write_bytes(b"content B")
        assert fs.get_hash(p1) != fs.get_hash(p2)

    def test_directory_raises(self, fs, td):
        subdir = td / "adir"
        subdir.mkdir()
        with pytest.raises(ValueError, match="Not a file"):
            fs.get_hash(subdir)

    def test_empty_file(self, fs, td):
        path = td / "empty.txt"
        path.write_bytes(b"")
        h = fs.get_hash(path)
        import hashlib

        assert h == hashlib.sha256(b"").hexdigest()

    def test_large_file(self, fs, td):
        """Hash computation works for files larger than the 4096-byte chunk."""
        path = td / "large.bin"
        data = os.urandom(4096 * 5)  # 20 KB
        path.write_bytes(data)
        h = fs.get_hash(path)
        import hashlib

        assert h == hashlib.sha256(data).hexdigest()


# ==============================================================================
# 10. find_duplicates
# ==============================================================================


@pytest.mark.unit
class TestFindDuplicates:
    def test_finds_duplicates(self, fs, td):
        content = "duplicate content"
        fs.create_file(td / "orig.txt", content)
        fs.create_file(td / "copy.txt", content)
        fs.create_file(td / "unique.txt", "different")
        dupes = fs.find_duplicates(td)
        assert len(dupes) == 1
        paths = next(iter(dupes.values()))
        assert len(paths) == 2
        names = {p.name for p in paths}
        assert "orig.txt" in names
        assert "copy.txt" in names

    def test_no_duplicates(self, fs, td):
        fs.create_file(td / "a.txt", "alpha")
        fs.create_file(td / "b.txt", "bravo")
        dupes = fs.find_duplicates(td)
        assert dupes == {}

    def test_empty_directory(self, fs, td):
        subdir = td / "empty"
        subdir.mkdir()
        dupes = fs.find_duplicates(subdir)
        assert dupes == {}

    def test_multiple_duplicate_groups(self, fs, td):
        fs.create_file(td / "a1.txt", "alpha")
        fs.create_file(td / "a2.txt", "alpha")
        fs.create_file(td / "b1.txt", "bravo")
        fs.create_file(td / "b2.txt", "bravo")
        fs.create_file(td / "unique.txt", "unique")
        dupes = fs.find_duplicates(td)
        assert len(dupes) == 2

    def test_nested_duplicates(self, fs, td):
        fs.create_file(td / "top.txt", "same")
        fs.create_directory(td / "sub")
        fs.create_file(td / "sub" / "nested.txt", "same")
        dupes = fs.find_duplicates(td)
        assert len(dupes) == 1

    def test_three_copies(self, fs, td):
        for name in ("c1.txt", "c2.txt", "c3.txt"):
            fs.create_file(td / name, "triple")
        dupes = fs.find_duplicates(td)
        assert len(dupes) == 1
        paths = next(iter(dupes.values()))
        assert len(paths) == 3


# ==============================================================================
# 11. get_disk_usage
# ==============================================================================


@pytest.mark.unit
class TestGetDiskUsage:
    def test_returns_expected_keys(self, fs, td):
        usage = fs.get_disk_usage(td)
        assert "total" in usage
        assert "used" in usage
        assert "free" in usage
        assert "percent" in usage

    def test_total_positive(self, fs, td):
        usage = fs.get_disk_usage(td)
        assert usage["total"] > 0

    def test_percent_in_range(self, fs, td):
        usage = fs.get_disk_usage(td)
        assert 0 <= usage["percent"] <= 100

    def test_total_equals_used_plus_free(self, fs, td):
        usage = fs.get_disk_usage(td)
        # Allow for minor rounding or concurrent changes
        assert abs(usage["total"] - (usage["used"] + usage["free"])) < 1024 * 1024

    def test_nonexistent_path_falls_back(self, fs, td):
        """get_disk_usage with nonexistent path uses '.' as fallback."""
        usage = fs.get_disk_usage(td / "nonexistent_sub")
        assert usage["total"] > 0

    def test_string_path_accepted(self, fs, td):
        usage = fs.get_disk_usage(str(td))
        assert usage["total"] > 0


# ==============================================================================
# 12. create_file_system_manager Factory
# ==============================================================================


@pytest.mark.unit
class TestFactory:
    def test_creates_instance(self):
        fs = create_file_system_manager()
        assert isinstance(fs, FileSystemManager)

    def test_default_config(self):
        fs = create_file_system_manager()
        assert fs.config == {}

    def test_custom_config(self):
        config = {"root": "/tmp", "max_size": 1024}
        fs = create_file_system_manager(config)
        assert fs.config == config

    def test_none_config(self):
        fs = create_file_system_manager(None)
        assert fs.config == {}


# ==============================================================================
# 13. FileSystemManager Constructor
# ==============================================================================


@pytest.mark.unit
class TestFileSystemManagerInit:
    def test_default_config(self):
        fs = FileSystemManager()
        assert fs.config == {}

    def test_custom_config(self):
        config = {"key": "value"}
        fs = FileSystemManager(config=config)
        assert fs.config == config

    def test_config_is_stored_not_copied(self):
        config = {"mutable": True}
        fs = FileSystemManager(config=config)
        assert fs.config is config


# ==============================================================================
# 14. Edge Cases
# ==============================================================================


@pytest.mark.unit
class TestEdgeCases:
    def test_create_file_with_special_chars_in_name(self, fs, td):
        path = td / "file with spaces.txt"
        fs.create_file(path, "spaces")
        assert fs.read_file(path) == "spaces"

    def test_create_file_with_long_name(self, fs, td):
        # Most filesystems support up to 255 chars
        name = "x" * 200 + ".txt"
        path = td / name
        fs.create_file(path, "long name")
        assert fs.read_file(path) == "long name"

    def test_large_file_content(self, fs, td):
        path = td / "large.txt"
        content = "A" * 100_000
        fs.create_file(path, content)
        assert len(fs.read_file(path)) == 100_000

    def test_create_read_delete_cycle(self, fs, td):
        """Full CRUD lifecycle."""
        path = td / "lifecycle.txt"
        fs.create_file(path, "born")
        assert fs.read_file(path) == "born"
        fs.append_to_file(path, " grown")
        assert fs.read_file(path) == "born grown"
        assert fs.delete(path) is True
        assert not path.exists()

    def test_get_info_on_symlink_target(self, fs, td):
        """get_info resolves to the file."""
        real = td / "real.txt"
        fs.create_file(real, "real content")
        link = td / "link.txt"
        link.symlink_to(real)
        info = fs.get_info(link)
        assert info["size"] == len("real content")

    def test_find_files_with_dot_pattern(self, fs, td):
        fs.create_file(td / ".gitignore", "*.pyc")
        results = fs.find_files(".gitignore", td)
        assert len(results) == 1

    def test_list_dir_with_mixed_types(self, fs, td):
        fs.create_file(td / "file.txt", "f")
        fs.create_directory(td / "dir")
        link = td / "link.txt"
        link.symlink_to(td / "file.txt")
        items = fs.list_dir(td)
        names = {p.name for p in items}
        assert "file.txt" in names
        assert "dir" in names
        assert "link.txt" in names

    def test_overwrite_with_shorter_content(self, fs, td):
        """Overwrite should fully replace, not leave trailing bytes."""
        path = td / "shrink.txt"
        fs.create_file(path, "long content here")
        fs.create_file(path, "short", overwrite=True)
        assert fs.read_file(path) == "short"

    def test_hash_binary_file(self, fs, td):
        path = td / "binary.bin"
        data = bytes(range(256))
        path.write_bytes(data)
        import hashlib

        expected = hashlib.sha256(data).hexdigest()
        assert fs.get_hash(path) == expected

    def test_find_duplicates_ignores_directories(self, fs, td):
        """find_duplicates should only consider files, not directories."""
        fs.create_file(td / "a.txt", "dup")
        fs.create_file(td / "b.txt", "dup")
        fs.create_directory(td / "subdir")
        dupes = fs.find_duplicates(td)
        assert len(dupes) == 1
        for paths in dupes.values():
            assert all(p.is_file() for p in paths)
