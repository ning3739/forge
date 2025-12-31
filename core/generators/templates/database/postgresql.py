"""PostgreSQL 数据库管理器生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class DatabasePostgreSQLGenerator(BaseTemplateGenerator):
    """PostgreSQL 数据库管理器生成器"""
    
    def generate(self) -> None:
        """生成 app/core/database/postgresql.py"""
        if not self.config_reader.has_database():
            return
        
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
        
        # 添加 Base 定义
        base_definition = '''# SQLAlchemy 声明式基类
Base = declarative_base()

'''
        
        content = base_definition + '''class PostgreSQLManager:
    """PostgreSQL 连接管理器 - 使用 SQLAlchemy/SQLModel ORM"""
    
    def __init__(self):
        self.logger = logger_manager.get_logger(__name__)
        self.async_engine: create_async_engine | None = None
        self.async_session_maker: async_sessionmaker | None = None
        self.sync_engine: create_engine | None = None
        self.sync_session_maker: sessionmaker | None = None
    
    def get_sqlalchemy_url(self) -> str:
        """构建 SQLAlchemy 异步连接 URL"""
        url = settings.database.DATABASE_URL
        # 确保使用 asyncpg 驱动
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql+psycopg2://"):
            return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        return url
    
    def get_sync_sqlalchemy_url(self) -> str:
        """构建 SQLAlchemy 同步连接 URL"""
        url = settings.database.DATABASE_URL
        # 确保使用 psycopg2 驱动
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        return url
    
    async def initialize(self) -> None:
        """初始化异步连接和会话（幂等）"""
        if self.async_engine:
            self.logger.debug("PostgreSQLManager is already initialized.")
            return
        
        try:
            db = settings.database
            
            # 初始化异步引擎
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
            
            # 初始化同步引擎（用于后台任务）
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
        """FastAPI 依赖注入使用：返回异步会话生成器"""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.async_session_maker() as session:
            yield session
    
    def get_sync_db(self) -> Session:
        """后台任务使用：返回同步会话"""
        if not self.sync_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.sync_session_maker()
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
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
        """关闭连接池并释放资源"""
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


# 单例实例
postgresql_manager = PostgreSQLManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/postgresql.py",
            docstring="PostgreSQL 数据库连接管理器",
            imports=imports,
            content=content,
            overwrite=True
        )
