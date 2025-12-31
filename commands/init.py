"""Init命令模块"""
import typer
import time
import questionary
from pathlib import Path
from typing import Optional, Dict, Tuple, Any, List
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.live import Live

from ui.logo import show_logo
from ui.components import create_gradient_bar, create_highlighted_panel, create_questionary_style, console
from ui.colors import get_colors
from core.utils import ProjectConfig
from core.project_generator import ProjectGenerator


def collect_project_name(name: Optional[str], style: questionary.Style) -> str:
    """收集项目名称"""
    if name is None:
        name = questionary.text(
            "Project name:",
            default="forge-project",
            style=style
        ).ask()
        if not name:
            name = "forge-project"
    return name


def collect_database_config(style: questionary.Style) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """收集数据库配置"""
    database = questionary.select(
        "Database:",
        choices=[
            "PostgreSQL (Recommended)",
            "MySQL",
            "None - Skip database"
        ],
        style=style
    ).ask()
    
    # 如果选择跳过数据库
    if database and "None" in database:
        return None, None, None
    
    # 提取实际数据库名称
    database = database.split(" (")[0]

    orm = questionary.select(
        "ORM:",
        choices=[
            "SQLModel (Recommended)",
            "SQLAlchemy"
        ],
        style=style
    ).ask()
    
    # 提取实际 ORM 名称
    orm = orm.split(" (")[0]
    
    enable_migration = questionary.confirm(
        "Enable database migrations (Alembic)?",
        default=True,
        auto_enter=True,
        style=style
    ).ask()
    
    migration_tool = "Alembic" if enable_migration else None

    return database, orm, migration_tool


def collect_features(style: questionary.Style, has_database: bool = True) -> Dict[str, Any]:
    """收集功能选择
    
    Args:
        style: questionary 样式
        has_database: 是否选择了数据库
    """
    colors = get_colors()

    # ========== 1. 认证配置 ==========
    auth_config = {
        "type": "none",
        "refresh_token": False,
        "features": []
    }
    
    if has_database:
        # 只有选择了数据库才能配置认证
        auth_type = questionary.select(
            "Authentication:",
            choices=[
                "Complete JWT Auth (Recommended)",
                "Basic JWT Auth (login/register only)",
                "None - Skip authentication"
            ],
            style=style
        ).ask()
        
        # 如果启用认证，配置相关功能
        if auth_type and "None" not in auth_type:
            if "Complete" in auth_type:
                auth_config["type"] = "complete"
                auth_config["refresh_token"] = True  # Complete Auth 默认包含 Refresh Token
                auth_config["features"] = [
                    "Email Verification",
                    "Password Reset",
                    "Email Service"
                ]
                console.print(
                    f"\n  [dim]ℹ️  Complete JWT Auth includes:[/dim]\n"
                    f"  [dim]   • Email verification[/dim]\n"
                    f"  [dim]   • Password reset[/dim]\n"
                    f"  [dim]   • Email service (SMTP)[/dim]\n"
                    f"  [dim]   • Refresh Token[/dim]\n"
                )
            else:
                auth_config["type"] = "basic"
                auth_config["refresh_token"] = False  # Basic Auth 不支持 Refresh Token
                console.print(
                    f"\n  [dim]ℹ️  Basic JWT Auth includes:[/dim]\n"
                    f"  [dim]   • Login and Register only[/dim]\n"
                )
    else:
        # 没有数据库时跳过认证配置
        console.print(
            f"\n  [dim {colors.text_muted}]ℹ️  Authentication skipped (requires database)[/dim {colors.text_muted}]\n"
        )
    
    # ========== 2. 安全功能 ==========
    enable_cors = questionary.confirm(
        "Enable CORS?",
        default=True,
        auto_enter=True,
        style=style
    ).ask()

    # ========== 3. 开发工具 ==========
    enable_dev_tools = questionary.confirm(
        "Include dev tools (Black + Ruff)?",
        default=True,
        auto_enter=True,
        style=style
    ).ask()

    # ========== 4. 测试工具 ==========
    enable_testing = questionary.confirm(
        "Include testing setup (pytest)?",
        default=True,
        auto_enter=True,
        style=style
    ).ask()

    # ========== 5. 部署配置 ==========
    enable_docker = questionary.confirm(
        "Include Docker configs?",
        default=True,
        auto_enter=True,
        style=style
    ).ask()

    return {
        "auth": auth_config,
        "cors": enable_cors,
        "dev_tools": enable_dev_tools,
        "testing": enable_testing,
        "docker": enable_docker
    }


