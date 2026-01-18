# Redis Caching

When Redis is enabled, Forge generates a Redis connection manager that supports both async operations (for FastAPI) and sync operations (for Celery tasks).

## Configuration

Enable Redis during project creation, then configure via environment variables:

```bash
REDIS_CONNECTION_URL=redis://localhost:6379
REDIS_POOL_SIZE=5
REDIS_SOCKET_TIMEOUT=10
REDIS_DEFAULT_TTL=3600  # Default expiration in seconds
```

For Docker deployments, the URL changes to use the service name:

```bash
REDIS_CONNECTION_URL=redis://redis:6379
```

## RedisManager

The `RedisManager` class in `app/core/redis.py` provides a unified interface for Redis operations.

### Initialization

Redis is initialized during application startup in `main.py`:

```python
async def lifespan(_app: FastAPI):
    # Startup
    await redis_manager.initialize_async()
    
    yield
    
    # Shutdown
    await redis_manager.close()
```

### Async Operations (FastAPI)

Use async methods in your FastAPI routes:

```python
from app.core.redis import redis_manager

@router.get("/cached-data")
async def get_cached_data(key: str):
    # Get from cache
    cached = await redis_manager.get_async(key)
    if cached:
        return {"data": cached, "source": "cache"}
    
    # Compute and cache
    data = expensive_computation()
    await redis_manager.set_async(key, data, ex=3600)
    return {"data": data, "source": "computed"}
```

### Sync Operations (Celery)

Use sync methods in Celery tasks:

```python
from app.core.redis import redis_manager

@celery_app.task
def process_data(key: str):
    # Get from cache
    cached = redis_manager.get_sync(key)
    if cached:
        return cached
    
    # Process and cache
    result = heavy_processing()
    redis_manager.set_sync(key, result, ex=3600)
    return result
```

## Available Methods

### Async Methods

| Method | Description |
|--------|-------------|
| `get_async(key)` | Get value by key |
| `set_async(key, value, ex=None)` | Set value with optional TTL |
| `delete_async(*keys)` | Delete one or more keys |
| `delete_pattern_async(pattern)` | Delete keys matching pattern |
| `async_test_connection()` | Test Redis connectivity |

### Sync Methods

| Method | Description |
|--------|-------------|
| `get_sync(key)` | Get value by key |
| `set_sync(key, value, ex=None)` | Set value with optional TTL |
| `delete_sync(*keys)` | Delete one or more keys |
| `delete_pattern_sync(pattern)` | Delete keys matching pattern |
| `sync_test_connection()` | Test Redis connectivity |

## Common Use Cases

### Caching API Responses

```python
import json
from app.core.redis import redis_manager

async def get_user_profile(user_id: int, db: AsyncSession):
    cache_key = f"user:profile:{user_id}"
    
    # Try cache first
    cached = await redis_manager.get_async(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query database
    user = await user_crud.get_by_id(db, user_id)
    if user:
        # Cache for 5 minutes
        await redis_manager.set_async(
            cache_key, 
            json.dumps(user.dict()), 
            ex=300
        )
    
    return user
```

### Cache Invalidation

```python
async def update_user_profile(user_id: int, data: dict, db: AsyncSession):
    # Update database
    user = await user_crud.update(db, user_id, data)
    
    # Invalidate cache
    await redis_manager.delete_async(f"user:profile:{user_id}")
    
    return user
```

### Pattern-Based Invalidation

```python
async def clear_user_caches(user_id: int):
    # Delete all caches for a user
    await redis_manager.delete_pattern_async(f"user:{user_id}:*")
```

### Rate Limiting

```python
from fastapi import HTTPException

async def check_rate_limit(user_id: int, limit: int = 100, window: int = 60):
    key = f"rate_limit:{user_id}"
    
    current = await redis_manager.get_async(key)
    if current and int(current) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Increment counter
    client = await redis_manager.get_async_client()
    pipe = client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window)
    await pipe.execute()
```

### Session Storage

```python
import secrets
import json

async def create_session(user_id: int, data: dict) -> str:
    session_id = secrets.token_urlsafe(32)
    session_key = f"session:{session_id}"
    
    session_data = {
        "user_id": user_id,
        **data
    }
    
    # Store session for 24 hours
    await redis_manager.set_async(
        session_key,
        json.dumps(session_data),
        ex=86400
    )
    
    return session_id

async def get_session(session_id: str) -> dict | None:
    session_key = f"session:{session_id}"
    data = await redis_manager.get_async(session_key)
    
    if data:
        return json.loads(data)
    return None
```

## Connection Management

### Health Check

Test Redis connectivity:

```python
@router.get("/health/redis")
async def redis_health():
    try:
        await redis_manager.async_test_connection()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Direct Client Access

For advanced operations, access the Redis client directly:

```python
client = await redis_manager.get_async_client()

# Use Redis commands directly
await client.hset("user:1", mapping={"name": "John", "email": "john@example.com"})
user_data = await client.hgetall("user:1")
```

## Docker Setup

When Docker is enabled, Redis is included in `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: my_project_redis
  ports:
    - "6379:6379"
  restart: unless-stopped
  networks:
    - app-network
```

The application service depends on Redis:

```yaml
app:
  depends_on:
    redis:
      condition: service_started
  environment:
    - REDIS_CONNECTION_URL=redis://redis:6379
```
