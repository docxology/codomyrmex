import os
import sys

import _virtualenv


class _StubMagicMock:
    pass


def test_parse_config_files_filters_install_bases():
    class MockDist:
        def __init__(self):
            self.install_options = {
                "install_purelib": ("config_file", "/global/path/purelib"),
                "install_platlib": ("config_file", "/global/path/platlib"),
                "install_headers": ("config_file", "/global/path/headers"),
                "install_scripts": ("config_file", "/global/path/scripts"),
                "install_data": ("config_file", "/global/path/data"),
                "other_option": ("config_file", "some_value"),
            }

        def get_option_dict(self, command):
            if command == "install":
                return self.install_options
            return {}

    class MockDistribution:
        def parse_config_files(self, *args, **kwargs):
            return "original_result"

    dist_module = _StubMagicMock()
    dist_module.Distribution = MockDistribution

    # Apply the patch
    _virtualenv.patch_dist(dist_module)

    # Create an instance and call the patched method
    dist_instance = MockDist()
    result = dist_module.Distribution.parse_config_files(dist_instance)

    assert result == "original_result"

    # Check that hijack paths were popped
    assert "install_purelib" not in dist_instance.install_options
    assert "install_platlib" not in dist_instance.install_options
    assert "install_headers" not in dist_instance.install_options
    assert "install_scripts" not in dist_instance.install_options
    assert "install_data" not in dist_instance.install_options

    # Check that other options remain
    assert "other_option" in dist_instance.install_options
    assert dist_instance.install_options["other_option"] == (
        "config_file",
        "some_value",
    )


def test_parse_config_files_patches_prefix():
    class MockDist:
        def __init__(self):
            self.install_options = {"prefix": ("config_file", "/global/path/prefix")}

        def get_option_dict(self, command):
            if command == "install":
                return self.install_options
            return {}

    class MockDistribution:
        def parse_config_files(self, *args, **kwargs):
            return "original_result"

    dist_module = _StubMagicMock()
    dist_module.Distribution = MockDistribution

    # Apply the patch
    _virtualenv.patch_dist(dist_module)

    # Create an instance and call the patched method
    dist_instance = MockDist()
    dist_module.Distribution.parse_config_files(dist_instance)

    # Check that prefix was patched to point to the current environment prefix
    assert "prefix" in dist_instance.install_options
    assert (
        dist_instance.install_options["prefix"][0] == _virtualenv.VIRTUALENV_PATCH_FILE
    )
    assert dist_instance.install_options["prefix"][1] == os.path.abspath(sys.prefix)


def test_parse_config_files_no_install_options():
    class MockDist:
        def __init__(self):
            self.install_options = {}

        def get_option_dict(self, command):
            if command == "install":
                return self.install_options
            return {}

    class MockDistribution:
        def parse_config_files(self, *args, **kwargs):
            return "original_result"

    dist_module = _StubMagicMock()
    dist_module.Distribution = MockDistribution

    # Apply the patch
    _virtualenv.patch_dist(dist_module)

    # Create an instance and call the patched method
    dist_instance = MockDist()
    result = dist_module.Distribution.parse_config_files(dist_instance)

    assert result == "original_result"
    assert dist_instance.install_options == {}
