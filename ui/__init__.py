"""UI模块 - 终端界面相关"""
from .colors import get_colors, get_gradients, COLORS, GRADIENTS, console
from .logo import show_logo
from .components import (
    create_highlighted_panel,
    create_gradient_bar,
    create_questionary_style,
)

__all__ = [
    # 颜色
    "get_colors",
    "get_gradients",
    "COLORS",
    "GRADIENTS",
    "console",
    # Logo
    "show_logo",
    # 组件
    "create_highlighted_panel",
    "create_gradient_bar",
    "create_questionary_style",
]
