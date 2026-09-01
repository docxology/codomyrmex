import src


def test_get_main_package_info() -> None:
    info = src.get_main_package_info()
    assert isinstance(info, dict)
    assert info["name"] == "codomyrmex"
    assert "version" in info
    assert isinstance(info["version"], str)
    assert "modules" in info
    assert isinstance(info["modules"], list)
    assert info["description"] == "Core Codomyrmex functionality and modules"
