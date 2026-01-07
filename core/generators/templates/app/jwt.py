"""JWT Configuration file generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=16,
    requires=["ConfigBaseGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate JWT configuration (app/core/config/modules/jwt.py)"
)
class ConfigJwtGenerator(BaseTemplateGenerator):
    """generate app/core/config/modules/jwt.py file"""
    
    def generate(self) -> None:
        """generate JWT configurationfile"""
        # onlyenableauthenticationwhengenerate
        if not self.config_reader.has_auth():
            return
        
        imports = [
            "from typing import Optional",
            "from pydantic import Field, PositiveInt, SecretStr",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        auth_type = self.config_reader.get_auth_type()
        project_name = self.config_reader.get_project_name()
        
        # Generate project identifier (for issuer and audience)
        project_identifier = project_name.lower().replace('-', '_').replace(' ', '_')
        
        # Base JWT configuration (required for all authentication types)
        base_fields = f'''    JWT_SECRET_KEY: SecretStr = Field(
        ...,
        repr=False,
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_ACCESS_TOKEN_EXPIRATION: PositiveInt = Field(
        default=1800,
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )'''
        
        # Only Complete JWT Auth includes Refresh Token
        if auth_type == "complete":
            base_fields += f'''
    JWT_REFRESH_TOKEN_EXPIRATION: PositiveInt = Field(
        default=86400,
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )'''
        
        # add issuer and audience
        base_fields += f'''
    JWT_ISSUER: Optional[str] = Field(
        default="{project_identifier}",
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )
    JWT_AUDIENCE: Optional[str] = Field(
        default="{project_identifier}_users",
        description="Generate JWT configuration (app/core/config/modules/jwt.py)"
    )'''
        
        content = f'''class JWTSettings(EnvBaseSettings):
    """JWT authenticationconfiguration"""

{base_fields}
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/jwt.py",
            docstring="JWT authenticationconfigurationmodule",
            imports=imports,
            content=content,
            overwrite=True
        )
