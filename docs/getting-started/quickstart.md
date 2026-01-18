# Quickstart

This guide walks you through creating your first FastAPI project with Forge.

## Create a Project

Run the init command to start the interactive project creation:

```bash
forge init
```

Forge will guide you through a series of questions to configure your project:

1. **Project name**: The name of your project (use `.` for current directory)
2. **Database type**: Choose from PostgreSQL, MySQL, or SQLite
3. **ORM**: Choose SQLModel or SQLAlchemy
4. **Database migrations**: Enable Alembic migrations
5. **Authentication**: Choose Basic JWT or Complete JWT (with email verification)
6. **Redis**: Enable for caching, sessions, and message queues
7. **Celery**: Enable for background tasks (requires Redis)
8. **CORS**: Enable Cross-Origin Resource Sharing
9. **Dev tools**: Include Black and Ruff
10. **Testing**: Include pytest setup
11. **Docker**: Include Docker and Docker Compose configs

## Project Structure

After answering the questions, Forge generates a complete project structure:

```
my-project/
├── .forge/
│   └── config.json          # Your project configuration
├── alembic/                  # Database migrations
│   ├── versions/
│   └── env.py
├── app/
│   ├── core/
│   │   ├── config/          # Settings modules
│   │   ├── database/        # Database connection
│   │   ├── celery.py        # Celery app (if enabled)
│   │   ├── redis.py         # Redis manager (if enabled)
│   │   └── security.py      # Auth utilities
│   ├── crud/                # CRUD operations
│   ├── models/              # Database models
│   ├── routers/v1/          # API routes
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── main.py              # Application entry point
├── secret/
│   ├── .env.development     # Development environment
│   ├── .env.production      # Production environment
│   └── .env.example         # Example configuration
├── tests/                   # Test files (if enabled)
├── alembic.ini
├── pyproject.toml
├── Dockerfile               # (if Docker enabled)
└── docker-compose.yml       # (if Docker enabled)
```

## Run the Project

Navigate to your project directory and install dependencies:

```bash
cd my-project
uv sync
```

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

If you enabled Celery for background tasks, start the Celery worker in a separate terminal:

```bash
uv run celery -A app.core.celery worker --loglevel=info
```

## Access the API

Open your browser and visit:

- **API Documentation**: http://127.0.0.1:8000/docs (Swagger UI)
- **Alternative Docs**: http://127.0.0.1:8000/redoc (ReDoc)
- **Health Check**: http://127.0.0.1:8000/health

## What's Next

- [First Project](first-project.md): A detailed walkthrough of building a complete project
- [Configuration](../user-guide/configuration.md): Understanding the configuration options
- [Database](../user-guide/database.md): Setting up and using the database
