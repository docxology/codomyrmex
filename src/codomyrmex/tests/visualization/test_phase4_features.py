import pytest
from codomyrmex.data_visualization.plots.wordcloud import WordCloud
from codomyrmex.data_visualization.plots.confusion_matrix import ConfusionMatrix
from codomyrmex.data_visualization.components.chat_bubble import ChatBubble
from codomyrmex.data_visualization.components.json_view import JsonView

def test_word_cloud_render():
    words = [("Hello", 10), ("World", 20)]
    plot = WordCloud("Test Cloud", words)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test Cloud\"" in html

def test_confusion_matrix_render():
    matrix = [[10, 2], [3, 8]]
    labels = ["A", "B"]
    plot = ConfusionMatrix("Test CM", matrix, labels)
    html = plot.to_html()
    assert "data:image/png;base64" in html
    assert "alt=\"Test CM\"" in html

def test_chat_bubble_component():
    b1 = ChatBubble("Hello", "user", "10:00")
    html1 = str(b1)
    assert "Hello" in html1
    assert "User" in html1
    assert "float: right" in html1 # User aligned right
    
    b2 = ChatBubble("Hi there", "agent", "10:01")
    html2 = str(b2)
    assert "Hi there" in html2
    assert "Agent" in html2
    assert "float: left" in html2 # Agent aligned left

def test_json_view_component():
    data = {"key": "value", "list": [1, 2]}
    view = JsonView(data, "Config")
    html = str(view)
    assert "Config" in html
    assert "key" in html
    assert "value" in html
    assert "details" in html # Uses html details/summary tags
