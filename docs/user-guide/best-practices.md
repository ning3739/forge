# Best Practices & FAQ

This guide covers best practices, common patterns, and frequently asked questions when using Forge-generated projects.

## Project Setup Best Practices

### 1. Choose the Right Database

**PostgreSQL** (Recommended for Production):
- Best for production applications
- Full-featured with excellent performance
- Strong data integrity and ACID compliance
- Great for complex queries and relationships

**MySQL**:
- Good for existing MySQL infrastructure
- Wide hosting support
- Solid performance for most use cases

**SQLite**:
- Perfect for development and testing
- Great for small applications and prototypes
- No server setup required
- Easy to backup (single file)

### 2. Authentication Mode Selection

**Complete JWT Auth** (Recommended):
- Use when you need email verification
- Required for password reset functionality
- Better security with refresh tokens
- Multi-device login support
- Suitable for production applications

**Basic JWT Auth**:
- Use for internal tools or MVPs
- Simpler setup (no email configuration)
- Faster development for prototypes
- Can upgrade to Complete later

### 3. When to Enable Redis

Enable Redis if you need:
- **Caching**: Frequently accessed data
- **Session Storage**: User sessions across multiple servers
- **Rate Limiting**: API request throttling
- **Celery**: Background task processing (required)

**Note**: Redis adds complexity. Skip it for simple applications.

### 4. When to Enable Celery

Enable Celery if you need:
- **Email Sending**: Async email delivery
- **Report Generation**: Long-running reports
- **Data Processing**: Batch data processing
- **Scheduled Tasks**: Cron-like periodic jobs
- **Image Processing**: Thumbnail generation, etc.

**Note**: Celery requires Redis and adds operational complexity.

## Development Workflow

### 1. Environment Management

Always use environment-specific configuration:

```bash
# Development
export ENVIRONMENT=development
uv run uvicorn app.main:app --reload

# Production
export ENVIRONMENT=production
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Database Migrations

Follow this workflow for database changes:

```bash
# 1. Modify your models
# Edit app/models/user.py, etc.

# 2. Generate migration
uv run alembic revision --autogenerate -m "add user profile fields"

# 3. Review the generated migration
# Check alembic/versions/xxx_add_user_profile_fields.py

# 4. Apply migration
uv run alembic upgrade head

# 5. Test in development first!
```

**Important**: Always review auto-generated migrations before applying them.

### 3. Testing Strategy

Write tests for:
- **API Endpoints**: All routes and status codes
- **Authentication**: Login, registration, token refresh
- **Business Logic**: Services and CRUD operations
- **Edge Cases**: Invalid inputs, error handling

```bash
# Run tests before committing
uv run pytest

# Check coverage
uv run pytest --cov=app --cov-report=html

# Aim for 80%+ coverage
```

### 4. Code Quality

Use the included dev tools:

```bash
# Format code
uv run black app/

# Check linting
uv run ruff check app/

# Fix auto-fixable issues
uv run ruff check app/ --fix

# Run before committing
uv run black app/ && uv run ruff check app/ --fix
```

## Security Best Practices

### 1. Environment Variables

**Never commit secrets to version control!**

```bash
# ✅ Good - Use environment variables
JWT_SECRET_KEY=your-secret-key-here

# ❌ Bad - Hardcoded in code
SECRET_KEY = "my-secret-key"
```

### 2. JWT Secret Key

Generate a strong secret key:

```python
import secrets
print(secrets.token_urlsafe(32))
# Use this in production!
```

**Change the default secret key before deploying!**

### 3. Password Requirements

The generated code includes basic password hashing. Consider adding:

```python
# app/schemas/user.py
from pydantic import validator

class UserCreate(BaseModel):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

### 4. CORS Configuration

Be specific with CORS origins in production:

```ini
# Development - Allow localhost
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Production - Specific domains only
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Rate Limiting

When Redis is enabled, use the rate limiting decorator:

```python
from app.core.decorators.rate_limit import rate_limit

@router.post("/login")
@rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
async def login(user_data: UserLogin):
    # Login logic
    pass
```

## Performance Optimization

### 1. Database Connection Pooling

The generated code includes connection pooling. Adjust for your needs:

```ini
# For high-traffic applications
POOL_SIZE=20
POOL_MAX_OVERFLOW=10

