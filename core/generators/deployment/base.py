"""部署配置生成器基类"""
from pathlib import Path
from typing import Optional


class DeploymentFileGenerator:
    """部署配置文件生成器基类"""
    
    def __init__(self, project_path: Path):
        """初始化部署配置生成器
        
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
    
    def generate(self, content: str, filename: str, subdir: Optional[str] = None) -> Path:
        """生成部署配置文件
        
        Args:
            content: 文件内容
            filename: 文件名
            subdir: 子目录（可选）
            
        Returns:
            生成的文件路径
        """
        if subdir:
            target_dir = self.project_path / subdir
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / filename
        else:
            file_path = self.project_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
