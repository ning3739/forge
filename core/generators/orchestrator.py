"""生成器协调器模块

负责协调所有代码生成器，按照配置生成项目文件
"""
from pathlib import Path
from core.config_reader import ConfigReader

# 配置文件生成器
from .configs.pyproject import PyprojectGenerator
from .configs.readme import ReadmeGenerator
from .configs.gitignore import GitignoreGenerator
from .configs.env import EnvGenerator

# 部署配置生成器
from .deployment.dockerfile import DockerfileGenerator
from .deployment.docker_compose import DockerComposeGenerator
from .deployment.dockerignore import DockerignoreGenerator

# 应用代码生成器
from .templates.app.security import SecurityGenerator
from .templates.app.main import MainGenerator
from .templates.app.base import ConfigBaseGenerator
from .templates.app.app import ConfigAppGenerator
from .templates.app.logger_config import ConfigLoggerGenerator  # Pydantic 日志配置
from .templates.app.logger_manager import LoggerManagerGenerator  # Logger 管理器
from .templates.app.cors import ConfigCorsGenerator
from .templates.app.database import ConfigDatabaseGenerator
from .templates.app.jwt import ConfigJwtGenerator
from .templates.app.email import ConfigEmailGenerator
from .templates.app.settings import ConfigSettingsGenerator
from .templates.app.deps import CoreDepsGenerator  # 核心依赖注入

# 邮件服务生成器
from .templates.email.email import EmailServiceGenerator
from .templates.email.email_template import EmailTemplateGenerator

# 数据库生成器
from .templates.database.connection import DatabaseConnectionGenerator
from .templates.database.mysql import DatabaseMySQLGenerator
from .templates.database.postgresql import DatabasePostgreSQLGenerator
from .templates.database.dependencies import DatabaseDependenciesGenerator

# 模型生成器
from .templates.models.user import UserModelGenerator
from .templates.models.token import TokenModelGenerator

# Schema 生成器
from .templates.schemas.user import UserSchemaGenerator
from .templates.schemas.token import TokenSchemaGenerator

# CRUD 生成器
from .templates.crud.user import UserCRUDGenerator
from .templates.crud.token import TokenCRUDGenerator

# 服务生成器
from .templates.services.auth import AuthServiceGenerator

# 路由生成器
from .templates.routers.auth import AuthRouterGenerator
from .templates.routers.user import UserRouterGenerator
from .templates.routers.api_v1 import ApiV1Generator


class GeneratorOrchestrator:
    """生成器协调器 - 协调所有文件生成器"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """初始化生成器协调器
        
        按照依赖关系顺序初始化所有生成器：
        1. 基础配置文件
        2. 数据库系统
        3. 认证系统
        4. 应用入口
        5. 部署配置
        
        Args:
            project_path: 项目根目录路径
            config_reader: 配置读取器实例
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.generators = []
        
        # ========== 1. 基础配置文件（总是生成） ==========
        self._add_base_config_generators()
        
        # ========== 2. 数据库系统（如果启用数据库） ==========
        if config_reader.has_database():
            self._add_database_generators()
        
        # ========== 3. 认证系统（如果启用认证） ==========
        if config_reader.has_auth():
            self._add_auth_generators()
        
        # ========== 4. 应用入口（总是生成） ==========
        self.generators.append(MainGenerator(project_path, config_reader))
        
        # ========== 5. 部署配置（如果启用 Docker） ==========
        if config_reader.has_docker():
            self._add_docker_generators()
    
    def _add_base_config_generators(self) -> None:
        """添加基础配置文件生成器"""
        self.generators.extend([
            # 项目配置文件
            PyprojectGenerator(self.project_path, self.config_reader),
            ReadmeGenerator(self.project_path, self.config_reader),
            GitignoreGenerator(self.project_path, self.config_reader),
            EnvGenerator(self.project_path, self.config_reader),
            
            # 应用配置模块
            ConfigBaseGenerator(self.project_path, self.config_reader),
            ConfigAppGenerator(self.project_path, self.config_reader),
            ConfigLoggerGenerator(self.project_path, self.config_reader),
            LoggerManagerGenerator(self.project_path, self.config_reader),
            ConfigCorsGenerator(self.project_path, self.config_reader),
            ConfigDatabaseGenerator(self.project_path, self.config_reader),
            ConfigJwtGenerator(self.project_path, self.config_reader),
            ConfigEmailGenerator(self.project_path, self.config_reader),
            ConfigSettingsGenerator(self.project_path, self.config_reader),
        ])
    
    def _add_database_generators(self) -> None:
        """添加数据库相关生成器"""
        # 数据库连接管理器
        self.generators.append(
            DatabaseConnectionGenerator(self.project_path, self.config_reader)
        )
        
        # 根据数据库类型添加对应的管理器
        db_type = self.config_reader.get_database_type()
        if db_type == "MySQL":
            self.generators.append(
                DatabaseMySQLGenerator(self.project_path, self.config_reader)
            )
        elif db_type == "PostgreSQL":
            self.generators.append(
                DatabasePostgreSQLGenerator(self.project_path, self.config_reader)
            )
        
        # 如果启用认证，添加数据库依赖注入
        if self.config_reader.has_auth():
            self.generators.append(
                DatabaseDependenciesGenerator(self.project_path, self.config_reader)
            )
    
    def _add_auth_generators(self) -> None:
        """添加认证系统生成器"""
        auth_type = self.config_reader.get_auth_type()
        has_database = self.config_reader.has_database()
        
        # 核心安全模块
        self.generators.extend([
            SecurityGenerator(self.project_path, self.config_reader),
            CoreDepsGenerator(self.project_path, self.config_reader),
        ])
        
        # 如果有数据库，生成数据模型和 CRUD
        if has_database:
            # 用户模型、Schema 和 CRUD
            self.generators.extend([
                UserModelGenerator(self.project_path, self.config_reader),
                UserSchemaGenerator(self.project_path, self.config_reader),
                UserCRUDGenerator(self.project_path, self.config_reader),
            ])
            
            # Complete JWT Auth 需要 Token 相关文件
            if auth_type == "complete":
                self.generators.extend([
                    TokenModelGenerator(self.project_path, self.config_reader),
                    TokenSchemaGenerator(self.project_path, self.config_reader),
                    TokenCRUDGenerator(self.project_path, self.config_reader),
                ])
        
        # 认证服务和路由
        self.generators.extend([
            AuthServiceGenerator(self.project_path, self.config_reader),
            AuthRouterGenerator(self.project_path, self.config_reader),
            UserRouterGenerator(self.project_path, self.config_reader),
            ApiV1Generator(self.project_path, self.config_reader),
        ])
        
        # Complete JWT Auth 需要邮件服务
        if auth_type == "complete":
            self.generators.extend([
                EmailServiceGenerator(self.project_path, self.config_reader),
                EmailTemplateGenerator(self.project_path, self.config_reader),
            ])
    
    def _add_docker_generators(self) -> None:
        """添加 Docker 部署配置生成器"""
        self.generators.extend([
            DockerfileGenerator(self.project_path, self.config_reader),
            DockerComposeGenerator(self.project_path, self.config_reader),
            DockerignoreGenerator(self.project_path, self.config_reader),
        ])
    
    def generate(self) -> None:
        """生成所有项目文件"""
        for generator in self.generators:
            generator.generate()

