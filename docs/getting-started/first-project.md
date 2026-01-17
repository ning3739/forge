# Your First Project

This guide provides a detailed walkthrough of exploring and working with your first Forge-generated FastAPI project.

## Creating the Project

Let's create a complete example project:

```bash
forge init blog-api
```

Select these options for a full-featured blog API:

- **Database**: PostgreSQL
- **ORM**: SQLModel
- **Migrations**: Enabled (Alembic)
- **Auth**: Complete JWT Auth
- **CORS**: Enabled
- **Dev Tools**: Standard (Black + Ruff)
- **Testing**: Enabled
- **Redis**: Enabled
- **Celery**: Enabled
- **Docker**: Enabled

## Project Structure Overview

After creation, your project structure looks like this:

```
blog-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── core/                      # Core configurations
│   │   ├── config/               # Modular configuration
│   │   │   ├── base.py
│   │   │   ├── settings.py
│   │   │   └── modules/         # Config modules
│   │   ├── database/            # Database setup
│   │   ├── security.py          # Security utilities
│   │   ├── logger.py            # Logging configuration
│   │   ├── redis.py             # Redis connection
│   │   └── celery.py            # Celery configuration
│   ├── models/                   # Database models
│   │   ├── user.py
│   │   └── token.py
│   ├── schemas/                  # Pydantic schemas
│   │   ├── user.py
│   │   └── token.py
│   ├── crud/                     # Database operations
│   │   ├── user.py
│   │   └── token.py
│   ├── services/                 # Business logic
│   │   └── auth.py
│   ├── routers/                  # API routes
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── users.py
│   ├── tasks/                    # Celery background tasks
│   │   └── backup_database_task.py
│   ├── utils/                    # Utility functions
│   │   └── email.py
│   └── decorators/              # Custom decorators
│       └── rate_limit.py
├── tests/                        # Test suite
│   ├── conftest.py
│   ├── test_main.py
│   └── api/
│       ├── test_auth.py
│       └── test_users.py
├── alembic/                      # Database migrations
├── static/                       # Static files
│   └── email_template/          # Email templates
├── secret/                       # Environment files
│   ├── .env.example
│   ├── .env.development
│   └── .env.production
├── .forge/                       # Forge configuration
│   └── config.json
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Initial Setup

### 1. Install Dependencies

```bash
cd blog-api

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment

The project includes environment files in the `secret/` directory:

```bash
# Copy the example file
cp secret/.env.example secret/.env.development

# Edit the file
nano secret/.env.development
```

Key environment variables to configure:

```ini
# Application
APP_NAME=Blog API
APP_ENV=development
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/blog_api

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (for Complete JWT Auth)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 3. Setup Database

If using PostgreSQL or MySQL, create the database:

**PostgreSQL**:
```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE blog_api;

# Create user (optional)
CREATE USER blog_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE blog_api TO blog_user;
```

**MySQL**:
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE blog_api;

# Create user (optional)
CREATE USER 'blog_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blog_api.* TO 'blog_user'@'localhost';
```

**SQLite**:
No setup needed - database file will be created automatically.

### 4. Run Migrations

Initialize and run database migrations:

```bash
# Initialize Alembic (if not done)
alembic upgrade head
```

## Running the Application

### Development Server

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Or with uv:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at:

- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

### Running with Redis and Celery

If you enabled Redis and Celery, you need to run them:

```bash
# Terminal 1: Redis (if not running as service)
redis-server

# Terminal 2: Celery worker
celery -A app.core.celery worker --loglevel=info

# Terminal 3: Celery beat (for scheduled tasks)
celery -A app.core.celery beat --loglevel=info

# Terminal 4: FastAPI
uvicorn app.main:app --reload
```

### Using Docker

Alternatively, run everything with Docker Compose:

```bash
docker-compose up
```

This starts:
- FastAPI application
- PostgreSQL database
- Redis server
- Celery worker
- Celery beat scheduler

## Exploring the API

### 1. Check Health

Visit http://127.0.0.1:8000/health

```json
{
  "status": "healthy",
  "timestamp": "2024-01-17T10:00:00"
}
```

### 2. Register a User

Using the Swagger UI at http://127.0.0.1:8000/docs:

1. Go to **POST /api/v1/auth/register**
2. Click "Try it out"
3. Enter user details:

```json
{
  "email": "user@example.com",
  "password": "strongpassword123",
  "full_name": "John Doe"
}
```

### 3. Login

1. Go to **POST /api/v1/auth/login**
2. Enter credentials:

```json
{
  "username": "user@example.com",
  "password": "strongpassword123"
}
```

You'll receive an access token:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4. Access Protected Routes

1. Click the **Authorize** button in Swagger UI
2. Enter: `Bearer your-access-token`
3. Try **GET /api/v1/users/me** to get current user

## Running Tests

The project includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/api/test_auth.py

# Run with verbose output
pytest -v

# Run and show print statements
pytest -s
```

Expected output:

```
tests/test_main.py ✓✓✓
tests/api/test_auth.py ✓✓✓✓✓
tests/api/test_users.py ✓✓✓✓

========== 12 passed in 2.34s ==========
```

## Understanding Key Files

### main.py

The application entry point:

```python
from fastapi import FastAPI
from app.core.config.settings import settings
from app.routers.v1 import api_router

app = FastAPI(
    title=settings.app.APP_NAME,
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")
```

### models/user.py

Database model using SQLModel:

```python
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str | None = None
    is_active: bool = True
```

### routers/v1/auth.py

Authentication endpoints:

```python
from fastapi import APIRouter, Depends
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate):
    return await AuthService.register(user_data)
```

## Next Steps

Now that you've explored your first project:

1. **Customize the Models** - Add your own database models
2. **Create New Endpoints** - Add API routes for your use case
3. **Write Tests** - Add tests for your new features
4. **Deploy** - Use the included Docker configuration

Learn more:

- [Configuration Options](../user-guide/configuration.md)
- [Database Setup](../user-guide/database.md)
- [Authentication Guide](../user-guide/authentication.md)
- [Testing Guide](../user-guide/testing.md)
- [Deployment Guide](../user-guide/deployment.md)
