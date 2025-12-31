"""基础模板生成器"""
from pathlib import Path
from abc import ABC, abstractmethod
from core.utils import FileOperations
from core.config_reader import ConfigReader


class BaseTemplateGenerator(ABC):
    """基础模板生成器抽象类"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """初始化模板生成器
        
        Args:
            project_path: 项目根目录路径
            config_reader: 配置读取器实例
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)
    
    @abstractmethod
    def generate(self) -> None:
        """生成文件 - 子类必须实现"""
        pass
