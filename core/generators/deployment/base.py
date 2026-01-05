"""Deployment configurationgenerategeneratorbase class"""
from pathlib import Path
from typing import Optional


class DeploymentFileGenerator:
    """deploymentConfiguration file generator base class"""
    
    def __init__(self, project_path: Path):
        """InitializeDeployment configurationgenerategenerator
        
        Args:
            project_path: Project root directory path
        """
        self.project_path = Path(project_path)
    
    def generate(self, content: str, filename: str, subdir: Optional[str] = None) -> Path:
        """generateDeployment configurationfile
        
        Args:
            content: File content
            filename: File name
            subdir: Subdirectory(optional)
            
        Returns:
            generateFile path
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
