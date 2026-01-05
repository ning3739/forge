"""Generator coordinator module

Responsible for coordinating all code generators and generating project files according to configuration
"""
from pathlib import Path
from core.config_reader import ConfigReader

# Configuration file generators
from .configs.pyproject import PyprojectGenerator
from .configs.readme import ReadmeGenerator
from .configs.gitignore import GitignoreGenerator
from .configs.env import EnvGenerator

# Deployment configuration generators
from .deployment.dockerfile import DockerfileGenerator
from .deployment.docker_compose import DockerComposeGenerator
from .deployment.dockerignore import DockerignoreGenerator

# Test generators
from .templates.tests.conftest import ConftestGenerator
from .templates.tests.test_main import TestMainGenerator
from .templates.tests.test_auth import TestAuthGenerator
from .templates.tests.test_users import TestUsersGenerator

# Application code generators
from .templates.app.security import SecurityGenerator
from .templates.app.main import MainGenerator
from .templates.app.base import ConfigBaseGenerator
from .templates.app.app import ConfigAppGenerator
from .templates.app.logger_config import ConfigLoggerGenerator  # Pydantic logging configuration
from .templates.app.logger_manager import LoggerManagerGenerator  # Logger manager
from .templates.app.cors import ConfigCorsGenerator
from .templates.app.database import ConfigDatabaseGenerator
from .templates.app.jwt import ConfigJwtGenerator
from .templates.app.email import ConfigEmailGenerator
from .templates.app.settings import ConfigSettingsGenerator
from .templates.app.deps import CoreDepsGenerator  # Core dependency injection

# Email service generators
from .templates.email.email import EmailServiceGenerator
from .templates.email.email_template import EmailTemplateGenerator

# Database generators
from .templates.database.connection import DatabaseConnectionGenerator
from .templates.database.mysql import DatabaseMySQLGenerator
from .templates.database.postgresql import DatabasePostgreSQLGenerator
from .templates.database.dependencies import DatabaseDependenciesGenerator

# Model generators
from .templates.models.user import UserModelGenerator
from .templates.models.token import TokenModelGenerator

# Schema generators
from .templates.schemas.user import UserSchemaGenerator
from .templates.schemas.token import TokenSchemaGenerator

# CRUD generators
from .templates.crud.user import UserCRUDGenerator
from .templates.crud.token import TokenCRUDGenerator

# Service generators
from .templates.services.auth import AuthServiceGenerator

# Router generators
from .templates.routers.auth import AuthRouterGenerator
from .templates.routers.user import UserRouterGenerator
from .templates.routers.api_v1 import ApiV1Generator


class GeneratorOrchestrator:
    """Generator coordinator - coordinates all file generators"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """Initialize generator coordinator
        
        Args:
            project_path: Project root directory path
            config_reader: Configuration reader instance
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.generators = self._initialize_generators()
    
    def _initialize_generators(self) -> list:
        """Initialize all generators (in dependency order)"""
        generators = []
        
        # 1. Base configuration files (always generated)
        generators.extend(self._get_base_config_generators())
        
        # 2. Database system (always generated)
        generators.extend(self._get_database_generators())
        
        # 3. Authentication system (always generated)
        generators.extend(self._get_auth_generators())
        
        # 4. Application entry point (always generated)
        generators.append(MainGenerator(self.project_path, self.config_reader))
        
        # 5. Deployment configuration (if enabled)
        if self.config_reader.has_docker():
            generators.extend(self._get_docker_generators())
        
        # 6. Test code (if enabled)
        if self.config_reader.has_testing():
            generators.extend(self._get_test_generators())
        
        return generators
    
    def _get_base_config_generators(self) -> list:
        """Get base configuration file generators"""
        return [
            # Project configuration files
            PyprojectGenerator(self.project_path, self.config_reader),
            ReadmeGenerator(self.project_path, self.config_reader),
            GitignoreGenerator(self.project_path, self.config_reader),
            EnvGenerator(self.project_path, self.config_reader),
            
            # Application configuration modules
            ConfigBaseGenerator(self.project_path, self.config_reader),
            ConfigAppGenerator(self.project_path, self.config_reader),
            ConfigLoggerGenerator(self.project_path, self.config_reader),
            LoggerManagerGenerator(self.project_path, self.config_reader),
            ConfigCorsGenerator(self.project_path, self.config_reader),
            ConfigDatabaseGenerator(self.project_path, self.config_reader),
            ConfigJwtGenerator(self.project_path, self.config_reader),
            ConfigEmailGenerator(self.project_path, self.config_reader),
            ConfigSettingsGenerator(self.project_path, self.config_reader),
        ]
    
    def _get_database_generators(self) -> list:
        """Get database-related generators"""
        generators = [DatabaseConnectionGenerator(self.project_path, self.config_reader)]
        
        # Add corresponding manager based on database type
        db_type = self.config_reader.get_database_type()
        if db_type == "MySQL":
            generators.append(DatabaseMySQLGenerator(self.project_path, self.config_reader))
        elif db_type == "PostgreSQL":
            generators.append(DatabasePostgreSQLGenerator(self.project_path, self.config_reader))
        
        # Add database dependency injection (required for authentication)
        generators.append(DatabaseDependenciesGenerator(self.project_path, self.config_reader))
        
        return generators
    
    def _get_auth_generators(self) -> list:
        """Get authentication system generators"""
        auth_type = self.config_reader.get_auth_type()
        
        generators = [
            # Core security module
            SecurityGenerator(self.project_path, self.config_reader),
            CoreDepsGenerator(self.project_path, self.config_reader),
            
            # User model, schema and CRUD
            UserModelGenerator(self.project_path, self.config_reader),
            UserSchemaGenerator(self.project_path, self.config_reader),
            UserCRUDGenerator(self.project_path, self.config_reader),
        ]
        
        # Complete JWT Auth requires Token-related files
        if auth_type == "complete":
            generators.extend([
                TokenModelGenerator(self.project_path, self.config_reader),
                TokenSchemaGenerator(self.project_path, self.config_reader),
                TokenCRUDGenerator(self.project_path, self.config_reader),
            ])
        
        # Authentication service and routes
        generators.extend([
            AuthServiceGenerator(self.project_path, self.config_reader),
            AuthRouterGenerator(self.project_path, self.config_reader),
            UserRouterGenerator(self.project_path, self.config_reader),
            ApiV1Generator(self.project_path, self.config_reader),
        ])
        
        # Complete JWT Auth requires email service
        if auth_type == "complete":
            generators.extend([
                EmailServiceGenerator(self.project_path, self.config_reader),
                EmailTemplateGenerator(self.project_path, self.config_reader),
            ])
        
        return generators
    
    def _get_docker_generators(self) -> list:
        """Get Docker deployment config generators"""
        return [
            DockerfileGenerator(self.project_path, self.config_reader),
            DockerComposeGenerator(self.project_path, self.config_reader),
            DockerignoreGenerator(self.project_path, self.config_reader),
        ]
    
    def _get_test_generators(self) -> list:
        """Get test code generators"""
        generators = [
            ConftestGenerator(self.project_path, self.config_reader),
            TestMainGenerator(self.project_path, self.config_reader),
        ]
        
        # Add auth tests if authentication is enabled
        if self.config_reader.has_auth():
            generators.extend([
                TestAuthGenerator(self.project_path, self.config_reader),
                TestUsersGenerator(self.project_path, self.config_reader),
            ])
        
        return generators
    
    def generate(self) -> None:
        """generate all project files"""
        for generator in self.generators:
            generator.generate()

