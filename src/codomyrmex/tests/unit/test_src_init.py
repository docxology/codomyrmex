import src

import codomyrmex


def test_get_source_version():
    """Test get_source_version function."""
    assert src.get_source_version() == src.__version__


def test_get_main_package_info():
    """Test get_main_package_info function."""
    info = src.get_main_package_info()
    assert isinstance(info, dict)
    assert info["name"] == "codomyrmex"
    assert info["version"] == codomyrmex.__version__
    assert info["description"] == "Core Codomyrmex functionality and modules"
    assert isinstance(info["modules"], list)


def test_get_template_info():
    """Test get_template_info function."""
    info = src.get_template_info()
    assert isinstance(info, dict)
    assert info["name"] == "module_template"
    assert info["location"] == "codomyrmex/module_template/"
    assert "components" in info
    assert isinstance(info["components"], list)
