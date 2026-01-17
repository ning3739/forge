# Creating Custom Generators

This guide walks you through creating custom generators for Forge. You'll learn how to extend Forge with your own code generation logic.

## Prerequisites

- Understanding of Python and FastAPI
- Familiarity with Forge's architecture
- Knowledge of the `@Generator` decorator

## Quick Start

### 1. Create Generator File

Create a new file in `core/generators/templates/`:

```python
# core/generators/templates/my_feature.py

from core.decorators.generator import Generator
from core.generators.templates.base import BaseTemplateGenerator
from core.config_reader import ConfigReader

@Generator(
    category="feature",
    priority=55,
    requires=[],
    enabled_when=None  # Always enabled
)
class MyFeatureGenerator(BaseTemplateGenerator):
    """Generate my custom feature"""
    
    def __init__(self, config: ConfigReader):
        super().__init__(config)
        self.project_name = config.project_name()
    
    def generate(self):
        """Generate feature files"""
        content = self._generate_content()
        self._write_file("app/features/my_feature.py", content)
    
    def _generate_content(self) -> str:
        return '''"""My custom feature"""

def my_function():
    return "Hello from my feature!"
'''
```

### 2. Import Generator

Add import to `core/generators/templates/__init__.py`:

```python
from core.generators.templates.my_feature import MyFeatureGenerator
```

### 3. Test Generator

```python
from core.config_reader import ConfigReader
from core.generators.orchestrator import GeneratorOrchestrator

config = ConfigReader({"project_name": "test_api"})
orchestrator = GeneratorOrchestrator(config)
orchestrator.run()
```

## Step-by-Step Tutorial

### Example: Blog Post Feature

Let's create a complete blog post feature with model, schema, CRUD, and router.

#### Step 1: Create Model Generator

```python
# core/generators/templates/models/post.py

from core.decorators.generator import Generator
from core.generators.templates.base import BaseTemplateGenerator

@Generator(
    category="model",
    priority=37,
    requires=["DatabaseGenerator"],
    enabled_when=None
)
class PostModelGenerator(BaseTemplateGenerator):
    """Generate Post model"""
    
    def generate(self):
        self._ensure_directory("app/models")
        
        if self.config.orm() == "sqlmodel":
            content = self._generate_sqlmodel()
        else:
            content = self._generate_sqlalchemy()
        
        self._write_file("app/models/post.py", content)
    
    def _generate_sqlmodel(self) -> str:
        return '''from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Post(SQLModel, table=True):
    """Blog post model"""
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    content: str
    slug: str = Field(unique=True, index=True)
    published: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    author: Optional["User"] = Relationship(back_populates="posts")
'''
    
    def _generate_sqlalchemy(self) -> str:
        # Similar implementation for SQLAlchemy
        pass
```

#### Step 2: Create Schema Generator

```python
# core/generators/templates/schemas/post.py

from core.decorators.generator import Generator
from core.generators.templates.base import BaseTemplateGenerator

@Generator(
    category="model",
    priority=38,
    requires=["PostModelGenerator"],
    enabled_when=None
)
class PostSchemaGenerator(BaseTemplateGenerator):
    """Generate Post schemas"""
    
    def generate(self):
        self._ensure_directory("app/schemas")
        content = self._generate_content()
        self._write_file("app/schemas/post.py", content)
    
    def _generate_content(self) -> str:
        return '''from pydantic import BaseModel, Field
from datetime import datetime

class PostBase(BaseModel):
    """Base post schema"""
    title: str = Field(..., max_length=200)
    content: str
    slug: str
    published: bool = False

class PostCreate(PostBase):
    """Schema for creating post"""
    pass

class PostUpdate(BaseModel):
    """Schema for updating post"""
    title: str | None = None
    content: str | None = None
    slug: str | None = None
    published: bool | None = None

class PostResponse(PostBase):
    """Schema for post response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
'''
```

#### Step 3: Create CRUD Generator

