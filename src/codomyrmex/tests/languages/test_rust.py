import pytest

from codomyrmex.languages.rust.manager import RustManager


def test_rust_manager_operations():
    """Test Rust manager functions."""
    manager = RustManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'fn main() {\n    println!("Hello from Rust zero-mock test");\n}\n'
        result = manager.use_script(script)
        assert "Hello from Rust zero-mock test" in result
