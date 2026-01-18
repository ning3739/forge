# Best Practices

This guide covers recommended practices for working with Forge-generated projects.

## Project Structure

### Keep the Generated Structure

The generated structure follows FastAPI conventions. Maintain this organization:

```
app/
├── core/           # Configuration, database, security
├── models/         # Database models
├── schemas/        # Pydantic schemas
├── crud/           # Database operations
├── services/       # Business logic
├── routers/v1/     # API endpoints
└── main.py         # Application entry
```

### Adding New Features

When adding new features, follow the existing patterns:

1. **Model**: Create in `app/models/`
2. **Schema**: Create in `app/schemas/`
3. **CRUD**: Create in `app/crud/`
4. **Service** (if needed): Create in `app/services/`
5. **Router**: Create in `app/routers/v1/`
6. **Register router** in `app/main.py`

### Example: Adding a Posts Feature

```python
# 1. app/models/post.py
class Post(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="users.id")

# 2. app/schemas/post.py
class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int

# 3. app/crud/post.py
class PostCRUD:
    @staticmethod
    async def create(db: AsyncSession, post: PostCreate, author_id: int):
        ...

# 4. app/routers/v1/posts.py
router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostResponse)
async def create_post(...):
    ...

# 5. app/main.py - add import and include_router
```

## Security

### Environment Variables

Never commit secrets to version control:

```bash
# .gitignore should include:
secret/.env.development
secret/.env.production
```

Use `.env.example` as a template without real values.

### JWT Configuration

1. **Generate strong secrets**: Use at least 32 random characters
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Keep access tokens short-lived**: 15-30 minutes is recommended

3. **Rotate secrets periodically**: Update JWT_SECRET_KEY regularly

### Password Security

The generated code uses Argon2 with secure defaults. Don't weaken these settings.

### CORS Configuration

In production, restrict allowed origins:

```bash
# Development
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Production - be specific
CORS_ALLOWED_ORIGINS=https://myapp.com,https://www.myapp.com
```

## Database

### Connection Pool Tuning

Adjust pool settings based on your workload:

```bash
# For low-traffic applications
POOL_SIZE=3
POOL_MAX_OVERFLOW=2

# For high-traffic applications
POOL_SIZE=10
POOL_MAX_OVERFLOW=5
```

### Migration Best Practices

1. **Review auto-generated migrations**: Always check before applying
2. **Test migrations**: Apply to a test database first
3. **Backup before migrating**: Especially in production
4. **Use descriptive messages**: `alembic revision -m "Add user email index"`

### Query Optimization

Use indexes for frequently queried fields:

```python
class User(SQLModel, table=True):
    email: str = Field(unique=True, index=True)  # Indexed
    username: str = Field(unique=True, index=True)  # Indexed
```

## API Design

### Versioning

The generated structure uses `/api/v1/` prefix. When making breaking changes:

1. Create new routers in `app/routers/v2/`
2. Keep v1 endpoints working
3. Deprecate v1 gradually

### Error Handling

Use consistent error responses:

```python
from fastapi import HTTPException

# Good - consistent format
raise HTTPException(
    status_code=404,
    detail="User not found"
)

# The global exception handler formats this as:
# {"status": 404, "error": "User not found"}
```

### Pagination

For list endpoints, implement pagination:

```python
@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    return await user_crud.get_all(db, skip=skip, limit=limit)
```

## Performance

### Async Operations

Use async throughout the request path:

```python
# Good - async database operations
async def get_user(db: AsyncSession, user_id: int):
    return await db.get(User, user_id)

# Avoid - blocking operations in async context
def get_user_sync(db: Session, user_id: int):  # Don't do this
    return db.get(User, user_id)
```

### Caching with Redis

Cache expensive operations:

```python
async def get_user_profile(user_id: int):
    cache_key = f"user:profile:{user_id}"
    
    # Try cache
    cached = await redis_manager.get_async(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query and cache
    profile = await fetch_profile(user_id)
    await redis_manager.set_async(cache_key, json.dumps(profile), ex=300)
    return profile
```

### Background Tasks

Offload heavy operations to Celery:

```python
@router.post("/reports")
async def generate_report(data: ReportRequest):
    # Queue the task instead of processing inline
    task = generate_report_task.delay(data.dict())
    return {"task_id": task.id, "status": "processing"}
```

## Testing

### Test Coverage

Aim for high coverage on critical paths:

- Authentication flows
- Business logic in services
- Data validation in schemas
- Database operations in CRUD

### Test Isolation

Each test should be independent:

```python
@pytest.fixture
async def db_session():
    # Fresh session for each test
    # Rollback after test
    # Clear data for isolation
```

### Mock External Services

Don't call real external services in tests:

```python
from unittest.mock import patch

@pytest.mark.asyncio
async def test_send_email():
    with patch('app.utils.email.email_service.send_email') as mock:
        mock.return_value = None
        # Test code that sends email
```

## Logging

### Use the Logger

The generated project includes Loguru configuration:

```python
from app.core.logger import logger_manager

logger = logger_manager.get_logger(__name__)

logger.info("User registered", user_id=user.id)
logger.error("Database error", error=str(e))
```

### Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General operational events
- `WARNING`: Something unexpected but not critical
- `ERROR`: Something failed

## Code Quality

### Type Hints

Use type hints throughout:

```python
async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)
```

### Development Tools

If dev_tools is enabled, use them:

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy app/
```
