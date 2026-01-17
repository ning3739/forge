# Configuration Options

Forge uses a configuration-first approach. All project settings are stored in `.forge/config.json` and used to generate your FastAPI project.

## Configuration File Location

After running `forge init`, the configuration is saved to:

```
your-project/
└── .forge/
    └── config.json
```

## Configuration Structure

```json
{
  "project_name": "my_api",
  "database": {
    "type": "PostgreSQL",
    "orm": "SQLModel",
    "migration_tool": "Alembic"
  },
  "features": {
    "auth": {
      "type": "complete",
      "refresh_token": true
    },
    "redis": {
      "enabled": true,
      "features": ["caching", "sessions", "queues"]
    },
    "celery": {
      "enabled": true,
      "features": ["background_tasks", "scheduled_tasks", "task_monitoring"]
    },
    "cors": true,
    "dev_tools": true,
    "testing": true,
    "docker": true
  },
  "metadata": {
    "created_at": "2026-01-18T12:00:00.000000",
    "forge_version": "0.1.8.4"
  }
}
```

## Configuration Options

### Project Settings

#### `project_name`

- **Type**: `string`
- **Required**: Yes
- **Description**: Name of your project (used for directory name and package name)
- **Example**: `"my_api"`, `"blog_backend"`
- **Rules**: 
  - Must be a valid Python package name
  - Use lowercase with underscores
  - Use `.` to generate in current directory

### Database Options

#### `database.type`

- **Type**: `string`
- **Required**: Yes
- **Options**: `"PostgreSQL"`, `"MySQL"`, `"SQLite"`
- **Description**: Database system to use
- **Default**: `"PostgreSQL"`

**PostgreSQL** (Recommended for production):
- Async driver: `asyncpg`
- Full-featured relational database
- Best for production applications

**MySQL**:
- Async driver: `aiomysql`
- Popular relational database
- Good compatibility with existing systems

**SQLite**:
- Async driver: `aiosqlite`
- File-based database
- Perfect for development and small applications

#### `database.orm`

- **Type**: `string`
- **Required**: Yes
- **Options**: `"SQLModel"`, `"SQLAlchemy"`
- **Description**: ORM framework to use
- **Default**: `"SQLModel"`

**SQLModel** (Recommended):
- Modern, type-safe ORM
- Built on top of SQLAlchemy and Pydantic
- Better integration with FastAPI
- Cleaner syntax

**SQLAlchemy**:
- Mature, battle-tested ORM
- More features and flexibility
- Larger ecosystem

### Authentication Options

#### `features.auth.type`

- **Type**: `string`
- **Required**: Yes
- **Options**: `"basic"`, `"complete"`
- **Description**: Authentication system to include

**Basic**:
- JWT token authentication
- User registration and login
- Password hashing with bcrypt
- Token-based API access

**Complete**:
- Everything in Basic, plus:
- Email verification system
- Password reset functionality
- Email templates
- Token refresh mechanism

### Optional Features

#### `features.redis`

- **Type**: `object` or `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include Redis for caching and session storage

When enabled as object:
```json
"redis": {
  "enabled": true,
  "features": ["caching", "sessions", "queues"]
}
```

When enabled as boolean:
```json
"redis": true
```

#### `features.celery`

- **Type**: `object` or `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include Celery for background tasks

When enabled as object:
```json
"celery": {
  "enabled": true,
  "features": ["background_tasks", "scheduled_tasks", "task_monitoring"]
}
```

When enabled as boolean:
```json
"celery": true
```

**Note**: Celery requires Redis, so `redis` will be automatically enabled.

#### `features.cors`

- **Type**: `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Enable CORS middleware

#### `features.dev_tools`

- **Type**: `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include development tools (Black + Ruff)

#### `features.testing`

- **Type**: `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include pytest test suite

When enabled:
- Test configuration (`conftest.py`)
- Database test fixtures
- API endpoint tests
- Authentication tests
- User management tests
- 80%+ code coverage

#### `features.docker`

- **Type**: `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include Docker deployment configuration

When enabled:
- `Dockerfile` for application
- `docker-compose.yml` for all services
- `.dockerignore` file
- Production-ready configuration
- Health checks and dependencies

## Modifying Configuration

### Before Generation

Simply re-run `forge init` and provide new answers to the prompts.

### After Generation

You can manually edit `.forge/config.json` and regenerate specific components, but it's generally easier to:

1. Create a new project with the desired configuration
2. Copy your custom code to the new project
3. Or manually add the features you need

## Configuration Examples

### Minimal API (SQLite, Basic Auth)

```json
{
  "project_name": "simple_api",
  "database": {
    "type": "SQLite",
    "orm": "SQLModel",
    "migration_tool": "Alembic"
  },
  "features": {
    "auth": {
      "type": "basic",
      "refresh_token": false
    },
    "cors": true,
    "dev_tools": false,
    "testing": false,
    "docker": false
  }
}
```

### Full-Featured Production API

```json
{
  "project_name": "production_api",
  "database": {
    "type": "PostgreSQL",
    "orm": "SQLModel",
    "migration_tool": "Alembic"
  },
  "features": {
    "auth": {
      "type": "complete",
      "refresh_token": true
    },
    "redis": {
      "enabled": true,
      "features": ["caching", "sessions", "queues"]
    },
    "celery": {
      "enabled": true,
      "features": ["background_tasks", "scheduled_tasks", "task_monitoring"]
    },
    "cors": true,
    "dev_tools": true,
    "testing": true,
    "docker": true
  }
}
```

### Development API with Testing

```json
{
  "project_name": "dev_api",
  "database": {
    "type": "SQLite",
    "orm": "SQLModel",
    "migration_tool": "Alembic"
  },
  "features": {
    "auth": {
      "type": "basic",
      "refresh_token": false
    },
    "cors": true,
    "dev_tools": true,
    "testing": true,
    "docker": false
  }
}
```

## Environment Variables

After generation, your project will have environment files:

- `.env.development` - Development settings (localhost)
- `.env.production` - Production settings (Docker service names)

These files contain:
- Database connection strings
- JWT secret keys
- Redis URLs (if enabled)
- Email settings (if complete auth)
- Application settings

## See Also

- [Quick Start](../getting-started/quickstart.md) - Get started quickly
- [First Project](../getting-started/first-project.md) - Detailed walkthrough
- [CLI Commands](cli-commands.md) - Command reference
