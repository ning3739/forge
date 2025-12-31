# 配置文件生成器

这个目录包含用于生成 FastAPI 项目配置文件的生成器。

## 文件说明

### base.py - ConfigBaseGenerator
生成 `app/core/config/base.py` 文件，包含：
- 环境变量加载逻辑
- `EnvBaseSettings` 基类，所有配置类都继承自它
- 支持从 `secret/.env.{ENV}` 文件加载环境变量

### settings.py - ConfigSettingsGenerator
生成 `app/core/config/settings.py` 文件，包含：
- `Settings` 类，统一管理所有配置
- 使用 `cached_property` 延迟加载配置，提高性能
- 根据启用的功能动态生成配置属性
- 全局 `settings` 实例，方便在应用中使用

### app.py - ConfigAppGenerator
生成 `app/core/config/modules/app.py` 文件，包含：
- `AppSettings` 类，用于应用元数据配置
- 应用名称、描述、版本等配置项

### logger.py - ConfigLoggerGenerator
生成 `app/core/config/modules/logger.py` 文件，包含：
- `LoggingSettings` 类，用于 Loguru 日志配置
- 日志级别、文件路径、轮转策略等配置项

### cors.py - ConfigCorsGenerator
生成 `app/core/config/modules/cors.py` 文件（仅在启用 CORS 时），包含：
- `CORSSettings` 类，用于 CORS 配置
- 允许的源、凭证、方法、请求头、响应头等配置项

### database.py - ConfigDatabaseGenerator
生成 `app/core/config/modules/database.py` 文件（仅在选择数据库时），包含：
- `DatabaseSettings` 类，用于数据库配置
- 数据库连接 URL（根据数据库类型自动生成）
- 连接池配置（大小、超时、溢出等）

### jwt.py - ConfigJwtGenerator
生成 `app/core/config/modules/jwt.py` 文件（仅在启用认证时），包含：
- `JWTSettings` 类，用于 JWT 认证配置
- JWT 密钥、算法、过期时间等配置
- Complete Auth 或启用 Refresh Token 时包含刷新令牌配置
- 自动生成项目相关的 issuer 和 audience

## 生成的文件结构

```
app/
└── core/
    └── config/
        ├── base.py              # 配置基类
        ├── settings.py          # 全局配置管理（动态生成）
        └── modules/
            ├── __init__.py      # 导出所有配置类
            ├── app.py           # 应用配置
            ├── logger.py        # 日志配置
            ├── cors.py          # CORS 配置（可选）
            ├── database.py      # 数据库配置（可选）
            └── jwt.py           # JWT 认证配置（可选）
```

## 使用方式

这些生成器会在项目初始化时自动调用，通过 `ProjectFilesGenerator` 协调执行。

```python
from core.generators.files.config import (
    ConfigBaseGenerator,
    ConfigAppGenerator,
    ConfigLoggerGenerator,
    ConfigCorsGenerator,
    ConfigDatabaseGenerator,
    ConfigJwtGenerator,
    ConfigSettingsGenerator,
)

# 在 ProjectFilesGenerator 中使用
generators = [
    ConfigBaseGenerator(project_path, config_reader),
    ConfigAppGenerator(project_path, config_reader),
    ConfigLoggerGenerator(project_path, config_reader),
    ConfigCorsGenerator(project_path, config_reader),      # 仅在启用 CORS 时生成
    ConfigDatabaseGenerator(project_path, config_reader),  # 仅在选择数据库时生成
    ConfigJwtGenerator(project_path, config_reader),       # 仅在启用认证时生成
    ConfigSettingsGenerator(project_path, config_reader),  # 动态生成配置管理
]
```

## 使用示例

生成的 `settings.py` 可以在应用中这样使用：

```python
from app.core.config.settings import settings

# 访问应用配置
app_name = settings.app.APP_NAME

# 访问日志配置
log_level = settings.logging.LOG_LEVEL

# 访问数据库配置（如果启用）
if hasattr(settings, 'database'):
    db_url = settings.database.DATABASE_URL

# 访问 CORS 配置（如果启用）
if hasattr(settings, 'cors'):
    origins = settings.cors.CORS_ALLOWED_ORIGINS

# 访问 JWT 配置（如果启用认证）
if hasattr(settings, 'jwt'):
    secret_key = settings.jwt.JWT_SECRET_KEY
    algorithm = settings.jwt.JWT_ALGORITHM
```
