"""applicationConfiguration file generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=11,
    requires=["ConfigBaseGenerator"],
    description="Generate app/core/config/modules/app.py"
)
class ConfigAppGenerator(BaseTemplateGenerator):
    """generate app/core/config/modules/app.py file"""
    
    def generate(self) -> None:
        """generateapplicationconfigurationfile"""
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
            docstring="applicationconfigurationmodule",
            imports=imports,
            content=content,
            overwrite=True
        )
