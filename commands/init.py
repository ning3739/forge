"""Init command module"""
import json
import time
import typer
import questionary
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from collections import OrderedDict
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live

from ui.logo import show_logo
from ui.components import (
    create_gradient_bar,
    create_highlighted_panel,
    create_questionary_style,
    console
)
from ui.colors import get_colors
from core.utils.version_checker import check_for_updates
from core.version import __version__
from core.utils import ProjectConfig
from core.project_generator import ProjectGenerator


# ============================================================================
# Constants
# ============================================================================

DATABASE_CHOICES = [
    "PostgreSQL (Recommended)",
    "MySQL", 
    "SQLite (Development/Small Projects)"
]

ORM_CHOICES = [
    "SQLModel (Recommended)",
    "SQLAlchemy"
]

AUTH_CHOICES = [
    "Complete JWT Auth (Recommended)",
    "Basic JWT Auth (login/register only)"
]

DEFAULT_NON_INTERACTIVE_CONFIG = {
    "database": "MySQL",
    "orm": "SQLModel",
    "migration_tool": "Alembic",
    "features": {
        "auth": {
            "type": "complete",
            "refresh_token": True,
            "features": ["Email Verification", "Password Reset", "Email Service"]
        },
        "cors": True,
        "dev_tools": True,
        "testing": True,
        "docker": True,
        "redis": True,
        "celery": True
    }
}


# ============================================================================
# Helper Functions
# ============================================================================

def extract_choice(choice: str, default: str = "") -> str:
    """Extract actual value from choice (remove description in parentheses)"""
    return choice.split(" (")[0] if choice else default


def get_auth_config(auth_type: str) -> Dict[str, Any]:
    """generate configuration based on authentication type"""
    if "Complete" in auth_type:
        return {
            "type": "complete",
            "refresh_token": True,
            "features": ["Email Verification", "Password Reset", "Email Service"]
        }
    else:
        return {
            "type": "basic",
            "refresh_token": False,
            "features": []
        }


# ============================================================================
# Configuration Collection
# ============================================================================

def collect_project_name(name: Optional[str], style: questionary.Style) -> str:
    """Collect project name"""
    if name:
        return name
    return questionary.text(
        "Project name:",
        default="forge-project",
        style=style
    ).ask() or "forge-project"


def collect_database_config(style: questionary.Style) -> tuple[str, str, Optional[str]]:
    """Collect database configuration
    
    Returns:
        (database_type, orm_type, migration_tool)
    """
    database = extract_choice(
        questionary.select("Database:", choices=DATABASE_CHOICES, style=style).ask(),
        "PostgreSQL"
    )
    
    orm = extract_choice(
        questionary.select("ORM:", choices=ORM_CHOICES, style=style).ask(),
        "SQLModel"
    )
    
    enable_migration = questionary.confirm(
        "Enable database migrations (Alembic)?",
        default=True,
        auto_enter=True,
        style=style
    ).ask()
    
    migration_tool = "Alembic" if enable_migration else None
    return database, orm, migration_tool


def collect_features(style: questionary.Style) -> Dict[str, Any]:
    """Collect feature configuration"""
    auth_choice = questionary.select(
        "Authentication:",
        choices=AUTH_CHOICES,
        style=style
    ).ask()
    
    # Redis configuration
    enable_redis = questionary.confirm(
        "Enable Redis (caching, sessions, queues)?", 
        default=True,
        auto_enter=True,
        style=style
    ).ask()
    
    # Ask about Celery only if Redis is enabled (Celery needs a message broker)
    enable_celery = False
    if enable_redis:
        enable_celery = questionary.confirm(
            "Enable Celery (background tasks, job queues)?",
            default=True,
            auto_enter=True,
            style=style
        ).ask()
    
    # Show auth info after Redis/Celery questions
    auth_config = get_auth_config(auth_choice)
    
    features = {
        "auth": auth_config,
        "cors": questionary.confirm("Enable CORS?", default=True, auto_enter=True, style=style).ask(),
        "dev_tools": questionary.confirm("Include dev tools (Black + Ruff)?", default=True, auto_enter=True, style=style).ask(),
        "testing": questionary.confirm("Include testing setup (pytest)?", default=True, auto_enter=True, style=style).ask(),
        "docker": questionary.confirm("Include Docker configs?", default=True, auto_enter=True, style=style).ask()
    }
    
    # Add Redis and Celery to features if enabled
    if enable_redis:
        features["redis"] = True
    
    if enable_celery:
        features["celery"] = True
    
    return features


