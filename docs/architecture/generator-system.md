# Generator System

The Generator System is the heart of Forge's code generation capabilities. It uses a decorator-based approach for automatic discovery and dependency management.

## Overview

The generator system consists of three main components:

1. **@Generator Decorator** - Automatic registration
2. **Generator Classes** - Code generation logic  
3. **GeneratorOrchestrator** - Coordination and execution

Forge includes **49 generators** organized into 13 categories that work together to create a complete FastAPI project. Each generator is automatically discovered, dependency-resolved, and executed in the correct order.

## Complete Generator List

Forge includes 49 generators organized into 13 categories. Here's the complete list with priorities and purposes:

### Configuration Files (Priority 1-10)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| PyprojectGenerator | 1 | Generate pyproject.toml with dependencies | Always |
| ReadmeGenerator | 2 | Generate README.md with project info | Always |
| GitignoreGenerator | 3 | Generate .gitignore for Python projects | Always |
| EnvGenerator | 4 | Generate .env files for different environments | Always |
| LicenseGenerator | 4 | Generate LICENSE file | Always |
| RedisConfigGenerator | 45 | Generate Redis configuration | `has_redis()` |
| CeleryConfigGenerator | 46 | Generate Celery configuration | `has_celery()` |

### App Configuration (Priority 10-20)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| ConfigBaseGenerator | 10 | Generate app/core/config/base.py | Always |
| ConfigAppGenerator | 11 | Generate app/core/config/app.py | Always |
| ConfigLoggerGenerator | 12 | Generate app/core/config/logger_config.py | Always |
| LoggerManagerGenerator | 13 | Generate app/core/logger.py | Always |
| ConfigCorsGenerator | 14 | Generate app/core/config/cors.py | `has_cors()` |
| ConfigDatabaseGenerator | 15 | Generate app/core/config/database.py | Always |
| ConfigJwtGenerator | 16 | Generate app/core/config/jwt.py | `has_auth()` |
| ConfigEmailGenerator | 17 | Generate app/core/config/email.py | `get_auth_type() == 'complete'` |
| ConfigSettingsGenerator | 18 | Generate app/core/config/settings.py | Always |
| SecurityGenerator | 19 | Generate app/core/security.py | `has_auth()` |
| CoreDepsGenerator | 20 | Generate app/core/deps.py | `has_auth()` |

### Database (Priority 30-32)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| DatabaseConnectionGenerator | 30 | Generate database connection manager | Always |
| DatabasePostgreSQLGenerator | 31 | Generate PostgreSQL-specific code | `get_database_type() == 'PostgreSQL'` |
| DatabaseMySQLGenerator | 31 | Generate MySQL-specific code | `get_database_type() == 'MySQL'` |
| SQLiteGenerator | 31 | Generate SQLite-specific code | `get_database_type() == 'SQLite'` |
| DatabaseDependenciesGenerator | 32 | Generate database dependencies | Always |

### Models (Priority 40-41)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| UserModelGenerator | 40 | Generate User model | `has_auth()` |
| TokenModelGenerator | 41 | Generate RefreshToken and VerificationCode models | `get_auth_type() == 'complete'` |

### App Core (Priority 47-48)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| CeleryAppGenerator | 47 | Generate Celery app instance | `has_celery()` |
| RedisAppGenerator | 48 | Generate Redis connection manager | `has_redis()` |

### Schemas (Priority 50-51)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| UserSchemaGenerator | 50 | Generate User Pydantic schemas | `has_auth()` |
| TokenSchemaGenerator | 51 | Generate Token Pydantic schemas | `get_auth_type() == 'complete'` |

### Tasks (Priority 59-60)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| TasksInitGenerator | 59 | Generate app/tasks/__init__.py | `has_celery()` |
| BackupDatabaseTaskGenerator | 60 | Generate database backup task | `has_celery()` |

### CRUD (Priority 60-61)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| UserCRUDGenerator | 60 | Generate User CRUD operations | `has_auth()` |
| TokenCRUDGenerator | 61 | Generate Token CRUD operations | `get_auth_type() == 'complete'` |

### Services (Priority 70)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| AuthServiceGenerator | 70 | Generate authentication service | `has_auth()` |

### Email (Priority 75-76)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| EmailServiceGenerator | 75 | Generate email service | `get_auth_type() == 'complete'` |
| EmailTemplateGenerator | 76 | Generate email HTML templates | `get_auth_type() == 'complete'` |

### Routers (Priority 80-82)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| AuthRouterGenerator | 80 | Generate authentication router | `has_auth()` |
| UserRouterGenerator | 81 | Generate user management router | `has_auth()` |
| RouterAggregatorGenerator | 82 | Generate router aggregator | Always |

