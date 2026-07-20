import pytest
from src import get_main_package_info


def test_get_main_package_info():
    info = get_main_package_info()
    assert isinstance(info, dict)
    assert info["name"] == "codomyrmex"
    assert "version" in info
    assert "modules" in info
    assert isinstance(info["modules"], list)
    assert "description" in info
    assert info["description"] == "Core Codomyrmex functionality and modules"


def test_get_main_package_info_structure():
    info = get_main_package_info()

    expected_keys = {"name", "version", "modules", "description"}
    assert set(info.keys()) == expected_keys
