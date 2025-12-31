# Generators 目录结构说明

本目录包含 Forge CLI 的所有代码生成器，按照**文件用途**进行分类组织。

## 📁 目录结构

```
core/generators/
├── __init__.py
├── README.md                    # 本文档
├── structure.py                 # 项目目录结构生成器
├── project_files.py             # 项目文件生成协调器
├── alembic.py                   # Alembic 数据库迁移生成器
├── response.py                  # 响应模型生成器
│
├── templates/                   # 应用代码模板生成器
│   ├── __init__.py
│   ├── base.py                 # 模板生成器基类
│   │
│   ├── app/                    # 应用核心代码
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── security.py        # 安全工具（密码哈希、JWT）
│   │   ├── logger.py          # 日志配置
│   │   ├── base.py            # 配置基类
│   │   ├── app.py             # 应用配置
│   │   ├── cors.py            # CORS 配置
│   │   ├── database.py        # 数据库配置
│   │   ├── jwt.py             # JWT 配置
│   │   ├── email.py           # 邮件配置
│   │   └── settings.py        # 统一配置入口
│   │
│   ├── database/              # 数据库相关
│   │   ├── connection.py      # 数据库连接
│   │   ├── dependencies.py    # 依赖注入
│   │   ├── postgresql.py      # PostgreSQL 配置
│   │   └── mysql.py           # MySQL 配置
│   │
│   ├── models/                # 数据模型（ORM）
│   │   ├── user.py            # 用户模型
│   │   └── token.py           # Token 模型
│   │
│   ├── schemas/               # Pydantic Schemas
│   │   ├── user.py            # 用户 Schema
│   │   └── token.py           # Token Schema
│   │
│   ├── crud/                  # CRUD 操作
│   │   ├── user.py            # 用户 CRUD
│   │   └── token.py           # Token CRUD
│   │
│   ├── routers/               # API 路由
│   │   ├── api_v1.py          # API v1 路由聚合
│   │   ├── auth.py            # 认证路由
│   │   └── user.py            # 用户路由
│   │
│   ├── services/              # 业务逻辑服务
│   │   └── auth.py            # 认证服务
│   │
│   └── email/                 # 邮件服务
│       ├── email.py           # 邮件发送服务
│       └── email_template.py  # 邮件模板
│
├── configs/                   # 项目配置文件生成器
│   ├── __init__.py
│   ├── base.py               # 配置文件生成器基类
│   ├── pyproject.py          # pyproject.toml
│   ├── env.py                # .env 环境变量
│   ├── gitignore.py          # .gitignore
│   └── readme.py             # README.md
│
└── deployment/               # 部署配置生成器
    ├── __init__.py
    ├── base.py              # 部署配置生成器基类
    ├── dockerfile.py        # Dockerfile
    ├── dockerignore.py      # .dockerignore
    └── docker_compose.py    # docker-compose.yml
```

## 🎯 设计原则

### 1. 按用途分类

- **templates/** - 生成到 `app/` 目录的应用代码
- **configs/** - 生成到项目根目录的配置文件
- **deployment/** - 生成部署相关的配置文件

### 2. 模块化设计

每个生成器都是独立的模块，可以单独使用或组合使用。

### 3. 清晰的职责划分

- **structure.py** - 负责创建目录结构
- **project_files.py** - 协调所有文件生成器
- **alembic.py** - 专门处理数据库迁移
- **response.py** - 生成响应模型

## 📝 使用示例

### 生成单个文件

```python
from pathlib import Path
from core.config_reader import ConfigReader
from core.generators.configs.pyproject import PyprojectGenerator

project_path = Path("./my-project")
config_reader = ConfigReader(project_path)
config_reader.load_config()

generator = PyprojectGenerator(project_path, config_reader)
generator.generate()
```

### 生成所有文件

```python
from pathlib import Path
from core.generator import ProjectGenerator

project_path = Path("./my-project")
generator = ProjectGenerator(project_path)
generator.config_reader.load_config()
generator.generate()
```

## 🔄 迁移指南

如果你的代码引用了旧的 `core.generators.files` 路径，请按照以下规则更新：

### 旧路径 → 新路径映射

```python
# 配置文件
from core.generators.files.pyproject import PyprojectGenerator
# 改为
from core.generators.configs.pyproject import PyprojectGenerator

# 部署文件
from core.generators.files.dockerfile import DockerfileGenerator
# 改为
from core.generators.deployment.dockerfile import DockerfileGenerator

# 应用代码
from core.generators.files.main import MainGenerator
# 改为
from core.generators.templates.app.main import MainGenerator

# 数据库代码
from core.generators.files.database.connection import DatabaseConnectionGenerator
# 改为
from core.generators.templates.database.connection import DatabaseConnectionGenerator

# 模型
from core.generators.files.models.user import UserModelGenerator
# 改为
from core.generators.templates.models.user import UserModelGenerator
```

## 🚀 扩展指南

### 添加新的配置文件生成器

1. 在 `configs/` 目录创建新文件
2. 继承 `ConfigFileGenerator` 基类
3. 在 `project_files.py` 中注册

### 添加新的应用代码生成器

1. 在 `templates/` 对应子目录创建新文件
2. 继承 `base.py` 中的基类
3. 在 `project_files.py` 中注册

### 添加新的部署配置生成器

1. 在 `deployment/` 目录创建新文件
2. 继承 `DeploymentFileGenerator` 基类
3. 在 `project_files.py` 中注册

## 📚 相关文档

- [项目架构文档](../../README.md)
- [配置文件说明](../config_reader.py)
- [生成器基类](./templates/base.py)
