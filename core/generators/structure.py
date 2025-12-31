"""项目结构生成模块

负责创建项目的目录结构和初始化文件
"""
from pathlib import Path
from core.utils import FileOperations
from .response import ResponseGenerator
from .orchestrator import GeneratorOrchestrator
from .alembic import AlembicGenerator


class StructureGenerator:
    """项目结构生成器类

    负责创建项目的目录结构和 __init__.py 文件
    """

    def __init__(self, project_path: Path, config_reader: 'ConfigReader'):
        """初始化结构生成器

        Args:
            project_path: 项目根目录路径
            config_reader: 配置读取器实例
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)

    def create_project_structure(self) -> None:
        """创建项目目录结构"""
        # 基础目录结构
        directories = [
            "app",
            "app/core",
            "app/core/config",
            "app/core/config/modules",
            "app/decorators",
            "app/schemas",
            "app/utils",
            "script",
        ]

        # 根据配置添加可选目录
        if self.config_reader.has_database():
            directories.extend([
                "app/core/database",
                "app/crud",
                "app/models",
            ])

        if self.config_reader.has_auth():
            directories.extend([
                "app/services",
                "app/routers",        # 有认证时才创建 routers 目录
                "app/routers/v1",     # API v1 路由
            ])

        if self.config_reader.has_migration():
            directories.append("alembic")

        if self.config_reader.has_testing():
            directories.extend([
                "tests",
                "tests/api",
                "tests/unit",
            ])

        # 创建所有目录
        for directory in directories:
            dir_path = self.project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # 创建 __init__.py 文件
        self._create_init_files()
        
        # 创建配置模块的 __init__.py
        self._create_config_modules_init()
        
        # 生成响应工具
        self._create_response_utils()
        
        # 生成项目配置文件（包括 app/main.py）
        self._create_project_files()
        
        # 初始化 Alembic（如果启用了迁移）
        self._init_alembic()

    def _create_init_files(self) -> None:
        """创建所有必需的 __init__.py 文件"""
        init_files = [
            "app/__init__.py",
            "app/core/__init__.py",
            "app/core/config/__init__.py",
            "app/decorators/__init__.py",
            "app/schemas/__init__.py",
            "app/utils/__init__.py",
        ]

        # 根据配置添加可选的 __init__.py
        if self.config_reader.has_database():
            init_files.extend([
                "app/crud/__init__.py",
                "app/models/__init__.py",
            ])
            # app/core/database/__init__.py 需要特殊处理（导出 db_manager）
            self._create_database_init()

        if self.config_reader.has_auth():
            init_files.extend([
                "app/services/__init__.py",
                "app/routers/__init__.py",
                "app/routers/v1/__init__.py",
            ])

        if self.config_reader.has_testing():
            init_files.extend([
                "tests/__init__.py",
                "tests/api/__init__.py",
                "tests/unit/__init__.py",
            ])

        # 创建所有 __init__.py 文件
        for init_file in init_files:
            self.file_ops.create_file(
                file_path=init_file,
                content="",
                overwrite=False
            )
        
        # 创建 app/core/config/__init__.py 并导出 settings
        self._create_config_init()
    
    def _create_config_init(self) -> None:
        """创建 app/core/config/__init__.py 文件并导出 settings"""
        content = '''"""配置模块"""
from .settings import settings

__all__ = ["settings"]
'''
        self.file_ops.create_file(
            file_path="app/core/config/__init__.py",
            content=content,
            overwrite=True
        )
    
    def _create_config_modules_init(self) -> None:
        """创建 app/core/config/modules/__init__.py 文件"""
        # 基础导入
        imports = [
            "from .app import AppSettings",
            "from .logger import LoggingSettings",
        ]
        
        exports = [
            "AppSettings",
            "LoggingSettings",
        ]
        
        # 如果启用数据库，添加数据库配置
        if self.config_reader.has_database():
            imports.append("from .database import DatabaseSettings")
            exports.append("DatabaseSettings")
        
        # 如果启用认证，添加 JWT 配置
        if self.config_reader.has_auth():
            imports.append("from .jwt import JWTSettings")
            exports.append("JWTSettings")
        
        # 如果是 Complete JWT Auth，添加邮件配置
        if self.config_reader.get_auth_type() == "complete":
            imports.append("from .email import EmailSettings")
            exports.append("EmailSettings")
        
        # 如果启用 CORS，添加 CORS 配置
        if self.config_reader.has_cors():
            imports.append("from .cors import CORSSettings")
            exports.append("CORSSettings")
        
        # 构建文件内容
        content = f'''"""配置模块"""
{chr(10).join(imports)}

__all__ = [
    {f',{chr(10)}    '.join([f'"{exp}"' for exp in exports])},
]
'''
        
        self.file_ops.create_file(
            file_path="app/core/config/modules/__init__.py",
            content=content,
            overwrite=True
        )
    
    def _create_database_init(self) -> None:
        """创建 app/core/database/__init__.py 文件（导出 db_manager, Base, get_db）"""
        db_type = self.config_reader.get_database_type()
        
        if db_type == "PostgreSQL":
            db_manager_import = "postgresql_manager"
        else:  # MySQL
            db_manager_import = "mysql_manager"
        
        content = f'''"""数据库模块"""
from .connection import db_manager
from .{db_type.lower()} import {db_manager_import}, Base

# 数据库会话依赖（用于 FastAPI Depends）
async def get_db():
    """获取数据库会话（异步）"""
    async for session in {db_manager_import}.get_db():
        yield session

__all__ = ["db_manager", "{db_manager_import}", "Base", "get_db"]
'''
        
        self.file_ops.create_file(
            file_path="app/core/database/__init__.py",
            content=content,
            overwrite=True
        )



    def _create_router_files(self) -> None:
        """生成基础路由文件（仅在有认证时调用）"""
        # 创建 v1 路由入口
        imports = ["from fastapi import APIRouter"]
        
        v1_router_content = '''api_router = APIRouter()

# 认证路由会在这里自动注册
# 由 orchestrator 中的路由生成器负责
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/__init__.py",
            docstring="API v1 路由",
            imports=imports,
            content=v1_router_content,
            overwrite=True
        )

    def _create_response_utils(self) -> None:
        """生成响应工具"""
        response_gen = ResponseGenerator(self.project_path)
        response_gen.generate()
    
    def _create_project_files(self) -> None:
        """生成项目配置文件"""
        orchestrator = GeneratorOrchestrator(self.project_path, self.config_reader)
        orchestrator.generate()
    
    def _init_alembic(self) -> None:
        """初始化 Alembic 迁移工具"""
        alembic_gen = AlembicGenerator(self.project_path, self.config_reader)
        alembic_gen.generate()
