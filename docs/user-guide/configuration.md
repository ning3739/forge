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
  "database": "postgresql",
  "orm": "sqlmodel",
  "auth_mode": "complete",
  "use_redis": true,
  "use_celery": true,
  "use_docker": true,
  "include_tests": true
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

#### `database`

- **Type**: `string`
- **Required**: Yes
- **Options**: `"postgresql"`, `"mysql"`, `"sqlite"`
- **Description**: Database system to use
- **Default**: `"postgresql"`

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

#### `orm`

- **Type**: `string`
- **Required**: Yes
- **Options**: `"sqlmodel"`, `"sqlalchemy"`
- **Description**: ORM framework to use
- **Default**: `"sqlmodel"`

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

#### `auth_mode`

- **Type**: `string`
- **Required**: Yes
- **Options**: `"none"`, `"basic"`, `"complete"`
- **Description**: Authentication system to include

**None**:
- No authentication system
- Use for public APIs or when implementing custom auth

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

#### `use_redis`

- **Type**: `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include Redis for caching and session storage

When enabled:
- Redis client configuration
- Async Redis connection
- Cache utilities
- Session management support

#### `use_celery`

- **Type**: `boolean`
- **Required**: No
- **Default**: `false`
- **Description**: Include Celery for background tasks

When enabled:
- Celery worker configuration
- Celery Beat for scheduled tasks
- Database backup task example
- Task monitoring setup

**Note**: Celery requires Redis, so `use_redis` will be automatically enabled.

#### `use_docker`

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

#### `include_tests`

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

## Modifying Configuration

### Before Generation

Simply re-run `forge init` and provide new answers to the prompts.

### After Generation

You can manually edit `.forge/config.json` and regenerate specific components, but it's generally easier to:

1. Create a new project with the desired configuration
2. Copy your custom code to the new project
3. Or manually add the features you need

## Configuration Examples

### Minimal API (No Auth, SQLite)

```json
{
  "project_name": "simple_api",
  "database": "sqlite",
  "orm": "sqlmodel",
  "auth_mode": "none",
  "use_redis": false,
  "use_celery": false,
  "use_docker": false,
  "include_tests": false
}
```

### Full-Featured Production API

```json
{
  "project_name": "production_api",
  "database": "postgresql",
  "orm": "sqlmodel",
  "auth_mode": "complete",
  "use_redis": true,
  "use_celery": true,
  "use_docker": true,
  "include_tests": true
}
```

### Development API with Testing

```json
{
  "project_name": "dev_api",
  "database": "sqlite",
  "orm": "sqlmodel",
  "auth_mode": "basic",
  "use_redis": false,
  "use_celery": false,
  "use_docker": false,
  "include_tests": true
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
