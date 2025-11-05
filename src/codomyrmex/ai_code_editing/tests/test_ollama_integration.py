from codomyrmex.language_models import generate_with_ollama


def test_generate_with_ollama():
    out = generate_with_ollama('hello')
    assert 'hello' in out