def show_saving_progress(name: str) -> None:
    """显示保存配置和生成项目进度"""
    colors = get_colors()
    create_gradient_bar("rainbow")

    # 创建进度条
    progress = Progress(
        SpinnerColumn(style=colors.primary_light, spinner_name="dots12"),
        TextColumn(
            f"[bold {colors.primary}]▸[/bold {colors.primary}] "
            f"[bold {colors.text_primary}]{{task.description}}"
        ),
        BarColumn(
            complete_style=colors.neon_green,
            finished_style=colors.neon_green,
            pulse_style=colors.primary_light,
            bar_width=None
        ),
        console=console,
        transient=True
    )

    # 扩展的任务列表，包含项目生成步骤
    steps = [
        "Creating project directory",
        "Saving configuration",
        "Creating project structure",
        "Generating code files",
        "Generating configuration files"
    ]

    # 使用Live确保进度条同步刷新
    with Live(progress, refresh_per_second=10):
        for step in steps:
            task = progress.add_task(step, total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.008)
            progress.remove_task(task)


def show_config_summary(
    name: str,
    database: Optional[str],
    orm: Optional[str],
    migration_tool: Optional[str],
    features: Dict[str, Any]
) -> None:
    """显示配置摘要"""
    colors = get_colors()
    console.print()

    # 构建配置内容
    lines = [
        f"[bold {colors.primary_light}]Project:[/bold {colors.primary_light}] "
        f"[bold {colors.text_primary}]{name}[/bold {colors.text_primary}]",
    ]
    
    # 只有选择了数据库才显示数据库配置
    if database:
        lines.append(
            f"[bold {colors.primary_light}]Database:[/bold {colors.primary_light}] "
            f"[{colors.secondary}]{database} with {orm}[/{colors.secondary}]"
        )
        if migration_tool:
            lines.append(
                f"[bold {colors.primary_light}]Migration:[/bold {colors.primary_light}] "
                f"[{colors.secondary}]{migration_tool}[/{colors.secondary}]"
            )
    else:
        lines.append(
            f"[bold {colors.primary_light}]Database:[/bold {colors.primary_light}] "
            f"[{colors.text_muted}]None (API only)[/{colors.text_muted}]"
        )

    # 认证配置
    auth_config = features.get("auth", {})
    if auth_config.get("type") != "none":
        auth_type = "Complete JWT Auth" if auth_config.get("type") == "complete" else "Basic JWT Auth"
        refresh_token = " (with Refresh Token)" if auth_config.get("refresh_token") else ""
        lines.append(
            f"[bold {colors.primary}]Authentication:[/bold {colors.primary}] "
            f"[dim]{auth_type}{refresh_token}[/dim]"
        )
        
        # 如果是 Complete JWT Auth，显示包含的功能
        if auth_config.get("type") == "complete":
            auth_features = auth_config.get("features", [])
            if auth_features:
                lines.append(
                    f"[{colors.text_muted}]  • {', '.join(auth_features)}[/{colors.text_muted}]"
                )

    # 安全配置
    security_items = []
    if features.get("cors"):
        security_items.append("CORS")
    security_items.extend(["Input Validation", "Password Hashing"])
    
    lines.append(
        f"[bold {colors.neon_green}]Security:[/bold {colors.neon_green}] "
        f"[dim]{', '.join(security_items)}[/dim]"
    )

    # 开发工具
    if features.get("dev_tools"):
        lines.append(
            f"[bold {colors.secondary}]Dev Tools:[/bold {colors.secondary}] "
            f"[dim]API Docs, Black, Ruff[/dim]"
        )

    # 测试
    if features.get("testing"):
        lines.append(
            f"[bold {colors.info}]Testing:[/bold {colors.info}] "
            f"[dim]pytest, httpx, coverage[/dim]"
        )

    # 部署
    if features.get("docker"):
        lines.append(
            f"[bold {colors.accent}]Deployment:[/bold {colors.accent}] "
            f"[dim]Docker, Docker Compose[/dim]"
        )

    panel = create_highlighted_panel(
        "\n".join(lines),
        title="Configuration Summary",
        accent_color=colors.neon_pink,
        icon=":package:"
    )
    console.print(panel)
    
    # 如果是 Complete JWT Auth，显示邮件配置提示
    if auth_config.get("type") == "complete":
        console.print()
        warning_content = (
            f"[bold {colors.warning}]⚠️  Important: Configure Email Service[/bold {colors.warning}]\n\n"
            f"[{colors.text_muted}]Before running the application, update these settings in .env:[/{colors.text_muted}]\n\n"
            f"[{colors.secondary}]  SMTP_HOST=smtp.gmail.com[/{colors.secondary}]\n"
            f"[{colors.secondary}]  SMTP_PORT=587[/{colors.secondary}]\n"
            f"[{colors.secondary}]  SMTP_USER=your-email@gmail.com[/{colors.secondary}]\n"
            f"[{colors.secondary}]  SMTP_PASSWORD=your-app-password[/{colors.secondary}]\n"
            f"[{colors.secondary}]  EMAILS_FROM_EMAIL=noreply@yourdomain.com[/{colors.secondary}]\n\n"
            f"[{colors.text_muted}]For Gmail: https://support.google.com/accounts/answer/185833[/{colors.text_muted}]"
        )
        warning_panel = create_highlighted_panel(
            warning_content,
            title="Email Configuration",
            accent_color=colors.warning,
            icon="⚠️"
        )
        console.print(warning_panel)


