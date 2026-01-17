# Configuration Guide

This guide explains how configuration works in Forge-generated projects. You'll learn about the two types of configuration files, what each setting does, and how to configure your project for different environments.

## Two Types of Configuration

Forge uses two different configuration files for different purposes:

### 1. Project Configuration (`.forge/config.json`)

This file tells Forge what features your project has. It's created when you run `forge init` and contains your answers to the setup questions.

**Purpose**: Forge reads this file to understand your project structure. It's used during code generation.

**Location**: `.forge/config.json`

**When it's used**: Only when Forge generates or regenerates code

**Example**:
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
    "redis": true,
    "celery": true,
    "cors": true,
    "dev_tools": true,
    "testing": true,
    "docker": true
  },
  "metadata": {
    "created_at": "2024-01-18T10:30:00.000000",
    "forge_version": "0.1.8.5"
  }
}
```

**Important**: Don't delete this file! If you want to regenerate parts of your project later, Forge needs this file to understand your project structure.

### 2. Environment Configuration (`secret/.env.*`)

These files contain runtime settings like database passwords, API keys, and other secrets. Your application reads these files when it starts.

**Purpose**: Configure your application's behavior at runtime

**Location**: `secret/` directory (in `.gitignore` - never commit these!)

**Files**:
- `.env.example` - Template showing all available settings
- `.env.development` - Settings for local development
- `.env.production` - Settings for production deployment

**When they're used**: Every time your application starts

**Important**: These files contain secrets (passwords, API keys). They're automatically added to `.gitignore` so you don't accidentally commit them to Git.

## Project Configuration (`.forge/config.json`)

Let's understand each section of the project configuration:

### Project Name

```json
{
  "project_name": "my_api"
}
```

This is your project's name. It's used for:
- The project directory name
- The Python package name
- The default database name
- The JWT issuer/audience values

**Rules**:
- Must be a valid Python package name
- Use lowercase with underscores
- No spaces or special characters

### Database Configuration

```json
{
  "database": {
    "type": "PostgreSQL",
    "orm": "SQLModel",
    "migration_tool": "Alembic"
  }
}
```

**type**: Which database system to use
- `"PostgreSQL"` - Recommended for production (uses asyncpg driver)
- `"MySQL"` - Good for existing MySQL infrastructure (uses aiomysql driver)
- `"SQLite"` - Perfect for development (uses aiosqlite driver)

**orm**: Which ORM framework to use
- `"SQLModel"` - Modern, type-safe, recommended for new projects
- `"SQLAlchemy"` - Traditional, more features, more boilerplate

**migration_tool**: Database migration tool
- `"Alembic"` - Enable database migrations
- `null` - No migrations (not recommended)

### Features Configuration

```json
{
  "features": {
    "auth": {
      "type": "complete",
      "refresh_token": true
    },
    "redis": true,
    "celery": true,
    "cors": true,
    "dev_tools": true,
    "testing": true,
    "docker": true
  }
}
```

**auth**: Authentication configuration (required)
- `type`: `"basic"` or `"complete"`
- `refresh_token`: `true` or `false` (only for complete auth)

Authentication is mandatory in Forge projects. You must choose either basic or complete.

**redis**: Enable Redis for caching and message queues
- `true` - Include Redis support
- `false` - No Redis

**celery**: Enable Celery for background tasks
- `true` - Include Celery support (requires Redis)
- `false` - No Celery

**cors**: Enable CORS middleware
- `true` - Allow cross-origin requests
- `false` - Same-origin only

**dev_tools**: Include development tools
- `true` - Include Black and Ruff
- `false` - No dev tools

**testing**: Include test suite
- `true` - Include pytest and test files
- `false` - No tests

**docker**: Include Docker configuration
- `true` - Generate Dockerfile and docker-compose.yml
- `false` - No Docker files

### Metadata

```json
{
  "metadata": {
    "created_at": "2024-01-18T10:30:00.000000",
    "forge_version": "0.1.8.5"
  }
}
```

This section is automatically generated and tracks when the project was created and which Forge version was used.

## Environment Configuration (`secret/.env.*`)

Now let's look at the runtime configuration files. These contain the actual settings your application uses.

### Application Settings

These settings are always included:

```ini
# Application Configuration
APP_NAME="My API"
APP_VERSION="1.0.0"
APP_DESCRIPTION="My API Description"
```

**APP_NAME**: Your application's display name (used in emails, logs, etc.)

**APP_VERSION**: Your application's version number

**APP_DESCRIPTION**: A brief description of your application

### Database Settings

These settings are always included:

```ini
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mydb

