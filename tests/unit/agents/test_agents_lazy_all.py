"""Every public name in codomyrmex.agents.__all__ must resolve (PEP 562 lazy loading)."""

import codomyrmex.agents as agents_pkg


def test_all_names_resolve() -> None:
    missing = []
    for name in agents_pkg.__all__:
        try:
            getattr(agents_pkg, name)
        except (AttributeError, ImportError) as exc:
            missing.append(f"{name}: {exc!r}")
    assert not missing, f"unresolvable __all__ entries: {missing}"


def test_lazy_import_does_not_load_framework_subpackages() -> None:
    import sys

    for mod in list(sys.modules):
        if mod.startswith("codomyrmex.agents."):
            del sys.modules[mod]
    import codomyrmex.agents  # fresh module attributes

    assert "codomyrmex.agents.core" not in sys.modules
    assert "codomyrmex.agents.claude" not in sys.modules


def test_unknown_attribute_raises_attribute_error() -> None:
    try:
        agents_pkg.definitely_not_a_real_name  # type: ignore[attr-defined]  # noqa: B018
    except AttributeError:
        pass
    else:
        raise AssertionError("expected AttributeError for unknown attribute")
