<div align="center">
  <img src="https://github.com/ning3739/forge/blob/main/assets/logo.svg?raw=true" alt="Forge Logo" width="480"/>
</div>

<br/>

<div align="center">

[![PyPI version](https://badge.fury.io/py/ningfastforge.svg)](https://badge.fury.io/py/ningfastforge)
[![Python Versions](https://img.shields.io/pypi/pyversions/ningfastforge.svg)](https://pypi.org/project/ningfastforge/)
[![Downloads](https://static.pepy.tech/badge/ningfastforge)](https://pepy.tech/project/ningfastforge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

**Forge** is a powerful command-line tool that helps you quickly bootstrap production-ready FastAPI projects with best practices, intelligent defaults, and a beautiful interactive interface.

## ✨ Features

- 🎨 **Beautiful Interactive UI** - Stunning terminal interface with gradient colors
- 🗄️ **Multiple Databases** - PostgreSQL, MySQL, SQLite with SQLModel/SQLAlchemy
- 🔐 **Authentication Ready** - Complete JWT auth with email verification & password reset
- 🔴 **Redis & Celery** - Background tasks, caching, and message queues
- 🐳 **Docker Ready** - Production-ready containerization with Docker Compose
- 🧪 **Testing Setup** - pytest with async support and coverage
- 📚 **Auto Documentation** - Swagger UI and ReDoc
- 🛠️ **Dev Tools** - Black, Ruff, and development utilities
- ⚡ **Async First** - Optimized for FastAPI's async capabilities

## 🚀 Quick Start

### Installation

```bash
pip install ningfastforge
```

### Create Your First Project

```bash
forge init forge-project
```

Follow the interactive prompts to configure your project with:
- Database choice (PostgreSQL/MySQL/SQLite)
- Authentication system (Complete/Basic JWT)
- Redis & Celery for background tasks
- CORS, testing, Docker setup

### Run Your Project

```bash
cd forge-project
uv sync  # or pip install -e .
uv run uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs for your API documentation!

## 🎯 Configuration Options

### Database Support
- **PostgreSQL** (Recommended) - Production-ready with full features
- **MySQL** - Popular choice with excellent performance  
- **SQLite** - Perfect for development and small projects

### Authentication & Security
- **Complete JWT Auth** - Email verification, password reset, refresh tokens
- **Basic JWT Auth** - Simple login/register system
- **Security Features** - CORS, rate limiting, input validation, password hashing

### Background Tasks & Caching
- **Redis** - Caching, sessions, and message broker
- **Celery** - Background task processing with automatic database backups
- **Scheduled Tasks** - Cron-based scheduling for production

### Development & Deployment
- **Testing** - pytest with async support and coverage reporting
- **Code Quality** - Black formatter and Ruff linter
- **Docker** - Complete containerization with docker-compose
- **API Documentation** - Auto-generated Swagger UI and ReDoc for your APIs

## 📁 Generated Project Structure

```
forge-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core configurations
│   │   ├── config/          # Settings management modules
│   │   ├── database/        # Database connection managers
│   │   ├── celery.py        # Celery configuration (if enabled)
│   │   ├── redis.py         # Redis client (if enabled)
│   │   ├── deps.py          # Dependency injection
│   │   ├── logger.py        # Logging configuration
│   │   └── security.py      # Authentication & security
│   ├── models/              # Database models (SQLModel/SQLAlchemy)
│   ├── schemas/             # Pydantic schemas for API validation
│   ├── crud/                # Database CRUD operations
│   ├── routers/             # API route definitions
│   │   └── v1/              # API version 1 endpoints
│   ├── services/            # Business logic layer
│   ├── tasks/               # Celery background tasks (if enabled)
│   ├── utils/               # Utility functions
│   └── decorators/          # Custom decorators (rate limiting, etc.)
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration
│   ├── test_main.py         # Main application tests
│   ├── api/                 # API endpoint tests
│   └── unit/                # Unit tests
├── alembic/                 # Database migrations (if enabled)
│   ├── versions/            # Migration files
│   ├── env.py               # Alembic environment
│   └── alembic.ini          # Alembic configuration
├── static/                  # Static files
│   └── email_template/      # Email templates (if auth enabled)
├── script/                  # Custom scripts
├── secret/                  # Environment configuration
│   ├── .env.example         # Environment template
│   ├── .env.development     # Development settings
│   └── .env.production      # Production settings
├── docker-compose.yml       # Multi-service deployment
├── Dockerfile               # Container configuration
├── .dockerignore            # Docker ignore rules
├── .gitignore               # Git ignore rules
├── pyproject.toml           # Project dependencies and metadata
├── LICENSE                  # MIT license
└── README.md                # Project documentation
```

## 🐳 Docker Deployment

For projects with Redis, Celery, or external databases:

```bash
# Production deployment with all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

This starts:
- FastAPI application (port 8000)
- Database (MySQL/PostgreSQL)
- Redis (if enabled)
- Celery worker & beat (if enabled)
- Automatic database migrations

## 🛠️ Commands

### Create New Project
```bash
forge init <project-name>     # Interactive mode
forge init forge-project --no-interactive  # Use defaults
```

### Check Version
```bash
forge --version
```

## 📚 Generated Project Features

Once your project is running, you'll have access to:

- **API Documentation**: http://127.0.0.1:8000/docs (Swagger UI)
- **Alternative Docs**: http://127.0.0.1:8000/redoc (ReDoc)
- **Health Check**: http://127.0.0.1:8000/health

## 🎯 Best Practices

### Recommended Stack
```bash
forge init forge-project
# Choose: PostgreSQL + SQLModel + Complete JWT + Redis + Celery + Docker
```

### Simple API
```bash  
forge init simple-project
# Choose: SQLite + SQLModel + Basic JWT + No Redis + No Docker
```

## 📝 License

[MIT License](https://github.com/ning3739/forge/blob/main/LICENSE)

## 🙏 Acknowledgments

Built with ❤️ using:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with type safety
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output

---

**Need help?** Check out the [full documentation](https://github.com/ning3739/forge) or open an issue on GitHub.