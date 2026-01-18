# Creating Generators

Generators are the core building blocks of Forge. Each generator is responsible for creating specific files in the generated project.

## How Generators Work

1. Generators are Python classes decorated with `@Generator`
2. The decorator registers them in a global registry
3. `GeneratorOrchestrator` discovers all registered generators
4. Generators are filtered based on configuration (e.g., skip Redis generator if Redis is disabled)
5. Generators are sorted by priority and dependencies
6. Each generator's `generate()` method is called in order

## Generator Structure

A generator consists of:

```python
from core.decorators import Generator
from core.generators.templates.base import BaseTemplateGenerator


@Generator(
    category="router",
    priority=80,
    requires=["UserModelGenerator", "UserSchemaGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate user router (app/routers/v1/users.py)"
)
class UserRouterGenerator(BaseTemplateGenerator):
    """User router generator"""
    
    def generate(self) -> None:
        """Generate the user router file"""
        # Implementation here
        pass
```

## @Generator Decorator Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | str | Yes | Generator category for organization |
| `priority` | int | Yes | Execution order (lower = earlier) |
| `requires` | list[str] | No | Generator class names that must run first |
| `enabled_when` | callable | No | Function that returns True if generator should run |
| `description` | str | No | Human-readable description |

### Category

Categories help organize generators logically:

| Category | Priority Range | Purpose |
|----------|---------------|---------|
| `config` | 1-10 | Configuration files (pyproject.toml, .env) |
| `app_config` | 11-20 | Application configuration modules |
| `database` | 21-30 | Database connection and setup |
| `model` | 31-50 | Database models |
| `schema` | 51-60 | Pydantic schemas |
| `crud` | 61-70 | CRUD operations |
| `service` | 71-80 | Business logic services |
| `router` | 81-90 | API routes |
| `email` | 71-80 | Email service |
| `task` | 55-65 | Celery tasks |
| `test` | 100-115 | Test files |
| `deployment` | 100-110 | Docker and deployment |
| `migration` | 120 | Database migrations |

### Priority

Priority determines execution order within and across categories. Lower numbers execute first.

Guidelines:
- Configuration files: 1-10
- Core infrastructure: 11-30
- Data layer (models, schemas): 31-60
- Business logic: 61-80
- API layer: 81-90
- Tests and deployment: 100+

### Requires

The `requires` parameter lists generator class names that must complete before this generator runs:

```python
@Generator(
    category="router",
    priority=80,
    requires=["UserModelGenerator", "UserSchemaGenerator", "UserCRUDGenerator"]
)
class UserRouterGenerator(BaseTemplateGenerator):
    ...
```

The orchestrator uses this to build a dependency graph and ensure correct execution order.

### enabled_when

A function that receives a `ConfigReader` instance and returns `True` if the generator should run:

```python
@Generator(
    category="router",
    priority=80,
    enabled_when=lambda c: c.has_auth()  # Only run if auth is enabled
)
class AuthRouterGenerator(BaseTemplateGenerator):
    ...
```

Common conditions:
- `lambda c: c.has_auth()` - Authentication enabled
- `lambda c: c.has_redis()` - Redis enabled
- `lambda c: c.has_celery()` - Celery enabled
- `lambda c: c.has_testing()` - Testing enabled
- `lambda c: c.has_docker()` - Docker enabled
- `lambda c: c.get_auth_type() == "complete"` - Complete auth mode
- `lambda c: c.get_database_type() == "PostgreSQL"` - Specific database

## BaseTemplateGenerator

All generators inherit from `BaseTemplateGenerator`:

```python
class BaseTemplateGenerator:
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)
    
    def generate(self) -> None:
        raise NotImplementedError("Subclasses must implement generate()")
```

### Available Properties

| Property | Type | Description |
|----------|------|-------------|
| `self.project_path` | Path | Root directory of generated project |
| `self.config_reader` | ConfigReader | Access to project configuration |
| `self.file_ops` | FileOperations | File writing utilities |

