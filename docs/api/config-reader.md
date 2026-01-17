# ConfigReader API

The `ConfigReader` class provides a clean API for reading and validating project configuration from `.forge/config.json`.

## Overview

`ConfigReader` is the central component for accessing project configuration throughout Forge. It:

- Loads and validates configuration from `.forge/config.json`
- Provides type-safe accessfor configuration values
- Validates configuration integrity
- Used by all generators to check enabled features

## Class Definition

```python
class ConfigReader:
    """Configuration file reader
    
    Responsible for reading and parsing .forge/config.json configuration file
    """
    
    REQUIRED_FIELDS = ['project_name', 'database', 'features']
    
    def __init__(self, project_path: Path):
        """Initialize configuration reader
        
        Args:
            project_path: Project root directory path
        """
```

## Initialization

### ConfigReader(project_path)

Create a new ConfigReader instance.

**Parameters:**

- `project_path` (Path): Project root directory containing `.forge/config.json`

**Example:**

```python
from pathlib import Path
from core.config_reader import ConfigReader

project_path = Path("/path/to/my-project")
config_reader = ConfigReader(project_path)
```

## Loading Configuration

### load_config()

Load configuration from `.forge/config.json`.

**Returns:** `Dict[str, Any]` - Configuration dictionary

**Raises:**
- `FileNotFoundError` - Configuration file does not exist
- `json.JSONDecodeError` - Configuration file format error

**Example:**

```python
config = config_reader.load_config()
print(config['project_name'])  # "my-project"
```

## Validation

### validate_config()

Validate configuration file integrity.

**Returns:** `bool` - Whether configuration is valid

**Raises:**
- `ConfigValidationError` - Configuration validation failed

**Example:**

```python
try:
    is_valid = config_reader.validate_config()
    print(f"Config is valid: {is_valid}")
except ConfigValidationError as e:
    print(f"Validation error: {e}")
```

## Project Information

### get_project_name()

Get the project name.

**Returns:** `str` - Project name

**Example:**

```python
name = config_reader.get_project_name()
print(f"Project: {name}")  # "my-api-project"
```

## Database Configuration

### get_database_config()

Get complete database configuration.

**Returns:** `Dict[str, Any]` - Database configuration

**Example:**

```python
db_config = config_reader.get_database_config()
# {
#     "type": "postgresql",
#     "orm": "sqlmodel",
#     "migration_tool": "alembic"
# }
```

### get_database_type()

Get database type.

**Returns:** `str` - Database type: `"postgresql"`, `"mysql"`, or `"sqlite"`

**Example:**

```python
db_type = config_reader.get_database_type()
if db_type == "postgresql":
    # PostgreSQL-specific logic
    ...
```

### get_orm_type()

Get ORM type.

**Returns:** `str` - ORM type: `"sqlmodel"` or `"sqlalchemy"`

**Example:**

```python
orm = config_reader.get_orm_type()
if orm == "sqlmodel":
    # Use SQLModel templates
    ...
```

### get_migration_tool()

Get migration tool.

**Returns:** `Optional[str]` - Migration tool name or `None`

**Example:**

```python
migration_tool = config_reader.get_migration_tool()
if migration_tool == "alembic":
    # Setup Alembic
    ...
```

### has_migration()

Check if database migration is enabled.

**Returns:** `bool` - Whether migrations are enabled

**Example:**

```python
if config_reader.has_migration():
    # Generate migration files
    ...
```

## Feature Detection

### get_features()

Get all feature configuration.

**Returns:** `Dict[str, Any]` - Feature configuration

**Example:**

```python
features = config_reader.get_features()
# {
#     "auth": {"type": "complete", "refresh_token": true},
#     "cors": true,
#     "redis": true,
#     ...
# }
```

## Authentication

### has_auth()

Check if authentication is enabled.

**Returns:** `bool` - Always `True` (authentication is required)

**Example:**

```python
if config_reader.has_auth():
    # Generate auth code
    ...
```

### get_auth_type()

Get authentication type.

**Returns:** `str` - Authentication type: `"basic"` or `"complete"`

**Example:**

```python
auth_type = config_reader.get_auth_type()
if auth_type == "complete":
    # Include email verification and password reset
    ...
```

### has_refresh_token()

Check if Refresh Token is enabled.

**Returns:** `bool` - Whether refresh tokens are enabled

**Example:**

```python
if config_reader.has_refresh_token():
    # Generate token model and endpoints
    ...
```

## CORS

### has_cors()

Check if CORS is enabled.