```python
# core/generators/templates/crud/post.py

from core.decorators.generator import Generator
from core.generators.templates.base import BaseTemplateGenerator

@Generator(
    category="service",
    priority=52,
    requires=["PostModelGenerator", "PostSchemaGenerator"],
    enabled_when=None
)
class PostCRUDGenerator(BaseTemplateGenerator):
    """Generate Post CRUD operations"""
    
    def generate(self):
        self._ensure_directory("app/crud")
        content = self._generate_content()
        self._write_file("app/crud/post.py", content)
    
    def _generate_content(self) -> str:
        return '''from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

async def create_post(
    db: AsyncSession,
    post_data: PostCreate,
    user_id: int
) -> Post:
    """Create new post"""
    post = Post(**post_data.dict(), user_id=user_id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

async def get_post(db: AsyncSession, post_id: int) -> Post | None:
    """Get post by ID"""
    result = await db.execute(
        select(Post).where(Post.id == post_id)
    )
    return result.scalar_one_or_none()

async def get_posts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Post]:
    """Get all posts"""
    result = await db.execute(
        select(Post).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_post(
    db: AsyncSession,
    post: Post,
    post_data: PostUpdate
) -> Post:
    """Update post"""
    for field, value in post_data.dict(exclude_unset=True).items():
        setattr(post, field, value)
    
    await db.commit()
    await db.refresh(post)
    return post

async def delete_post(db: AsyncSession, post: Post) -> None:
    """Delete post"""
    await db.delete(post)
    await db.commit()
'''
```

#### Step 4: Create Router Generator

```python
# core/generators/templates/routers/post.py

from core.decorators.generator import Generator
from core.generators.templates.base import BaseTemplateGenerator

@Generator(
    category="router",
    priority=62,
    requires=["PostCRUDGenerator"],
    enabled_when=lambda c: c.has_auth()  # Requires authentication
)
class PostRouterGenerator(BaseTemplateGenerator):
    """Generate Post router"""
    
    def generate(self):
        self._ensure_directory("app/routers")
        content = self._generate_content()
        self._write_file("app/routers/post.py", content)
    
    def _generate_content(self) -> str:
        return '''from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.crud import post as post_crud

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new post"""
    post = await post_crud.create_post(db, post_data, current_user.id)
    return post

@router.get("/", response_model=list[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all posts"""
    posts = await post_crud.get_posts(db, skip, limit)
    return posts

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get post by ID"""
    post = await post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update post"""
    post = await post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    post = await post_crud.update_post(db, post, post_data)
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete post"""
    post = await post_crud.get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    await post_crud.delete_post(db, post)
'''
```

#### Step 5: Register Router in Main

```python
# core/generators/templates/app/main.py (modify existing generator)

# Add to router registration section:
if config.has_auth():  # Only if auth enabled
    from app.routers import post
    app.include_router(post.router, prefix="/api/v1")
```

## Advanced Patterns

### Configuration-Driven Generation

```python
@Generator(category="feature", priority=55)
class ConfigurableGenerator(BaseTemplateGenerator):
    def generate(self):
        # Different output based on configuration
        if self.config.database() == "postgresql":
            self._generate_postgres_specific()
        elif self.config.database() == "mysql":
            self._generate_mysql_specific()
        else:
            self._generate_sqlite_specific()
```

### Template-Based Generation

```python
from string import Template

@Generator(category="feature", priority=55)
class TemplateBasedGenerator(BaseTemplateGenerator):
    def generate(self):
        template = Template('''
from fastapi import APIRouter

router = APIRouter(prefix="/$prefix", tags=["$tag"])

@router.get("/")
async def get_$resource():
    return {"message": "Hello from $resource!"}
''')
        
        content = template.substitute(
            prefix="items",
            tag="items",
            resource="items"
        )
        
        self._write_file("app/routers/items.py", content)
```

### Multi-File Generation

