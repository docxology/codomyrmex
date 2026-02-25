from codomyrmex.data_visualization.components.media import Image, Video
from codomyrmex.data_visualization.components.text import CodeBlock, TextBlock


def test_image_component():
    """Test functionality: image component."""
    img = Image(src="test.png", alt="Test Image", caption="A caption")
    html = str(img)
    assert 'src="test.png"' in html
    assert 'alt="Test Image"' in html
    assert "<figcaption>A caption</figcaption>" in html

def test_video_component():
    """Test functionality: video component."""
    vid = Video(src="test.mp4", controls=True)
    html = str(vid)
    assert 'src="test.mp4"' in html
    assert "controls" in html

def test_text_block():
    """Test functionality: text block."""
    txt = TextBlock(content="Hello\nWorld", is_markdown=True)
    html = str(txt)
    assert "Hello<br>World" in html
    assert "markdown" in html

def test_code_block():
    """Test functionality: code block."""
    code = "print('hello')"
    block = CodeBlock(code=code, language="python")
    html = str(block)
    assert 'class="language-python"' in html
    assert "print('hello')" in html
