"""配置基类文件生成器"""
from ..base import BaseTemplateGenerator


class ConfigBaseGenerator(BaseTemplateGenerator):
    """生成 app/core/config/base.py 文件"""
    
    def generate(self) -> None:
        """生成配置基类文件"""
        imports = [
            "import os",
            "from pathlib import Path",
            "from dotenv import load_dotenv",
            "from pydantic_settings import BaseSettings",
        ]
        
        content = '''# Load environment variables from .env file
ENV = os.getenv("ENV", "development")

# Calculate path to project root (3 levels up from config/base.py)
ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / f"secret/.env.{ENV}"

# Try to load environment file if it exists, otherwise use system environment variables
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    import warnings
    warnings.warn(
        f"Environment file {ENV_FILE} does not exist. "
        "Using system environment variables.",
        UserWarning
    )


class EnvBaseSettings(BaseSettings):
    """Base settings class that loads environment variables.
    
    All settings should inherit from this class.
    """
    
    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields not defined in the model
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/base.py",
            docstring="配置基类 - 所有配置类的基类",
            imports=imports,
            content=content,
            overwrite=True
        )
