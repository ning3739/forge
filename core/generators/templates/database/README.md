# Database 文件生成器

这个模块负责生成数据库相关的文件，包括连接管理器、数据库驱动和依赖注入。

## 生成器列表

### 1. DatabaseConnectionGenerator
生成 `app/core/database/connection.py` - 数据库连接管理器

统一管理数据库连接的初始化、测试和关闭。

### 2. DatabaseMySQLGenerator
生成 `app/core/database/mysql.py` - MySQL 连接管理器

提供 MySQL 数据库的异步和同步连接管理，使用 aiomysql 和 pymysql 驱动。

### 3. DatabasePostgreSQLGenerator
生成 `app/core/database/postgresql.py` - PostgreSQL 连接管理器

提供 PostgreSQL 数据库的异步和同步连接管理，使用 asyncpg 和 psycopg2 驱动。

### 4. DatabaseDependenciesGenerator
生成 `app/core/database/dependencies.py` - FastAPI 依赖注入

根据认证类型（basic/complete）生成不同的依赖注入代码：
- **Complete Auth**: 包含 access_token 和 refresh_token 验证，支持邮箱验证、密码重置等功能
- **Basic Auth**: 仅包含基础的 access_token 验证

## 使用方式

这些生成器会在 `ProjectFilesGenerator` 中根据配置自动调用：

```python
# 如果启用数据库
if config_reader.has_database():
    # 生成连接管理器
    DatabaseConnectionGenerator(project_path, config_reader).generate()
    
    # 根据数据库类型生成对应的驱动
    if db_type == "MySQL":
        DatabaseMySQLGenerator(project_path, config_reader).generate()
    elif db_type == "PostgreSQL":
        DatabasePostgreSQLGenerator(project_path, config_reader).generate()
    
    # 如果启用认证，生成依赖注入
    if config_reader.has_auth():
        DatabaseDependenciesGenerator(project_path, config_reader).generate()
```

## 生成的文件结构

```
app/
└── core/
    └── database/
        ├── __init__.py
        ├── connection.py          # 数据库连接管理器
        ├── mysql.py               # MySQL 驱动（如果选择 MySQL）
        ├── postgresql.py          # PostgreSQL 驱动（如果选择 PostgreSQL）
        └── dependencies.py        # FastAPI 依赖注入（如果启用认证）
```
