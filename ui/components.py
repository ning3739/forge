"""UI components module - simplified version"""
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from typing import Optional, Literal, Union
from rich import box
import questionary
from ui.colors import get_colors, get_gradients, console


def create_questionary_style() -> questionary.Style:
    """
    Create unified questionary style
    
    Returns:
        questionary.Style object
    """
    colors = get_colors()
    return questionary.Style([
        ('qmark', f'fg:{colors.primary} bold'),
        ('question', f'bold {colors.text_primary}'),
        ('answer', f'fg:{colors.neon_green} bold'),
        ('pointer', f'fg:{colors.neon_green}'),
        ('highlighted', f'fg:{colors.neon_green}'),  # Cursor position item, only change font color
        ('selected', f'fg:{colors.neon_green}'),  # Multi-select checked item marker (circle) color, no background
        ('separator', f'fg:{colors.muted_dark}'),
        ('instruction', f'fg:{colors.text_muted}'),
        ('text', f'fg:{colors.text_primary}'),  # Normal text color
        ('disabled', f'fg:{colors.muted_dark} italic')
    ])


def create_highlighted_panel(
    content: Union[str, Text],
    title: str = "",
    accent_color: Optional[str] = None,
    icon: str = "⚡"
) -> Panel:
    """
    Create highlighted panel - for displaying important information

    Args:
        content: Panel content
        title: Panel title
        accent_color: Accent color
        icon: Title icon

    Returns:
        Panel object
    """
    colors = get_colors()
    accent = accent_color or colors.neon_yellow
    title_text = f"[bold {accent}]{icon}[/bold {accent}]  [bold white]{title}[/bold white]"

    return Panel(
        content,
        title=title_text,
        border_style=accent,
        padding=(1, 3),
        box=box.DOUBLE
    )


def create_gradient_bar(
    style: Literal["default", "rainbow", "neon"] = "default"
) -> None:
    """
    Create gradient separator bar - responsive

    Args:
        style: Style type (default, rainbow, neon)
    """
    colors = get_colors()
    gradients = get_gradients()
    width = console.width

    # If screen is too narrow, only show simple line
    if width < 20:
        console.print(Text("─" * width, style="dim white"))
        return

    bar = Text()
    # Use thick line character uniformly to keep all styles consistent
    char = "━"

    # Select color list based on style
    if style == "rainbow":
        colors_list = gradients.RAINBOW
    elif style == "neon":
        colors_list = gradients.PURPLE_GRADIENT * 2
    else:
        colors_list = gradients.PURPLE_GRADIENT

    num_colors = len(colors_list)
    segment_width = width // num_colors
    remaining_chars = width % num_colors

    for i, color in enumerate(colors_list):
        # Distribute remaining characters to the last segment
        current_segment_width = segment_width + (
            remaining_chars if i == num_colors - 1 else 0
        )
        if current_segment_width > 0:
            bar.append(
                char * current_segment_width,
                style=f"bold {color}"
            )

    console.print(Align.left(bar))


# Exports
__all__ = [
    "console",
    "create_questionary_style",
    "create_highlighted_panel",
    "create_gradient_bar",
]
