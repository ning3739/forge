# Welcome to Forge

<div align="center">
  <img src="../assets/logo.svg" alt="Forge Logo" width="480"/>
</div>

<br/>

<div align="center">

[![PyPI version](https://badge.fury.io/py/ningfastforge.svg)](https://badge.fury.io/py/ningfastforge)
[![Python Versions](https://img.shields.io/pypi/pyversions/ningfastforge.svg)](https://pypi.org/project/ningfastforge/)
[![Downloads](https://static.pepy.tech/badge/ningfastforge)](https://pepy.tech/project/ningfastforge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

Forge is a powerful command-line tool that helps you quickly bootstrap **production-ready FastAPI projects** with best practices, intelligent defaults, and a beautiful interactive interface.

## ✨ Key Features

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

## Why Forge?

Building a FastAPI project from scratch involves many repetitive tasks: setting up project structure, configuring databases, implementing authentication, adding testing, Docker setup, and more. **Forge eliminates this tedious work** by generating production-ready projects in seconds.

### What Makes Forge Different?

1. **Configuration-First Design** - All decisions are saved in `.forge/config.json` for traceability and easy project regeneration
2. **Dynamic Generator System** - Automatic generator discovery with dependency resolution
3. **Intelligent Defaults** - Best practices and recommended configurations out of the box
4. **Comprehensive Features** - From basic CRUD to complex authentication and background tasks
5. **Beautiful UX** - Enjoyable interactive experience that makes project creation fun

## Quick Start

Get started with Forge in just a few commands:

```bash
# Install from PyPI
pip install ningfastforge

# Create your first project (interactive mode)
forge init

# Navigate to project and run
cd my-project
uv sync
uv run uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to see your API documentation!

## What You Get

When you create a project with Forge, you get:

- ✅ Fully structured FastAPI application
- ✅ Database models and migrations (Alembic)
- ✅ JWT authentication with user management
- ✅ CRUD operations and API routers
- ✅ Redis caching and session management
- ✅ Celery background tasks and scheduling
- ✅ Docker and Docker Compose configuration
- ✅ Comprehensive test suite with pytest
- ✅ Development tools (Black, Ruff)
- ✅ Environment configuration files
- ✅ Complete documentation and examples

## Documentation Structure

- **[Getting Started](getting-started/installation.md)** - Installation, quick start, and first project
- **[User Guide](user-guide/configuration.md)** - Configuration options, CLI commands, and features
- **[Architecture](architecture/overview.md)** - How Forge works under the hood
- **[Developer Guide](developer-guide/contributing.md)** - Contributing and extending Forge
- **[API Reference](api/config-reader.md)** - Detailed API documentation
- **[Advanced Topics](advanced/custom-templates.md)** - Custom templates and best practices

## Community and Support

- **GitHub**: [ning3739/forge](https://github.com/ning3739/forge)
- **PyPI**: [ningfastforge](https://pypi.org/project/ningfastforge/)
- **Issues**: [Report bugs or request features](https://github.com/ning3739/forge/issues)

## License

Forge is released under the [MIT License](https://opensource.org/licenses/MIT).

---

Made with ❤️ for the FastAPI community
