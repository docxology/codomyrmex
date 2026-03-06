
from codomyrmex.languages.csharp.manager import CSharpManager


def test_csharp_manager_operations():
    """Test C# manager functions."""
    manager = CSharpManager()

    is_installed = manager.is_installed()
    assert isinstance(is_installed, bool)

    instructions = manager.install_instructions()
    assert isinstance(instructions, str)

    if is_installed:
        script = 'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello from C# zero-mock test");\n    }\n}\n'
        result = manager.use_script(script)
        assert "Hello from C# zero-mock test" in result
