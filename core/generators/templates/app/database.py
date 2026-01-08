"""databaseConfiguration file generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="app_config",
    priority=15,
    requires=["ConfigBaseGenerator"],
    description="Generate database configuration (app/core/config/modules/database.py)"
)
class ConfigDatabaseGenerator(BaseTemplateGenerator):
    """generate app/core/config/modules/database.py file"""
    
    def generate(self) -> None:
        """generatedatabaseconfigurationfile"""
        imports = [
            "from pydantic import Field, PositiveInt",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        # Generate different default URL based on database type
        db_type = self.config_reader.get_database_type()
        project_name = self.config_reader.get_project_name()
        
        # Generate database name (convert project name to valid database name)
        db_name = project_name.lower().replace('-', '_').replace(' ', '_')
        
        if db_type == "PostgreSQL":
            default_url = f"postgresql://user:password@localhost:5432/{db_name}_dev"
        elif db_type == "MySQL":
            default_url = f"mysql://user:password@localhost:3306/{db_name}_dev"
        elif db_type == "SQLite":
            default_url = f"sqlite:///./{db_name}.db"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        content = f'''class DatabaseSettings(EnvBaseSettings):
    """databaseconfiguration"""
    
    # database connection URL
    DATABASE_URL: str = Field(
        default="{default_url}",
        description="Database connection URL",
    )
    
    # connectionpoolconfiguration
    ECHO: bool = Field(
        default=False,
        description="Generate database configuration (app/core/config/modules/database.py)"
    )
    POOL_PRE_PING: bool = Field(
        default=True,
        description="Generate database configuration (app/core/config/modules/database.py)"
    )
    POOL_TIMEOUT: PositiveInt = Field(
        default=30,
        description="Generate database configuration (app/core/config/modules/database.py)"
    )
    POOL_SIZE: PositiveInt = Field(
        default=6,
        description="Database connection pool size (conservative strategy: suitable for 2-core 2GB server)",
    )
    POOL_MAX_OVERFLOW: PositiveInt = Field(
        default=2,
        description="Database connection pool max overflow (conservative strategy: reduce overflow connections)",
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/database.py",
            docstring="databaseconfigurationmodule",
            imports=imports,
            content=content,
            overwrite=True
        )
