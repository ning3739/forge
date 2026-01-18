# @Generator Decorator

The `@Generator` decorator registers a class as a code generator in Forge's global registry.

## Location

```python
from core.decorators import Generator
```

## Signature

```python
@Generator(
    category: str,
    priority: int,
    requires: list[str] = None,
    enabled_when: callable = None,
    description: str = ""
)
```

## Parameters

### category (required)

**Type:** `str`

The category this generator belongs to. Used for organization and logging.

Common categories:
- `config` - Configuration files
- `app_config` - Application configuration modules
- `database` - Database connection
- `model` - Database models
- `schema` - Pydantic schemas
- `crud` - CRUD operations
- `service` - Business logic
- `router` - API routes
- `email` - Email service
- `task` - Celery tasks
- `test` - Test files
- `deployment` - Docker and deployment
- `migration` - Database migrations

### priority (required)

**Type:** `int`

Execution order. Lower numbers execute first.

Recommended ranges:
| Range | Purpose |
|-------|---------|
| 1-10 | Configuration files |
| 11-20 | Application configuration |
| 21-30 | Database setup |
| 31-50 | Models |
| 51-60 | Schemas |
| 61-70 | CRUD operations |
| 71-80 | Services |
| 81-90 | Routers |
| 100-115 | Tests |
| 100-110 | Deployment |
| 120 | Migrations |

### requires (optional)

**Type:** `list[str]`  
**Default:** `None` (empty list)

List of generator class names that must execute before this generator.

```python
@Generator(
    category="router",
    priority=80,
    requires=["UserModelGenerator", "UserSchemaGenerator", "UserCRUDGenerator"]
)
```

The orchestrator ensures all required generators complete before executing this one.

### enabled_when (optional)

**Type:** `callable(ConfigReader) -> bool`  
**Default:** `None` (always enabled)

A function that receives a `ConfigReader` instance and returns `True` if the generator should run.

```python
@Generator(
    category="router",
    priority=80,
    enabled_when=lambda c: c.has_auth()
)
```

If `None`, the generator always runs.

### description (optional)

**Type:** `str`  
**Default:** `""`

Human-readable description of what the generator creates.

```python
@Generator(
    category="router",
    priority=80,
    description="Generate authentication router (app/routers/v1/auth.py)"
)
```

## How It Works

When Python imports a module containing a decorated class, the decorator:

1. Registers the class in `GENERATOR_REGISTRY`
2. Stores all metadata (category, priority, requires, enabled_when, description)
3. Returns the original class unchanged

```python
# core/decorators/generator.py
GENERATOR_REGISTRY = {}

def Generator(category, priority, requires=None, enabled_when=None, description=""):
    def decorator(cls):
        GENERATOR_REGISTRY[cls.__name__] = {
            "class": cls,
            "category": category,
            "priority": priority,
            "requires": requires or [],
            "enabled_when": enabled_when,
            "description": description,
        }
        return cls
    return decorator
```

## Examples

### Basic Generator

```python
from core.decorators import Generator
from core.generators.templates.base import BaseTemplateGenerator


@Generator(
    category="config",
    priority=1,
    description="Generate pyproject.toml"
)
class PyprojectGenerator(BaseTemplateGenerator):
    def generate(self) -> None:
        # Always runs, no dependencies
        self.file_ops.create_file("pyproject.toml", content)
```

### Generator with Dependencies

```python
@Generator(
    category="crud",
    priority=60,
    requires=["UserModelGenerator", "UserSchemaGenerator"],
    description="Generate user CRUD operations"
)
class UserCRUDGenerator(BaseTemplateGenerator):
    def generate(self) -> None:
        # Runs after UserModelGenerator and UserSchemaGenerator
        pass
```

### Conditional Generator

```python
@Generator(
    category="router",
    priority=80,
    requires=["AuthServiceGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate auth router"
)
class AuthRouterGenerator(BaseTemplateGenerator):
    def generate(self) -> None:
        # Only runs if authentication is enabled
        pass
```

### Generator with Complex Condition

```python
@Generator(
    category="email",
    priority=75,
    requires=["ConfigEmailGenerator"],
    enabled_when=lambda c: c.get_auth_type() == "complete",
    description="Generate email service"
)
class EmailServiceGenerator(BaseTemplateGenerator):
    def generate(self) -> None:
        # Only runs for complete authentication
        pass
```

## Accessing the Registry

```python
from core.decorators import GENERATOR_REGISTRY

# List all registered generators
for name, info in GENERATOR_REGISTRY.items():
    print(f"{name}: {info['category']} (priority={info['priority']})")

# Get a specific generator
user_model_info = GENERATOR_REGISTRY.get("UserModelGenerator")
if user_model_info:
    generator_class = user_model_info["class"]
```

## Common Patterns

### Feature-Specific Generator

```python
@Generator(
    category="app",
    priority=48,
    enabled_when=lambda c: c.has_redis(),
    requires=["RedisConfigGenerator"],
    description="Generate Redis connection manager"
)
class RedisAppGenerator(BaseTemplateGenerator):
    ...
```

### Database-Specific Generator

```python
@Generator(
    category="database",
    priority=31,
    requires=["ConfigDatabaseGenerator"],
    enabled_when=lambda c: c.get_database_type() == "PostgreSQL",
    description="Generate PostgreSQL connection"
)
class PostgreSQLGenerator(BaseTemplateGenerator):
    ...
```

### Auth-Type-Specific Generator

```python
@Generator(
    category="model",
    priority=41,
    requires=["UserModelGenerator"],
    enabled_when=lambda c: c.get_auth_type() == "complete",
    description="Generate token models for complete auth"
)
class TokenModelGenerator(BaseTemplateGenerator):
    ...
```
