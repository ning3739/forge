"""configurationbase classFile generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=10,
    description="Generate app/core/config/base.py"
)
class ConfigBaseGenerator(BaseTemplateGenerator):
    """generate app/core/config/base.py file"""
    
    def generate(self) -> None:
        """generateconfigurationbase classfile"""
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
            docstring="configurationbase class - allconfigurationclassbase class",
            imports=imports,
            content=content,
            overwrite=True
        )
