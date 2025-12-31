"""项目配置工具类"""
import json
from pathlib import Path
from typing import Optional, Dict, Any


class ProjectConfig:
    """项目配置工具类"""
    
    @staticmethod
    def exists(project_path: Path) -> bool:
        """
        检查项目配置是否存在
        
        Args:
            project_path: 项目路径
        
        Returns:
            配置文件是否存在
        """
        return (project_path / ".forge" / "config.json").exists()
    
    @staticmethod
    def load(project_path: Path) -> Optional[Dict[str, Any]]:
        """
        加载项目配置
        
        Args:
            project_path: 项目路径
        
        Returns:
            配置字典，如果不存在或无效则返回 None
        """
        config_file = project_path / ".forge" / "config.json"
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
