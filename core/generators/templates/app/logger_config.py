"""日志配置文件生成器 - 生成 Pydantic 配置类"""
from ..base import BaseTemplateGenerator


class ConfigLoggerGenerator(BaseTemplateGenerator):
    """生成 app/core/config/modules/logger.py 文件 - Pydantic 日志配置类"""
    
    def generate(self) -> None:
        """生成日志配置文件"""
        imports = [
            "from typing import Optional",
            "from pydantic import Field",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        content = '''class LoggingSettings(EnvBaseSettings):
    """Loguru 日志配置设置"""
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )
    LOG_TO_FILE: bool = Field(
        default=False,
        description="是否将日志写入文件"
    )
    LOG_FILE_PATH: str = Field(
        default="logs/app.log",
        description="日志文件路径"
    )
    LOG_TO_CONSOLE: bool = Field(
        default=True,
        description="是否输出到控制台"
    )
    LOG_CONSOLE_LEVEL: str = Field(
        default="INFO",
        description="控制台日志级别"
    )
    LOG_ROTATION: Optional[str] = Field(
        default="1 day",
        description="日志轮转周期，支持格式: '1 day', '500 MB', '10:00' 等"
    )
    LOG_RETENTION_PERIOD: Optional[str] = Field(
        default="7 days",
        description="日志保留期，超过此时间的日志文件会被自动删除，支持格式: '7 days', '1 week', '1 month' 等"
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/logger.py",
            docstring="日志配置模块",
            imports=imports,
            content=content,
            overwrite=True
        )
