"""
Unit tests for the peft module MCP tools.

Strictly zero-mock tests for PEFT adapter creation and comparison tools.
"""

import pytest

from codomyrmex.peft.mcp_tools import peft_compare_methods, peft_create_adapter


class TestMCPTools:
    """Zero-mock tests for PEFT MCP tools."""

    @pytest.mark.unit
    def test_create_adapter_lora(self):
        """Test creating a LoRA adapter via MCP tool."""
        result = peft_create_adapter(method="lora", d_model=256, rank=4, alpha=8.0)

        assert result["method"] == "lora"
        assert result["trainable_params"] == (4 * 256 + 256 * 4)  # 2048
        assert result["full_finetune_params"] == 256 * 256  # 65536
        assert result["reduction_factor"] == round(65536 / 2048, 2)

    @pytest.mark.unit
    def test_create_adapter_ia3(self):
        """Test creating an IA3 adapter via MCP tool."""
        result = peft_create_adapter(method="ia3", d_model=256)

        assert result["method"] == "ia3"
        assert result["trainable_params"] == (256 + 256 + 4 * 256)  # 1536
        assert result["full_finetune_params"] == 256 * 256  # 65536
        assert result["reduction_factor"] == round(65536 / 1536, 2)

    @pytest.mark.unit
    def test_create_adapter_prefix(self):
        """Test creating a Prefix Tuning adapter via MCP tool."""
        result = peft_create_adapter(method="prefix", d_model=256)

        assert result["method"] == "prefix"
        assert result["trainable_params"] == (2 * 2 * 10 * 256)  # 10240
        assert result["full_finetune_params"] == 256 * 256  # 65536
        assert result["reduction_factor"] == round(65536 / 10240, 2)

    @pytest.mark.unit
    def test_create_adapter_unknown_raises(self):
        """Test creating an unknown adapter raises ValueError naturally."""
        with pytest.raises(
            ValueError,
            match="Unknown PEFT method: 'unknown'. Supported: lora, prefix, ia3",
        ):
            peft_create_adapter(method="unknown", d_model=256)

    @pytest.mark.unit
    def test_compare_methods(self):
        """Test comparing PEFT methods via MCP tool."""
        result = peft_compare_methods(d_model=512, rank=4)

        assert "full_finetune" in result
        assert "lora" in result
        assert "prefix" in result
        assert "ia3" in result

        assert result["full_finetune"] == 512 * 512
        assert result["lora"] == (4 * 512 + 512 * 4)
        assert result["prefix"] == (2 * 2 * 10 * 512)
        assert result["ia3"] == (512 + 512 + 4 * 512)

        assert result["full_finetune"] > result["prefix"]
        assert result["prefix"] > result["lora"]
        assert result["lora"] > result["ia3"]
