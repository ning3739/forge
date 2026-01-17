# Database Setup

Forge supports three database systems: PostgreSQL, MySQL, and SQLite. This guide covers setup, configuration, and best practices for each.

## Database Selection

Choose your database during `forge init`:

```bash
? Select database: 
  PostgreSQL (Recommended for production)
  MySQL
❯ SQLite (Good for development)
```

## PostgreSQL

### Installation

**macOS (Homebrew)**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**:
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### Configuration

**Development** (`.env.development`):
```ini
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

**Production** (`.env.production`):
```ini
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/dbname
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE myapi;
CREATE USER myapi_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE myapi TO myapi_user;
```

### Python Dependencies

Automatically included in `pyproject.toml`:
```toml
asyncpg = "^0.29.0"  # Async PostgreSQL driver
```

## MySQL

### Installation

**macOS (Homebrew)**:
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

**Windows**:
Download from [mysql.com](https://dev.mysql.com/downloads/installer/)

### Configuration

**Development** (`.env.development`):
```ini
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
```

**Production** (`.env.production`):
```ini
DATABASE_URL=mysql+aiomysql://user:password@db:3306/dbname
```

### Create Database

```bash
# Connect to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE myapi;
CREATE USER 'myapi_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON myapi.* TO 'myapi_user'@'localhost';
FLUSH PRIVILEGES;
```

### Python Dependencies

Automatically included in `pyproject.toml`:
```toml
aiomysql = "^0.2.0"  # Async MySQL driver
cryptography = "^41.0.0"  # Required by aiomysql
```

## SQLite

### Installation

SQLite comes pre-installed with Python. No additional installation needed!

### Configuration

**Development** (`.env.development`):
```ini
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

**Production**:
SQLite is not recommended for production with multiple workers. Use PostgreSQL or MySQL instead.

### Python Dependencies

Automatically included in `pyproject.toml`:
```toml
aiosqlite = "^0.19.0"  # Async SQLite driver
```

### Advantages

- Zero configuration
- Perfect for development
- Single file database
- Great for testing
- No separate server needed

### Limitations

- Not suitable for high-concurrency production
- Limited concurrent write operations
- No network access
- Single file can be a bottleneck

## Database Migrations

Forge uses Alembic for database migrations.

### Initial Migration

After project generation, create the initial migration:

```bash
# Generate migration from models
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Creating Migrations

When you modify models:

```bash
# Generate migration
alembic revision --autogenerate -m "Add user profile fields"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### Migration Commands

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

## ORM Configuration

### SQLModel (Recommended)

Generated code uses SQLModel for type-safe database operations:

```python
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
```

### SQLAlchemy

If you chose SQLAlchemy:

```python
from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

## Database Connection

### Connection Pool

Generated projects use async connection pooling:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max overflow connections
)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
```

### Dependency Injection

Use FastAPI's dependency injection:

```python
from app.core.deps import get_db

@router.get("/users/")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

## Docker Database Setup

When using Docker (`use_docker: true`), databases are configured in `docker-compose.yml`:

### PostgreSQL Service

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### MySQL Service

```yaml
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Backup and Restore

### Celery Backup Task

If you enabled Celery, a database backup task is included:

```python
# Runs daily at 2 AM
@celery_app.task
def backup_database_task():
    """Backup database based on type"""
    # PostgreSQL: pg_dump
    # MySQL: mysqldump
    # SQLite: file copy
```

### Manual Backup

**PostgreSQL**:
```bash
pg_dump -U user dbname > backup.sql
```

**MySQL**:
```bash
mysqldump -u user -p dbname > backup.sql
```

**SQLite**:
```bash
cp app.db backup.db
```

### Restore

**PostgreSQL**:
```bash
psql -U user dbname < backup.sql
```

**MySQL**:
```bash
mysql -u user -p dbname < backup.sql
```

**SQLite**:
```bash
cp backup.db app.db
```

## Best Practices

### Development

1. Use SQLite for quick prototyping
2. Enable SQL query logging (`echo=True`)
3. Use migrations from the start
4. Test with production database type before deploying

### Production

1. Use PostgreSQL or MySQL
2. Disable SQL query logging (`echo=False`)
3. Use connection pooling
4. Set up regular backups
5. Monitor database performance
6. Use read replicas for scaling
7. Implement proper indexing

### Security

1. Never commit `.env` files
2. Use strong database passwords
3. Limit database user permissions
4. Use SSL/TLS for connections
5. Keep database software updated
6. Regular security audits

## Troubleshooting

### Connection Refused

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Ensure database server is running:
```bash
# PostgreSQL
brew services start postgresql@15

# MySQL
brew services start mysql
```

### Authentication Failed

```
sqlalchemy.exc.OperationalError: authentication failed
```

**Solution**: Check credentials in `.env.development`:
- Verify username and password
- Ensure user has proper permissions
- Check database exists

### Database Does Not Exist

```
sqlalchemy.exc.OperationalError: database "myapi" does not exist
```

**Solution**: Create the database:
```bash
# PostgreSQL
createdb myapi

# MySQL
mysql -u root -p -e "CREATE DATABASE myapi;"
```

### Migration Conflicts

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution**: 
```bash
# Check current state
alembic current

# Upgrade to latest
alembic upgrade head

# Or start fresh (development only!)
alembic downgrade base
alembic upgrade head
```

## See Also

- [Configuration Options](configuration.md) - Database configuration
- [Authentication Guide](authentication.md) - User models and auth
- [Testing Guide](testing.md) - Database testing
- [Deployment Guide](deployment.md) - Production database setup
