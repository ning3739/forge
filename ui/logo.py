"""Logo rendering module"""
from rich.console import Group, RenderableType
from rich.text import Text
from rich.align import Align
from typing import List

from ui.colors import get_colors, get_gradients, console
from core.version import __version__

# Constants
AUTHOR = "@ning3739"
NARROW_THRESHOLD = 60

# ASCII Logo
ASCII_LOGO = [
    "  ███████╗ ██████╗ ██████╗  ██████╗ ███████╗",
    "  ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝",
    "  █████╗  ██║   ██║██████╔╝██║  ███╗█████╗  ",
    "  ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  ",
    "  ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗",
    "  ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
]


def create_ascii_logo() -> Text:
    """Create ASCII art Logo"""
    logo = Text()
    colors = get_colors()
    gradients = get_gradients()
    gradient = gradients.PURPLE_GRADIENT

    for i, line in enumerate(ASCII_LOGO):
        color = gradient[i % len(gradient)]
        logo.append(line + "\n", style=f"bold {color}")
    return logo


def create_subtitle() -> Text:
    """Create subtitle"""
    colors = get_colors()
    content = Text()
    indent = "  "

    content.append(indent)
    content.append("⚡ ", style=f"bold {colors.neon_yellow}")
    content.append(
        "High-performance development scaffolding tool",
        style=f"bold {colors.text_primary} italic"
    )
    return content


def create_version_badge() -> Text:
    """Create version badge"""
    colors = get_colors()
    badge = Text()
    indent = "  "

    badge.append(indent)

    # Handle version number
    version_str = __version__.lstrip("v")
    badge.append("v", style=f"dim {colors.text_secondary}")
    badge.append(version_str, style=f"bold {colors.text_primary}")

    badge.append("  •  ", style=f"dim {colors.text_secondary}")
    badge.append("By ", style=f"dim {colors.text_secondary}")
    badge.append(AUTHOR, style=f"bold {colors.primary_light}")

    return badge


def get_logo_renderable() -> RenderableType:
    """Get Logo renderable object"""
    renderables: List[RenderableType] = [
        Align.left(create_ascii_logo()),
        Align.left(create_subtitle()),
        Text("\n"),
        Align.left(create_version_badge()),
        Text("\n")
    ]
    return Group(*renderables)


def show_logo(clear_screen: bool = True) -> None:
    """Show Logo"""
    if clear_screen:
        console.clear()
    console.print()
    console.print(get_logo_renderable())
