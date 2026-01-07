"""Logger Manager generategenerator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=13,
    requires=["ConfigLoggerGenerator"],
    description="Generate logger manager (app/core/logger.py)"
)
class LoggerManagerGenerator(BaseTemplateGenerator):
    """generate app/core/logger.py file - Logger managementgenerator"""
    
    def generate(self) -> None:
        """generate Logger Manager file"""
        imports = [
            "import sys",
            "import logging",
            "from pathlib import Path",
            "from typing import Optional",
            "from loguru import logger",
            "",
            "from app.core.config.settings import settings",
        ]
        
        content = '''class LoggerManager:
    """Logging management generator
    
    Use Loguru as logging library, provides unified logging management interface
    """
    
    def __init__(self):
        self._initialized = False
        self._loggers = {}
    
    def setup(self) -> None:
        """Initializeloggingconfiguration"""
        if self._initialized:
            return
        
        # removedefault handler
        logger.remove()
        
        # Console output
        if settings.logging.LOG_TO_CONSOLE:
            logger.add(
                sys.stdout,
                level=settings.logging.LOG_CONSOLE_LEVEL,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                       "<level>{message}</level>",
                colorize=True,
            )
        
        # fileoutput
        if settings.logging.LOG_TO_FILE:
            log_path = Path(settings.logging.LOG_FILE_PATH)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                settings.logging.LOG_FILE_PATH,
                level=settings.logging.LOG_LEVEL,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                rotation=settings.logging.LOG_ROTATION,
                retention=settings.logging.LOG_RETENTION_PERIOD,
                compression="zip",
                encoding="utf-8",
            )
        
        # Intercept standard library logging
        self._intercept_standard_logging()
        
        self._initialized = True
        logger.info("Logger initialized successfully")
    
    def _intercept_standard_logging(self) -> None:
        """Intercept standard library logging, redirect to Loguru"""
        
        class InterceptHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                # Get corresponding Loguru level
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno
                
                # Find caller
                frame, depth = logging.currentframe(), 2
                while frame.f_code.co_filename == logging.__file__:
                    frame = frame.f_back
                    depth += 1
                
                logger.opt(depth=depth, exception=record.exc_info).log(
                    level, record.getMessage()
                )
        
        # Intercept standard library logging
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        
        # Intercept common library logging
        for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
            logging.getLogger(logger_name).handlers = [InterceptHandler()]
    
    def get_logger(self, name: Optional[str] = None):
        """Get logger instance
        
        Args:
            name: Logger name, usually use __name__
        
        Returns:
            logger instance
        """
        if not self._initialized:
            self.setup()
        
        if name:
            return logger.bind(name=name)
        return logger


# Createglobalsingleton
logger_manager = LoggerManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/logger.py",
            docstring="Logger managementgeneratormodule",
            imports=imports,
            content=content,
            overwrite=True
        )
