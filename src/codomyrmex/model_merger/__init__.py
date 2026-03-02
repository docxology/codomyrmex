"""Model merger -- SLERP interpolation and model soups."""
from .merger import ModelMerger, linear_interpolate, model_soup, slerp

__all__ = ["slerp", "linear_interpolate", "model_soup", "ModelMerger"]
