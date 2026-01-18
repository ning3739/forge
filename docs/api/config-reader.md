# ConfigReader API

The `ConfigReader` class provides access to project configuration stored in `.forge/config.json`.

## Location

```python
from core.config_reader import ConfigReader
```

## Constructor

```python
ConfigReader(project_path: Path)
```

**Parameters:**
- `project_path`: Path to the project root directory (containing `.forge/config.json`)

**Example:**
```python
from pathlib import Path
from core.config_reader import ConfigReader

config_reader = ConfigReader(Path("./my-project"))
```

## Methods

### Project Information

#### get_project_name()

Returns the project name.

```python
def get_project_name(self) -> str
```

**Returns:** Project name string

**Example:**
```python
name = config_reader.get_project_name()  # "my-project"
```

---

### Database Configuration

#### get_database_type()

Returns the selected database type.

```python
def get_database_type(self) -> str
```

**Returns:** One of `"PostgreSQL"`, `"MySQL"`, `"SQLite"`

**Example:**
```python
db_type = config_reader.get_database_type()  # "PostgreSQL"
```

#### get_orm_type()

Returns the selected ORM.

```python
def get_orm_type(self) -> str
```

**Returns:** One of `"SQLModel"`, `"SQLAlchemy"`

**Example:**
```python
orm = config_reader.get_orm_type()  # "SQLModel"
```

---

### Authentication

#### has_auth()

Checks if authentication is enabled.

```python
def has_auth(self) -> bool
```

**Returns:** `True` if authentication is enabled

**Example:**
```python
if config_reader.has_auth():
    # Generate auth-related code
```

#### get_auth_type()

Returns the authentication type.

```python
def get_auth_type(self) -> str
```

**Returns:** One of `"basic"`, `"complete"`

**Example:**
```python
auth_type = config_reader.get_auth_type()  # "complete"
```

#### has_refresh_token()

Checks if refresh tokens are enabled.

```python
def has_refresh_token(self) -> bool
```

**Returns:** `True` if refresh tokens are enabled (always `True` for complete auth)

**Example:**
```python
if config_reader.has_refresh_token():
    # Generate refresh token code
```

---

### Feature Flags

#### has_cors()

Checks if CORS is enabled.

```python
def has_cors(self) -> bool
```

**Returns:** `True` if CORS middleware should be configured

#### has_redis()

Checks if Redis is enabled.

```python
def has_redis(self) -> bool
```

**Returns:** `True` if Redis integration is enabled

#### has_celery()

Checks if Celery is enabled.

```python
def has_celery(self) -> bool
```

**Returns:** `True` if Celery background tasks are enabled

#### has_testing()

Checks if testing is enabled.

```python
def has_testing(self) -> bool
```

**Returns:** `True` if pytest configuration should be generated

#### has_docker()

Checks if Docker is enabled.

```python
def has_docker(self) -> bool
```

**Returns:** `True` if Docker files should be generated

#### has_migration()

Checks if database migrations are enabled.

```python
def has_migration(self) -> bool
```

**Returns:** `True` if Alembic should be configured

#### has_dev_tools()

Checks if development tools are enabled.

```python
def has_dev_tools(self) -> bool
```

**Returns:** `True` if Black, Ruff, mypy should be included

---

### Raw Configuration Access

#### config

The raw configuration dictionary.

```python
config_reader.config  # dict
```

**Example:**
```python
# Access nested configuration
features = config_reader.config.get("features", {})
custom_value = features.get("custom_feature", False)
```

## Configuration Structure

The `.forge/config.json` file has this structure:

```json
{
  "project_name": "my-project",
  "description": "Project description",
  "author": "Author Name",
  "database": {
    "type": "PostgreSQL",
    "orm": "SQLModel"
  },
  "features": {
    "auth": {
      "type": "complete",
      "refresh_token": true
    },
    "cors": true,
    "redis": true,
    "celery": true,
    "testing": true,
    "docker": true,
    "migration": true,
    "dev_tools": true
  }
}
```

## Usage in Generators

```python
from core.decorators import Generator
from core.generators.templates.base import BaseTemplateGenerator


@Generator(
    category="router",
    priority=80,
    enabled_when=lambda c: c.has_auth()
)
class AuthRouterGenerator(BaseTemplateGenerator):
    def generate(self) -> None:
        # Access configuration
        auth_type = self.config_reader.get_auth_type()
        
        if auth_type == "basic":
            self._generate_basic_auth()
        else:
            self._generate_complete_auth()
        
        # Check other features
        if self.config_reader.has_redis():
            # Add Redis-based rate limiting
            pass
```