# For low-traffic applications
POOL_SIZE=5
POOL_MAX_OVERFLOW=2
```

### 2. Redis Caching Strategy

Cache expensive operations:

```python
from app.core.redis import redis_manager
import json

async def get_user_stats(user_id: int):
    # Try cache first
    cache_key = f"user_stats:{user_id}"
    cached = await redis_manager.get_async(cache_key)
    if cached:
        return json.loads(cached)
    
    # Compute stats (expensive)
    stats = await compute_user_stats(user_id)
    
    # Cache for 1 hour
    await redis_manager.set_async(
        cache_key,
        json.dumps(stats),
        ex=3600
    )
    return stats
```

### 3. Async Operations

Use async/await for I/O operations:

```python
# ✅ Good - Async database queries
async def get_users():
    async with get_db() as db:
        result = await db.execute(select(User))
        return result.scalars().all()

# ❌ Bad - Blocking operations
def get_users():
    # Blocks the event loop
    time.sleep(1)
    return users
```

### 4. Background Tasks

Move slow operations to Celery:

```python
# ✅ Good - Async email sending
@router.post("/register")
async def register(user_data: UserCreate):
    user = await create_user(user_data)
    # Queue email task
    send_welcome_email.delay(user.email)
    return user

# ❌ Bad - Blocking email sending
@router.post("/register")
async def register(user_data: UserCreate):
    user = await create_user(user_data)
    # Blocks the request
    send_email_sync(user.email)
    return user
```

## Common Patterns

### 1. Adding Custom Endpoints

Create a new router:

```python
# app/routers/v1/posts.py
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/")
async def list_posts():
    return {"posts": []}

@router.post("/")
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user)
):
    # Create post
    pass
```

Register in router aggregator:

```python
# app/routers/v1/__init__.py
from app.routers.v1 import auth, user, posts

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(posts.router)  # Add this
```

### 2. Adding Database Models

Create model file:

```python
# app/models/post.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from datetime import datetime

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str
    author_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    author: Optional["User"] = Relationship(back_populates="posts")
```

Update User model:

```python
# app/models/user.py
class User(SQLModel, table=True):
    # ... existing fields ...
    
    # Add relationship
    posts: list["Post"] = Relationship(back_populates="author")
```

Create migration:

```bash
uv run alembic revision --autogenerate -m "add posts table"
uv run alembic upgrade head
```

### 3. Custom Celery Tasks

Create task file:

```python
# app/tasks/report_task.py
from app.core.celery import celery_app, with_db_init

@celery_app.task(name="generate_report")
@with_db_init
def generate_report(user_id: int):
    # Generate report logic
    report = create_report(user_id)
    return {"status": "completed", "report_id": report.id}
```

Schedule periodic task:

```python
# app/core/celery.py
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'generate-daily-report': {
        'task': 'app.tasks.report_task.generate_report',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    }
}
```

### 4. Custom Middleware

Add middleware to main.py:

```python
# app/main.py
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Frequently Asked Questions

### General Questions

**Q: Can I regenerate my project after making changes?**

A: Yes, but be careful! Running `forge init` again will overwrite generated files. Save your custom code first or use version control.

**Q: Can I use Forge with an existing project?**

A: Forge is designed for new projects. For existing projects, you can generate a new project and copy relevant code.

**Q: How do I upgrade Forge?**

```bash
pip install --upgrade ningfastforge
```

**Q: Where are the logs stored?**

A: Logs are in the `logs/` directory. Check `logs/app_development.log` for development logs.

### Database Questions

**Q: How do I switch databases after generation?**

A: Update `DATABASE_URL` in your `.env` file and run migrations:

```bash
# Update .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/newdb

# Run migrations
uv run alembic upgrade head
```

**Q: How do I backup my database?**

```bash
# PostgreSQL
pg_dump mydb > backup.sql

# MySQL
mysqldump mydb > backup.sql

# SQLite
cp mydb.db backup.db
```

**Q: Can I use multiple databases?**

A: Yes, but you'll need to configure additional database connections manually. The generated code uses a single database.

### Authentication Questions

**Q: How do I customize the User model?**

A: Edit `app/models/user.py` and create a migration:

```python
# Add fields
phone: Optional[str] = None
avatar_url: Optional[str] = None

# Create migration
uv run alembic revision --autogenerate -m "add user fields"
uv run alembic upgrade head
```

**Q: How do I change token expiration?**

A: Update `.env` file:

