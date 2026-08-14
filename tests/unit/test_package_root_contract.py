import importlib.metadata

import codomyrmex


def test_package_version_matches_installed_metadata() -> None:
    metadata_version = importlib.metadata.version("codomyrmex")

    assert codomyrmex.__version__ == metadata_version
    assert codomyrmex.get_version() == metadata_version


def test_colony_kernel_is_public_root_lazy_export() -> None:
    assert "colony_kernel" in codomyrmex.list_modules()
    assert "colony_kernel" in codomyrmex.__all__
    assert codomyrmex.colony_kernel.__name__ == "codomyrmex.colony_kernel"


def test_module_navigation_excludes_loose_support_files_and_includes_packages() -> None:
    modules = codomyrmex.list_modules()
    assert modules == sorted(modules)
    assert "conftest" not in modules
    for name in ("defense", "embodiment", "manuscript"):
        assert name in modules
        assert name in codomyrmex.__all__
        assert getattr(codomyrmex, name).__name__ == f"codomyrmex.{name}"
