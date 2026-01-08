"""Alembic migration tool generator"""
from pathlib import Path
from core.decorators import Generator
from core.utils import FileOperations
from core.config_reader import ConfigReader


@Generator(
    category="migration",
    priority=120,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.has_migration(),
    description="Generate Alembic migration configuration"
)
class AlembicGenerator:
    """Alembic migration tool generator"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """Initialize Alembic generator
        
        Args:
            project_path: Project root directory path
            config_reader: Configuration reader instance
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)
    
    def generate(self) -> None:
        """generate Alembic configuration"""
        # Only generate if migration tool is enabled
        if not self.config_reader.has_migration():
            return
        
        # Check if already initialized
        env_py = self.project_path / "alembic" / "env.py"
        if env_py.exists():
            return
        
        # Always manually create complete Alembic structure
        # This ensures the project has complete migration files even if Alembic is not installed
        self._create_alembic_structure()
    
    def _create_alembic_structure(self) -> None:
        """Create complete Alembic structure"""
        # Create directories
        alembic_dir = self.project_path / "alembic"
        alembic_dir.mkdir(exist_ok=True)
        (alembic_dir / "versions").mkdir(exist_ok=True)
        
        # Create all required files
        self._create_alembic_ini()
        self._create_env_py()
        self._create_script_mako()
        self._create_alembic_readme()
        
        # Create .gitkeep in versions directory
        gitkeep = alembic_dir / "versions" / ".gitkeep"
        gitkeep.touch(exist_ok=True)
    
    def _create_alembic_ini(self) -> None:
        """Create alembic.ini file"""
        db_type = self.config_reader.get_database_type()
        
        if db_type == "PostgreSQL":
            db_url_example = "postgresql://user:password@localhost/dbname"
        elif db_type == "MySQL":
            db_url_example = "mysql://user:password@localhost/dbname"
        elif db_type == "SQLite":
            db_url_example = "sqlite:///./database.db"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        content = f'''# Alembic configuration file

[alembic]
# Path to migration scripts
script_location = alembic

# Template file
file_template = %%(rev)s_%%(slug)s

# Timezone setting
timezone = UTC

# Database URL (read from environment variables)
# sqlalchemy.url = {db_url_example}
# Database URL is configured in env.py from environment variables

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''
        
        self.file_ops.create_file(
            file_path="alembic.ini",
            content=content,
            overwrite=True
        )
    
    def _create_env_py(self) -> None:
        """Create env.py file"""
        orm_type = self.config_reader.get_orm_type()
        
        if orm_type == "SQLModel":
            self._create_sqlmodel_env_py()
        elif orm_type == "SQLAlchemy":
            self._create_sqlalchemy_env_py()
    
    def _create_sqlmodel_env_py(self) -> None:
        """Create env.py for SQLModel (async version)"""
        db_type = self.config_reader.get_database_type()
        project_name = self.config_reader.get_project_name()
        db_name = project_name.lower().replace('-', '_').replace(' ', '_')
        
        # Set default URL based on database type
        if db_type == "PostgreSQL":
            default_url = f"postgresql://user:password@localhost:5432/{db_name}_dev"
        elif db_type == "MySQL":
            default_url = f"mysql://user:password@localhost:3306/{db_name}_dev"
        elif db_type == "SQLite":
            default_url = f"sqlite:///./{db_name}.db"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Generate model imports based on authentication type
        auth_type = self.config_reader.get_auth_type() if self.config_reader.has_auth() else None
        
        model_imports = "# Import all models so Alembic can detect them\nfrom app.models.user import User"
        
        if auth_type == "complete":
            model_imports += "\nfrom app.models.token import RefreshToken, VerificationCode"
        
        content = f'''"""Alembic environment configuration - SQLModel (async version)"""
from logging.config import fileConfig
import asyncio
import os
from pathlib import Path
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "secret" / ".env.development"
if env_file.exists():
    load_dotenv(env_file)

# Import SQLModel Base
from sqlmodel import SQLModel