# Connection Pool Configuration
ECHO=false
POOL_PRE_PING=true
POOL_TIMEOUT=30
POOL_SIZE=6
POOL_MAX_OVERFLOW=2
```

**DATABASE_URL**: The database connection string

Format: `dialect+driver://username:password@host:port/database`

Examples:
- PostgreSQL: `postgresql+asyncpg://postgres:password@localhost:5432/mydb`
- MySQL: `mysql+aiomysql://root:password@localhost:3306/mydb`
- SQLite: `sqlite+aiosqlite:///./mydb.db`

**ECHO**: Log all SQL queries (useful for debugging)
- `true` - Log all queries
- `false` - Don't log queries (recommended for production)

**POOL_PRE_PING**: Test connections before using them
- `true` - Prevents "connection lost" errors (recommended)
- `false` - Slightly faster but less reliable

**POOL_TIMEOUT**: How long to wait for a connection (seconds)

**POOL_SIZE**: Number of connections to keep open

**POOL_MAX_OVERFLOW**: Additional connections allowed when pool is full

### JWT Settings

These settings are always included (authentication is mandatory):

```ini
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRATION=1800
JWT_REFRESH_TOKEN_EXPIRATION=604800
JWT_ISSUER=my_api
JWT_AUDIENCE=my_api_users
```

**JWT_SECRET_KEY**: Secret key for signing JWT tokens

**CRITICAL**: Change this to a strong random value in production! Generate one with:
```python
import secrets
print(secrets.token_urlsafe(32))
```

**JWT_ALGORITHM**: Algorithm for signing tokens (HS256 is standard)

**JWT_ACCESS_TOKEN_EXPIRATION**: Access token lifetime in seconds
- Default: 1800 (30 minutes)
- Recommended: 1800-3600 (30 minutes to 1 hour)

**JWT_REFRESH_TOKEN_EXPIRATION**: Refresh token lifetime in seconds (Complete Auth only)
- Default: 604800 (7 days)
- Recommended: 604800-2592000 (7-30 days)

**JWT_ISSUER**: Token issuer (usually your app name)

**JWT_AUDIENCE**: Token audience (usually your app name + "_users")

### Email Settings (Complete Auth Only)

If you chose Complete JWT Auth, these settings are included:

```ini
# SMTP Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_TIMEOUT=30
EMAIL_EXPIRATION=3600

# Email From Configuration
EMAIL_FROM_NAME="My API"
EMAIL_FROM_EMAIL=noreply@yourdomain.com
```

**EMAIL_HOST**: SMTP server hostname

**EMAIL_PORT**: SMTP server port
- 587 for TLS (most common)
- 465 for SSL
- 25 for unencrypted (not recommended)

**EMAIL_HOST_USER**: SMTP username (usually your email address)

**EMAIL_HOST_PASSWORD**: SMTP password
- For Gmail: Use an App Password, not your regular password
- For other providers: Use your SMTP password or API key

**EMAIL_USE_TLS**: Use TLS encryption
- `true` - Use TLS (recommended for port 587)
- `false` - Don't use TLS

**EMAIL_USE_SSL**: Use SSL encryption
- `true` - Use SSL (for port 465)
- `false` - Don't use SSL (recommended for port 587)

**EMAIL_TIMEOUT**: How long to wait for email server (seconds)

**EMAIL_EXPIRATION**: How long verification codes are valid (seconds)
- Default: 3600 (1 hour)

**EMAIL_FROM_NAME**: Display name in "From" field

**EMAIL_FROM_EMAIL**: Email address in "From" field

### CORS Settings (If Enabled)

If you enabled CORS, these settings are included:

```ini
# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
CORS_ALLOW_HEADERS=*
CORS_EXPOSE_HEADERS=
```

**CORS_ALLOWED_ORIGINS**: Comma-separated list of allowed origins

Development example:
```ini
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000
```

