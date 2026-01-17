# Redis Caching Guide

Forge provides integrated Redis support for caching, sessions, and queues. This guide covers setup, usage, and best practices.

## Overview

Redis is an in-memory data store that provides:
- **Caching**: Store frequently accessed data for fast retrieval
- **Session Storage**: Manage user sessions across multiple servers
- **Message Queues**: Handle background job queues (used by Celery)
- **Rate Limiting**: Implement API rate limiting

## Configuration

Enable Redis during project initialization:

```bash
forge init
# Select "Yes" when asked about Redis
```

Or in `.forge/config.json`:

```json
{
  "features": {
    "redis": {
      "enabled": true,
      "features": ["caching", "sessions", "queues"]
    }
  }
}
```

## Generated Components

### Redis Manager

The generated `app/core/redis.py` provides both async and sync Redis clients:

```python
from app.core.redis import redis_manager

# Async methods (for FastAPI endpoints)
await redis_manager.set_async("key", "value", ex=3600)
value = await redis_manager.get_async("key")
await redis_manager.delete_async("key")

# Sync methods (for Celery tasks)
redis_manager.set_sync("key", "value", ex=3600)
value = redis_manager.get_sync("key")
redis_manager.delete_sync("key")
```

### Configuration Settings

Redis settings in `app/core/config/redis.py`:

```python
class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_CONNECTION_URL: str = "redis://localhost:6379/0"
    
    # Pool settings
    REDIS_POOL_SIZE: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_DEFAULT_TTL: int = 3600  # 1 hour
```

## Common Use Cases

### 1. Caching API Responses

Cache expensive database queries or API calls:

```python
from fastapi import APIRouter, Depends
from app.core.redis import redis_manager
import json

router = APIRouter()

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    # Try to get from cache
    cache_key = f"user:{user_id}"
    cached = await redis_manager.get_async(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # If not in cache, fetch from database
    user = await fetch_user_from_db(user_id)
    
    # Store in cache for 1 hour
    await redis_manager.set_async(
        cache_key,
        json.dumps(user),
        ex=3600
    )
    
    return user
```

### 2. Session Storage

Store user session data:

```python
from app.core.redis import redis_manager
import json

async def create_session(user_id: int, session_data: dict):
    """Create user session"""
    session_key = f"session:{user_id}"
    await redis_manager.set_async(
        session_key,
        json.dumps(session_data),
        ex=86400  # 24 hours
    )

async def get_session(user_id: int) -> dict:
    """Get user session"""
    session_key = f"session:{user_id}"
    data = await redis_manager.get_async(session_key)
    return json.loads(data) if data else None

async def delete_session(user_id: int):
    """Delete user session"""
    session_key = f"session:{user_id}"
    await redis_manager.delete_async(session_key)
```

### 3. Rate Limiting

Implement API rate limiting with Redis:

```python
from app.core.redis import redis_manager
from fastapi import HTTPException

async def check_rate_limit(user_id: int, max_requests: int = 100, window: int = 3600):
    """Check if user exceeded rate limit"""
    key = f"rate_limit:{user_id}"
    
    # Get current count
    current = await redis_manager.get_async(key)
    
    if current is None:
        # First request in window
        await redis_manager.set_async(key, "1", ex=window)
        return True
    
    count = int(current)
    if count >= max_requests:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
    
    # Increment counter
    client = await redis_manager.get_async_client()
    await client.incr(key)
    return True
```

When Redis is enabled, a rate limiting decorator is automatically generated:

```python
from app.core.decorators.rate_limit import rate_limit

@router.get("/api/data")
@rate_limit(max_requests=100, window_seconds=3600)
async def get_data():
    return {"data": "value"}
```

### 4. Caching Decorator

Create a reusable caching decorator:

```python
from functools import wraps
from app.core.redis import redis_manager
import json
import hashlib

def cache_result(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Try to get from cache
            cached = await redis_manager.get_async(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await redis_manager.set_async(
                cache_key,
                json.dumps(result),
                ex=ttl
            )
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=1800, key_prefix="products")
async def get_products(category: str):
    # Expensive database query
    return await db.query(Product).filter_by(category=category).all()
```

### 5. Distributed Locks

Implement distributed locks for critical sections:

```python
from app.core.redis import redis_manager
import asyncio

async def acquire_lock(lock_name: str, timeout: int = 10):
    """Acquire distributed lock"""
    lock_key = f"lock:{lock_name}"
    
    # Try to set lock with NX (only if not exists)
    client = await redis_manager.get_async_client()
    acquired = await client.set(lock_key, "1", ex=timeout, nx=True)
    
    return acquired

async def release_lock(lock_name: str):
    """Release distributed lock"""
    lock_key = f"lock:{lock_name}"
    await redis_manager.delete_async(lock_key)

# Usage
async def process_payment(order_id: int):
    lock_name = f"payment:{order_id}"
    
    if not await acquire_lock(lock_name):
        raise Exception("Payment already being processed")
    
    try:
        # Process payment
        await process_payment_logic(order_id)
    finally:
        await release_lock(lock_name)
```

