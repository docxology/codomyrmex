import pytest
from codomyrmex.data_visualization.components.media import Image, Video
from codomyrmex.data_visualization.components.text import TextBlock, CodeBlock

def test_image_component():
    img = Image(src="test.png", alt="Test Image", caption="A caption")
    html = str(img)
    assert "<img src=\"test.png\"" in html
    assert "alt=\"Test Image\"" in html
    assert "<figcaption>A caption</figcaption>" in html

def test_video_component():
    vid = Video(src="test.mp4", controls=True)
    html = str(vid)
    assert "<video src=\"test.mp4\"" in html
    assert "controls" in html

def test_text_block():
    txt = TextBlock("Hello\nWorld", is_markdown=True)
    html = str(txt)
    assert "Hello<br>World" in html
    assert "markdown" in html

def test_code_block():
    code = "print('hello')"
    block = CodeBlock(code, language="python")
    html = str(block)
    assert "<code class=\"language-python\">" in html
    assert "print('hello')" in html