{model_imports}

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set MetaData
target_metadata = SQLModel.metadata


# Get database URL from environment variables
def get_url():
    """Get database URL from environment variables"""
    url = os.getenv("DATABASE_URL", "{default_url}")
    # Convert to async driver (SQLite doesn't need conversion)
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+aiomysql://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # SQLite URLs remain unchanged (sqlite:/// or sqlite+aiosqlite:///)
    return url


def run_migrations_offline() -> None:
    """Run migrations in offline mode (sync mode)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to execute migrations"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in online mode (async mode)"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
'''
        
        self.file_ops.create_file(
            file_path="alembic/env.py",
            content=content,
            overwrite=True
        )
    
    def _create_sqlalchemy_env_py(self) -> None:
        """Create env.py for SQLAlchemy (async version)"""
        db_type = self.config_reader.get_database_type()
        project_name = self.config_reader.get_project_name()
        db_name = project_name.lower().replace('-', '_').replace(' ', '_')
        
        # Set default URL based on database type
        if db_type == "PostgreSQL":
            default_url = f"postgresql://user:password@localhost:5432/{db_name}_dev"
        elif db_type == "MySQL":
            default_url = f"mysql://user:password@localhost:3306/{db_name}_dev"
        elif db_type == "SQLite":
            default_url = f"sqlite:///./{db_name}.db"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Generate model imports based on authentication type
        auth_type = self.config_reader.get_auth_type() if self.config_reader.has_auth() else None
        
        model_imports = "# Import all models so Alembic can detect them\nfrom app.models.user import User"
        
        if auth_type == "complete":
            model_imports += "\nfrom app.models.token import RefreshToken, VerificationCode"
        
        content = f'''"""Alembic environment configuration - SQLAlchemy (async version)"""
from logging.config import fileConfig
import asyncio
import os
from pathlib import Path
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Load environment variables
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "secret" / ".env.development"
if env_file.exists():
    load_dotenv(env_file)

# Import Base
from app.core.database import Base

{model_imports}

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set MetaData
target_metadata = Base.metadata


# Get database URL from environment variables
def get_url():
    """Get database URL from environment variables"""
    url = os.getenv("DATABASE_URL", "{default_url}")
    # Convert to async driver (SQLite doesn't need conversion)
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+aiomysql://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # SQLite URLs remain unchanged (sqlite:/// or sqlite+aiosqlite:///)
    return url


def run_migrations_offline() -> None:
    """Run migrations in offline mode (sync mode)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to execute migrations"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in online mode (async mode)"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
'''
        
        self.file_ops.create_file(
            file_path="alembic/env.py",
            content=content,
            overwrite=True
        )
    
    def _create_script_mako(self) -> None:
        """Create migration script template"""
        content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        
        self.file_ops.create_file(
            file_path="alembic/script.py.mako",
            content=content,
            overwrite=True
        )
    
    def _create_alembic_readme(self) -> None:
        """Create Alembic usage guide"""
        content = '''# Alembic Database Migration

This directory contains database migration scripts.

## Install Dependencies

Make sure Alembic is installed:

```bash
pip install alembic
# or
uv add alembic
```

## Usage

### Create New Migration

```bash
# Auto-generate migration (recommended)
alembic revision --autogenerate -m "describe your changes"

# Manually create empty migration
alembic revision -m "describe your changes"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific version
alembic upgrade <revision_id>
```

### Rollback Migrations

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### View Migration History

```bash
# View current version
alembic current

# View migration history
alembic history

# View detailed history
alembic history --verbose
```

## Configuration

Database connection URL is read from the `DATABASE_URL` environment variable.

Please set it in your `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Notes

1. Before creating migrations, ensure all models are imported in `alembic/env.py`
2. When using `--autogenerate`, Alembic will automatically detect model changes
3. Always review generated migration scripts to ensure they meet expectations
4. Test migrations in development environment before applying to production
'''
        
        self.file_ops.create_markdown_file(
            file_path="alembic/README.md",
            title=None,
            content=content,
            overwrite=True
        )
