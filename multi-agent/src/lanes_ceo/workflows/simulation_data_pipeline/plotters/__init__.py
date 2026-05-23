"""Plotter templates and nature-figure bridge for simulation data pipeline."""

from .nature_figure_bridge import NatureFigureBridge
from .templates import TEMPLATE_REGISTRY, get_template

__all__ = ["NatureFigureBridge", "TEMPLATE_REGISTRY", "get_template"]
