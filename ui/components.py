"""UI组件模块 - 简化版本"""
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from typing import Optional, Literal, Union
from rich import box
import questionary
from ui.colors import get_colors, get_gradients, console


def create_questionary_style() -> questionary.Style:
    """
    创建统一的 questionary 样式
    
    Returns:
        questionary.Style 对象
    """
    colors = get_colors()
    return questionary.Style([
        ('qmark', f'fg:{colors.primary} bold'),
        ('question', f'bold {colors.text_primary}'),
        ('answer', f'fg:{colors.neon_green} bold'),
        ('pointer', f'fg:{colors.neon_green}'),
        ('highlighted', f'fg:{colors.neon_green}'),  # 光标所在项，只改字体颜色
        ('selected', f'fg:{colors.neon_green}'),  # 多选时选中项的标记（圆圈）颜色，无背景
        ('separator', f'fg:{colors.muted_dark}'),
        ('instruction', f'fg:{colors.text_muted}'),
        ('text', f'fg:{colors.text_primary}'),  # 普通文本颜色
        ('disabled', f'fg:{colors.muted_dark} italic')
    ])


def create_highlighted_panel(
    content: Union[str, Text],
    title: str = "",
    accent_color: Optional[str] = None,
    icon: str = "⚡"
) -> Panel:
    """
    创建高亮面板 - 用于重要信息展示

    Args:
        content: 面板内容
        title: 面板标题
        accent_color: 强调色
        icon: 标题图标

    Returns:
        Panel对象
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
    创建渐变分隔条 - 响应式

    Args:
        style: 样式类型（default, rainbow, neon）
    """
    colors = get_colors()
    gradients = get_gradients()
    width = console.width

    # 如果屏幕太窄，只显示简单的线
    if width < 20:
        console.print(Text("─" * width, style="dim white"))
        return

    bar = Text()
    # 统一使用粗线字符，保持所有样式粗细一致
    char = "━"

    # 根据样式选择颜色列表
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
        # 将剩余的字符分配给最后一个片段
        current_segment_width = segment_width + (
            remaining_chars if i == num_colors - 1 else 0
        )
        if current_segment_width > 0:
            bar.append(
                char * current_segment_width,
                style=f"bold {color}"
            )

    console.print(Align.left(bar))


# 导出
__all__ = [
    "console",
    "create_questionary_style",
    "create_highlighted_panel",
    "create_gradient_bar",
]
