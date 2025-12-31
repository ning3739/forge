"""数据库配置文件生成器"""
from ..base import BaseTemplateGenerator


class ConfigDatabaseGenerator(BaseTemplateGenerator):
    """生成 app/core/config/modules/database.py 文件"""
    
    def generate(self) -> None:
        """生成数据库配置文件"""
        # 只有选择了数据库时才生成
        if not self.config_reader.has_database():
            return
        
        imports = [
            "from pydantic import Field, PositiveInt",
            "from app.core.config.base import EnvBaseSettings",
        ]
        
        # 根据数据库类型生成不同的默认 URL
        db_type = self.config_reader.get_database_type()
        project_name = self.config_reader.get_project_name()
        
        # 生成数据库名称（将项目名转换为合法的数据库名）
        db_name = project_name.lower().replace('-', '_').replace(' ', '_')
        
        if db_type == "PostgreSQL":
            default_url = f"postgresql://user:password@localhost:5432/{db_name}_dev"
        elif db_type == "MySQL":
            default_url = f"mysql://user:password@localhost:3306/{db_name}_dev"
        else:
            default_url = "sqlite:///./app.db"
        
        content = f'''class DatabaseSettings(EnvBaseSettings):
    """数据库配置"""
    
    # 数据库连接 URL
    DATABASE_URL: str = Field(
        default="{default_url}",
        description="Database connection URL",
    )
    
    # 连接池配置
    ECHO: bool = Field(
        default=False,
        description="Database connection pool echo"
    )
    POOL_PRE_PING: bool = Field(
        default=True,
        description="Database connection pool pre-ping"
    )
    POOL_TIMEOUT: PositiveInt = Field(
        default=30,
        description="Database connection pool timeout (seconds)"
    )
    POOL_SIZE: PositiveInt = Field(
        default=6,
        description="Database connection pool size (保守策略：适合 2核心 2GB 服务器)",
    )
    POOL_MAX_OVERFLOW: PositiveInt = Field(
        default=2,
        description="Database connection pool max overflow (保守策略：降低溢出连接)",
    )
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/config/modules/database.py",
            docstring="数据库配置模块",
            imports=imports,
            content=content,
            overwrite=True
        )
