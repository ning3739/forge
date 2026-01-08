"""Version checker utility"""
import json
import urllib.request
import urllib.error
import subprocess
import sys
from typing import Optional, Tuple
from packaging import version
from core.version import __version__
from ui.colors import get_colors, console
import questionary


def get_latest_version() -> Optional[str]:
    """Get latest version from PyPI"""
    try:
        with urllib.request.urlopen(
            "https://pypi.org/pypi/ningfastforge/json", 
            timeout=3
        ) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError):
        return None


def compare_versions(current: str, latest: str) -> Tuple[bool, str]:
    """Compare current and latest versions
    
    Returns:
        Tuple of (is_outdated, comparison_result)
    """
    try:
        current_ver = version.parse(current.lstrip('v'))
        latest_ver = version.parse(latest.lstrip('v'))
        
        if current_ver < latest_ver:
            return True, f"{current} < {latest}"
        elif current_ver > latest_ver:
            return False, f"{current} > {latest} (dev version)"
        else:
            return False, f"{current} = {latest} (up to date)"
    except Exception:
        return False, "Unable to compare versions"


def auto_update() -> bool:
    """Attempt to auto-update the package
    
    Returns:
        True if update was successful, False otherwise
    """
    try:
        console.print("[yellow]🔄 Updating Forge...[/yellow]")
        
        # Try different update commands based on how it was installed
        update_commands = [
            [sys.executable, "-m", "pip", "install", "--upgrade", "ningfastforge"],
            ["pip", "install", "--upgrade", "ningfastforge"],
            ["pip3", "install", "--upgrade", "ningfastforge"],
        ]
        
        for cmd in update_commands:
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                if result.returncode == 0:
                    console.print("[green]✅ Update successful![/green]")
                    console.print("[dim]Please restart the command to use the new version.[/dim]")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        console.print("[red]❌ Auto-update failed. Please update manually:[/red]")
        console.print("[bold]pip install --upgrade ningfastforge[/bold]")
        return False
        
    except Exception as e:
        console.print(f"[red]❌ Update error: {e}[/red]")
        return False


def check_for_updates(silent: bool = False, interactive: bool = True) -> bool:
    """Check for updates and optionally show notification
    
    Args:
        silent: If True, don't show any output
        interactive: If True, offer to auto-update
        
    Returns:
        True if update is available, False otherwise
    """
    latest = get_latest_version()
    if not latest:
        if not silent:
            console.print("[dim yellow]⚠️  Unable to check for updates[/dim yellow]")
        return False
    
    is_outdated, comparison = compare_versions(__version__, latest)
    
    if is_outdated and not silent:
        if interactive:
            show_interactive_update_prompt(latest)
        else:
            show_update_notification(latest)
    
    return is_outdated


def show_interactive_update_prompt(latest_version: str) -> None:
    """Show interactive update prompt with auto-update option"""
    colors = get_colors()
    
    console.print()
    console.print(f"[bold {colors.warning}]📦 Update Available![/bold {colors.warning}]")
    console.print(f"[{colors.text_secondary}]Current version:[/{colors.text_secondary}] [bold]{__version__}[/bold]")
    console.print(f"[{colors.text_secondary}]Latest version:[/{colors.text_secondary}] [bold {colors.success}]{latest_version}[/bold {colors.success}]")
    console.print()
    
    try:
        # Ask user if they want to update now
        choice = questionary.select(
            "Would you like to update now?",
            choices=[
                "✅ Yes, update automatically",
                "📋 No, show me the command",
                "⏭️  Skip for now"
            ],
            style=questionary.Style([
                ('question', 'bold'),
                ('pointer', 'fg:#8B5CF6 bold'),
                ('highlighted', 'fg:#8B5CF6 bold'),
                ('selected', 'fg:#A855F7'),
                ('answer', 'fg:#C084FC bold')
            ])
        ).ask()
        
        if choice == "✅ Yes, update automatically":
            success = auto_update()
            if success:
                console.print("[bold green]🎉 Update completed! Please restart your command.[/bold green]")
                sys.exit(0)
        elif choice == "📋 No, show me the command":
            show_update_notification(latest_version)
        # For "Skip for now", just continue
        
    except (KeyboardInterrupt, EOFError):
        # User pressed Ctrl+C or similar, just show the manual command
        console.print()
        show_update_notification(latest_version)


def show_update_notification(latest_version: str) -> None:
    """Show update notification"""
    colors = get_colors()
    
    console.print(f"[{colors.text_secondary}]To update, run:[/{colors.text_secondary}]")
    console.print(f"[bold {colors.primary}]pip install --upgrade ningfastforge[/bold {colors.primary}]")
    console.print()