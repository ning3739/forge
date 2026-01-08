"""Redis app generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="app",
    priority=48,
    enabled_when=lambda c: c.has_redis(),
    requires=["RedisConfigGenerator"],
    description="Generate Redis connection manager (app/core/redis.py)"
)
class RedisAppGenerator(BaseTemplateGenerator):
    """Redis connection manager generator"""
    
    def generate(self) -> None:
        """Generate Redis connection manager file"""
        
        imports = [
            "from redis.asyncio import Redis as AsyncRedis",
            "from redis.asyncio import from_url as async_from_url",
            "from redis import Redis as SyncRedis",
            "from redis import from_url as sync_from_url",
            "from app.core.config.settings import settings",
            "from app.core.logger import logger_manager",
        ]
        
        content = '''class RedisManager:
    """Redis connection manager - supports async and sync clients"""
    
    def __init__(self):
        self.logger = logger_manager.get_logger(__name__)
        self.async_client: AsyncRedis | None = None
        self.sync_client: SyncRedis | None = None
        self.config = settings.redis
    
    async def initialize_async(self) -> None:
        """Initialize async Redis client - for FastAPI"""
        if self.async_client:
            self.logger.debug("Redis async client already initialized.")
            return
        
        try:
            self.async_client = async_from_url(
                self.config.REDIS_CONNECTION_URL,
                decode_responses=True,
                max_connections=self.config.REDIS_POOL_SIZE,
                socket_timeout=self.config.REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            self.logger.info("✅ Redis async client initialized.")
        except Exception:
            self.logger.exception("❌ Failed to initialize Redis async client.")
            raise
    
    def initialize_sync(self) -> None:
        """Initialize sync Redis client - for Celery"""
        if self.sync_client:
            self.logger.debug("Redis sync client already initialized.")
            return
        
        try:
            self.sync_client = sync_from_url(
                self.config.REDIS_CONNECTION_URL,
                decode_responses=True,
                max_connections=self.config.REDIS_POOL_SIZE,
                socket_timeout=self.config.REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            self.logger.info("✅ Redis sync client initialized.")
        except Exception:
            self.logger.exception("❌ Failed to initialize Redis sync client.")
            raise
    
    # -------------------------------
    # ✅ Async methods - for FastAPI
    # -------------------------------
    
    async def get_async_client(self) -> AsyncRedis:
        if not self.async_client:
            await self.initialize_async()
        return self.async_client
    
    async def get_async(self, key: str) -> str | None:
        client = await self.get_async_client()
        return await client.get(key)
    
    async def set_async(self, key: str, value: str, ex: int = None) -> bool:
        client = await self.get_async_client()
        ex = ex or self.config.REDIS_DEFAULT_TTL
        return await client.set(key, value, ex=ex)
    
    async def delete_async(self, *keys: str) -> int:
        client = await self.get_async_client()
        return await client.delete(*keys)
    
    async def delete_pattern_async(self, pattern: str) -> int:
        client = await self.get_async_client()
        keys = await client.keys(pattern)
        return await client.delete(*keys) if keys else 0
    
    async def async_test_connection(self) -> bool:
        try:
            client = await self.get_async_client()
            await client.ping()
            self.logger.info("✅ Redis async client connection test successful.")
            return True
        except Exception:
            self.logger.exception("❌ Redis async client connection test failed.")
            raise
    
    # -------------------------------
    # ✅ Sync methods - for Celery / scripts
    # -------------------------------
    
    def get_sync_client(self) -> SyncRedis:
        if not self.sync_client:
            self.initialize_sync()
        return self.sync_client
    
    def get_sync(self, key: str) -> str | None:
        return self.get_sync_client().get(key)
    
    def set_sync(self, key: str, value: str, ex: int = None) -> bool:
        ex = ex or self.config.REDIS_DEFAULT_TTL
        return self.get_sync_client().set(key, value, ex=ex)
    
    def delete_sync(self, *keys: str) -> int:
        return self.get_sync_client().delete(*keys)
    
    def delete_pattern_sync(self, pattern: str) -> int:
        client = self.get_sync_client()
        keys = client.keys(pattern)
        return client.delete(*keys) if keys else 0
    
    def sync_test_connection(self) -> bool:
        try:
            client = self.get_sync_client()
            client.ping()
            self.logger.info("✅ Redis sync client connection test successful.")
            return True
        except Exception:
            self.logger.exception("❌ Redis sync client connection test failed.")
            raise
    
    # -------------------------------
    # ✅ Resource cleanup
    # -------------------------------
    
    async def close(self) -> None:
        """Close async and sync clients"""
        if self.async_client:
            try:
                await self.async_client.close()
                self.async_client = None
                self.logger.info("✅ Redis async client closed.")
            except Exception:
                self.logger.exception("❌ Failed to close Redis async client.")
        
        if self.sync_client:
            try:
                self.sync_client.close()
                self.sync_client = None
                self.logger.info("✅ Redis sync client closed.")
            except Exception:
                self.logger.exception("❌ Failed to close Redis sync client.")
    
    async def __aenter__(self) -> "RedisManager":
        await self.initialize_async()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


# Singleton instance
redis_manager = RedisManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/redis.py",
            docstring="Redis connection manager - supports async and sync clients",
            imports=imports,
            content=content,
            overwrite=True
        )