"""CORS 配置文件生成器"""
from ..base import BaseTemplateGenerator


class ConfigCorsGenerator(BaseTemplateGenerator):
    """生成 app/core/config/modules/cors.py 文件"""
    
    def generate(self) -> None:
        """生成 CORS 配置文件"""
        # 只有启用 CORS 时才生成
        if not self.config_reader.has_cors():
            return
        
        imports = [
            "from pydantic import Field",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        content = '''class CORSSettings(EnvBaseSettings):
    """CORS (Cross-Origin Resource Sharing) 配置"""
    
    CORS_ALLOWED_ORIGINS: str = Field(
        default='https://heyxiaoli.com',
        description="Allowed CORS origins (comma-separated)",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow CORS credentials"
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
            docstring="CORS 配置模块",
            imports=imports,
            content=content,
            overwrite=True
        )