Production example:
```ini
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**CORS_ALLOW_CREDENTIALS**: Allow cookies and authentication headers
- `true` - Allow credentials (needed for authentication)
- `false` - Don't allow credentials

**CORS_ALLOW_METHODS**: Allowed HTTP methods (comma-separated)

**CORS_ALLOW_HEADERS**: Allowed request headers
- `*` - Allow all headers
- Or specify: `Content-Type,Authorization`

**CORS_EXPOSE_HEADERS**: Headers exposed to the browser (usually empty)

### Redis Settings (If Enabled)

If you enabled Redis, these settings are included:

```ini
# Redis Configuration
REDIS_CONNECTION_URL=redis://localhost:6379
REDIS_POOL_SIZE=5
REDIS_SOCKET_TIMEOUT=10
REDIS_DEFAULT_TTL=3600
```

**REDIS_CONNECTION_URL**: Redis connection string

Format: `redis://[password@]host:port[/database]`

Examples:
- Local: `redis://localhost:6379`
- With password: `redis://:password@localhost:6379`
- Specific database: `redis://localhost:6379/1`
- Docker: `redis://redis:6379` (uses service name)

**REDIS_POOL_SIZE**: Number of connections to keep open
- Development: 3-5
- Production: 10-20

**REDIS_SOCKET_TIMEOUT**: Connection timeout in seconds

**REDIS_DEFAULT_TTL**: Default cache expiration in seconds
- Default: 3600 (1 hour)

### Celery Settings (If Enabled)

If you enabled Celery, these settings are included:

```ini
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_ACCEPT_CONTENT=["json"]
CELERY_TIMEZONE=UTC
CELERY_ENABLE_UTC=true
CELERY_TASK_ALWAYS_EAGER=false
CELERY_TASK_EAGER_PROPAGATES=true
CELERY_WORKER_CONCURRENCY=4
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_RESULT_EXPIRES=3600
CELERY_TASK_ROUTES={}
```

**CELERY_BROKER_URL**: Message broker URL (Redis)
- Use a different database number than Redis cache
- Example: `redis://localhost:6379/1`

**CELERY_RESULT_BACKEND**: Where to store task results
- Use a different database number than broker
- Example: `redis://localhost:6379/2`

**CELERY_TASK_SERIALIZER**: How to serialize task arguments
- `json` - Standard, safe (recommended)
- `pickle` - More flexible but less safe

**CELERY_RESULT_SERIALIZER**: How to serialize task results
- `json` - Standard, safe (recommended)

**CELERY_ACCEPT_CONTENT**: Accepted serialization formats
- `["json"]` - Only accept JSON (recommended)

**CELERY_TIMEZONE**: Timezone for scheduled tasks
- `UTC` - Recommended

**CELERY_ENABLE_UTC**: Use UTC for all times
- `true` - Recommended

**CELERY_TASK_ALWAYS_EAGER**: Execute tasks immediately (for testing)
- `false` - Use Celery worker (production)
- `true` - Execute immediately (testing only)

**CELERY_WORKER_CONCURRENCY**: Number of worker processes
- Development: 2-4
- Production: 4-8 (depends on your server)

**CELERY_WORKER_PREFETCH_MULTIPLIER**: Tasks to prefetch per worker
- `1` - Fetch one task at a time (recommended)
- Higher values can improve throughput but may cause uneven distribution

**CELERY_RESULT_EXPIRES**: How long to keep task results (seconds)
- Default: 3600 (1 hour)

**CELERY_TASK_ROUTES**: Task routing configuration (JSON format)
- Empty by default: `{}`

### Logging Settings

These settings are always included:

```ini
# Logging Configuration
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=logs/app.log
LOG_TO_CONSOLE=true
LOG_CONSOLE_LEVEL=INFO
LOG_ROTATION=1 day
LOG_RETENTION_PERIOD=7 days
```

**LOG_LEVEL**: Minimum log level to record
- `DEBUG` - Everything (very verbose)
- `INFO` - General information (recommended for development)
- `WARNING` - Warnings and errors only
- `ERROR` - Errors only (recommended for production)

**LOG_TO_FILE**: Write logs to file
- `true` - Write to file (recommended)
- `false` - Don't write to file

**LOG_FILE_PATH**: Where to write log files

**LOG_TO_CONSOLE**: Print logs to console
- `true` - Print to console (recommended for development)
- `false` - Don't print to console (recommended for production)

**LOG_CONSOLE_LEVEL**: Minimum level for console logs

**LOG_ROTATION**: When to rotate log files
- `1 day` - Daily rotation (recommended)
- `1 week` - Weekly rotation
- `100 MB` - Rotate when file reaches 100MB

**LOG_RETENTION_PERIOD**: How long to keep old log files
- `7 days` - Keep for 7 days (recommended)
- `30 days` - Keep for 30 days

## Development vs Production Configuration

