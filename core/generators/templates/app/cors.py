"""CORS Configuration file generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=14,
    requires=["ConfigBaseGenerator"],
    enabled_when=lambda c: c.has_cors(),
    description="Generate CORS configuration (app/core/config/modules/cors.py)"
)
class ConfigCorsGenerator(BaseTemplateGenerator):
    """generate app/core/config/modules/cors.py file"""
    
    def generate(self) -> None:
        """generate CORS configurationfile"""
        # onlyenable CORS whengenerate
        if not self.config_reader.has_cors():
            return
        
        imports = [
            "from pydantic import Field",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        content = '''class CORSSettings(EnvBaseSettings):
    """CORS (Cross-Origin Resource Sharing) configuration"""
    
    CORS_ALLOWED_ORIGINS: str = Field(
        default='https://heyxiaoli.com',
        description="Allowed CORS origins (comma-separated)",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Generate CORS configuration (app/core/config/modules/cors.py)"
    )
    CORS_ALLOW_METHODS: str = Field(
        default='GET,POST,PUT,DELETE,PATCH,OPTIONS,HEAD,TRACE,CONNECT',
        description="Allowed HTTP methods (comma-separated)",
    )
    CORS_ALLOW_HEADERS: str = Field(
        default='Authorization,Content-Type,X-Language,Accept-Language',
        description="Allowed HTTP headers (comma-separated)",
    )
    CORS_EXPOSE_HEADERS: str = Field(
        default='Content-Disposition,Content-Length,Content-Type,ETag,Last-Modified',
        description="Exposed HTTP headers (comma-separated)",
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/cors.py",
            docstring="CORS configurationmodule",
            imports=imports,
            content=content,
            overwrite=True
        )