## Using ConfigReader

Query project configuration:

```python
def generate(self) -> None:
    # Project info
    name = self.config_reader.get_project_name()
    
    # Database
    db_type = self.config_reader.get_database_type()  # PostgreSQL, MySQL, SQLite
    orm_type = self.config_reader.get_orm_type()      # SQLModel, SQLAlchemy
    
    # Authentication
    auth_type = self.config_reader.get_auth_type()    # basic, complete
    
    # Feature flags
    if self.config_reader.has_auth():
        # Generate auth-related code
    
    if self.config_reader.has_redis():
        # Generate Redis-related code
    
    if self.config_reader.has_celery():
        # Generate Celery-related code
    
    if self.config_reader.has_refresh_token():
        # Generate refresh token code
```

## Using FileOperations

Write files to the generated project:

### Create a File

```python
self.file_ops.create_file(
    file_path="app/routers/v1/posts.py",
    content="# Posts router\n...",
    overwrite=True
)
```

### Create a Python File

Automatically formats with docstring and imports:

```python
self.file_ops.create_python_file(
    file_path="app/services/post.py",
    docstring="Post service module",
    imports=[
        "from typing import Optional, List",
        "from sqlalchemy.ext.asyncio import AsyncSession",
        "from app.models.post import Post",
    ],
    content='''class PostService:
    """Post service class"""
    
    async def create(self, db: AsyncSession, data: dict) -> Post:
        ...
''',
    overwrite=True
)
```

### Create JSON File

```python
self.file_ops.create_json_file(
    file_path="config.json",
    data={"key": "value"},
    indent=2,
    overwrite=True
)
```

### Create Markdown File

```python
self.file_ops.create_markdown_file(
    file_path="README.md",
    title="My Project",
    content="Project description...",
    overwrite=True
)
```

## Complete Example

Here's a complete generator that creates a posts router:

```python
"""Posts router generator"""
from core.decorators import Generator
from core.generators.templates.base import BaseTemplateGenerator


@Generator(
    category="router",
    priority=85,
    requires=["PostModelGenerator", "PostSchemaGenerator", "PostCRUDGenerator"],
    enabled_when=lambda c: c.config.get("features", {}).get("posts", False),
    description="Generate posts router (app/routers/v1/posts.py)"
)
class PostRouterGenerator(BaseTemplateGenerator):
    """Posts router generator"""
    
    def generate(self) -> None:
        """Generate the posts router file"""
        imports = [
            "from fastapi import APIRouter, Depends, HTTPException, status",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from typing import List",
            "",
            "from app.core.database import get_db",
            "from app.core.deps import get_current_user",
            "from app.models.user import User",
            "from app.schemas.post import PostCreate, PostUpdate, PostResponse",
            "from app.crud.post import post_crud",
        ]
        
        content = '''router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all posts"""
    return await post_crud.get_all(db, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific post"""
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post"""
    return await post_crud.create(db, post_data, author_id=current_user.id)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a post"""
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    return await post_crud.update(db, post_id, post_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a post"""
    post = await post_crud.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    await post_crud.delete(db, post_id)
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/posts.py",
            docstring="Posts API router",
            imports=imports,
            content=content,
            overwrite=True
        )
```

## Generator File Locations

Place generators in the appropriate directory:

| Type | Location |
|------|----------|
| Config files | `core/generators/configs/` |
| Deployment | `core/generators/deployment/` |
| App modules | `core/generators/templates/app/` |
| Database | `core/generators/templates/database/` |
| Models | `core/generators/templates/models/` |
| Schemas | `core/generators/templates/schemas/` |
| CRUD | `core/generators/templates/crud/` |
| Services | `core/generators/templates/services/` |
| Routers | `core/generators/templates/routers/` |
| Tasks | `core/generators/templates/tasks/` |
| Tests | `core/generators/templates/tests/` |

Generators are automatically discovered from these locations—no manual registration needed.
