"""loggingConfiguration file generator - generate Pydantic configurationclass"""
from ..base import BaseTemplateGenerator


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
        description="Whether to write logging to file"
    )
    LOG_FILE_PATH: str = Field(
        default="logs/app.log",
        description="loggingFile path"
    )
    LOG_TO_CONSOLE: bool = Field(
        default=True,
        description="Whether to output to console"
    )
    LOG_CONSOLE_LEVEL: str = Field(
        default="INFO",
        description="Console logging level"
    )
    LOG_ROTATION: Optional[str] = Field(
        default="1 day",
        description="Log rotation period, supports formats: '1 day', '500 MB', '10:00', etc."
    )
    LOG_RETENTION_PERIOD: Optional[str] = Field(
        default="7 days",
        description="Log retention period, log files older than this will be automatically deleted, supports formats: '7 days', '1 week', '1 month', etc."
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/logger.py",
            docstring="loggingconfigurationmodule",
            imports=imports,
            content=content,
            overwrite=True
        )
