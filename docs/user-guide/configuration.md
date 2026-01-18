# Configuration

Forge uses a configuration-first approach. When you run `forge init`, your choices are saved to `.forge/config.json`. This file drives the code generation process.

## Configuration File Structure

The `.forge/config.json` file contains all project settings:

```json
{
  "project_name": "my-project",
  "database": {
    "type": "PostgreSQL",
    "orm": "SQLModel",
    "migration_tool": "Alembic"
  },
  "features": {
    "auth": {
      "type": "complete",
      "refresh_token": true,
      "features": ["Email Verification", "Password Reset", "Email Service"]
    },
    "cors": true,
    "redis": true,
    "celery": true,
    "testing": true,
    "docker": true,
    "dev_tools": true
  },
  "metadata": {
    "created_at": "2024-01-01T00:00:00",
    "forge_version": "0.1.8"
  }
}
```

## Project Information

| Field | Description |
|-------|-------------|
| `project_name` | Project directory name and Python package name |

## Database Configuration

### database.type

The database system to use:

| Value | Description |
|-------|-------------|
| `PostgreSQL` | Production-ready, full-featured (recommended) |
| `MySQL` | Alternative production database |
| `SQLite` | File-based, good for development and testing |

### database.orm

The ORM library:

| Value | Description |
|-------|-------------|
| `SQLModel` | Combines SQLAlchemy and Pydantic, simpler syntax |
| `SQLAlchemy` | Full-featured ORM with more flexibility |

## Feature Flags

### features.auth

Authentication configuration:

| Field | Values | Description |
|-------|--------|-------------|
| `type` | `basic`, `complete` | Authentication mode |
| `refresh_token` | `true`, `false` | Enable refresh tokens (auto-enabled for complete) |

**Basic JWT Auth** provides:
- User registration and login
- Access token generation
- Current user endpoint

**Complete JWT Auth** adds:
- Email verification
- Password reset via email
- Refresh token rotation
- Multi-device session management
- Device tracking

### features.cors

When `true`, generates CORS middleware configuration. Environment variables:

```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
CORS_ALLOW_HEADERS=*
```

### features.redis

When `true`, generates Redis connection manager with:
- Async client for FastAPI
- Sync client for Celery tasks
- Connection pooling
- Basic get/set/delete operations

### features.celery

When `true` (requires Redis), generates:
- Celery application configuration
- Worker and beat setup
- Database backup task example
- Docker services for worker and beat

### features.testing

When `true`, generates:
- pytest configuration in pyproject.toml
- Test fixtures in `tests/conftest.py`
- Example tests for authentication endpoints
- SQLite test database setup

### features.docker

When `true`, generates:
- `Dockerfile` for the application
- `docker-compose.yml` with all services
- Database service (PostgreSQL or MySQL)
- Redis service (if enabled)
- Celery services (if enabled)
- Automatic migration service

### features.migration

When `true`, generates Alembic configuration:
- `alembic.ini` configuration file
- `alembic/env.py` with async support
- Migration script template

### features.dev_tools

When `true`, adds development dependencies:
- Black (code formatting)
- Ruff (linting)
- mypy (type checking)

## Environment Variables

Generated projects use environment variables for configuration. Files are created in the `secret/` directory:

| File | Purpose |
|------|---------|
| `.env.example` | Template with all variables |
| `.env.development` | Development settings |
| `.env.production` | Production settings (update before deploying) |

### Application Settings

```bash
APP_NAME="my-project"
APP_VERSION="1.0.0"
APP_DESCRIPTION="My FastAPI project"
```

### Database Settings

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# MySQL
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname

# SQLite
DATABASE_URL=sqlite+aiosqlite:///./database.db

# Connection pool
ECHO=false
POOL_PRE_PING=true
POOL_TIMEOUT=30
POOL_SIZE=6
POOL_MAX_OVERFLOW=2
```

### JWT Settings

```bash
JWT_SECRET_KEY=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRATION=1800      # 30 minutes
JWT_REFRESH_TOKEN_EXPIRATION=86400    # 24 hours
JWT_ISSUER=my-project
JWT_AUDIENCE=my-project_users
```

### Email Settings (Complete Auth)

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=true
EMAIL_FROM_NAME="My Project"
EMAIL_FROM_EMAIL=noreply@example.com
```

### Redis Settings

```bash
REDIS_CONNECTION_URL=redis://localhost:6379
REDIS_POOL_SIZE=5
REDIS_SOCKET_TIMEOUT=10
REDIS_DEFAULT_TTL=3600
```

### Celery Settings

```bash
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_TIMEZONE=UTC
CELERY_WORKER_CONCURRENCY=4
```

### Logging Settings

```bash
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=logs/app.log
LOG_TO_CONSOLE=true
LOG_ROTATION=1 day
LOG_RETENTION_PERIOD=7 days
```

## Modifying Configuration

The `.forge/config.json` file is only used during initial generation. To change settings after generation:

1. **Environment variables**: Edit files in `secret/`
2. **Code changes**: Modify the generated code directly
3. **Regenerate**: Delete the project and run `forge init` again

Forge does not support incremental regeneration—it's designed for initial project scaffolding.
