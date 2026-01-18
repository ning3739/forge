# Database

Forge generates a complete database layer with async support, connection pooling, and migration management.

## Supported Databases

| Database | Driver | Best For |
|----------|--------|----------|
| PostgreSQL | asyncpg | Production environments |
| MySQL | aiomysql | Production environments |
| SQLite | aiosqlite | Development and testing |

## ORM Options

### SQLModel

SQLModel combines SQLAlchemy Core with Pydantic models. It's simpler and integrates well with FastAPI:

```python
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
```

### SQLAlchemy

SQLAlchemy provides more flexibility and advanced features:

```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
```

## Database Connection

### Connection Manager

For PostgreSQL and MySQL, Forge generates a `DatabaseConnectionManager` in `app/core/database/connection.py`:

```python
class DatabaseConnectionManager:
    async def initialize(self) -> None:
        """Initialize database connections"""
        await self.postgresql_manager.initialize()
    
    async def test_connections(self) -> bool:
        """Test database connectivity"""
        await self.postgresql_manager.test_connection()
        return True
    
    async def close(self) -> None:
        """Close all connections"""
        await self.postgresql_manager.close()
```

### Getting a Session

Use the `get_db` dependency in your routes:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    # Use db session here
    pass
```

### Connection Pool Settings

Configure the connection pool via environment variables:

```bash
ECHO=false              # Log SQL queries
POOL_PRE_PING=true      # Test connections before use
POOL_TIMEOUT=30         # Connection timeout in seconds
POOL_SIZE=6             # Number of connections to maintain
POOL_MAX_OVERFLOW=2     # Extra connections allowed
```

## Database Migrations

Forge uses Alembic for database migrations with async support.

### Configuration

The `alembic/env.py` file is configured to:
- Load database URL from environment variables
- Use async database drivers
- Auto-import all models for autogenerate

### Creating Migrations

Generate a migration after changing models:

```bash
alembic revision --autogenerate -m "Add new field"
```

Review the generated migration in `alembic/versions/` before applying.

### Applying Migrations

Apply all pending migrations:

```bash
alembic upgrade head
```

Apply one migration at a time:

```bash
alembic upgrade +1
```

### Rolling Back

Rollback one migration:

```bash
alembic downgrade -1
```

Rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

Rollback all migrations:

```bash
alembic downgrade base
```

### Viewing History

```bash
# Current revision
alembic current

# Migration history
alembic history

# Detailed history
alembic history --verbose
```

## Adding New Models

### Step 1: Create the Model

Create a new file in `app/models/`:

```python
# app/models/post.py
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Step 2: Import in env.py

Ensure the model is imported in `alembic/env.py`:

```python
# Import all models so Alembic can detect them
from app.models.user import User
from app.models.post import Post  # Add this
```

### Step 3: Generate Migration

```bash
alembic revision --autogenerate -m "Add posts table"
```

### Step 4: Apply Migration

```bash
alembic upgrade head
```

## CRUD Operations

Forge generates CRUD classes for authentication models. Follow the same pattern for new models:

```python
# app/crud/post.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.post import Post

class PostCRUD:
    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
        return await db.get(Post, post_id)
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Post]:
        statement = select(Post).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, post: Post) -> Post:
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post

post_crud = PostCRUD()
```

## Docker Database Setup

When Docker is enabled, `docker-compose.yml` includes the database service:

**PostgreSQL:**
```yaml
db:
  image: postgres:15-alpine
  environment:
    - POSTGRES_USER=postgres
    - POSTGRES_PASSWORD=postgres
    - POSTGRES_DB=my_project
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

**MySQL:**
```yaml
db:
  image: mysql:8.0
  environment:
    - MYSQL_ROOT_PASSWORD=mysql
    - MYSQL_DATABASE=my_project
  ports:
    - "3306:3306"
  volumes:
    - mysql_data:/var/lib/mysql
```

The `db-migrate` service automatically runs migrations on startup:

```yaml
db-migrate:
  build: .
  command: sh -c "alembic revision --autogenerate -m 'Auto migration' && alembic upgrade head"
  depends_on:
    db:
      condition: service_healthy
```
