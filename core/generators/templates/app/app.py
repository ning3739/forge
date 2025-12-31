"""应用配置文件生成器"""
from ..base import BaseTemplateGenerator


class ConfigAppGenerator(BaseTemplateGenerator):
    """生成 app/core/config/modules/app.py 文件"""
    
    def generate(self) -> None:
        """生成应用配置文件"""
        project_name = self.config_reader.get_project_name()
        
        imports = [
            "from pydantic import Field",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        content = f'''class AppSettings(EnvBaseSettings):
    """Application metadata configuration"""
    
    APP_NAME: str = Field(
        default="{project_name}",
        description="Application name"
    )
    APP_DESCRIPTION: str = Field(
        default="{project_name} is a FastAPI application.",
        description="Application description",
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        description="Application version"
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/app.py",
            docstring="应用配置模块",
            imports=imports,
            content=content,
            overwrite=True
        )
