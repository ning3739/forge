# Your First Project

This guide walks through creating a complete project with authentication, demonstrating the key features Forge provides.

## Creating the Project

Start by running the init command:

```bash
forge init
```

For this example, we'll make the following choices:

| Question | Choice |
|----------|--------|
| Project name | `blog-api` |
| Database | PostgreSQL |
| ORM | SQLModel |
| Enable migrations | Yes |
| Authentication | Complete JWT Auth |
| Redis | Yes |
| Celery | Yes |
| CORS | Yes |
| Dev tools | Yes |
| Testing | Yes |
| Docker | Yes |

## Understanding the Generated Code

### Entry Point: main.py

The `app/main.py` file is the FastAPI application entry point. It handles:

- Application lifecycle (startup/shutdown)
- Database connection initialization
- Redis connection (if enabled)
- CORS middleware configuration
- Router registration
- Global exception handlers

The lifespan function manages resource initialization:

```python
async def lifespan(_app: FastAPI):
    # Startup: Initialize connections
    await db_manager.initialize()
    await redis_manager.initialize_async()
    
    yield  # Application runs here
    
    # Shutdown: Close connections
    await db_manager.close()
    await redis_manager.close()
```

### Configuration: Settings

The `app/core/config/settings.py` aggregates all configuration modules using lazy loading:

```python
class Settings:
    @cached_property
    def app(self) -> AppSettings:
        return AppSettings()
    
    @cached_property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings()
    
    # ... other settings
```

Each settings module reads from environment variables defined in `secret/.env.development`.

### Database Models

With Complete JWT Auth, Forge generates a User model in `app/models/user.py`:

```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)  # Email verification
    is_superuser: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
```

### Authentication Flow

The Complete JWT Auth includes:

1. **Registration** (`POST /api/v1/auth/register`): Creates user, sends verification email
2. **Email Verification** (`POST /api/v1/auth/verify-email`): Verifies email with code
3. **Login** (`POST /api/v1/auth/login`): Returns access and refresh tokens
4. **Token Refresh** (`POST /api/v1/auth/refresh`): Gets new access token
5. **Password Reset** (`POST /api/v1/auth/forgot-password`, `POST /api/v1/auth/reset-password`)
6. **Logout** (`POST /api/v1/auth/logout`, `POST /api/v1/auth/logout-all`)

## Setting Up the Database

### Configure Environment

Edit `secret/.env.development` with your database credentials:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/blog_api
```

### Create the Database

Create the database in PostgreSQL:

```bash
createdb blog_api
```

### Run Migrations

Generate and apply the initial migration:

```bash
# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Running the Application

### Development Mode

```bash
uv run uvicorn app.main:app --reload
```

### With Docker

For a complete environment including PostgreSQL and Redis:

```bash
docker-compose up -d
```

This starts:
- Your FastAPI application
- PostgreSQL database
- Redis server
- Celery worker and beat (if enabled)
- Automatic database migrations

## Testing the API

### Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Response includes `access_token` and `refresh_token`.

### Access Protected Endpoint

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Running Tests

If you enabled testing, run the test suite:

```bash
uv run pytest
```

Tests use an in-memory SQLite database, so they don't affect your development database.

## Next Steps

Now that you have a working project:

- [Configuration](../user-guide/configuration.md): Customize your project settings
- [Database](../user-guide/database.md): Learn about database operations
- [Authentication](../user-guide/authentication.md): Understand the auth system in detail
- [Deployment](../user-guide/deployment.md): Deploy to production
