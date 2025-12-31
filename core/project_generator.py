"""项目生成器模块"""
from pathlib import Path

from core.config_reader import ConfigReader
from .generators.structure import StructureGenerator


class ProjectGenerator:
    """项目生成器类

    负责根据配置文件生成 FastAPI 项目结构和代码
    """

    def __init__(self, project_path: Path):
        """初始化项目生成器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.config_reader = ConfigReader(project_path)
        self.structure_generator = StructureGenerator(
            project_path, self.config_reader)

    def generate(self) -> None:
        """生成项目

        主要流程：
        1. 读取并验证配置文件
        2. 生成项目结构
        3. 生成代码文件
        4. 生成配置文件
        """
        # 1. 读取并验证配置
        self.config_reader.load_config()
        self.config_reader.validate_config()

        # 2. 生成项目结构
        self._create_project_structure()

    def _create_project_structure(self) -> None:
        """创建项目目录结构"""
        self.structure_generator.create_project_structure()
