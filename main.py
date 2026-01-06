"""Forge CLI Main Entry Point"""
import warnings
import typer
from typing import Optional

# Disable urllib3 OpenSSL warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

from ui.logo import show_logo
from commands.init import init_command

# Version constant
VERSION = "0.1.2"

# Create main application
app = typer.Typer(
    name="forge",
    help="Forge - A modern FastAPI project scaffolding CLI tool",
    rich_markup_mode="rich",
    add_completion=False
)

# Register commands
app.command(name="init", help="Initialize a new FastAPI project")(init_command)


def version_callback(value: bool) -> None:
    """Version information callback"""
    if value:
        typer.echo(f"Forge CLI v{VERSION}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        callback=version_callback,
        is_eager=True
    )
):
    """
    Forge CLI Tool

    A powerful FastAPI project scaffolding generator
    """
    if ctx.invoked_subcommand is None:
        show_logo()
        typer.echo()  # Empty line
        typer.echo(ctx.get_help())  # Show help information


def main():
    """Main entry function"""
    app()


if __name__ == "__main__":
    main()
