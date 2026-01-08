"""SQLite database configuration generator"""
from core.decorators import Generator
from ..base import BaseTemplateGenerator


@Generator(
    category="database",
    priority=35,
    description="Generate SQLite database configuration"
)
class SQLiteGenerator(BaseTemplateGenerator):
    """SQLite database configuration generator"""
    
    def generate(self) -> None:
        """Generate SQLite database configuration"""
        if self.config_reader.get_database_type() != "SQLite":
            return
        
        # Generate database connection
        self._generate_database_connection()
        
        # Generate database dependencies
        self._generate_database_dependencies()
    
    def _generate_database_connection(self) -> None:
        """Generate database connection module"""
        content = '''"""Database connection configuration for SQLite"""
import os
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config.modules.database import DatabaseSettings
from app.core.logger import logger_manager

# Get database configuration
db_config = DatabaseSettings()
logger = logger_manager.get_logger(__name__)

# Create async engine for SQLite
engine = create_async_engine(
    db_config.DATABASE_URL,
    echo=db_config.ECHO,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,  # SQLite specific
    },
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_database_session() -> AsyncSession:
    """Get database session
    
    Returns:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database tables"""
    from sqlmodel import SQLModel
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_database():
    """Close database connections"""
    await engine.dispose()


class DatabaseConnectionManager:
    """SQLite database connection manager"""
    
    def __init__(self):
        pass
    
    async def initialize(self) -> None:
        """Initialize database connection"""
        await init_database()
        logger.info("✅ SQLite database initialized")
    
    async def test_connections(self) -> bool:
        """Test database connection"""
        try:
            from sqlalchemy import text
            async with AsyncSessionLocal() as session:
                # Simple test query
                await session.execute(text("SELECT 1"))
            logger.info("✅ SQLite database connection tested successfully")
            return True
        except Exception as e:
            logger.error(f"❌ SQLite connection test failed: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connections"""
        await close_database()
        logger.info("✅ SQLite database connections closed")
    
    async def __aenter__(self) -> "DatabaseConnectionManager":
        """Enter context manager"""
        await self.initialize()
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[Any],
    ) -> None:
        """Exit context manager"""
        if exc_type is not None:
            logger.error(
                f"❌ Exception occurred in DatabaseConnectionManager context: "
                f"{exc_type.__name__}: {exc_value}"
            )
        await self.close()
        return False


db_manager = DatabaseConnectionManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/connection.py",
            content=content,
            overwrite=True
        )
    
    def _generate_database_dependencies(self) -> None:
        """Generate database dependencies"""
        content = '''"""Database dependencies for SQLite"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database.connection import get_database_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency
    
    Yields:
        AsyncSession: Database session
    """
    async for session in get_database_session():
        yield session


# Database dependency
DatabaseDep = Depends(get_db)
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/dependencies.py", 
            content=content,
            overwrite=True
        )