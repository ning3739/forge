"""Docker 命令模块"""
from pathlib import Path
import typer
from rich.console import Console

from core.config_reader import ConfigReader
from core.generators.deployment.dockerfile import DockerfileGenerator
from core.generators.deployment.docker_compose import DockerComposeGenerator
from core.generators.deployment.dockerignore import DockerignoreGenerator

console = Console()


def docker_command(
    path: Path = typer.Argument(
        Path.cwd(),
        help="项目路径"
    )
):
    """为现有项目生成 Docker 配置文件"""
    
    try:
        # 检查配置文件
        config_reader = ConfigReader(path)
        config_reader.load_config()
        
        # 检查是否启用了 Docker
        if not config_reader.has_docker():
            console.print("[yellow]⚠️  项目配置中未启用 Docker[/yellow]")
            console.print("请在 .forge/config.json 中设置 'docker': true")
            raise typer.Exit(1)
        
        # 生成 Docker 文件
        console.print("[cyan]📦 正在生成 Docker 配置文件...[/cyan]")
        
        DockerfileGenerator(path, config_reader).generate()
        console.print("  ✓ Dockerfile")
        
        DockerComposeGenerator(path, config_reader).generate()
        console.print("  ✓ docker-compose.yml")
        
        DockerignoreGenerator(path, config_reader).generate()
        console.print("  ✓ .dockerignore")
        
        console.print("\n[green]✅ Docker 配置文件生成成功！[/green]")
        
        # 显示使用说明
        console.print("\n[cyan]使用方法：[/cyan]")
        console.print("  docker-compose up -d    # 启动服务")
        console.print("  docker-compose logs -f  # 查看日志")
        console.print("  docker-compose down     # 停止服务")
        
    except FileNotFoundError as e:
        console.print(f"[red]❌ 错误: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ 生成失败: {e}[/red]")
        raise typer.Exit(1)