# ============================================================================
# Project Handling
# ============================================================================

def handle_existing_project(name: str, style: questionary.Style) -> bool:
    """Handle existing project
    
    Returns:
        True to continue, False to cancel
    """
    colors = get_colors()
    console.print()
    console.print(
        f"[bold {colors.warning}]⚠️  Project '{name}' already exists![/bold {colors.warning}]"
    )
    
    # Load existing configuration
    user_cwd = Path.cwd()
    project_path = user_cwd / name
    existing_config = ProjectConfig.load(project_path)
    if existing_config:
        console.print(
            f"[{colors.text_muted}]Found existing configuration from "
            f"{existing_config.get('metadata', {}).get('created_at', 'unknown date')}[/{colors.text_muted}]"
        )
    
    console.print()
    
    # Ask user how to handle
    action = questionary.select(
        "What would you like to do?",
        choices=[
            "Cancel - Keep existing project",
            "Overwrite - Regenerate entire project"
        ],
        style=style
    ).ask()
    
    if not action or "Cancel" in action:
        console.print(f"\n[{colors.info}]Operation cancelled.[/{colors.info}]")
        raise typer.Exit(code=0)
    elif "Overwrite" in action:
        # Remove existing project directory
        import shutil
        project_path = Path.cwd() / name
        try:
            console.print(f"\n[{colors.warning}]Removing existing project...[/{colors.warning}]")
            shutil.rmtree(project_path)
            console.print(f"[{colors.success}]✅ Existing project removed.[/{colors.success}]")
        except Exception as e:
            console.print(f"\n[bold red]Error removing existing project:[/bold red] {str(e)}")
            raise typer.Exit(code=1)
    
    return True  # Continue with project generation


def build_project_config(name: str, database: str, orm: str, migration_tool: Optional[str], features: Dict[str, Any]) -> Dict[str, Any]:
    """Build project configuration dictionary"""
    return {
        "project_name": name,
        "database": {
            "type": database,
            "orm": orm,
            "migration_tool": migration_tool
        },
        "features": features
    }


def save_config_file(project_path: Path, config: Dict[str, Any]) -> None:
    """Save configuration file to .forge/config.json"""
    # Create .forge directory
    forge_dir = project_path / ".forge"
    forge_dir.mkdir(parents=True, exist_ok=True)
    
    # Build configuration in init interaction order
    ordered_config = OrderedDict()
    ordered_config["project_name"] = config.get("project_name")
    
    if "database" in config:
        ordered_config["database"] = config["database"]
    
    ordered_config["features"] = config.get("features")
    
    # Add metadata
    ordered_config["metadata"] = {
        "created_at": datetime.now().isoformat(),
        "forge_version": __version__
    }
    
    # Save configuration file
    config_file = forge_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(ordered_config, f, indent=2, ensure_ascii=False)


def generate_project(project_path: Path, config: Dict[str, Any]) -> None:
    """generate project structure and code"""
    try:
        # Save configuration file to .forge/config.json
        save_config_file(project_path, config)
        
        # Call ProjectGenerator to generate project structure
        generator = ProjectGenerator(project_path)
        generator.config_reader.load_config()
        generator.config_reader.validate_config()
        generator.generate()
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


# ============================================================================
# Progress and Display
# ============================================================================

