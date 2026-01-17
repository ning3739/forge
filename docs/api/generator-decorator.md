# Generator Decorator API

The `@Generator` decorator is the core of Forge's code generation system. It enables automatic discovery, dependency resolution, and conditional execution of generators.

## Overview

```python
from core.decorators.generator import Generator

@Generator(
    category="model",
    priority=40,
    requires=["DatabaseGenerator"],
    enabled_when=lambda config: config.has_auth()
)
class UserModelGenerator(BaseTemplateGenerator):
    def generate(self):
        # Generation logic
        pass
```

## Decorator Parameters

### category

- **Type**: `str`
- **Required**: Yes
- **Description**: Logical grouping of generators for organization and execution order

**Available Categories**:
- `"config"` (priority 1-10): Configuration files
- `"core"` (priority 11-30): Core application modules
- `"model"` (priority 31-50): Database models and schemas
- `"service"` (priority 41-60): Business logic
- `"router"` (priority 51-70): API routes
- `"test"` (priority 71-90): Test files
- `"deployment"` (priority 81-100): Docker and deployment

**Example**:
```python
@Generator(category="model", priority=35)
class UserModelGenerator(BaseTemplateGenerator):
    pass
```

### priority

- **Type**: `int`
- **Required**: Yes
- **Description**: Execution order within category (lower numbers run first)
- **Range**: 1-100

**Priority Guidelines**:
- 1-10: Base configuration (pyproject.toml, .env)
- 11-30: Core infrastructure (database, security)
- 31-50: Data models and schemas
- 41-60: Business logic and services
- 51-70: API routes and endpoints
- 71-90: Tests
- 81-100: Deployment configuration

**Example**:
```python
# Database connection runs before models
@Generator(category="core", priority=15)
class DatabaseGenerator(BaseTemplateGenerator):
    pass

# Models run after database is set up
@Generator(category="model", priority=35)
class UserModelGenerator(BaseTemplateGenerator):
    pass
```

### requires

- **Type**: `list[str]` or `None`
- **Required**: No
- **Default**: `None`
- **Description**: List of generator class names that must run before this generator

**Example**:
```python
@Generator(
    category="router",
    priority=60,
    requires=["UserModelGenerator", "AuthServiceGenerator"]
)
class AuthRouterGenerator(BaseTemplateGenerator):
    pass
```

**Dependency Resolution**:
- Generators are sorted by dependencies before execution
- Circular dependencies will raise an error
- Missing dependencies will raise an error

### enabled_when

- **Type**: `Callable[[ConfigReader], bool]` or `None`
- **Required**: No
- **Default**: `None` (always enabled)
- **Description**: Function that determines if generator should run based on configuration

**Example**:
```python
@Generator(
    category="service",
    priority=50,
    enabled_when=lambda config: config.has_auth()
)
class AuthServiceGenerator(BaseTemplateGenerator):
    pass

@Generator(
    category="core",
    priority=20,
    enabled_when=lambda config: config.use_redis()
)
class RedisGenerator(BaseTemplateGenerator):
    pass
```

**Common Conditions**:
```python
# Authentication enabled
enabled_when=lambda c: c.has_auth()

# Complete authentication mode
enabled_when=lambda c: c.auth_mode() == "complete"

# Redis enabled
enabled_when=lambda c: c.use_redis()

# Celery enabled
enabled_when=lambda c: c.use_celery()

# Docker enabled
enabled_when=lambda c: c.use_docker()

# Tests enabled
enabled_when=lambda c: c.include_tests()

# Specific database
enabled_when=lambda c: c.database() == "postgresql"

# Multiple conditions
enabled_when=lambda c: c.has_auth() and c.use_redis()
```

## Base Generator Class

All generators must inherit from `BaseTemplateGenerator`:

```python
from core.generators.templates.base import BaseTemplateGenerator

class MyGenerator(BaseTemplateGenerator):
    def __init__(self, config: ConfigReader):
        super().__init__(config)
    
    def generate(self):
        """Generate files based on configuration"""
        # Implementation
        pass
```

### BaseTemplateGenerator Methods

#### `__init__(self, config: ConfigReader)`

Initialize generator with configuration.

```python
def __init__(self, config: ConfigReader):
    super().__init__(config)
    self.project_name = config.project_name()
```

#### `generate(self) -> None`

**Required method**. Implement file generation logic.

```python
def generate(self):
    content = self._generate_content()
    self._write_file("app/models/user.py", content)
```

#### `_write_file(self, path: str, content: str) -> None`

Write content to file relative to project root.

```python
def generate(self):
    content = "# Generated file\n"
    self._write_file("app/config.py", content)
```

#### `_ensure_directory(self, path: str) -> None`

Create directory if it doesn't exist.

```python
def generate(self):
    self._ensure_directory("app/models")
    self._write_file("app/models/user.py", content)
```

## ConfigReader API

The `ConfigReader` provides access to project configuration:

### Configuration Methods

```python
# Project settings
config.project_name() -> str
config.database() -> str  # "postgresql", "mysql", "sqlite"
config.orm() -> str  # "sqlmodel", "sqlalchemy"

# Authentication
config.has_auth() -> bool
config.auth_mode() -> str  # "none", "basic", "complete"

# Optional features
config.use_redis() -> bool
config.use_celery() -> bool
config.use_docker() -> bool
config.include_tests() -> bool
```

