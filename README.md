<div align="center">
  <img src="https://github.com/ning3739/forge/blob/main/assets/logo.svg?raw=true" alt="Forge Logo" width="480"/>
</div>

<br/>

<div align="center">

[![PyPI version](https://badge.fury.io/py/ningfastforge.svg)](https://badge.fury.io/py/ningfastforge)
[![Python Versions](https://img.shields.io/pypi/pyversions/ningfastforge.svg)](https://pypi.org/project/ningfastforge/)
[![Downloads](https://static.pepy.tech/badge/ningfastforge)](https://pepy.tech/project/ningfastforge)
[![Downloads per month](https://static.pepy.tech/badge/ningfastforge/month)](https://pepy.tech/project/ningfastforge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

Forge is a powerful command-line tool that helps you quickly bootstrap production-ready FastAPI projects with best practices, intelligent defaults, and a beautiful interactive interface.

## ✨ Features

- 🎨 **Beautiful Interactive UI** - Stunning terminal interface with gradient colors and smooth animations
- 🚀 **Smart Presets** - Carefully curated presets for testing, dev tools, deployment, and monitoring
- 🔐 **Authentication Ready** - Built-in support for JWT authentication (Basic & Complete)
- 🗄️ **Database Flexibility** - Support for PostgreSQL, MySQL, and SQLite with SQLModel/SQLAlchemy
- 🔴 **Redis Integration** - Built-in Redis support for caching, sessions, and message queues
- 📋 **Background Tasks** - Celery integration with Redis broker for async task processing
- 💾 **Database Backup** - Automated database backup tasks supporting all database types
- 📦 **Modular Architecture** - Choose only the features you need
- 🧪 **Testing Built-in** - Pre-configured pytest with async support and coverage
- 🐳 **Docker Ready** - Production-ready Docker and Docker Compose configurations
- 🔍 **Type Safe** - Full type hints throughout generated code
- ⚡ **Async First** - Optimized for FastAPI's async capabilities

## 📋 Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)

```bash
pip install ningfastforge
```

#### Upgrade to Latest Version

If you already have Forge installed, upgrade to the latest version:

```bash
pip install --upgrade ningfastforge
```

> 💡 **Tip**: Always use the latest version to get new features, bug fixes, and security updates!

#### From Source

```bash
# Clone the repository
git clone https://github.com/ning3739/forge.git
cd forge

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Verify Installation

Check that Forge is installed correctly and see the current version:

```bash
forge --version
```

### Create Your First Project

```bash
# Interactive mode (recommended)
forge init

# Or specify project name
forge init forge-project

# Non-interactive mode with defaults
forge init forge-project --no-interactive
```

### Run Your Project

```bash
cd forge-project
uv sync
uv run uvicorn app.main:app --reload
# Visit:
http://127.0.0.1:8000/docs # docs
http://127.0.0.1:8000/redoc #redoc
```

## 🏗️ Architecture

Forge follows a **"Configuration-First"** design principle with a **dynamic generator system**:

1. **Init Command** collects user preferences interactively
2. **Configuration File** (`.forge/config.json`) is saved first
3. **Dynamic Generator System** automatically discovers and executes generators based on configuration

### Dynamic Generator System

Forge uses a decorator-based system for automatic generator discovery and management:

```python
@Generator(
    category="model",
    priority=40,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.has_auth()
)
class UserModelGenerator:
    def generate(self):
        # Generate user model code
```

**Benefits:**
- ✅ Automatic generator discovery - no manual registration needed
- ✅ Dependency resolution - generators execute in correct order
- ✅ Conditional execution - only enabled generators run
- ✅ Easy extensibility - add new generators by creating files

This separation ensures:

- ✅ Configuration persistence and traceability
- ✅ Clear separation of concerns
- ✅ Easy project regeneration and updates
- ✅ Configuration sharing and templates
- ✅ Modular and maintainable codebase

## 🎯 Configuration Options

### Database Options

- **PostgreSQL** (Recommended) - Robust, feature-rich, excellent for production
- **MySQL** - Popular, widely supported relational database
- **SQLite** - Lightweight, serverless database perfect for development and small projects

### ORM Support

- **SQLModel** (Recommended) - Modern, type-safe ORM built on SQLAlchemy and Pydantic
- **SQLAlchemy** - Mature and powerful ORM with extensive features

### Authentication & Security

#### Authentication Options

- **Complete JWT Auth** (Recommended) - Full-featured authentication system
  - Login & Register
  - Email Verification
  - Password Reset (Forgot Password)
  - Email Service (SMTP)
  - Refresh Token
- **Basic JWT Auth** - Simple authentication
  - Login & Register only
  - Optional Refresh Token

#### Security Features

- CORS (Configurable)
- Rate Limiting (Built-in decorator - auto-included)
- Input Validation (Pydantic - auto-included)
- Password Hashing (bcrypt - auto-included with auth)
- SQL Injection Protection (ORM - auto-included)
- XSS Protection (FastAPI - auto-included)

### Core Features

All projects include:

- **Logging** - Structured logging with Loguru (automatically included)
- **API Documentation** - Swagger UI and ReDoc (automatically included)
- **Health Check** - Basic health check endpoint (automatically included)
- **Rate Limiting** - Decorator-based rate limiting for API protection (automatically included)

### Background Tasks & Caching

- **Redis** - In-memory data structure store for caching, sessions, and message queues
- **Celery** - Distributed task queue for background job processing
- **Database Backup** - Automated backup tasks supporting MySQL, PostgreSQL, and SQLite
- **Task Scheduling** - Cron-based task scheduling with Celery Beat (production)

### Development Tools

- **Standard** (Recommended) - Black (formatter) + Ruff (linter)
- **None** - Skip dev tools

### Testing Setup

When you enable testing, Forge generates:

- **pytest** - Testing framework with async support
- **httpx** - HTTP client for testing
- **pytest-cov** - Code coverage
- **pytest-asyncio** - Async test support

**Generated Test Files:**

- `tests/conftest.py` - Pytest configuration with database fixtures
- `tests/test_main.py` - Tests for main API endpoints (health check, docs)
- `tests/api/test_auth.py` - Authentication endpoint tests
- `tests/api/test_users.py` - User endpoint tests

**Running Tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v
```

### Deployment

- **Docker** - Dockerfile and docker-compose.yml
- Includes database service configuration
- Production-ready setup

## 📁 Generated Project Structure

```
forge-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config/          # Configuration management
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # Base configuration
│   │   │   ├── settings.py  # Settings aggregator
│   │   │   └── modules/     # Config modules (app, database, jwt, cors, email, logger, redis, celery)
│   │   │       ├── __init__.py
│   │   │       ├── app.py
│   │   │       ├── celery.py
│   │   │       ├── cors.py
│   │   │       ├── database.py
│   │   │       ├── email.py
│   │   │       ├── jwt.py
│   │   │       ├── logger.py
│   │   │       └── redis.py
│   │   ├── database/        # Database connection
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── dependencies.py
│   │   │   └── mysql.py     # Database-specific connection (mysql/postgresql/sqlite)
│   │   ├── redis.py         # Redis connection manager (if Redis enabled)
│   │   ├── celery.py        # Celery configuration (if Celery enabled)
│   │   ├── deps.py          # Global dependencies
│   │   ├── logger.py        # Logging configuration
│   │   └── security.py      # Security utilities (password hashing, JWT)
│   ├── decorators/          # Custom decorators
│   │   ├── __init__.py
│   │   └── rate_limit.py    # Rate limiting decorator
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── token.py         # (if refresh token enabled)
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── token.py
│   ├── crud/                # CRUD operations
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── token.py         # (if refresh token enabled)
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── tasks/               # Celery tasks (if Celery enabled)
│   │   ├── __init__.py      # Task exports
│   │   └── backup_database_task.py  # Database backup task
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   └── v1/              # API version 1
│   │       ├── __init__.py  # Router aggregator
│   │       ├── auth.py
│   │       └── users.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       └── email.py         # (if complete auth enabled)
├── tests/                   # Test files (if enabled)
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_main.py         # Main API endpoint tests
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_auth.py     # Authentication tests
│   │   └── test_users.py    # User endpoint tests
│   └── unit/                # Unit tests directory
│       └── __init__.py
├── alembic/                 # Database migrations (if enabled)
│   ├── versions/            # Migration versions
│   │   └── .gitkeep
│   ├── env.py               # Alembic environment
│   ├── script.py.mako       # Migration template
│   └── README.md
├── static/                  # Static files
│   └── email_template/      # Email templates (if complete auth)
│       ├── base.html
│       ├── verification.html
│       ├── password_reset.html
│       └── welcome.html
├── script/                  # Custom scripts directory
├── secret/                  # Environment files
│   ├── .env.example         # Environment variables template
│   ├── .env.development     # Development environment
│   └── .env.production      # Production environment
├── .forge/                  # Forge configuration
│   └── config.json          # Project configuration
├── docker-compose.yml       # Docker Compose configuration (if enabled)
├── Dockerfile               # Docker configuration (if enabled)
├── .dockerignore            # Docker ignore file (if enabled)
├── .gitignore               # Git ignore file
├── alembic.ini              # Alembic configuration (if migrations enabled)
├── pyproject.toml           # Project dependencies
├── uv.lock                  # UV lock file
├── LICENSE                  # MIT license
└── README.md                # Project documentation
```

## 🎨 Smart Features

### Intelligent Defaults

- **Database**: PostgreSQL with SQLModel
- **Migration**: Alembic enabled
- **Authentication**: Complete JWT Auth with Refresh Token
- **Caching**: Redis enabled
- **Background Tasks**: Celery with Redis broker
- **Security**: CORS enabled
- **Dev Tools**: Black + Ruff
- **Testing**: pytest with coverage
- **Deployment**: Docker + Docker Compose

### Technology Recommendations

- **PostgreSQL** for database (production-ready, feature-rich)
- **SQLModel** for ORM (modern, type-safe, FastAPI-friendly)
- **JWT** for authentication (stateless, scalable, API-friendly)
- **Redis** for caching and message queues (fast, reliable)
- **Celery** for background tasks (mature, scalable)
- **Alembic** for migrations (industry standard)

## 🛠️ Commands

### `forge init`

Initialize a new FastAPI project with interactive prompts.

```bash
# Interactive mode
forge init

# Specify project name
forge init forge-project

# Non-interactive mode (uses defaults)
forge init forge-project --no-interactive
```

### `forge --version`

Show the current version of Forge.

```bash
forge --version
# or
forge -v
```

## 🎯 Best Practices

### For API Projects

```
✅ PostgreSQL + SQLModel
✅ Complete JWT Auth
✅ Redis + Celery
✅ CORS enabled
✅ Black + Ruff
✅ pytest with coverage
✅ Docker deployment
```

### For Simple Projects

```
✅ SQLite + SQLModel
✅ Basic JWT Auth (or no auth)
✅ CORS enabled
✅ Docker deployment
```

## 📂 Project Structure

```
Forge/
├── commands/              # CLI command modules
│   ├── __init__.py       # Command exports
│   └── init.py           # Project initialization command
├── core/                 # Core business logic
│   ├── decorators/       # Decorator system
│   │   └── generator.py  # @Generator decorator and registry
│   ├── config_reader.py  # Configuration file reader
│   ├── project_generator.py  # Project generator
│   ├── generators/       # Code generators
│   │   ├── structure.py  # Project structure generator
│   │   ├── orchestrator.py  # Dynamic generator coordinator
│   │   ├── configs/      # Config file generators
│   │   ├── deployment/   # Deployment config generators
│   │   └── templates/    # Application code generators
│   └── utils/            # Utility functions
├── ui/                   # User interface components
│   ├── colors.py         # Color management system
│   ├── components.py     # UI components
│   └── logo.py           # Logo rendering
├── main.py               # CLI entry point
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

### Key Components

- **`@Generator` Decorator** - Automatic generator registration system
- **`orchestrator.py`** - Discovers and executes generators in correct order
- **40+ Generators** - Each responsible for specific files/features
- **Configuration-First** - All decisions driven by `.forge/config.json`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ning3739/forge.git
cd forge

# Install dependencies
uv sync

# Test build
./scripts/test_build.sh
```


## 📝 License

[MIT License](LICENSE)

## 🎉 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## 🙏 Acknowledgments

Built with:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
- [Questionary](https://questionary.readthedocs.io/) - Interactive prompts

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

Made with ❤️ for the FastAPI community
