"""Base template generator"""
from pathlib import Path
from core.config_reader import ConfigReader
from core.utils import FileOperations


class BaseTemplateGenerator:
    """Base generator class for all code generators"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """
        Initialize base generator
        
        Args:
            project_path: Project root directory path
            config_reader: Configuration reader instance
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)
    
    def generate(self) -> None:
        """generate files - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate() method")
