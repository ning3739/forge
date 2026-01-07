"""loggingConfiguration file generator - generate Pydantic configurationclass"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=12,
    requires=["ConfigBaseGenerator"],
    description="Generate logger configuration (app/core/config/modules/logger.py)"
)
class ConfigLoggerGenerator(BaseTemplateGenerator):
    """generate app/core/config/modules/logger.py file - Pydantic loggingconfigurationclass"""
    
    def generate(self) -> None:
        """generateloggingconfigurationfile"""
        imports = [
            "from typing import Optional",
            "from pydantic import Field",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        content = '''class LoggingSettings(EnvBaseSettings):
    """Loguru loggingconfigurationSet"""
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    LOG_TO_FILE: bool = Field(
        default=False,
        description="Generate logger configuration (app/core/config/modules/logger.py)"
    )
    LOG_FILE_PATH: str = Field(
        default="logs/app.log",
        description="Generate logger configuration (app/core/config/modules/logger.py)"
    )
    LOG_TO_CONSOLE: bool = Field(
        default=True,
        description="Generate logger configuration (app/core/config/modules/logger.py)"
    )
    LOG_CONSOLE_LEVEL: str = Field(
        default="INFO",
        description="Generate logger configuration (app/core/config/modules/logger.py)"
    )
    LOG_ROTATION: Optional[str] = Field(
        default="1 day",
        description="Generate logger configuration (app/core/config/modules/logger.py)"
    )
    LOG_RETENTION_PERIOD: Optional[str] = Field(
        default="7 days",
        description="Generate logger configuration (app/core/config/modules/logger.py)"
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/logger.py",
            docstring="loggingconfigurationmodule",
            imports=imports,
            content=content,
            overwrite=True
        )