See [ConfigReader API](config-reader.md) for complete documentation.

## Generator Registry

The decorator automatically registers generators in a global registry:

```python
from core.decorators.generator import GENERATOR_REGISTRY

# Access all registered generators
all_generators = GENERATOR_REGISTRY

# Filter by category
model_generators = [
    g for g in GENERATOR_REGISTRY 
    if g["category"] == "model"
]

# Get generator class
generator_class = next(
    g["class"] for g in GENERATOR_REGISTRY 
    if g["class"].__name__ == "UserModelGenerator"
)
```

## Complete Example

```python
from core.decorators.generator import Generator
from core.generators.templates.base import BaseTemplateGenerator
from core.config_reader import ConfigReader

@Generator(
    category="model",
    priority=35,
    requires=["DatabaseGenerator"],
    enabled_when=lambda config: config.has_auth()
)
class UserModelGenerator(BaseTemplateGenerator):
    """Generate User model for authentication"""
    
    def __init__(self, config: ConfigReader):
        super().__init__(config)
        self.orm = config.orm()
        self.auth_mode = config.auth_mode()
    
    def generate(self):
        """Generate user model file"""
        # Ensure directory exists
        self._ensure_directory("app/models")
        
        # Generate content based on ORM choice
        if self.orm == "sqlmodel":
            content = self._generate_sqlmodel()
        else:
            content = self._generate_sqlalchemy()
        
        # Write file
        self._write_file("app/models/user.py", content)
    
    def _generate_sqlmodel(self) -> str:
        """Generate SQLModel user model"""
        fields = [
            "id: int | None = Field(default=None, primary_key=True)",
            "email: str = Field(unique=True, index=True)",
            "username: str = Field(unique=True, index=True)",
            "hashed_password: str",
            "is_active: bool = Field(default=True)",
        ]
        
        # Add verification field for complete auth
        if self.auth_mode == "complete":
            fields.append("is_verified: bool = Field(default=False)")
        
        return f'''from sqlmodel import Field, SQLModel
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    {chr(10).join(f"    {field}" for field in fields)}
    created_at: datetime = Field(default_factory=datetime.utcnow)
'''
    
    def _generate_sqlalchemy(self) -> str:
        """Generate SQLAlchemy user model"""
        # Similar implementation for SQLAlchemy
        pass
```

## Best Practices

### 1. Single Responsibility

Each generator should create one logical unit:

```python
# Good: One generator per model
@Generator(category="model", priority=35)
class UserModelGenerator(BaseTemplateGenerator):
    pass

@Generator(category="model", priority=36)
class TokenModelGenerator(BaseTemplateGenerator):
    pass

# Bad: One generator for all models
@Generator(category="model", priority=35)
class AllModelsGenerator(BaseTemplateGenerator):
    pass
```

### 2. Clear Dependencies

Explicitly declare dependencies:

```python
@Generator(
    category="router",
    priority=60,
    requires=[
        "UserModelGenerator",  # Need user model
        "AuthServiceGenerator",  # Need auth service
        "JWTGenerator"  # Need JWT utilities
    ]
)
class AuthRouterGenerator(BaseTemplateGenerator):
    pass
```

### 3. Conditional Generation

Use `enabled_when` for optional features:

```python
# Only generate if feature is enabled
@Generator(
    category="core",
    priority=20,
    enabled_when=lambda c: c.use_redis()
)
class RedisGenerator(BaseTemplateGenerator):
    pass
```

### 4. Configuration-Driven

Use configuration to customize output:

```python
def generate(self):
    if self.config.database() == "postgresql":
        driver = "asyncpg"
    elif self.config.database() == "mysql":
        driver = "aiomysql"
    else:
        driver = "aiosqlite"
    
    content = f"DATABASE_DRIVER = '{driver}'\n"
    self._write_file("app/config.py", content)
```

### 5. Error Handling

Validate configuration and handle errors:

```python
def generate(self):
    if not self.config.has_auth():
        raise ValueError("AuthRouter requires authentication to be enabled")
    
    try:
        content = self._generate_content()
        self._write_file("app/routers/auth.py", content)
    except Exception as e:
        logger.error(f"Failed to generate auth router: {e}")
        raise
```

## Testing Generators

```python
import pytest
from core.config_reader import ConfigReader
from core.generators.templates.app.user_model import UserModelGenerator

def test_user_model_generation():
    """Test user model generator"""
    config = ConfigReader({
        "project_name": "test_api",
        "database": "postgresql",
        "orm": "sqlmodel",
        "auth_mode": "basic"
    })
    
    generator = UserModelGenerator(config)
    generator.generate()
    
    # Verify file was created
    assert os.path.exists("test_api/app/models/user.py")
    
    # Verify content
    with open("test_api/app/models/user.py") as f:
        content = f.read()
        assert "class User(SQLModel, table=True)" in content
        assert "email: str" in content
```

## See Also

- [Generator System Architecture](../architecture/generator-system.md)
- [Orchestrator API](orchestrator.md)
- [ConfigReader API](config-reader.md)
- [Creating Custom Generators](../developer-guide/creating-generators.md)
