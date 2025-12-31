"""Info命令模块"""
import typer
from rich.text import Text as RichText
from rich.console import Group

from ui.colors import get_colors
from commands.helpers import PyPIStats
from ui.components import console, create_highlighted_panel


def create_info_content() -> Group:
    """创建信息内容"""
    colors = get_colors()
    pypi_stats = PyPIStats()

    info_lines = [
        f":zap: [bold {colors.primary}]Forge[/bold {colors.primary}]",
        f":rocket: [bold]Version:[/bold] v0.1.0",
        f":bust_in_silhouette: [bold]Author:[/bold] @ningli",
        f":scroll: [bold]License:[/bold] MIT License",
        RichText.assemble(
            ("📥 Downloads: ", None),
            (str(pypi_stats.get_downloads()), f"bold {colors.neon_green}")
        ),
        f":book: [bold]Docs:[/bold] https://forge.example.com"
    ]
    return Group(*info_lines)


def info_command():
    """Info command - show Forge project info"""
    colors = get_colors()
    content = create_info_content()
    panel = create_highlighted_panel(
        content,
        title="Forge Info",
        accent_color=colors.neon_pink,
        icon=":rocket:"
    )
    console.print(panel)