def show_saving_progress(name: str) -> None:
    """Show progress for saving configuration and generating project"""
    colors = get_colors()
    create_gradient_bar("rainbow")

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

    steps = [
        "Creating project directory",
        "Saving configuration",
        "Creating project structure",
        "Generating code files",
        "Generating configuration files"
    ]

    with Live(progress, refresh_per_second=10):
        for step in steps:
            task = progress.add_task(step, total=100)
            for _ in range(100):
                progress.update(task, advance=1)
                time.sleep(0.008)
            progress.remove_task(task)


def build_config_summary_lines(name: str, database: str, orm: str, migration_tool: Optional[str], features: Dict[str, Any]) -> list[str]:
    """Build configuration summary lines"""
    colors = get_colors()
    lines = [
        f"[bold {colors.primary_light}]Project:[/bold {colors.primary_light}] "
        f"[bold {colors.text_primary}]{name}[/bold {colors.text_primary}]",
        f"[bold {colors.primary_light}]Database:[/bold {colors.primary_light}] "
        f"[{colors.secondary}]{database} with {orm}[/{colors.secondary}]"
    ]
    
    if migration_tool:
        lines.append(
            f"[bold {colors.primary_light}]Migration:[/bold {colors.primary_light}] "
            f"[{colors.secondary}]{migration_tool}[/{colors.secondary}]"
        )

    # Authentication configuration
    auth_config = features.get("auth", {})
    auth_type = "Complete JWT Auth" if auth_config.get("type") == "complete" else "Basic JWT Auth"
    refresh_token = " (with Refresh Token)" if auth_config.get("refresh_token") else ""
    lines.append(
        f"[bold {colors.primary}]Authentication:[/bold {colors.primary}] "
        f"[dim]{auth_type}{refresh_token}[/dim]"
    )
    
    if auth_config.get("type") == "complete":
        auth_features = auth_config.get("features", [])
        if auth_features:
            lines.append(
                f"[{colors.text_muted}]  • {', '.join(auth_features)}[/{colors.text_muted}]"
            )

    # Redis and Celery configuration
    redis_enabled = features.get("redis", False)
    celery_enabled = features.get("celery", False)
    
    if redis_enabled or celery_enabled:
        cache_queue_items = []
        if redis_enabled:
            cache_queue_items.append("Redis")
        if celery_enabled:
            cache_queue_items.append("Celery")
        
        lines.append(
            f"[bold {colors.warning}]Cache & Queues:[/bold {colors.warning}] "
            f"[dim]{', '.join(cache_queue_items)}[/dim]"
        )

    # Security configuration
    security_items = ["Input Validation", "Password Hashing"]
    if features.get("cors"):
        security_items.insert(0, "CORS")
    
    lines.append(
        f"[bold {colors.neon_green}]Security:[/bold {colors.neon_green}] "
        f"[dim]{', '.join(security_items)}[/dim]"
    )

    # Development tools
    if features.get("dev_tools"):
        lines.append(
            f"[bold {colors.secondary}]Dev Tools:[/bold {colors.secondary}] "
            f"[dim]API Docs, Black, Ruff[/dim]"
        )

    # Testing
    if features.get("testing"):
        lines.append(
            f"[bold {colors.info}]Testing:[/bold {colors.info}] "
            f"[dim]pytest, httpx, coverage[/dim]"
        )

    # Deployment
    if features.get("docker"):
        lines.append(
            f"[bold {colors.accent}]Deployment:[/bold {colors.accent}] "
            f"[dim]Docker, Docker Compose[/dim]"
        )
    
    return lines


def show_config_summary(name: str, database: str, orm: str, migration_tool: Optional[str], features: Dict[str, Any]) -> None:
    """Show configuration summary"""
    colors = get_colors()
    console.print()

    lines = build_config_summary_lines(name, database, orm, migration_tool, features)
    panel = create_highlighted_panel(
        "\n".join(lines),
        title="Configuration Summary",
        accent_color=colors.neon_pink,
        icon=":package:"
    )
    console.print(panel)
    
    # Show email configuration warning for Complete JWT Auth
    auth_config = features.get("auth", {})
    if auth_config.get("type") == "complete":
        show_email_config_warning()


