# Quick Start

This guide will walk you through creating your first FastAPI project with Forge in just a few minutes.

## Basic Usage

The simplest way to use Forge is with the interactive mode:

```bash
forge init
```

This will launch an interactive prompt that guides you through the project setup process.

## Step-by-Step Example

Let's create a simple API project step by step:

### 1. Start the Interactive Prompt

```bash
forge init
```

You'll see the beautiful Forge logo and welcome message!

### 2. Choose Your Project Name

```
What is your project name? my-api-project
```

!!! tip "Using Current Directory"
    You can also use `.` as the project name to create the project in the current directory.

### 3. Select Database Type

```
? Select database type: (Use arrow keys)
 ❯ PostgreSQL (Recommended)
   MySQL
   SQLite (Development/Small Projects)
```

For this example, let's choose **SQLite** for simplicity.

### 4. Choose ORM

```
? Select ORM: (Use arrow keys)
 ❯ SQLModel (Recommended)
   SQLAlchemy
```

Select **SQLModel** for modern, type-safe ORM.

### 5. Enable Migrations

```
? Enable database migrations? (Y/n) Y
```

Type `Y` to enable Alembic migrations.

### 6. Select Authentication Type

```
? Select authentication type: (Use arrow keys)
 ❯ Complete JWT Auth (Recommended)
   Basic JWT Auth (login/register only)
```

Choose based on your needs. **Complete JWT Auth** includes email verification and password reset.

### 7. Configure Features

You'll be asked about various features:

- **CORS**: Enable if you're building an API for web apps
- **Development Tools**: Black and Ruff for code quality
- **Testing**: pytest with coverage
- **Redis**: For caching and sessions
- **Celery**: For background tasks
- **Docker**: Docker and Docker Compose configuration

### 8. Review Configuration

Forge will show a summary of your choices:

```
╭─ Project Configuration ─╮
│ my-api-project          │
│ • Database: SQLite      │
│ • ORM: SQLModel         │
│ • Auth: Complete JWT    │
│ • Redis: Enabled        │
│ • Testing: Enabled      │
╰─────────────────────────╯
```

### 9. Generate Project

Forge will generate your project structure:

```
✓ Creating project structure
✓ Generating configuration files
✓ Setting up database
✓ Configuring authentication
✓ Adding test suite
✓ Creating Docker files

🎉 Project created successfully!
```

## Non-Interactive Mode

For automation or CI/CD, use non-interactive mode with defaults:

```bash
forge init my-project --no-interactive
```

This creates a project with all recommended defaults:

- PostgreSQL database
- SQLModel ORM
- Complete JWT authentication
- Redis and Celery
- Full test suite
- Docker configuration

## What Gets Created

After running `forge init`, you'll have:

```
my-api-project/
├── app/
│   ├── core/          # Core configurations
│   ├── models/        # Database models
│   ├── routers/       # API routes
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── tests/             # Test suite
├── .forge/            # Forge configuration
│   └── config.json
├── pyproject.toml     # Dependencies
└── README.md          # Project docs
```

## Running Your Project

Navigate to your project and run it:

```bash
# Enter project directory
cd my-api-project

# Install dependencies
uv sync
# or: pip install -e .

# Run development server
uv run uvicorn app.main:app --reload
# or: uvicorn app.main:app --reload
```

Visit these URLs:

- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

## Quick Commands Reference

| Command | Description |
|---------|-------------|
| `forge init` | Interactive project creation |
| `forge init <name>` | Create project with specific name |
| `forge init --no-interactive` | Use default settings |
| `forge --version` | Show Forge version |
| `forge --help` | Show help message |

## Next Steps

Now that you've created your first project, learn more about:

- [First Project Walkthrough](first-project.md) - Detailed project exploration
- [Configuration Options](../user-guide/configuration.md) - All available options
- [CLI Commands](../user-guide/cli-commands.md) - Complete command reference

## Common Workflows

### Minimal Project

For a simple API without extras:

```bash
forge init minimal-api
# Choose SQLite, Basic Auth, disable Redis/Celery
```

### Full-Featured API

For production-ready API with all features:

```bash
forge init production-api
# Choose PostgreSQL, Complete Auth, enable all features
```

### Microservice

For a microservice with background tasks:

```bash
forge init microservice
# Enable Redis, Celery, Docker
# Keep authentication minimal
```
