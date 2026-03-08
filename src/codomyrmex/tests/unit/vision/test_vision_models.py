"""Zero-mock tests for the vision module models."""

from __future__ import annotations

import pytest

from codomyrmex.vision.models import (
    Annotation,
    BoundingBox,
    PageContent,
    VLMConfig,
    VLMResponse,
)


@pytest.mark.unit
class TestVLMConfig:
    def test_defaults(self):
        cfg = VLMConfig()
        assert cfg.model_name == "llava"
        assert cfg.host == "localhost"
        assert cfg.port == 11434
        assert cfg.temperature == 0.2
        assert cfg.max_tokens == 2048
        assert cfg.timeout == 60.0

    def test_custom_values(self):
        cfg = VLMConfig(model_name="bakllava", host="192.168.1.1", port=9999)
        assert cfg.model_name == "bakllava"
        assert cfg.host == "192.168.1.1"
        assert cfg.port == 9999

    def test_frozen_immutable(self):
        cfg = VLMConfig()
        with pytest.raises((AttributeError, TypeError)):
            cfg.model_name = "other"  # type: ignore[misc]

    def test_equality(self):
        a = VLMConfig(model_name="llava")
        b = VLMConfig(model_name="llava")
        assert a == b

    def test_inequality_different_model(self):
        a = VLMConfig(model_name="llava")
        b = VLMConfig(model_name="bakllava")
        assert a != b


@pytest.mark.unit
class TestVLMResponse:
    def test_minimal_construction(self):
        r = VLMResponse(text="hello")
        assert r.text == "hello"
        assert r.model == ""
        assert r.confidence == 0.0
        assert r.metadata == {}

    def test_full_construction(self):
        r = VLMResponse(text="cat detected", model="llava", confidence=0.92, metadata={"source": "test"})
        assert r.text == "cat detected"
        assert r.model == "llava"
        assert r.confidence == 0.92
        assert r.metadata["source"] == "test"

    def test_metadata_is_mutable(self):
        r = VLMResponse(text="x")
        r.metadata["added"] = True
        assert r.metadata["added"] is True

    def test_empty_text(self):
        r = VLMResponse(text="")
        assert r.text == ""


@pytest.mark.unit
class TestBoundingBox:
    def test_defaults_zero(self):
        bb = BoundingBox()
        assert bb.x == 0.0
        assert bb.y == 0.0
        assert bb.width == 0.0
        assert bb.height == 0.0

    def test_area_zero_default(self):
        bb = BoundingBox()
        assert bb.area == 0.0

    def test_area_calculation(self):
        bb = BoundingBox(x=0.0, y=0.0, width=0.5, height=0.4)
        assert bb.area == pytest.approx(0.2)

    def test_center_origin(self):
        bb = BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0)
        assert bb.center == pytest.approx((0.5, 0.5))

    def test_center_offset(self):
        bb = BoundingBox(x=0.2, y=0.3, width=0.4, height=0.2)
        cx, cy = bb.center
        assert cx == pytest.approx(0.4)
        assert cy == pytest.approx(0.4)

    def test_frozen_immutable(self):
        bb = BoundingBox(x=0.1)
        with pytest.raises((AttributeError, TypeError)):
            bb.x = 0.9  # type: ignore[misc]

    def test_equality(self):
        a = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
        b = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
        assert a == b

    def test_unit_square_area(self):
        bb = BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0)
        assert bb.area == pytest.approx(1.0)


@pytest.mark.unit
class TestAnnotation:
    def test_minimal_construction(self):
        ann = Annotation(label="cat")
        assert ann.label == "cat"
        assert ann.confidence == 0.0
        assert isinstance(ann.bounding_box, BoundingBox)
        assert ann.attributes == {}

    def test_with_bounding_box(self):
        bb = BoundingBox(x=0.1, y=0.1, width=0.5, height=0.5)
        ann = Annotation(label="dog", bounding_box=bb, confidence=0.88)
        assert ann.bounding_box.x == 0.1
        assert ann.confidence == 0.88

    def test_attributes_mutable(self):
        ann = Annotation(label="person")
        ann.attributes["age_group"] = "adult"
        assert ann.attributes["age_group"] == "adult"

    def test_default_bounding_box_area_zero(self):
        ann = Annotation(label="x")
        assert ann.bounding_box.area == 0.0

    def test_high_confidence(self):
        ann = Annotation(label="car", confidence=0.999)
        assert ann.confidence > 0.99


@pytest.mark.unit
class TestPageContent:
    def test_defaults(self):
        pc = PageContent()
        assert pc.page_number == 1
        assert pc.text == ""
        assert pc.images == []
        assert pc.annotations == []
        assert pc.metadata == {}

    def test_custom_page_number(self):
        pc = PageContent(page_number=5, text="page five content")
        assert pc.page_number == 5
        assert pc.text == "page five content"

    def test_images_list(self):
        pc = PageContent(images=["img1.png", "img2.jpg"])
        assert len(pc.images) == 2
        assert "img1.png" in pc.images

    def test_annotations_list(self):
        ann = Annotation(label="table")
        pc = PageContent(annotations=[ann])
        assert len(pc.annotations) == 1
        assert pc.annotations[0].label == "table"

    def test_metadata(self):
        pc = PageContent(metadata={"language": "en", "dpi": 300})
        assert pc.metadata["dpi"] == 300

    def test_default_lists_independent(self):
        """Verify default_factory prevents shared list across instances."""
        pc1 = PageContent()
        pc2 = PageContent()
        pc1.images.append("x.png")
        assert pc2.images == []