### Decorators (Priority 85)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| RateLimitDecoratorGenerator | 85 | Generate rate limiting decorator | `has_redis()` |

### Main App (Priority 90)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| MainGenerator | 90 | Generate main.py FastAPI app | Always |

### Deployment (Priority 100-102)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| DockerfileGenerator | 100 | Generate Dockerfile | `has_docker()` |
| DockerComposeGenerator | 101 | Generate docker-compose.yml | `has_docker()` |
| DockerignoreGenerator | 102 | Generate .dockerignore | `has_docker()` |

### Tests (Priority 110-113)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| ConftestGenerator | 110 | Generate pytest configuration | `has_testing()` |
| TestMainGenerator | 111 | Generate main app tests | `has_testing()` |
| TestAuthGenerator | 112 | Generate authentication tests | `has_testing() and has_auth()` |
| TestUsersGenerator | 113 | Generate user management tests | `has_testing() and has_auth()` |

### Migration (Priority 120)

| Generator | Priority | Purpose | Enabled When |
|-----------|----------|---------|--------------|
| AlembicGenerator | 120 | Generate Alembic migration setup | `has_migration()` |

## The @Generator Decorator

### Basic Usage

```python
from core.decorators import Generator
from core.generators.base import BaseTemplateGenerator

@Generator(
    category="model",
    priority=40,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.has_auth()
)
class UserModelGenerator(BaseTemplateGenerator):
    def generate(self):
        # Generate user model code
        content = self.render_template("user_model.py.j2")
        self.write_file("app/models/user.py", content)
```

### Decorator Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | str | Generator category (e.g., "model", "router", "config") |
| `priority` | int | Execution priority (1-100, lower executes first) |
| `requires` | List[str] | List of required generator class names |
| `conflicts` | List[str] | List of conflicting generator names |
| `enabled_when` | Callable | Function that determines if generator should run |
| `description` | str | Human-readable description |

### Example with All Parameters

```python
@Generator(
    category="auth",
    priority=55,
    requires=["UserModelGenerator", "SecurityGenerator"],
    conflicts=["NoAuthGenerator"],
    enabled_when=lambda c: c.has_auth() and c.get_auth_type() == "complete",
    description="Generates complete JWT authentication router with email verification"
)
class CompleteAuthRouterGenerator(BaseTemplateGenerator):
    def generate(self):
        # Implementation
        ...
```

## Generator Definition

When you use the `@Generator` decorator, it creates a `GeneratorDefinition`:

```python
@dataclass
class GeneratorDefinition:
    name: str                           # Class name
    category: str                       # Category
    priority: int                       # Execution priority
    requires: List[str]                 # Dependencies
    conflicts: List[str]                # Conflicts
    enabled_when: Optional[Callable]    # Enablement condition
    generator_class: type               # The actual class
    description: str                    # Description
```

All generators are registered in a global registry:

```python
GENERATORS: Dict[str, GeneratorDefinition] = {}
```

## Base Generator Class

All generators inherit from `BaseTemplateGenerator`:

```python
class BaseTemplateGenerator:
    """Base class for all template generators"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """Initialize generator
        
        Args:
            project_path: Project root directory
            config_reader: Configuration reader instance
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(project_path)
    
    def generate(self) -> None:
        """Generate files - must be implemented by subclasses"""
        raise NotImplementedError
```

## Creating a Generator

### Step 1: Choose Category and Location

Create your generator in the appropriate category directory:

```
core/generators/
├── configs/          # Configuration files
├── deployment/       # Docker, docker-compose
└── templates/        # Application code
    ├── auth/        # Authentication
    ├── database/    # Database code
    ├── models/      # Database models
    ├── routers/     # API routers
    ├── services/    # Business logic
    └── tasks/       # Background tasks
```

### Step 2: Define the Generator

```python
# core/generators/templates/models/post.py

from core.decorators import Generator
from core.generators.base import BaseTemplateGenerator

@Generator(
    category="model",
    priority=42,  # After UserModelGenerator (40)
    requires=["DatabaseConnectionGenerator", "UserModelGenerator"],
    enabled_when=lambda c: c.get_database_type() is not None
)
class PostModelGenerator(BaseTemplateGenerator):
    """Generates Post model for blog posts"""
    
    def generate(self):
        """Generate post model file"""
        # Your generation logic here
        ...
```

### Step 3: Implement Generation Logic