**Returns:** `bool` - Whether CORS is enabled

**Example:**

```python
if config_reader.has_cors():
    # Add CORS middleware
    ...
```

## Development Tools

### has_dev_tools()

Check if development tools are included.

**Returns:** `bool` - Whether dev tools are enabled

**Example:**

```python
if config_reader.has_dev_tools():
    # Add Black and Ruff to pyproject.toml
    ...
```

## Testing

### has_testing()

Check if testing tools are included.

**Returns:** `bool` - Whether testing is enabled

**Example:**

```python
if config_reader.has_testing():
    # Generate test files
    ...
```

## Docker

### has_docker()

Check if Docker configuration is included.

**Returns:** `bool` - Whether Docker is enabled

**Example:**

```python
if config_reader.has_docker():
    # Generate Dockerfile and docker-compose.yml
    ...
```

## Redis

### has_redis()

Check if Redis is enabled.

**Returns:** `bool` - Whether Redis is enabled

**Example:**

```python
if config_reader.has_redis():
    # Generate Redis connection
    ...
```

### get_redis_features()

Get Redis features list.

**Returns:** `List[str]` - List of Redis features

**Example:**

```python
redis_features = config_reader.get_redis_features()
# ["caching", "sessions", "message_queue"]
```

## Celery

### has_celery()

Check if Celery is enabled.

**Returns:** `bool` - Whether Celery is enabled

**Example:**

```python
if config_reader.has_celery():
    # Generate Celery configuration
    ...
```

### get_celery_features()

Get Celery features list.

**Returns:** `List[str]` - List of Celery features

**Example:**

```python
celery_features = config_reader.get_celery_features()
# ["background_tasks", "scheduling", "database_backup"]
```

## Metadata

### get_metadata()

Get metadata information.

**Returns:** `Dict[str, Any]` - Metadata dictionary

**Example:**

```python
metadata = config_reader.get_metadata()
# {
#     "created_at": "2024-01-17T10:00:00",
#     "forge_version": "0.1.8.3"
# }
```

### get_created_at()

Get configuration creation time.

**Returns:** `Optional[str]` - ISO format timestamp or `None`

**Example:**

```python
created = config_reader.get_created_at()
print(f"Created at: {created}")
```

### get_forge_version()

Get Forge version used to create the project.

**Returns:** `Optional[str]` - Version string or `None`

**Example:**

```python
version = config_reader.get_forge_version()
print(f"Generated with Forge v{version}")
```

## Usage in Generators

ConfigReader is commonly used in generators through the `@Generator` decorator's `enabled_when` parameter:

```python
from core.decorators import Generator
from core.generators.base import BaseTemplateGenerator

@Generator(
    category="cache",
    priority=25,
    requires=["RedisConnectionGenerator"],
    enabled_when=lambda c: c.has_redis()  # ConfigReader instance
)
class RedisCacheGenerator(BaseTemplateGenerator):
    def generate(self):
        # Access config through self.config_reader
        redis_features = self.config_reader.get_redis_features()
        
        if "caching" in redis_features:
            # Generate caching code
            ...
```

## Complete Example

```python
from pathlib import Path
from core.config_reader import ConfigReader

# Initialize
project_path = Path("/Users/user/my-api-project")
config = ConfigReader(project_path)

# Load and validate
config.load_config()
config.validate_config()

# Get project info
print(f"Project: {config.get_project_name()}")

# Check database
print(f"Database: {config.get_database_type()}")
print(f"ORM: {config.get_orm_type()}")

# Check features
if config.has_auth():
    print(f"Auth Type: {config.get_auth_type()}")
    print(f"Refresh Token: {config.has_refresh_token()}")

if config.has_redis():
    print(f"Redis Features: {config.get_redis_features()}")

if config.has_celery():
    print(f"Celery Features: {config.get_celery_features()}")

# Get metadata
metadata = config.get_metadata()
print(f"Created: {metadata.get('created_at')}")
print(f"Forge Version: {metadata.get('forge_version')}")
```

## Error Handling

```python
from core.config_reader import ConfigReader, ConfigValidationError

try:
    config = ConfigReader(project_path)
    config.load_config()
    config.validate_config()
except FileNotFoundError:
    print("Configuration file not found!")
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
except ConfigValidationError as e:
    print(f"Validation error: {e}")
```

## See Also

- [Generator Decorator](generator-decorator.md) - Using ConfigReader in generators
- [Orchestrator](orchestrator.md) - How orchestrator uses ConfigReader
- [Configuration Options](../user-guide/configuration.md) - All configuration options