def show_next_steps(name: str) -> None:
    """显示下一步操作"""
    colors = get_colors()
    console.print()

    content = (
        f"[bold {colors.neon_green}]:white_check_mark:[/bold {colors.neon_green}]  "
        f"[bold {colors.text_primary}]Project created successfully!"
        f"[/bold {colors.text_primary}]\n\n"
        f"[{colors.text_muted}]Project location:[/{colors.text_muted}]\n"
        f"[bold {colors.secondary}]{Path.cwd() / name}[/bold {colors.secondary}]\n\n"
        f"[{colors.text_muted}]Next steps:[/{colors.text_muted}]\n"
        f"[bold {colors.primary}]cd {name}[/bold {colors.primary}]\n"
        f"[bold {colors.secondary}]uv sync[/bold {colors.secondary}]  [{colors.text_muted}]# Install dependencies[/{colors.text_muted}]\n"
        f"[bold {colors.neon_green}]uvicorn app.main:app --reload[/bold {colors.neon_green}]  [{colors.text_muted}]# Start server[/{colors.text_muted}]"
    )

    panel = create_highlighted_panel(
        content,
        title="Next Steps",
        accent_color=colors.neon_pink,
        icon=":rocket:"
    )
    console.print(panel)
    console.print()


def save_config_file(project_path: Path, config: Dict[str, Any]) -> None:
    """
    保存配置文件到 .forge/config.json
    
    这是项目生成的第一步：
    1. init 命令收集用户配置
    2. 保存配置到 .forge/config.json
    3. ProjectGenerator 读取配置文件
    4. 根据配置生成项目代码
    
    Args:
        project_path: 项目路径
        config: 项目配置
    """
    from datetime import datetime
    import json
    from collections import OrderedDict
    
    # 创建 .forge 目录
    forge_dir = project_path / ".forge"
    forge_dir.mkdir(parents=True, exist_ok=True)
    
    # 按照 init 交互顺序构建配置
    # 1. 项目名称
    # 2. 数据库配置
    # 3. 功能配置
    # 4. 元数据
    ordered_config = OrderedDict()
    ordered_config["project_name"] = config.get("project_name")
    
    # 如果有数据库配置，放在 features 之前
    if "database" in config:
        ordered_config["database"] = config["database"]
    
    ordered_config["features"] = config.get("features")
    
    # 添加元数据
    ordered_config["metadata"] = {
        "created_at": datetime.now().isoformat(),
        "forge_version": "0.1.0"
    }
    
    # 保存配置文件
    config_file = forge_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(ordered_config, f, indent=2, ensure_ascii=False)


