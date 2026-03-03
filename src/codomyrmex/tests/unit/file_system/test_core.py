"""
Unit tests for the File System module.

Strictly zero-mock, using a real temporary filesystem for all tests.
"""

import pytest

from codomyrmex.file_system.core import FileSystemManager, create_file_system_manager


@pytest.fixture
def fs_manager():
    """Fixture to provide a FileSystemManager instance."""
    return FileSystemManager()


def test_create_and_read_file(fs_manager, tmp_path):
    """Test file creation and reading."""
    file_path = tmp_path / "test_file.txt"
    content = "Test content for file creation."

    # Create file
    result_path = fs_manager.create_file(file_path, content)
    assert result_path.exists()
    assert result_path.is_file()

    # Read file
    read_content = fs_manager.read_file(file_path)
    assert read_content == content

    # Overwrite protection
    with pytest.raises(FileExistsError):
        fs_manager.create_file(file_path, "new content", overwrite=False)


def test_read_non_existent_file(fs_manager, tmp_path):
    """Test reading a file that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        fs_manager.read_file(tmp_path / "non_existent.txt")


def test_append_to_file(fs_manager, tmp_path):
    """Test appending content to a file."""
    file_path = tmp_path / "append_test.txt"
    initial_content = "Initial content\n"
    appended_content = "Appended line."

    fs_manager.create_file(file_path, initial_content)
    fs_manager.append_to_file(file_path, appended_content)

    final_content = fs_manager.read_file(file_path)
    assert final_content == initial_content + appended_content


def test_delete_file_and_dir(fs_manager, tmp_path):
    """Test file and directory deletion."""
    # Test file deletion
    file_path = tmp_path / "to_delete.txt"
    fs_manager.create_file(file_path, "Delete me")
    assert file_path.exists()

    fs_manager.delete(file_path)
    assert not file_path.exists()

    # Non-existent path
    assert fs_manager.delete(tmp_path / "non_existent") is False

    # Test directory deletion
    dir_path = tmp_path / "test_dir"
    fs_manager.create_directory(dir_path)
    fs_manager.create_file(dir_path / "nested.txt", "Nested")
    assert dir_path.exists()

    # Non-recursive should fail for non-empty dir
    with pytest.raises(OSError):
        fs_manager.delete(dir_path, recursive=False)

    # Recursive should work
    fs_manager.delete(dir_path, recursive=True)
    assert not dir_path.exists()


def test_list_dir(fs_manager, tmp_path):
    """Test listing directory contents."""
    dir_path = tmp_path / "list_test"
    fs_manager.create_directory(dir_path)
    fs_manager.create_file(dir_path / "file1.txt")
    fs_manager.create_file(dir_path / "file2.txt")
    fs_manager.create_directory(dir_path / "sub_dir")
    fs_manager.create_file(dir_path / "sub_dir" / "file3.txt")

    # Non-recursive listing
    contents = fs_manager.list_dir(dir_path, recursive=False)
    assert len(contents) == 3
    assert any(c.name == "file1.txt" for c in contents)
    assert any(c.name == "sub_dir" for c in contents)

    # Recursive listing
    recursive_contents = fs_manager.list_dir(dir_path, recursive=True)
    assert len(recursive_contents) == 4
    assert any(c.name == "file3.txt" for c in recursive_contents)


def test_get_info(fs_manager, tmp_path):
    """Test getting file metadata."""
    file_path = tmp_path / "info_test.txt"
    content = "Some content"
    fs_manager.create_file(file_path, content)

    info = fs_manager.get_info(file_path)
    assert info["name"] == "info_test.txt"
    assert info["size"] == len(content.encode("utf-8"))
    assert info["is_dir"] is False
    assert info["extension"] == ".txt"
    assert "created_at" in info
    assert "modified_at" in info

    with pytest.raises(FileNotFoundError):
        fs_manager.get_info(tmp_path / "non_existent.txt")


def test_find_files(fs_manager, tmp_path):
    """Test searching for files."""
    fs_manager.create_file(tmp_path / "test1.py")
    fs_manager.create_file(tmp_path / "test2.txt")
    fs_manager.create_directory(tmp_path / "sub")
    fs_manager.create_file(tmp_path / "sub" / "test3.py")

    python_files = fs_manager.find_files("*.py", tmp_path)
    assert len(python_files) == 2
    assert all(f.suffix == ".py" for f in python_files)


def test_find_duplicates(fs_manager, tmp_path):
    """Test finding duplicate files."""
    content = "Unique content for testing duplicates."
    fs_manager.create_file(tmp_path / "original.txt", content)
    fs_manager.create_file(tmp_path / "copy.txt", content)
    fs_manager.create_file(tmp_path / "different.txt", "Different content.")

    duplicates = fs_manager.find_duplicates(tmp_path)
    assert len(duplicates) == 1

    paths = list(duplicates.values())[0]
    assert len(paths) == 2
    assert any(p.name == "original.txt" for p in paths)
    assert any(p.name == "copy.txt" for p in paths)


def test_get_hash_errors(fs_manager, tmp_path):
    """Test hashing error cases."""
    dir_path = tmp_path / "some_dir"
    fs_manager.create_directory(dir_path)
    with pytest.raises(ValueError, match="Not a file"):
        fs_manager.get_hash(dir_path)


def test_disk_usage(fs_manager, tmp_path):
    """Test disk usage reporting."""
    usage = fs_manager.get_disk_usage(tmp_path)
    assert "total" in usage
    assert "used" in usage
    assert "free" in usage
    assert "percent" in usage
    assert usage["total"] > 0
    assert 0 <= usage["percent"] <= 100

    # Test with non-existent path (falls back to .)
    usage2 = fs_manager.get_disk_usage(tmp_path / "non_existent")
    assert usage2["total"] > 0


def test_create_file_system_manager():
    """Test convenience creator function."""
    fs = create_file_system_manager({"some": "config"})
    assert isinstance(fs, FileSystemManager)
    assert fs.config == {"some": "config"}
