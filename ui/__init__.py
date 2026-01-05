"""UI module - user interface components"""
from .colors import get_colors, get_gradients, COLORS, GRADIENTS, console
from .logo import show_logo
from .components import (
    create_highlighted_panel,
    create_gradient_bar,
    create_questionary_style,
)

__all__ = [
    # Colors
    "get_colors",
    "get_gradients",
    "COLORS",
    "GRADIENTS",
    "console",
    # Logo
    "show_logo",
    # Components
    "create_highlighted_panel",
    "create_gradient_bar",
    "create_questionary_style",
]
