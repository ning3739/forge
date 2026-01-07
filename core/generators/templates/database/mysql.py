"""MySQL database managementgeneratorgenerategenerator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="database",
    priority=31,
    requires=["DatabaseConnectionGenerator"],
    enabled_when=lambda c: c.get_database_type() == 'MySQL',
    description="Generate MySQL database manager (app/core/database/mysql.py)"
)
class DatabaseMySQLGenerator(BaseTemplateGenerator):
    """MySQL database managementgeneratorgenerategenerator"""
    
    def generate(self) -> None:
        """generate app/core/database/mysql.py"""
        db_type = self.config_reader.get_database_type()
        if db_type != "MySQL":
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
        
        content = base_definition + '''class MySQLManager:
    """MySQL connectionmanagementgenerator - use SQLAlchemy/SQLModel ORM"""
    
    def __init__(self):
        self.logger = logger_manager.get_logger(__name__)
        self.async_engine: create_async_engine | None = None
        self.async_session_maker: async_sessionmaker | None = None
        self.sync_engine: create_engine | None = None
        self.sync_session_maker: sessionmaker | None = None
    
    def get_sqlalchemy_url(self) -> str:
        """Build SQLAlchemy asyncconnection URL"""
        url = settings.database.DATABASE_URL
        # ensure using aiomysql driver
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+aiomysql://", 1)
        elif url.startswith("mysql+pymysql://"):
            return url.replace("mysql+pymysql://", "mysql+aiomysql://", 1)
        return url
    
    def get_sync_sqlalchemy_url(self) -> str:
        """Build SQLAlchemy syncconnection URL"""
        url = settings.database.DATABASE_URL
        # ensure using pymysql driver
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+pymysql://", 1)
        elif url.startswith("mysql+aiomysql://"):
            return url.replace("mysql+aiomysql://", "mysql+pymysql://", 1)
        return url
    
    async def initialize(self) -> None:
        """Initialize async connection and session (idempotent)"""
        if self.async_engine:
            self.logger.debug("MySQLManager is already initialized.")
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
                # Set MySQL timezone to UTC (session level)
                connect_args={
                    "init_command": "SET SESSION time_zone = '+00:00'",
                },
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
                connect_args={
                    "init_command": "SET SESSION time_zone = '+00:00'",
                },
            )
            
            self.sync_session_maker = sessionmaker(
                self.sync_engine,
                class_=Session,
                expire_on_commit=False,
            )
            
            self.logger.info("✅ MySQL initialized successfully (async + sync).")
        except Exception:
            self.logger.exception("❌ Failed to initialize MySQL.")
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
                    raise RuntimeError("❌ MySQL connection test failed.")
                self.logger.info("✅ MySQL connection test passed.")
                return True
        except Exception:
            self.logger.exception("❌ MySQL connection test failed.")
            raise
    
    async def close(self) -> None:
        """Close connection pool and release resources"""
        if self.async_engine:
            try:
                await self.async_engine.dispose()
                self.async_engine = None
                self.async_session_maker = None
                self.logger.info("✅ MySQL async engine disposed successfully.")
            except Exception:
                self.logger.exception("❌ Failed to dispose MySQL async engine.")
                raise
        
        if self.sync_engine:
            try:
                self.sync_engine.dispose()
                self.sync_engine = None
                self.sync_session_maker = None
                self.logger.info("✅ MySQL sync engine disposed successfully.")
            except Exception:
                self.logger.exception("❌ Failed to dispose MySQL sync engine.")
                raise
    
    async def __aenter__(self) -> "MySQLManager":
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()


# singletoninstance
mysql_manager = MySQLManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/mysql.py",
            docstring="MySQL database connection managementgenerator",
            imports=imports,
            content=content,
            overwrite=True
        )