### 6. Cache Invalidation

Invalidate cache by pattern:

```python
from app.core.redis import redis_manager

async def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    pattern = f"user:{user_id}:*"
    await redis_manager.delete_pattern_async(pattern)

async def invalidate_all_users_cache():
    """Invalidate all user cache entries"""
    pattern = "user:*"
    await redis_manager.delete_pattern_async(pattern)
```

## Environment Configuration

### Development (`.env.development`)

```ini
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_CONNECTION_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10
REDIS_SOCKET_TIMEOUT=5
REDIS_DEFAULT_TTL=3600
```

### Production (`.env.production`)

```ini
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-strong-password
REDIS_DB=0
REDIS_CONNECTION_URL=redis://:your-strong-password@redis:6379/0
REDIS_POOL_SIZE=20
REDIS_SOCKET_TIMEOUT=5
REDIS_DEFAULT_TTL=3600
```

## Docker Setup

When Docker is enabled, Redis is automatically included in `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
```

## Testing Redis Connection

Test Redis connection:

```python
from app.core.redis import redis_manager

# Async test
async def test_redis_async():
    try:
        success = await redis_manager.async_test_connection()
        print(f"Redis async connection: {'✅ OK' if success else '❌ Failed'}")
    except Exception as e:
        print(f"Redis async connection failed: {e}")

# Sync test
def test_redis_sync():
    try:
        success = redis_manager.sync_test_connection()
        print(f"Redis sync connection: {'✅ OK' if success else '❌ Failed'}")
    except Exception as e:
        print(f"Redis sync connection failed: {e}")
```

## Best Practices

### 1. Use Appropriate TTL

Set reasonable expiration times:

```python
# Short-lived data (5 minutes)
await redis_manager.set_async("temp_data", value, ex=300)

# Medium-lived data (1 hour)
await redis_manager.set_async("user_session", value, ex=3600)

# Long-lived data (24 hours)
await redis_manager.set_async("daily_stats", value, ex=86400)
```

### 2. Use Namespaced Keys

Organize keys with prefixes:

```python
# Good - namespaced keys
"user:123:profile"
"user:123:settings"
"product:456:details"
"cache:api:users:list"

# Bad - flat keys
"123_profile"
"user_settings"
"product_456"
```

### 3. Handle Cache Misses Gracefully

Always have a fallback:

```python
async def get_data(key: str):
    # Try cache first
    cached = await redis_manager.get_async(key)
    if cached:
        return json.loads(cached)
    
    # Fallback to database
    data = await fetch_from_database(key)
    
    # Update cache
    await redis_manager.set_async(key, json.dumps(data), ex=3600)
    
    return data
```

### 4. Avoid Cache Stampede

Use locking to prevent multiple processes from regenerating the same cache:

```python
async def get_expensive_data(key: str):
    cached = await redis_manager.get_async(key)
    if cached:
        return json.loads(cached)
    
    # Acquire lock
    lock_key = f"lock:{key}"
    client = await redis_manager.get_async_client()
    
    if await client.set(lock_key, "1", ex=10, nx=True):
        try:
            # Generate data
            data = await expensive_operation()
            await redis_manager.set_async(key, json.dumps(data), ex=3600)
            return data
        finally:
            await redis_manager.delete_async(lock_key)
    else:
        # Wait for other process to finish
        await asyncio.sleep(0.1)
        return await get_expensive_data(key)
```

### 5. Monitor Memory Usage

Redis stores data in memory, so monitor usage:

```python
async def get_redis_info():
    """Get Redis memory info"""
    client = await redis_manager.get_async_client()
    info = await client.info("memory")
    return {
        "used_memory": info["used_memory_human"],
        "used_memory_peak": info["used_memory_peak_human"],
        "mem_fragmentation_ratio": info["mem_fragmentation_ratio"]
    }
```

## Troubleshooting

### Connection Refused

```bash
# Check if Redis is running
redis-cli ping

# Start Redis (macOS)
brew services start redis

# Start Redis (Linux)
sudo systemctl start redis

# Start Redis (Docker)
docker-compose up redis
```

### Memory Issues

```bash
# Check memory usage
redis-cli info memory

# Clear all data (development only!)
redis-cli FLUSHALL

# Set max memory limit
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Slow Queries

```bash
# Monitor slow commands
redis-cli --latency

# Check slow log
redis-cli SLOWLOG GET 10
```

## See Also

- [Configuration Options](configuration.md) - Redis configuration
- [Celery Background Tasks](celery-tasks.md) - Using Redis with Celery
- [Deployment Guide](deployment.md) - Production Redis setup