```python
def generate(self):
    """Generate post model file"""
    
    # Get configuration
    orm_type = self.config_reader.get_orm_type()
    db_type = self.config_reader.get_database_type()
    
    # Generate based on ORM type
    if orm_type == "sqlmodel":
        self._generate_sqlmodel()
    else:
        self._generate_sqlalchemy()

def _generate_sqlmodel(self):
    """Generate SQLModel version"""
    content = '''"""Post model"""
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class Post(SQLModel, table=True):
    """Blog post model"""
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    author: Optional["User"] = Relationship(back_populates="posts")
'''
    
    # Write to file
    self.file_ops.write_file("app/models/post.py", content)
```

## Generator Orchestrator

The `GeneratorOrchestrator` manages the generator lifecycle through automatic discovery and intelligent execution.

### Automatic Discovery

The orchestrator automatically discovers all generators without manual registration:

1. **Import Phase**: All generator modules are imported, triggering `@Generator` decorator execution
2. **Registration**: Each decorator automatically adds the generator to the global `GENERATORS` registry
3. **No Manual Registration**: Developers never need to manually register generators

```python
# In orchestrator._import_all_generators()
from core.generators.configs.pyproject import PyprojectGenerator
from core.generators.templates.models.user import UserModelGenerator
# ... 47 more imports

# Each import triggers @Generator decorator, which registers the generator
# No manual registration needed!
```

### Discovery Phase

1. **Import all generators**
   ```python
   orchestrator._import_all_generators()
   ```
   
   This imports all Python files in the generators directory, triggering `@Generator` decorator registration.

2. **Filter enabled generators**
   ```python
   enabled = orchestrator._filter_enabled_generators()
   ```
   
   Checks `enabled_when` condition for each generator.

3. **Check conflicts**
   ```python
   orchestrator._check_conflicts(enabled)
   ```
   
   Ensures no conflicting generators are both enabled.

### Dependency Resolution

The orchestrator uses **topological sorting** to determine execution order:

```python
def _resolve_dependencies(self, generators):
    """Resolve dependencies using topological sort"""
    
    # Build dependency graph
    graph = {gen.name: gen.requires for gen in generators}
    
    # Topological sort with cycle detection
    visited = set()
    stack = set()
    result = []
    
    def visit(node):
        if node in stack:
            raise CyclicDependencyError(f"Cyclic dependency detected: {node}")
        
        if node not in visited:
            stack.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            stack.remove(node)
            visited.add(node)
            result.append(node)
    
    for gen in generators:
        visit(gen.name)
    
    return result
```

### Execution Phase

```python
def generate(self):
    """Generate all project files"""
    
    for generator in self.generators:
        try:
            generator.generate()
        except Exception as e:
            logger.error(f"Error in {generator.__class__.__name__}: {e}")
            raise
```

## Dependency Management

### Declaring Dependencies

Use the `requires` parameter to declare dependencies:

```python
@Generator(
    category="router",
    priority=55,
    requires=[
        "UserModelGenerator",      # Needs User model
        "AuthServiceGenerator"      # Needs Auth service
    ]
)
class UserRouterGenerator(BaseTemplateGenerator):
    ...
```

### Dependency Resolution

The orchestrator ensures:

1. **Required generators exist**
2. **Required generators are enabled**
3. **No circular dependencies**
4. **Correct execution order**

Example execution order:

```
1. DatabaseConnectionGenerator (priority 15, no deps)
2. UserModelGenerator (priority 40, requires DatabaseConnection)
3. AuthServiceGenerator (priority 45, requires UserModel)
4. AuthRouterGenerator (priority 55, requires AuthService)
5. MainGenerator (priority 60, requires all routers)
```

## Conditional Generation

### enabled_when Function

The `enabled_when` parameter receives a `ConfigReader` instance:

```python
@Generator(
    category="cache",
    enabled_when=lambda c: c.has_redis()
)
class RedisCacheGenerator(BaseTemplateGenerator):
    ...
```

### Common Conditions

```python
# Check if feature is enabled
lambda c: c.has_auth()
lambda c: c.has_redis()
lambda c: c.has_celery()
lambda c: c.has_testing()
lambda c: c.has_docker()

# Check specific values
lambda c: c.get_database_type() == "mysql"
lambda c: c.get_orm_type() == "sqlmodel"
lambda c: c.get_auth_type() == "complete"

# Complex conditions
lambda c: c.has_auth() and c.has_refresh_token()
lambda c: c.has_redis() and c.has_celery()
lambda c: c.get_database_type() in ["mysql", "postgresql"]
```

### ConfigReader API

Available methods in enabled_when:

```python
# Database
c.get_database_type()      # "mysql" | "postgresql" | "sqlite"
c.get_orm_type()           # "sqlmodel" | "sqlalchemy"
c.has_migration()          # bool

# Features
c.has_auth()               # bool
c.get_auth_type()          # "basic" | "complete"
c.has_refresh_token()      # bool
c.has_cors()               # bool
c.has_dev_tools()          # bool
c.has_testing()            # bool
c.has_docker()             # bool
c.has_redis()              # bool
c.has_celery()             # bool
```

## Priority System

### Priority Ranges

| Range | Purpose | Examples |
|-------|---------|----------|
| 1-10 | Configuration files | pyproject.toml, .gitignore, .env |
| 11-20 | Core infrastructure | Database connection, logging, security |
| 21-30 | Configuration modules | App config, DB config, JWT config |
| 31-50 | Business models | User model, Token model, custom models |
| 51-70 | API layer | Routers, services, middleware |
| 71-90 | Testing & deployment | Test files, Dockerfile, docker-compose |

### Priority Examples

```python
@Generator(category="config", priority=1)
class PyprojectGenerator: ...

@Generator(category="database", priority=15)
class DatabaseConnectionGenerator: ...

@Generator(category="model", priority=40)
class UserModelGenerator: ...

@Generator(category="router", priority=55)
class AuthRouterGenerator: ...

@Generator(category="test", priority=80)
class TestMainGenerator: ...
```

## Complete Example

Here's a complete generator example:

```python
# core/generators/templates/routers/posts.py

from core.decorators import Generator
from core.generators.base import BaseTemplateGenerator

@Generator(
    category="router",
    priority=56,
    requires=[
        "PostModelGenerator",
        "PostSchemaGenerator",
        "PostCRUDGenerator"
    ],
    enabled_when=lambda c: c.has_auth(),
    description="Generates Post router with CRUD operations"
)
class PostRouterGenerator(BaseTemplateGenerator):
    """Generate post router with CRUD endpoints"""
    
    def generate(self):
        """Generate post router file"""
        auth_type = self.config_reader.get_auth_type()
        
        content = f'''"""Post router"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.core.database.dependencies import get_session
from app.core.deps import get_current_user
from app.models.user import User
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.crud.post import post_crud

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all posts"""
    posts = post_crud.get_multi(session, skip=skip, limit=limit)
    return posts


@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a new post"""
    post = post_crud.create(session, obj_in=post_data, author_id=current_user.id)
    return post


@router.get("/{{post_id}}", response_model=PostResponse)
async def get_post(
    post_id: int,
    session: Session = Depends(get_session)
):
    """Get post by ID"""
    post = post_crud.get(session, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{{post_id}}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a post"""
    post = post_crud.get(session, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post = post_crud.update(session, db_obj=post, obj_in=post_data)
    return post


@router.delete("/{{post_id}}", status_code=204)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a post"""
    post = post_crud.get(session, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    post_crud.remove(session, id=post_id)
'''
        
        # Write router file
        self.file_ops.write_file("app/routers/v1/posts.py", content)
        
        # Update router aggregator
        self._update_router_init()
    
    def _update_router_init(self):
        """Update router __init__.py to include posts router"""
        # Implementation for updating __init__.py
        ...
```

## Best Practices

1. **Single Responsibility** - Each generator should handle one specific file or feature
2. **Clear Dependencies** - Explicitly declare all dependencies
3. **Descriptive Names** - Use clear, descriptive class names
4. **Error Handling** - Handle errors gracefully
5. **Idempotent** - Generators should be safe to run multiple times
6. **Testing** - Write tests for your generators

## Testing Generators

```python
# tests/test_generators/test_post_generator.py

import pytest
from pathlib import Path
from core.config_reader import ConfigReader
from core.generators.templates.models.post import PostModelGenerator

def test_post_model_generation(tmp_path):
    """Test post model generator"""
    # Setup
    project_path = tmp_path / "test_project"
    project_path.mkdir()
    
    # Create mock config
    config = {
        "database": {"type": "postgresql", "orm": "sqlmodel"},
        "features": {"auth": {"type": "complete"}}
    }
    
    config_file = project_path / ".forge" / "config.json"
    config_file.parent.mkdir()
    config_file.write_text(json.dumps(config))
    
    # Generate
    config_reader = ConfigReader(project_path)
    generator = PostModelGenerator(project_path, config_reader)
    generator.generate()
    
    # Assert
    model_file = project_path / "app" / "models" / "post.py"
    assert model_file.exists()
    content = model_file.read_text()
    assert "class Post" in content
    assert "SQLModel" in content
```

## Learn More

- [Architecture Overview](overview.md) - Overall system design
- [Creating Generators](../developer-guide/creating-generators.md) - Detailed tutorial
- [API Reference](../api/generator-decorator.md) - Complete API docs
