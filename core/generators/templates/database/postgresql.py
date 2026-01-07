"""PostgreSQL database managementgeneratorgenerategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="database",
    priority=31,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.get_database_type() == 'PostgreSQL',
    description="Generate PostgreSQL database manager (app/core/database/postgresql.py)"
)
class DatabasePostgreSQLGenerator(BaseTemplateGenerator):
    """PostgreSQL database managementgeneratorgenerategenerator"""
    
    def generate(self) -> None:
        """generate app/core/database/postgresql.py"""
        db_type = self.config_reader.get_database_type()
        if db_type != "PostgreSQL":
            return
        
        orm_type = self.config_reader.get_orm_type()
        
        imports = [
            "from collections.abc import AsyncGenerator",
            "from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession",
            "from sqlalchemy import create_engine, text",
            "from sqlalchemy.orm import sessionmaker, Session, declarative_base",
            "from app.core.logger import logger_manager",
            "from app.core.config.settings import settings",
        ]
        
        # add Base definition
        base_definition = '''# SQLAlchemy declarativebase class
Base = declarative_base()

'''
        
        content = base_definition + '''class PostgreSQLManager:
    """PostgreSQL connectionmanagementgenerator - use SQLAlchemy/SQLModel ORM"""
    
    def __init__(self):
        self.logger = logger_manager.get_logger(__name__)
        self.async_engine: create_async_engine | None = None
        self.async_session_maker: async_sessionmaker | None = None
        self.sync_engine: create_engine | None = None
        self.sync_session_maker: sessionmaker | None = None
    
    def get_sqlalchemy_url(self) -> str:
        """Build SQLAlchemy asyncconnection URL"""
        url = settings.database.DATABASE_URL
        # ensure using asyncpg driver
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        return url
    
    def get_sync_sqlalchemy_url(self) -> str:
        """Build SQLAlchemy syncconnection URL"""
        url = settings.database.DATABASE_URL
        # ensure using psycopg2 driver
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        return url
    
    async def initialize(self) -> None:
        """Initialize async connection and session (idempotent)"""
        if self.async_engine:
            self.logger.debug("PostgreSQLManager is already initialized.")
            return
        
        try:
            db = settings.database
            
            # Initialize async engine
            self.async_engine = create_async_engine(
                self.get_sqlalchemy_url(),
                echo=db.ECHO,
                pool_pre_ping=db.POOL_PRE_PING,
                pool_timeout=db.POOL_TIMEOUT,
                pool_size=db.POOL_SIZE,
                max_overflow=db.POOL_MAX_OVERFLOW,
            )
            
            self.async_session_maker = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Initialize sync engine (for background tasks)
            self.sync_engine = create_engine(
                self.get_sync_sqlalchemy_url(),
                echo=db.ECHO,
                pool_pre_ping=db.POOL_PRE_PING,
                pool_timeout=db.POOL_TIMEOUT,
                pool_size=db.POOL_SIZE,
                max_overflow=db.POOL_MAX_OVERFLOW,
            )
            
            self.sync_session_maker = sessionmaker(
                self.sync_engine,
                class_=Session,
                expire_on_commit=False,
            )
            
            self.logger.info("✅ PostgreSQL initialized successfully (async + sync).")
        except Exception:
            self.logger.exception("❌ Failed to initialize PostgreSQL.")
            raise
    
    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """FastAPI dependenciesinjectionuse：returnasyncsessiongenerategenerator"""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.async_session_maker() as session:
            yield session
    
    def get_sync_db(self) -> Session:
        """For background tasks: return sync session"""
        if not self.sync_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.sync_session_maker()
    
    async def test_connection(self) -> bool:
        """testdatabase connection"""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized.")
        
        try:
            async with self.async_session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                if result.scalar() != 1:
                    raise RuntimeError("❌ PostgreSQL connection test failed.")
                self.logger.info("✅ PostgreSQL connection test passed.")
                return True
        except Exception:
            self.logger.exception("❌ PostgreSQL connection test failed.")
            raise
    
    async def close(self) -> None:
        """Close connection pool and release resources"""
        if self.async_engine:
            try:
                await self.async_engine.dispose()
                self.async_engine = None
                self.async_session_maker = None
                self.logger.info("✅ PostgreSQL async engine disposed successfully.")
            except Exception:
                self.logger.exception("❌ Failed to dispose PostgreSQL async engine.")
                raise
        
        if self.sync_engine:
            try:
                self.sync_engine.dispose()
                self.sync_engine = None
                self.sync_session_maker = None
                self.logger.info("✅ PostgreSQL sync engine disposed successfully.")
            except Exception:
                self.logger.exception("❌ Failed to dispose PostgreSQL sync engine.")
                raise
    
    async def __aenter__(self) -> "PostgreSQLManager":
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


# singletoninstance
postgresql_manager = PostgreSQLManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/postgresql.py",
            docstring="PostgreSQL database connection managementgenerator",
            imports=imports,
            content=content,
            overwrite=True
        )
