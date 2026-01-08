"""database connectionFile generator"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="database",
    priority=30,
    requires=["ConfigDatabaseGenerator"],
    description="Generate database connection manager (app/core/database/connection.py)"
)
class DatabaseConnectionGenerator(BaseTemplateGenerator):
    """database connection managementgeneratorgenerategenerator"""
    
    def generate(self) -> None:
        """generate app/core/database/connection.py"""
        db_type = self.config_reader.get_database_type()
        
        # SQLite uses a different connection pattern, skip this generator
        if db_type == "SQLite":
            return
        
        # determine management based on database typegeneratorname
        if db_type == "PostgreSQL":
            db_manager = "postgresql_manager"
        elif db_type == "MySQL":
            db_manager = "mysql_manager"
        else:  # SQLite
            db_manager = "sqlite_manager"
        
        imports = [
            "from typing import Any, Optional",
            "from app.core.logger import logger_manager",
            f"from app.core.database.{db_type.lower()} import {db_manager}",
        ]
        
        content = f'''logger = logger_manager.get_logger(__name__)


class DatabaseConnectionManager:
    """database connection managementgenerator - unifiedmanagementdatabase connection"""
    
    def __init__(self):
        self.{db_type.lower()}_manager = {db_manager}
    
    async def initialize(self) -> None:
        """Initializealldatabase connection"""
        await self.{db_type.lower()}_manager.initialize()
    
    async def test_connections(self) -> bool:
        """testalldatabase connection"""
        try:
            # testdatabase connection
            await self.{db_type.lower()}_manager.test_connection()
            logger.info("✅ All database connections tested successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {{e}}")
            raise
    
    async def close(self) -> None:
        """closealldatabase connection"""
        await self.{db_type.lower()}_manager.close()
    
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
                f"{{exc_type.__name__}}: {{exc_value}}"
            )
        await self.close()
        # return False means don't suppress exception, let it propagate
        return False


db_manager = DatabaseConnectionManager()
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/database/connection.py",
            docstring="database connection managementgenerator",
            imports=imports,
            content=content,
            overwrite=True
        )
