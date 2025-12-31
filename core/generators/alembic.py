"""Alembic 迁移工具生成器"""
from pathlib import Path
from core.utils import FileOperations
from core.config_reader import ConfigReader


class AlembicGenerator:
    """Alembic 迁移工具生成器"""
    
    def __init__(self, project_path: Path, config_reader: ConfigReader):
        """初始化 Alembic 生成器
        
        Args:
            project_path: 项目根目录路径
            config_reader: 配置读取器实例
        """
        self.project_path = Path(project_path)
        self.config_reader = config_reader
        self.file_ops = FileOperations(base_path=project_path)
    
    def generate(self) -> None:
        """生成 Alembic 配置"""
        # 只有配置了数据库且启用了迁移工具才生成
        if not self.config_reader.has_database():
            return
        
        if not self.config_reader.has_migration():
            return
        
        # 检查是否已经初始化
        env_py = self.project_path / "alembic" / "env.py"
        if env_py.exists():
            return
        
        # 始终手动创建完整的 Alembic 结构
        # 这样可以确保即使 Alembic 未安装，项目也有完整的迁移文件
        self._create_alembic_structure()
    
    def _create_alembic_structure(self) -> None:
        """创建完整的 Alembic 结构"""
        # 创建目录
        alembic_dir = self.project_path / "alembic"
        alembic_dir.mkdir(exist_ok=True)
        (alembic_dir / "versions").mkdir(exist_ok=True)
        
        # 创建所有必需的文件
        self._create_alembic_ini()
        self._create_env_py()
        self._create_script_mako()
        self._create_alembic_readme()
        
        # 创建 versions 目录的 .gitkeep
        gitkeep = alembic_dir / "versions" / ".gitkeep"
        gitkeep.touch(exist_ok=True)
    
    def _create_alembic_ini(self) -> None:
        """创建 alembic.ini 文件"""
        db_type = self.config_reader.get_database_type()
        
        if db_type == "PostgreSQL":
            db_url_example = "postgresql://user:password@localhost/dbname"
        elif db_type == "MySQL":
            db_url_example = "mysql://user:password@localhost/dbname"
        else:
            db_url_example = "sqlite:///./app.db"
        
        content = f'''# Alembic 配置文件

[alembic]
# 迁移脚本的路径
script_location = alembic

# 模板文件
file_template = %%(rev)s_%%(slug)s

# 时区设置
timezone = UTC

# 数据库 URL（从环境变量读取）
# sqlalchemy.url = {db_url_example}
# Database URL is configured in env.py from environment variables

# 日志配置
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''
        
        self.file_ops.create_file(
            file_path="alembic.ini",
            content=content,
            overwrite=True
        )
    
    def _create_env_py(self) -> None:
        """创建 env.py 文件"""
        orm_type = self.config_reader.get_orm_type()
        
        if orm_type == "SQLModel":
            self._create_sqlmodel_env_py()
        elif orm_type == "SQLAlchemy":
            self._create_sqlalchemy_env_py()
    
    def _create_sqlmodel_env_py(self) -> None:
        """创建 SQLModel 的 env.py（异步版本）"""
        content = '''"""Alembic 环境配置 - SQLModel (异步版本)"""
from logging.config import fileConfig
import asyncio
import os
from pathlib import Path
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 加载环境变量
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "secret" / ".env.development"
if env_file.exists():
    load_dotenv(env_file)

# 导入 SQLModel 的 Base
from sqlmodel import SQLModel

# 导入所有模型以便 Alembic 能够检测到它们
from app.models.user import User
from app.models.token import RefreshToken, VerificationCode

# Alembic Config 对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置 MetaData
target_metadata = SQLModel.metadata


# 从环境变量获取数据库 URL
def get_url():
    """从环境变量获取数据库 URL"""
    url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    # 转换为异步驱动
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+aiomysql://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    """在离线模式下运行迁移（同步模式）"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """执行迁移的辅助函数"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在在线模式下运行迁移（异步模式）"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
'''
        
        self.file_ops.create_file(
            file_path="alembic/env.py",
            content=content,
            overwrite=True
        )
    
    def _create_sqlalchemy_env_py(self) -> None:
        """创建 SQLAlchemy 的 env.py（异步版本）"""
        content = '''"""Alembic 环境配置 - SQLAlchemy (异步版本)"""
from logging.config import fileConfig
import asyncio
import os
from pathlib import Path
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 加载环境变量
from dotenv import load_dotenv
env_file = Path(__file__).parent.parent / "secret" / ".env.development"
if env_file.exists():
    load_dotenv(env_file)

# 导入 Base
from app.core.database import Base

# 导入所有模型以便 Alembic 能够检测到它们
from app.models.user import User
from app.models.token import RefreshToken, VerificationCode

# Alembic Config 对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置 MetaData
target_metadata = Base.metadata


# 从环境变量获取数据库 URL
def get_url():
    """从环境变量获取数据库 URL"""
    url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    # 转换为异步驱动
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+aiomysql://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    """在离线模式下运行迁移（同步模式）"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """执行迁移的辅助函数"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在在线模式下运行迁移（异步模式）"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
'''
        
        self.file_ops.create_file(
            file_path="alembic/env.py",
            content=content,
            overwrite=True
        )
    
    def _create_script_mako(self) -> None:
        """创建迁移脚本模板"""
        content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        
        self.file_ops.create_file(
            file_path="alembic/script.py.mako",
            content=content,
            overwrite=True
        )
    
    def _create_alembic_readme(self) -> None:
        """创建 Alembic 使用说明"""
        content = '''# Alembic 数据库迁移

这个目录包含数据库迁移脚本。

## 安装依赖

确保已安装 Alembic：

```bash
pip install alembic
# 或
uv add alembic
```

## 使用方法

### 创建新的迁移

```bash
# 自动生成迁移（推荐）
alembic revision --autogenerate -m "描述你的更改"

# 手动创建空迁移
alembic revision -m "描述你的更改"
```

### 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级一个版本
alembic upgrade +1

# 升级到特定版本
alembic upgrade <revision_id>
```

### 回滚迁移

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade <revision_id>

# 回滚所有
alembic downgrade base
```

### 查看迁移历史

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看详细历史
alembic history --verbose
```

## 配置

数据库连接 URL 从环境变量 `DATABASE_URL` 读取。

请在 `.env` 文件中设置：

```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 注意事项

1. 在创建迁移前，确保所有模型都已导入到 `alembic/env.py` 中
2. 使用 `--autogenerate` 时，Alembic 会自动检测模型变化
3. 始终检查生成的迁移脚本，确保符合预期
4. 在生产环境应用迁移前，先在开发环境测试
'''
        
        self.file_ops.create_markdown_file(
            file_path="alembic/README.md",
            title=None,
            content=content,
            overwrite=True
        )
