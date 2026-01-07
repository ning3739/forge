"""Project generator module"""
from pathlib import Path
from core.config_reader import ConfigReader
from .generators.structure import StructureGenerator
from .generators.orchestrator import GeneratorOrchestrator


class ProjectGenerator:
    """Project generator - generates FastAPI project based on configuration"""

    def __init__(self, project_path: Path):
        """Initialize project generator
        
        Args:
            project_path: Project root directory path
        """
        self.project_path = Path(project_path)
        self.config_reader = ConfigReader(project_path)
        self.structure_generator = StructureGenerator(project_path, self.config_reader)
        self.orchestrator = None  # Delay initialization until config is loaded

    def generate(self) -> None:
        """generate project structure and code"""
        # 1. Create directory structure
        self.structure_generator.create_project_structure()
        
        # 2. Initialize orchestrator after config is loaded
        self.orchestrator = GeneratorOrchestrator(self.project_path, self.config_reader)
        
        # 3. Generate all files using orchestrator
        self.orchestrator.generate()
