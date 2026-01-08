"""Settings Configuration file generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=18,
    requires=["ConfigBaseGenerator"],
    description="Generate settings aggregator (app/core/config/settings.py)"
)
class ConfigSettingsGenerator(BaseTemplateGenerator):
    """generate app/core/config/settings.py file"""
    
    def generate(self) -> None:
        """generate Settings configurationfile"""
        imports = ["from functools import cached_property"]
        
        # Collect all required configuration modules
        config_modules = []
        
        # Base configuration (always included)
        config_modules.append({
            "import": "from app.core.config.modules.app import AppSettings",
            "property": "app",
            "class": "AppSettings"
        })
        
        config_modules.append({
            "import": "from app.core.config.modules.logger import LoggingSettings",
            "property": "logging",
            "class": "LoggingSettings"
        })
        
        # databaseconfiguration(is nowrequired)
        config_modules.append({
            "import": "from app.core.config.modules.database import DatabaseSettings",
            "property": "database",
            "class": "DatabaseSettings"
        })
        
        # JWT configuration(ifenableauthentication)
        if self.config_reader.has_auth():
            config_modules.append({
                "import": "from app.core.config.modules.jwt import JWTSettings",
                "property": "jwt",
                "class": "JWTSettings"
            })
        
        # Email configuration(ifyes Complete JWT Auth)
        if self.config_reader.get_auth_type() == "complete":
            config_modules.append({
                "import": "from app.core.config.modules.email import EmailSettings",
                "property": "email",
                "class": "EmailSettings"
            })
        
        # CORS configuration(ifenable)
        if self.config_reader.has_cors():
            config_modules.append({
                "import": "from app.core.config.modules.cors import CORSSettings",
                "property": "cors",
                "class": "CORSSettings"
            })
        
        # Redis configuration (if enabled)
        if self.config_reader.has_redis():
            config_modules.append({
                "import": "from app.core.config.modules.redis import RedisSettings",
                "property": "redis",
                "class": "RedisSettings"
            })
        
        # Celery configuration (if enabled)
        if self.config_reader.has_celery():
            config_modules.append({
                "import": "from app.core.config.modules.celery import CelerySettings",
                "property": "celery",
                "class": "CelerySettings"
            })
        
        # Build import statements
        for module in config_modules:
            imports.append(module["import"])
        
        # Build Settings classattribute
        properties = []
        for module in config_modules:
            property_code = f'''    @cached_property
    def {module["property"]}(self) -> {module["class"]}:
        return {module["class"]}()'''
            properties.append(property_code)
        
        # BuildcompleteContent
        content = f'''class Settings:
    """Global configuration class
    
    Use cached_property for lazy loading configuration, improves performance
    """

{chr(10).join(properties)}


# Create a global settings instance
settings = Settings()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/settings.py",
            docstring="globalconfigurationmanagement",
            imports=imports,
            content=content,
            overwrite=True
        )
