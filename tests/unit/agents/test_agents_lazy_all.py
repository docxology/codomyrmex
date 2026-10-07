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
    """Importing the package must not import framework subpackages.

    Checked in a fresh interpreter: deleting ``codomyrmex.agents.*`` from this
    process's ``sys.modules`` (as this test used to) leaves later tests holding
    two copies of modules such as ``agents.core.config`` and the trust gateway,
    which broke singletons and isinstance checks depending on xdist ordering.
    """
    import subprocess
    import sys

    probe = (
        "import sys, codomyrmex.agents; "
        "print(int('codomyrmex.agents.core' in sys.modules), "
        "int('codomyrmex.agents.claude' in sys.modules))"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    assert result.stdout.split()[-2:] == ["0", "0"], result.stdout + result.stderr


def test_unknown_attribute_raises_attribute_error() -> None:
    try:
        agents_pkg.definitely_not_a_real_name  # noqa: B018
    except AttributeError:
        pass
    else:
        raise AssertionError("expected AttributeError for unknown attribute")


def test_cli_config_command_resolves_lazy_get_config(capsys) -> None:
    """Regression: ``_show_config`` referenced an unbound global ``get_config``.

    Lazy exports live behind module ``__getattr__``, which bare-name lookups
    inside the module never consult, so the command raised ``NameError``.
    """
    commands = agents_pkg.cli_commands()
    commands["config"]()
    out = capsys.readouterr().out
    assert out.startswith("Agent configuration:")
    assert "default_timeout" in out
