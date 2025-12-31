"""数据库连接文件生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class DatabaseConnectionGenerator(BaseTemplateGenerator):
    """数据库连接管理器生成器"""
    
    def generate(self) -> None:
        """生成 app/core/database/connection.py"""
        if not self.config_reader.has_database():
            return
        
        db_type = self.config_reader.get_database_type()
        
        # 根据数据库类型确定管理器名称
        if db_type == "PostgreSQL":
            db_manager = "postgresql_manager"
        else:  # MySQL
            db_manager = "mysql_manager"
        
        imports = [
            "from typing import Any, Optional",
            "from app.core.logger import logger_manager",
            f"from app.core.database.{db_type.lower()} import {db_manager}",
        ]
        
        content = f'''logger = logger_manager.get_logger(__name__)


class DatabaseConnectionManager:
    """数据库连接管理器 - 统一管理数据库连接"""
    
    def __init__(self):
        self.{db_type.lower()}_manager = {db_manager}
    
    async def initialize(self) -> None:
        """初始化所有数据库连接"""
        await self.{db_type.lower()}_manager.initialize()
    
    async def test_connections(self) -> bool:
        """测试所有数据库连接"""
        try:
            # 测试数据库连接
            await self.{db_type.lower()}_manager.test_connection()
            logger.info("✅ All database connections tested successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {{e}}")
            raise
    
    async def close(self) -> None:
        """关闭所有数据库连接"""
        await self.{db_type.lower()}_manager.close()
    
    async def __aenter__(self) -> "DatabaseConnectionManager":
        """进入上下文管理器"""
        await self.initialize()
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[Exception],
        traceback: Optional[Any],
    ) -> None:
        """退出上下文管理器"""
        if exc_type is not None:
            logger.error(
                f"❌ Exception occurred in DatabaseConnectionManager context: "
                f"{{exc_type.__name__}}: {{exc_value}}"
            )
        await self.close()
        # 返回 False 表示不抑制异常，让异常继续传播
        return False


db_manager = DatabaseConnectionManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/connection.py",
            docstring="数据库连接管理器",
            imports=imports,
            content=content,
            overwrite=True
        )
