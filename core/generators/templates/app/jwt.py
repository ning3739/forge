"""JWT 配置文件生成器"""
from ..base import BaseTemplateGenerator


class ConfigJwtGenerator(BaseTemplateGenerator):
    """生成 app/core/config/modules/jwt.py 文件"""
    
    def generate(self) -> None:
        """生成 JWT 配置文件"""
        # 只有启用认证时才生成
        if not self.config_reader.has_auth():
            return
        
        imports = [
            "from typing import Optional",
            "from pydantic import Field, PositiveInt, SecretStr",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        auth_type = self.config_reader.get_auth_type()
        project_name = self.config_reader.get_project_name()
        
        # 生成项目标识符（用于 issuer 和 audience）
        project_identifier = project_name.lower().replace('-', '_').replace(' ', '_')
        
        # 基础 JWT 配置（所有认证类型都需要）
        base_fields = f'''    JWT_SECRET_KEY: SecretStr = Field(
        ...,
        repr=False,
        description="Secret key used to sign JWTs"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm used for JWT"
    )
    JWT_ACCESS_TOKEN_EXPIRATION: PositiveInt = Field(
        default=1800,
        description="JWT access token expiration time (seconds)"
    )'''
        
        # 只有 Complete JWT Auth 才包含 Refresh Token
        if auth_type == "complete":
            base_fields += f'''
    JWT_REFRESH_TOKEN_EXPIRATION: PositiveInt = Field(
        default=86400,
        description="JWT refresh token expiration time (seconds)"
    )'''
        
        # 添加 issuer 和 audience
        base_fields += f'''
    JWT_ISSUER: Optional[str] = Field(
        default="{project_identifier}",
        description="JWT issuer"
    )
    JWT_AUDIENCE: Optional[str] = Field(
        default="{project_identifier}_users",
        description="JWT audience"
    )'''
        
        content = f'''class JWTSettings(EnvBaseSettings):
    """JWT 认证配置"""

{base_fields}
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/jwt.py",
            docstring="JWT 认证配置模块",
            imports=imports,
            content=content,
            overwrite=True
        )
