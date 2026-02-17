"""
Theme toggle unit tests.
Feature: local-web-viewer, Property 19: Theme preference localStorage round trip
Validates: Requirements 10.3, 10.4, 10.5
"""

import os

# Paths to the relevant source files
JS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "website", "assets", "js", "education.js"
)
HTML_PATH = os.path.join(
    os.path.dirname(__file__), "..", "website", "templates", "base.html"
)
CSS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "website", "assets", "css", "style.css"
)


def _read(path: str) -> str:
    with open(path) as f:
        return f.read()


class TestThemeToggle:
    """Property 19: Theme preference localStorage round trip."""

    def test_js_reads_localstorage_theme(self):
        """Theme init reads from localStorage."""
        js = _read(JS_PATH)
        assert (
            "localStorage.getItem('theme')" in js
            or 'localStorage.getItem("theme")' in js
        )

    def test_js_writes_localstorage_theme(self):
        """Theme toggle writes to localStorage."""
        js = _read(JS_PATH)
        assert (
            "localStorage.setItem('theme'" in js or 'localStorage.setItem("theme"' in js
        )

    def test_js_sets_data_theme_attribute(self):
        """Theme toggle sets data-theme attribute on html element."""
        js = _read(JS_PATH)
        assert "data-theme" in js
        assert "setAttribute" in js or "removeAttribute" in js

    def test_default_light_theme(self):
        """Default theme is light (no data-theme attribute set initially)."""
        # The JS only sets data-theme='dark' if localStorage has 'dark',
        # meaning light is the default.
        js = _read(JS_PATH)
        # initTheme only sets dark if saved === 'dark'
        assert "saved === 'dark'" in js or 'saved === "dark"' in js

    def test_html_has_theme_toggle_button(self):
        """base.html contains the theme toggle button."""
        html = _read(HTML_PATH)
        assert 'id="theme-toggle"' in html
        assert "aria-label" in html

    def test_css_has_dark_theme_variables(self):
        """CSS defines dark theme overrides."""
        css = _read(CSS_PATH)
        assert '[data-theme="dark"]' in css

    def test_css_has_light_theme_defaults(self):
        """CSS :root defines light theme defaults."""
        css = _read(CSS_PATH)
        assert ":root" in css
        assert "--bg-primary: #ffffff" in css or "--bg-primary: #fff" in css
