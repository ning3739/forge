"""Project configuration utility class"""
import json
from pathlib import Path
from typing import Optional, Dict, Any


class ProjectConfig:
    """Project configuration utility class"""
    
    @staticmethod
    def exists(project_path: Path) -> bool:
        """
        Check if project configuration exists
        
        Args:
            project_path: Project path
        
        Returns:
            Whether configuration file exists
        """
        return (project_path / ".forge" / "config.json").exists()
    
    @staticmethod
    def load(project_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load project configuration
        
        Args:
            project_path: Project path
        
        Returns:
            Configuration dictionary, or None if not exists or invalid
        """
        config_file = project_path / ".forge" / "config.json"
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
