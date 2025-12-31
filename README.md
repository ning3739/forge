# 🔥 Forge

> A modern, interactive FastAPI project scaffolding CLI tool

Forge is a powerful command-line tool that helps you quickly bootstrap production-ready FastAPI projects with best practices, intelligent defaults, and a beautiful interactive interface.

## ✨ Features

- 🎨 **Beautiful Interactive UI** - Stunning terminal interface with gradient colors and smooth animations
- 🚀 **Smart Presets** - Carefully curated presets for testing, dev tools, deployment, and monitoring
- 🔐 **Authentication Ready** - Built-in support for JWT, Session, OAuth2, and API Key authentication
- 🗄️ **Database Flexibility** - Support for PostgreSQL and MySQL
- 📦 **Modular Architecture** - Choose only the features you need
- 🧪 **Testing Built-in** - Pre-configured pytest with async support and coverage
- 🐳 **Docker Ready** - Production-ready Docker and Docker Compose configurations
- 🔍 **Type Safe** - Full type hints and optional MyPy support
- 📊 **Monitoring** - Built-in health checks, Prometheus metrics, and Sentry integration
- ⚡ **Async First** - Optimized for FastAPI's async capabilities

## 📋 Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd forge

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Create Your First Project

```bash
# Interactive mode (recommended)
forge init

# Or specify project name
forge init my-awesome-api

# Non-interactive mode with defaults
forge init my-api --no-interactive
```

### Run Your Project

```bash
cd my-awesome-api
uv sync
uv run uvicorn app.main:app --reload
```

Visit:
- 🌐 API: http://localhost:8000
- 📚 Docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

## 🏗️ Architecture

Forge follows a **"Configuration-First"** design principle:

1. **Init Command** collects user preferences interactively
2. **Configuration File** (`.forge/config.json`) is saved first
3. **ProjectGenerator** reads the config and generates code accordingly

This separation ensures:
- ✅ Configuration persistence and traceability
- ✅ Clear separation of concerns
- ✅ Easy project regeneration and updates
- ✅ Configuration sharing and templates

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design documentation.

---

## 🎯 Configuration Options

### Database Options

- **PostgreSQL** (Recommended) - Robust, feature-rich, excellent for production
- **MySQL** - Popular, widely supported relational database

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
  - Refresh Token (Optional)
- **Basic JWT Auth** - Simple authentication
  - Login & Register only
  - Refresh Token (Optional)

#### Security Features
- CORS (Configurable)
- Input Validation (Pydantic - auto-included)
- Password Hashing (bcrypt - auto-included with auth)
- SQL Injection Protection (ORM - auto-included)
- XSS Protection (FastAPI - auto-included)

### Core Features

All projects include:
- **Logging** - Structured logging (automatically included)
- **API Documentation** - Swagger UI and ReDoc (automatically included)
- **Health Check** - Basic health check endpoint (automatically included)

### Development Tools

- **Standard** (Recommended) - Black (formatter) + Ruff (linter)
- **None** - Skip dev tools

### Testing Setup

- **pytest** - Testing framework with async support
- **httpx** - HTTP client for testing
- **pytest-cov** - Code coverage
- **pytest-asyncio** - Async test support

### Deployment

- **Docker** - Dockerfile and docker-compose.yml
- Includes database service configuration
- Production-ready setup

## 📁 Generated Project Structure

```
my-awesome-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   └── users.py         # User endpoints
│   ├── core/                # Core functionality
│   │   ├── security.py      # Security utilities
│   │   └── deps.py          # Dependencies
│   └── tests/               # Test files
├── alembic/                 # Database migrations
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker configuration
├── pyproject.toml           # Project dependencies
├── .env.example             # Environment variables template
└── README.md                # Project documentation
```

## 🎨 Smart Features

### Intelligent Defaults

- **Database**: PostgreSQL with SQLModel
- **Migration**: Alembic enabled
- **Authentication**: Complete JWT Auth with Refresh Token
- **Security**: CORS enabled
- **Dev Tools**: Black + Ruff
- **Testing**: pytest with coverage
- **Deployment**: Docker + Docker Compose

### Technology Recommendations

- **PostgreSQL** for database (production-ready, feature-rich)
- **SQLModel** for ORM (modern, type-safe, FastAPI-friendly)
- **JWT** for authentication (stateless, scalable, API-friendly)
- **Alembic** for migrations (industry standard)

## 🛠️ Commands

### `forge init`

Initialize a new FastAPI project with interactive prompts.

```bash
# Interactive mode
forge init

# Specify project name
forge init my-project

# Non-interactive mode (uses defaults)
forge init my-project --no-interactive
```

### `forge info`

Display information about Forge CLI.

```bash
forge info
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
✅ CORS enabled
✅ Black + Ruff
✅ pytest with coverage
✅ Docker deployment
```

### For Simple Projects

```
✅ PostgreSQL + SQLModel
✅ Basic JWT Auth (or no auth)
✅ CORS enabled
✅ Docker deployment
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

[Your License Here]

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