def show_email_config_warning() -> None:
    """Show email configuration warning"""
    colors = get_colors()
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


def show_next_steps(name: str, features: Dict[str, Any]) -> None:
    """Show next steps"""
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
        f"[bold {colors.neon_green}]uv run uvicorn app.main:app --reload[/bold {colors.neon_green}]  [{colors.text_muted}]# Start server[/{colors.text_muted}]"
    )
    
    # Add Celery instructions if enabled
    celery_enabled = features.get("celery", False)
    if isinstance(celery_enabled, bool) and celery_enabled:
        content += (
            f"\n\n[{colors.text_muted}]For background tasks (Celery):[/{colors.text_muted}]\n"
            f"[bold {colors.warning}]uv run celery -A app.core.celery.celery_app worker --loglevel=info[/bold {colors.warning}]  [{colors.text_muted}]# Start Celery worker[/{colors.text_muted}]\n"
            f"[bold {colors.secondary}]uv run celery -A app.core.celery.celery_app flower[/bold {colors.secondary}]  [{colors.text_muted}]# Start monitoring (optional)[/{colors.text_muted}]"
        )
    elif isinstance(celery_enabled, dict) and celery_enabled.get("enabled", False):
        # Support legacy format
        content += (
            f"\n\n[{colors.text_muted}]For background tasks (Celery):[/{colors.text_muted}]\n"
            f"[bold {colors.warning}]uv run celery -A app.core.celery.celery_app worker --loglevel=info[/bold {colors.warning}]  [{colors.text_muted}]# Start Celery worker[/{colors.text_muted}]\n"
            f"[bold {colors.secondary}]uv run celery -A app.core.celery.celery_app flower[/bold {colors.secondary}]  [{colors.text_muted}]# Start monitoring (optional)[/{colors.text_muted}]"
        )

    panel = create_highlighted_panel(
        content,
        title="🚀  Next Steps",
        accent_color=colors.neon_pink,
        icon=":rocket:"
    )
    console.print(panel)
    console.print()


# ============================================================================
# Main Execution
# ============================================================================

def execute_init(name: Optional[str] = None, interactive: bool = True) -> Dict[str, Any]:
    """Execute init command"""
    show_logo()
    
    # Check for updates at the start of init command (interactive mode)
    check_for_updates(silent=False, interactive=interactive)
    
    style = create_questionary_style()

    if interactive:
        # Interactive mode
        name = collect_project_name(name, style)
        
        # Check if project already exists
        user_cwd = Path.cwd()
        project_path = user_cwd / name
        
        if ProjectConfig.exists(project_path):
            handle_existing_project(name, style)
        
        database, orm, migration_tool = collect_database_config(style)
        features = collect_features(style)
    else:
        # Non-interactive mode uses defaults
        name = name or "my-fastapi-project"
        database = DEFAULT_NON_INTERACTIVE_CONFIG["database"]
        orm = DEFAULT_NON_INTERACTIVE_CONFIG["orm"]
        migration_tool = DEFAULT_NON_INTERACTIVE_CONFIG["migration_tool"]
        features = DEFAULT_NON_INTERACTIVE_CONFIG["features"]
        user_cwd = Path.cwd()

    # Build project configuration
    project_config = build_project_config(name, database, orm, migration_tool, features)
    
    # Show saving progress
    show_saving_progress(name)

    # generate project
    project_path = user_cwd / name
    project_path.mkdir(parents=True, exist_ok=True)
    generate_project(project_path, project_config)

    # Show configuration summary and next steps
    show_config_summary(name, database, orm, migration_tool, features)
    show_next_steps(name, features)

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
    """Initialize a new FastAPI project"""
    execute_init(name=name, interactive=interactive)