```python
@Generator(category="feature", priority=55)
class MultiFileGenerator(BaseTemplateGenerator):
    def generate(self):
        # Generate multiple related files
        self._generate_model()
        self._generate_schema()
        self._generate_crud()
        self._generate_router()
    
    def _generate_model(self):
        self._write_file("app/models/item.py", "# Model")
    
    def _generate_schema(self):
        self._write_file("app/schemas/item.py", "# Schema")
    
    def _generate_crud(self):
        self._write_file("app/crud/item.py", "# CRUD")
    
    def _generate_router(self):
        self._write_file("app/routers/item.py", "# Router")
```

## Best Practices

### 1. Single Responsibility

Each generator should handle one logical unit:

```python
# Good: Separate generators
class UserModelGenerator(BaseTemplateGenerator):
    pass

class UserSchemaGenerator(BaseTemplateGenerator):
    pass

# Bad: One generator does everything
class UserEverythingGenerator(BaseTemplateGenerator):
    pass
```

### 2. Clear Dependencies

```python
@Generator(
    category="router",
    priority=60,
    requires=[
        "UserModelGenerator",
        "UserSchemaGenerator",
        "UserCRUDGenerator"
    ]
)
class UserRouterGenerator(BaseTemplateGenerator):
    pass
```

### 3. Conditional Generation

```python
@Generator(
    category="feature",
    priority=55,
    enabled_when=lambda c: c.get("enable_my_feature", False)
)
class OptionalFeatureGenerator(BaseTemplateGenerator):
    pass
```

### 4. Error Handling

```python
def generate(self):
    try:
        content = self._generate_content()
        self._write_file("app/feature.py", content)
    except Exception as e:
        logger.error(f"Failed to generate feature: {e}")
        raise
```

### 5. Testing

```python
def test_my_generator():
    config = ConfigReader({"project_name": "test"})
    generator = MyGenerator(config)
    generator.generate()
    
    assert os.path.exists("test/app/feature.py")
    with open("test/app/feature.py") as f:
        content = f.read()
        assert "expected_content" in content
```

## Common Patterns

### Adding Configuration Options

```python
# 1. Add to config collection (commands/init.py)
enable_feature = questionary.confirm(
    "Enable my feature?"
).ask()

config["enable_my_feature"] = enable_feature

# 2. Add ConfigReader method (core/config_reader.py)
def enable_my_feature(self) -> bool:
    return self.config.get("enable_my_feature", False)

# 3. Use in generator
@Generator(
    enabled_when=lambda c: c.enable_my_feature()
)
class MyFeatureGenerator(BaseTemplateGenerator):
    pass
```

### Modifying Existing Files

```python
def generate(self):
    # Read existing file
    with open("app/main.py", "r") as f:
        content = f.read()
    
    # Modify content
    import_line = "from app.routers import my_router\n"
    if import_line not in content:
        # Add import after other imports
        content = content.replace(
            "from app.core import config\n",
            f"from app.core import config\n{import_line}"
        )
    
    # Write back
    with open("app/main.py", "w") as f:
        f.write(content)
```

## Troubleshooting

### Generator Not Running

1. Check if imported in `__init__.py`
2. Verify `enabled_when` condition
3. Check dependencies are satisfied
4. Verify priority and category

### Circular Dependencies

```python
# Bad
@Generator(requires=["B"])
class A(BaseTemplateGenerator):
    pass

@Generator(requires=["A"])
class B(BaseTemplateGenerator):
    pass

# Good
@Generator(requires=[])
class A(BaseTemplateGenerator):
    pass

@Generator(requires=["A"])
class B(BaseTemplateGenerator):
    pass
```

### File Not Created

1. Check directory exists (use `_ensure_directory`)
2. Verify file path is correct
3. Check permissions
4. Look for exceptions in logs

## See Also

- [Generator Decorator API](../api/generator-decorator.md) - Decorator reference
- [Orchestrator API](../api/orchestrator.md) - Execution system
- [ConfigReader API](../api/config-reader.md) - Configuration access
- [Generator System Architecture](../architecture/generator-system.md) - System design
