"""Generator orchestrator - automatically discovers and manages generators"""
from pathlib import Path
from typing import List

from ..config_reader import ConfigReader
from ..decorators import GENERATORS, GeneratorDefinition


class GeneratorOrchestrator:
    """Generator orchestrator - automatically discovers and manages generators using decorators"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """
        Initialize orchestrator
        
        Args:
            project_path: Project root directory path
            config_reader: Configuration reader instance
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.generators = []
        self._initialize_generators()
    
    def _initialize_generators(self) -> None:
        """Initialize generators - auto-discover, filter, and sort"""
        # 1. Import all generator modules (triggers decorator registration)
        self._import_all_generators()
        
        # 2. Filter enabled generators
        enabled_generators = self._filter_enabled_generators()
        
        # 3. Check conflicts
        self._check_conflicts(enabled_generators)
        
        # 4. Resolve dependencies and sort
        sorted_generators = self._resolve_dependencies(enabled_generators)
        
        # 5. Instantiate generators
        self.generators = self._instantiate_generators(sorted_generators)
        
        # 6. Log generators (for debugging)
        self._log_generators()
    
    def _import_all_generators(self) -> None:
        """Import all generator modules to trigger decorator registration"""
        # Config file generators
        from core.generators.configs.pyproject import PyprojectGenerator
        from core.generators.configs.readme import ReadmeGenerator
        from core.generators.configs.gitignore import GitignoreGenerator
        from core.generators.configs.env import EnvGenerator
        from core.generators.configs.license import LicenseGenerator
        from core.generators.configs.redis import RedisConfigGenerator
        from core.generators.configs.celery import CeleryConfigGenerator
        
        # Deployment config generators
        from core.generators.deployment.dockerfile import DockerfileGenerator
        from core.generators.deployment.docker_compose import DockerComposeGenerator
        from core.generators.deployment.dockerignore import DockerignoreGenerator
        
        # Application code generators
        from core.generators.templates.app.security import SecurityGenerator
        from core.generators.templates.app.main import MainGenerator
        from core.generators.templates.app.base import ConfigBaseGenerator
        from core.generators.templates.app.app import ConfigAppGenerator
        from core.generators.templates.app.logger_config import ConfigLoggerGenerator
        from core.generators.templates.app.logger_manager import LoggerManagerGenerator
        from core.generators.templates.app.cors import ConfigCorsGenerator
        from core.generators.templates.app.database import ConfigDatabaseGenerator
        from core.generators.templates.app.jwt import ConfigJwtGenerator
        from core.generators.templates.app.email import ConfigEmailGenerator
        from core.generators.templates.app.settings import ConfigSettingsGenerator
        from core.generators.templates.app.deps import CoreDepsGenerator
        
        # Database generators
        from core.generators.templates.database.connection import DatabaseConnectionGenerator
        from core.generators.templates.database.mysql import DatabaseMySQLGenerator
        from core.generators.templates.database.postgresql import DatabasePostgreSQLGenerator
        from core.generators.templates.database.sqlite import SQLiteGenerator
        from core.generators.templates.database.dependencies import DatabaseDependenciesGenerator
        
        # Model generators
        from core.generators.templates.models.user import UserModelGenerator
        from core.generators.templates.models.token import TokenModelGenerator
        
        # Schema generators
        from core.generators.templates.schemas.user import UserSchemaGenerator
        from core.generators.templates.schemas.token import TokenSchemaGenerator
        
        # CRUD generators
        from core.generators.templates.crud.user import UserCRUDGenerator
        from core.generators.templates.crud.token import TokenCRUDGenerator
        
        # Service generators
        from core.generators.templates.services.auth import AuthServiceGenerator
        
        # Router generators
        from core.generators.templates.routers.auth import AuthRouterGenerator
        from core.generators.templates.routers.user import UserRouterGenerator
        from core.generators.templates.routers.router_aggregator import RouterAggregatorGenerator
        
        # Decorator generators
        from core.generators.templates.decorators.rate_limit import RateLimitDecoratorGenerator
        
        # Email generators
        from core.generators.templates.email.email import EmailServiceGenerator
        from core.generators.templates.email.email_template import EmailTemplateGenerator
        
        # Task generators
        from core.generators.templates.tasks.backup_database_task import BackupDatabaseTaskGenerator
        from core.generators.templates.tasks.tasks_init import TasksInitGenerator
        
        # App core generators
        from core.generators.templates.app.celery import CeleryAppGenerator
        from core.generators.templates.app.redis import RedisAppGenerator
        
        # Test generators
        from core.generators.templates.tests.conftest import ConftestGenerator
        from core.generators.templates.tests.test_main import TestMainGenerator
        from core.generators.templates.tests.test_auth import TestAuthGenerator
        from core.generators.templates.tests.test_users import TestUsersGenerator
        
        # Alembic generator
        from core.generators.alembic import AlembicGenerator
    
    def _filter_enabled_generators(self) -> List[GeneratorDefinition]:
        """Filter enabled generators"""
        enabled = []
        
        for name, gen_def in GENERATORS.items():
            if self._is_enabled(gen_def):
                enabled.append(gen_def)
        
        return enabled
    
    def _is_enabled(self, gen_def: GeneratorDefinition) -> bool:
        """Check if generator should be enabled"""
        if gen_def.enabled_when is None:
            return True
        
        try:
            return gen_def.enabled_when(self.config_reader)
        except Exception as e:
            print(f"Warning: Error checking if {gen_def.name} is enabled: {e}")
            return False
    
    def _check_conflicts(self, generators: List[GeneratorDefinition]) -> None:
        """Check for generator conflicts"""
        enabled_names = {gen.name for gen in generators}
        
        for gen_def in generators:
            for conflict in gen_def.conflicts:
                if conflict in enabled_names:
                    raise ValueError(
                        f"Generator conflict: {gen_def.name} conflicts with {conflict}"
                    )
    
    def _resolve_dependencies(
        self,
        generators: List[GeneratorDefinition]
    ) -> List[GeneratorDefinition]:
        """
        Resolve dependencies and sort (topological sort)
        
        Returns:
            Sorted list of generators
        """
        # Create name to definition mapping
        gen_map = {gen.name: gen for gen in generators}
        
        # Topological sort
        sorted_gens = []
        visited = set()
        visiting = set()
        
        def visit(gen_def: GeneratorDefinition):
            if gen_def.name in visited:
                return
            
            if gen_def.name in visiting:
                raise ValueError(f"Circular dependency detected: {gen_def.name}")
            
            visiting.add(gen_def.name)
            
            # Visit dependencies first
            for req_name in gen_def.requires:
                req_gen = gen_map.get(req_name)
                if req_gen:
                    visit(req_gen)
                else:
                    print(f"Warning: {gen_def.name} requires {req_name}, but it's not enabled")
            
            visiting.remove(gen_def.name)
            visited.add(gen_def.name)
            sorted_gens.append(gen_def)
        
        # Visit in priority order
        for gen_def in sorted(generators, key=lambda g: g.priority):
            visit(gen_def)
        
        return sorted_gens
    
    def _instantiate_generators(
        self,
        gen_defs: List[GeneratorDefinition]
    ) -> List:
        """Instantiate generators"""
        instances = []
        
        for gen_def in gen_defs:
            try:
                instance = gen_def.generator_class(
                    self.project_path,
                    self.config_reader
                )
                instances.append(instance)
            except Exception as e:
                print(f"Error: Failed to instantiate {gen_def.name}: {e}")
                raise
        
        return instances
    
    def _log_generators(self) -> None:
        """Log generator information (for debugging)"""
        # print(f"Debug: Total generators registered: {len(GENERATORS)}")
        # print(f"Debug: Enabled generators: {len(self.generators)}")
        # for i, gen in enumerate(self.generators, 1):
        #     print(f"  {i}. {gen.__class__.__name__}")
        pass
    
    def generate(self) -> None:
        """Generate all project files"""
        # print(f"Info: Starting generation with {len(self.generators)} generators")
        
        for generator in self.generators:
            try:
                # print(f"Debug: Running {generator.__class__.__name__}")
                generator.generate()
            except Exception as e:
                print(f"Error in {generator.__class__.__name__}: {e}")
                raise
        
        # print("Info: Generation completed successfully")