```ini
JWT_ACCESS_TOKEN_EXPIRATION=3600  # 1 hour in seconds
JWT_REFRESH_TOKEN_EXPIRATION=604800  # 7 days in seconds
```

**Q: Can I add OAuth (Google, GitHub, etc.)?**

A: The generated code doesn't include OAuth. You'll need to add it manually using libraries like `authlib` or `python-social-auth`.

### Redis & Celery Questions

**Q: Do I need Redis for caching?**

A: No, you can implement caching without Redis using in-memory caches or other solutions. Redis is recommended for distributed caching.

**Q: Can I use RabbitMQ instead of Redis for Celery?**

A: Yes, update `CELERY_BROKER_URL` in `.env`:

```ini
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
```

**Q: How do I monitor Celery tasks?**

A: Use Flower:

```bash
pip install flower
uv run celery -A app.core.celery:celery_app flower
# Visit http://localhost:5555
```

### Deployment Questions

**Q: How do I deploy to production?**

A: See the [Deployment Guide](deployment.md) for detailed instructions. Quick overview:

1. Update `secret/.env.production` with production credentials
2. Use Docker Compose or deploy to cloud platforms
3. Set up proper monitoring and logging
4. Use a reverse proxy (Nginx, Traefik)

**Q: Should I use Docker in production?**

A: Docker is recommended for production as it ensures consistency across environments and simplifies deployment.

**Q: How do I handle database migrations in production?**

```bash
# Run migrations before deploying new code
uv run alembic upgrade head

# Or in Docker
docker-compose exec api alembic upgrade head
```

### Email Questions (Complete Auth)

**Q: Email sending is slow. How do I fix it?**

A: Use Celery to send emails asynchronously. The generated code already does this for Complete Auth.

**Q: Can I use a different email provider?**

A: Yes, update SMTP settings in `.env`:

```ini
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
```

**Q: How do I customize email templates?**

A: Edit HTML files in `static/email_template/`:
- `verification_email.html`
- `reset_password_email.html`

### Testing Questions

**Q: How do I test endpoints that require authentication?**

```python
# tests/test_auth.py
def test_protected_endpoint(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
```

**Q: How do I mock external services in tests?**

```python
from unittest.mock import patch

@patch('app.utils.email.email_service.send_email')
def test_registration(mock_send_email, client):
    mock_send_email.return_value = None
    response = client.post("/api/v1/auth/register", json={...})
    assert response.status_code == 201
```

## Troubleshooting Guide

### Issue: "Module not found" errors

**Solution**:
```bash
# Reinstall dependencies
uv sync --reinstall

# Or with pip
pip install -e . --force-reinstall
```

### Issue: Database connection refused

**Solution**:
```bash
# Check if database is running
# PostgreSQL
pg_isready

# MySQL
mysqladmin ping

# Check connection string
cat secret/.env.development | grep DATABASE_URL
```

### Issue: Alembic can't detect model changes

**Solution**:
```python
# Make sure models are imported in alembic/env.py
from app.models.user import User
from app.models.post import Post  # Add your models here
```

### Issue: Celery tasks not executing

**Solution**:
```bash
# 1. Check if Redis is running
redis-cli ping

# 2. Check if worker is running
uv run celery -A app.core.celery:celery_app inspect active

# 3. Check task registration
uv run celery -A app.core.celery:celery_app inspect registered

# 4. Restart worker
# Stop worker (Ctrl+C) and start again
uv run celery -A app.core.celery:celery_app worker --loglevel=info
```

### Issue: CORS errors in browser

**Solution**:
```ini
# Update .env with your frontend URL
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Restart the server
```

### Issue: Email not sending (Complete Auth)

**Solution**:
1. Check SMTP credentials in `.env`
2. Test SMTP connection:
```python
from app.utils.email import email_service
email_service.test_connection()
```
3. Check logs: `logs/app_development.log`
4. For Gmail, use App Password, not regular password

## Getting Help

If you're still stuck:

1. **Check Documentation**: https://ningfastforge.readthedocs.io/
2. **Search Issues**: https://github.com/ning3739/forge/issues
3. **Create Issue**: Provide error messages, logs, and configuration
4. **Community**: Ask in GitHub Discussions

## Contributing

Found a bug or have a feature request?

1. Check existing issues: https://github.com/ning3739/forge/issues
2. Create a new issue with details
3. Submit a pull request if you'd like to contribute code