def execute_init(name: Optional[str] = None, interactive: bool = True) -> Dict[str, Any]:
    """
    执行init命令

    Args:
        name: 项目名称
        interactive: 是否使用交互式模式

    Returns:
        包含选择结果的字典
    """
    show_logo()

    style = create_questionary_style()

    if interactive:
        # 交互式模式
        name = collect_project_name(name, style)
        
        # 检查项目是否已存在
        user_cwd = Path.cwd()
        project_path = user_cwd / name
        
        if ProjectConfig.exists(project_path):
            colors = get_colors()
            console.print()
            console.print(
                f"[bold {colors.warning}]⚠️  Project '{name}' already exists![/bold {colors.warning}]"
            )
            
            # 加载现有配置
            existing_config = ProjectConfig.load(project_path)
            if existing_config:
                console.print(
                    f"[{colors.text_muted}]Found existing configuration from "
                    f"{existing_config.get('metadata', {}).get('created_at', 'unknown date')}[/{colors.text_muted}]"
                )
            
            console.print()
            
            # 询问用户如何处理
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Cancel - Keep existing project",
                    "Overwrite - Regenerate entire project",
                    "Update - Modify existing configuration"
                ],
                style=style
            ).ask()
            
            if not action or "Cancel" in action:
                console.print(f"\n[{colors.info}]Operation cancelled.[/{colors.info}]")
                raise typer.Exit(code=0)
            elif "Update" in action:
                console.print(f"\n[{colors.warning}]Update mode is not yet implemented.[/{colors.warning}]")
                console.print(f"[{colors.text_muted}]Please manually edit .forge/config.json or choose Overwrite.[/{colors.text_muted}]")
                raise typer.Exit(code=0)
            # 如果选择 Overwrite，继续执行
        
        database, orm, migration_tool = collect_database_config(style)
        features = collect_features(style, has_database=database is not None)
    else:
        # 非交互式模式使用默认值
        name = name or "my-fastapi-project"
        database = "PostgreSQL"
        orm = "SQLAlchemy"
        migration_tool = "Alembic"
        features = {
            "auth": {
                "type": "complete",
                "refresh_token": True,
                "features": ["Email Verification", "Password Reset", "Email Service"]
            },
            "cors": True,
            "dev_tools": True,
            "testing": True,
            "docker": True
        }
        user_cwd = Path.cwd()

    # 构建项目配置
    project_config = {
        "project_name": name,
        "features": features
    }
    
    # 只有选择了数据库才添加数据库配置
    if database:
        project_config["database"] = {
            "type": database,
            "orm": orm,
            "migration_tool": migration_tool
        }
    
    # 显示保存进度
    show_saving_progress(name)

    # 保存配置文件并生成项目
    try:
        # 创建项目目录
        project_path = user_cwd / name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # 保存配置文件到 .forge/config.json
        save_config_file(project_path, project_config)
        
        # 直接调用 ProjectGenerator 生成项目结构
        generator = ProjectGenerator(project_path)
        generator.config_reader.load_config()
        generator.config_reader.validate_config()
        generator.generate()
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

    # 显示配置摘要
    show_config_summary(name, database, orm, migration_tool, features)

    # 显示下一步操作
    show_next_steps(name)

    return {
        "project_name": name,
        "database": database,
        "orm": orm,
        "migration_tool": migration_tool,
        "features": features
    }


def init_command(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        "-i/-I",
        help="Interactive mode"
    )
):
    """
    Initialize a new FastAPI project

    A modern interactive project initialization tool to help you quickly set up a FastAPI project.
    """
    execute_init(name=name, interactive=interactive)
