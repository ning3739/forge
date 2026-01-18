# Changelog

All notable changes to Forge are documented here.

## [0.1.8] - Latest

### Features
- Complete JWT authentication with email verification
- Refresh token rotation and multi-device support
- Database backup Celery task
- Redis connection manager with async/sync support
- Docker Compose with health checks and automatic migrations

### Improvements
- Async database operations throughout
- Argon2 password hashing
- Improved error handling in generated code
- Better logging configuration

### Documentation
- Complete documentation rewrite
- Added developer guide
- Architecture documentation

## [0.1.7]

### Features
- Basic JWT authentication
- SQLModel and SQLAlchemy ORM support
- PostgreSQL, MySQL, SQLite database support

### Improvements
- Interactive CLI with questionary
- Beautiful terminal UI with Rich

## [0.1.6]

### Features
- Initial Celery integration
- Redis caching support
- Docker deployment configuration

## [0.1.5]

### Features
- Alembic database migrations
- pytest testing configuration
- Development tools (Black, Ruff)

## [0.1.0]

### Initial Release
- Project scaffolding with `forge init`
- FastAPI project generation
- Basic project structure
- pyproject.toml generation
