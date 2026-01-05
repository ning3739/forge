"""
Color management system - unified color constants
Cyberpunk style color scheme
"""
from typing import List
from dataclasses import dataclass, field
from rich.console import Console

console = Console()


@dataclass(frozen=True)
class ColorPalette:
    """Color palette - cyberpunk style"""

    # Primary colors - purple series
    primary: str = "#8b5cf6"
    primary_light: str = "#a78bfa"
    primary_lighter: str = "#c4b5fd"
    primary_dark: str = "#7c3aed"
    primary_darker: str = "#6d28d9"

    # Secondary colors - cyan series
    secondary: str = "#06b6d4"
    secondary_light: str = "#22d3ee"
    secondary_dark: str = "#0891b2"

    # Accent colors - neon series
    accent: str = "#f59e0b"
    accent_light: str = "#fbbf24"
    neon_pink: str = "#ec4899"
    neon_green: str = "#10b981"
    neon_yellow: str = "#fbbf24"
    electric_blue: str = "#3b82f6"

    # Status colors
    success: str = "#10b981"
    warning: str = "#f59e0b"
    error: str = "#ef4444"
    info: str = "#06b6d4"

    # Neutral colors
    muted: str = "#9ca3af"
    muted_light: str = "#d1d5db"
    muted_dark: str = "#6b7280"

    # Background and border
    bg: str = "#1e1e2e"
    bg_secondary: str = "#2d2d3d"
    border: str = "#8b5cf6"
    border_light: str = "#a78bfa"
    glass: str = "rgba(30, 30, 46, 0.8)"

    # Text colors
    text_primary: str = "#ffffff"
    text_secondary: str = "#e5e7eb"
    text_muted: str = "#9ca3af"
    text_inverse: str = "#000000"


@dataclass(frozen=True)
class GradientPresets:
    """Common gradient color combinations"""

    PURPLE_GRADIENT: List[str] = field(default_factory=lambda: [
        "#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe", "#ec4899"
    ])

    RAINBOW: List[str] = field(default_factory=lambda: [
        "#8b5cf6", "#a78bfa", "#06b6d4", "#10b981", "#fbbf24", "#f59e0b", "#ec4899"
    ])

    COOL: List[str] = field(default_factory=lambda: [
        "#7c3aed", "#8b5cf6", "#06b6d4", "#22d3ee"
    ])

    WARM: List[str] = field(default_factory=lambda: [
        "#f59e0b", "#fbbf24", "#ec4899"
    ])

    SUCCESS: List[str] = field(default_factory=lambda: [
        "#10b981", "#34d399", "#6ee7b7"
    ])


# Global instances
COLORS = ColorPalette()
GRADIENTS = GradientPresets()


def get_colors() -> ColorPalette:
    """Get color palette"""
    return COLORS


def get_gradients() -> GradientPresets:
    """Get gradient presets"""
    return GRADIENTS
