"""Settings 配置文件生成器"""
from ..base import BaseTemplateGenerator


class ConfigSettingsGenerator(BaseTemplateGenerator):
    """生成 app/core/config/settings.py 文件"""
    
    def generate(self) -> None:
        """生成 Settings 配置文件"""
        imports = ["from functools import cached_property"]
        
        # 收集所有需要的配置模块
        config_modules = []
        
        # 基础配置（始终包含）
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
        
        # 数据库配置（如果启用）
        if self.config_reader.has_database():
            config_modules.append({
                "import": "from app.core.config.modules.database import DatabaseSettings",
                "property": "database",
                "class": "DatabaseSettings"
            })
        
        # JWT 配置（如果启用认证）
        if self.config_reader.has_auth():
            config_modules.append({
                "import": "from app.core.config.modules.jwt import JWTSettings",
                "property": "jwt",
                "class": "JWTSettings"
            })
        
        # Email 配置（如果是 Complete JWT Auth）
        if self.config_reader.get_auth_type() == "complete":
            config_modules.append({
                "import": "from app.core.config.modules.email import EmailSettings",
                "property": "email",
                "class": "EmailSettings"
            })
        
        # CORS 配置（如果启用）
        if self.config_reader.has_cors():
            config_modules.append({
                "import": "from app.core.config.modules.cors import CORSSettings",
                "property": "cors",
                "class": "CORSSettings"
            })
        
        # 构建导入语句
        for module in config_modules:
            imports.append(module["import"])
        
        # 构建 Settings 类的属性
        properties = []
        for module in config_modules:
            property_code = f'''    @cached_property
    def {module["property"]}(self) -> {module["class"]}:
        return {module["class"]}()'''
            properties.append(property_code)
        
        # 构建完整内容
        content = f'''class Settings:
    """全局配置类
    
    使用 cached_property 延迟加载配置，提高性能
    """

{chr(10).join(properties)}


# Create a global settings instance
settings = Settings()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/settings.py",
            docstring="全局配置管理",
            imports=imports,
            content=content,
            overwrite=True
        )