Forge generates two environment files with different settings:

### Development (`.env.development`)

Optimized for local development:

- Database: `localhost` URLs
- Redis: `localhost:6379`
- Celery: `localhost` Redis URLs
- Logging: `DEBUG` level, console output
- CORS: Allows `localhost` origins
- ECHO: `true` (log SQL queries)

### Production (`.env.production`)

Optimized for Docker deployment:

- Database: Uses Docker service names (`db` instead of `localhost`)
- Redis: Uses Docker service name (`redis` instead of `localhost`)
- Celery: Uses Docker service names
- Logging: `INFO` level, file output only
- CORS: Specific production domains only
- ECHO: `false` (don't log SQL queries)

**Important**: Always review and update `.env.production` before deploying:
1. Change `JWT_SECRET_KEY` to a strong random value
2. Update database passwords
3. Update CORS origins to your actual domain
4. Update email settings with production SMTP credentials

## Environment Variable Loading

Your application automatically loads the correct environment file based on the `ENVIRONMENT` variable:

```bash
# Development (default)
export ENVIRONMENT=development
uvicorn app.main:app --reload

# Production
export ENVIRONMENT=production
uvicorn app.main:app
```

The loading logic is in your application's configuration code:

```python
from pathlib import Path
from dotenv import load_dotenv
import os

# Determine which environment file to load
env = os.getenv("ENVIRONMENT", "development")
env_file = Path(__file__).parent.parent / "secret" / f".env.{env}"

# Load the environment file
load_dotenv(env_file)
```

## Configuration Examples

### Minimal Development Setup

For quick local development with SQLite:

```json
{
  "project_name": "quick_api",
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
    "testing": false,
    "docker": false,
    "redis": false,
    "celery": false
  }
}
```

### Full Production Setup

For a production API with all features:

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
    "cors": true,
    "dev_tools": true,
    "testing": true,
    "docker": true,
    "redis": true,
    "celery": true
  }
}
```

## Security Best Practices

### 1. Never Commit Secrets

The `secret/` directory is in `.gitignore` by default. Never remove it from `.gitignore` and never commit these files:
- `.env.development`
- `.env.production`

### 2. Use Strong Secret Keys

Generate strong random keys for production:

```python
import secrets

# JWT secret key
print(secrets.token_urlsafe(32))

# Database password
print(secrets.token_urlsafe(16))
```

### 3. Use Environment-Specific Settings

Don't use development settings in production:
- Development: Verbose logging, localhost URLs, weak secrets
- Production: Minimal logging, production URLs, strong secrets

### 4. Restrict CORS Origins

In production, only allow your actual domains:

```ini
# Bad - allows any origin
CORS_ALLOWED_ORIGINS=*

# Good - specific domains only
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Use HTTPS in Production

Always use HTTPS in production. Update your URLs:

```ini
# Development
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Production
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## Troubleshooting

### "Configuration file not found"

Error: `FileNotFoundError: Configuration file not found: .forge/config.json`

Solution: Run `forge init` to create the configuration file.

### "Invalid JSON in configuration file"

Error: `ConfigValidationError: Invalid JSON in configuration file`

Solution: Check `.forge/config.json` for syntax errors (missing commas, quotes, etc.)

### Environment Variables Not Loading

Problem: Settings from `.env` file aren't being used

Solutions:
1. Check the file exists: `ls secret/.env.development`
2. Check `ENVIRONMENT` variable: `echo $ENVIRONMENT`
3. Check file permissions: `chmod 644 secret/.env.development`
4. Restart your application

### Database Connection Errors

Problem: Can't connect to database

Solutions:
1. Check `DATABASE_URL` is correct
2. Check database is running
3. Check username/password are correct
4. Check database exists

### Email Not Sending

Problem: Emails aren't being sent (Complete Auth)

Solutions:
1. Check SMTP settings are correct
2. For Gmail, use App Password not regular password
3. Check `EMAIL_USE_TLS` matches your port (587=TLS, 465=SSL)
4. Test SMTP connection manually
5. Check logs: `logs/app_development.log`

## Next Steps

- **[Database Guide](database.md)** - Configure database connections and migrations
- **[Authentication Guide](authentication.md)** - Configure JWT and email settings
- **[Redis Caching](redis-caching.md)** - Configure Redis for caching
- **[Celery Tasks](celery-tasks.md)** - Configure Celery for background tasks
- **[Deployment Guide](deployment.md)** - Production configuration best practices
