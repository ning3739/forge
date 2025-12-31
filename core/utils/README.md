# Core Utils - 核心工具模块

本目录包含 Forge CLI 的核心工具类，提供通用的功能支持。

## 📁 模块说明

### file_generator.py - 文件操作工具

**用途：** 提供文件创建、修改、追加等操作的通用方法

**主要功能：**
- `create_file()` - 创建文件
- `append_content()` - 追加内容
- `insert_content()` - 插入内容
- `insert_after_pattern()` - 在匹配行后插入
- `insert_before_pattern()` - 在匹配行前插入
- `replace_content()` - 替换内容
- `create_python_file()` - 创建 Python 文件
- `create_json_file()` - 创建 JSON 文件
- `create_yaml_file()` - 创建 YAML 文件
- `create_markdown_file()` - 创建 Markdown 文件

**使用场景：**
- 所有代码生成器都使用此工具类
- 通过 `BaseFileGenerator` 基类注入

**示例：**
```python
from core.utils import FileGenerator

generator = FileGenerator(base_path="./my-project")
generator.create_python_file(
    file_path="app/main.py",
    docstring="FastAPI 应用入口",
    imports=["from fastapi import FastAPI"],
    content="app = FastAPI()"
)
```

### project_config.py - 项目配置工具

**用途：** 检查和加载项目配置

**主要功能：**
- `ProjectConfig.exists()` - 检查项目配置是否存在
- `ProjectConfig.load()` - 加载项目配置

**使用场景：**
- 在 `forge init` 命令中检查项目是否已存在
- 加载现有项目配置

**示例：**
```python
from pathlib import Path
from core.utils import ProjectConfig

project_path = Path("./my-project")

# 检查配置是否存在
if ProjectConfig.exists(project_path):
    # 加载配置
    config = ProjectConfig.load(project_path)
    print(f"项目创建于: {config['metadata']['created_at']}")
```

## 🎯 设计原则

### 1. 纯工具类
- 无状态或最小状态
- 不依赖具体业务逻辑
- 可以在任何地方使用

### 2. 单一职责
- 每个工具类只负责一类功能
- 方法功能明确，易于理解

### 3. 易于测试
- 方法独立，便于单元测试
- 无副作用或副作用明确

## 📊 依赖关系

```
core/utils/
├── file_generator.py    (无依赖)
└── project_config.py    (无依赖)

被依赖：
├── core/generators/templates/base.py  (使用 FileGenerator)
├── core/generators/configs/base.py    (使用 FileGenerator)
├── core/generators/deployment/base.py (使用 FileGenerator)
└── commands/init.py                   (使用 ProjectConfig)
```

## 🔧 扩展指南

### 添加新的工具类

1. 在 `core/utils/` 创建新文件
2. 确保工具类是纯工具，不包含业务逻辑
3. 在 `__init__.py` 中导出
4. 更新本 README

### 工具类的判断标准

**应该放在 utils/ 的：**
- ✅ 文件操作工具
- ✅ 字符串处理工具
- ✅ 日期时间工具
- ✅ 数据验证工具
- ✅ 通用配置工具

**不应该放在 utils/ 的：**
- ❌ 业务逻辑
- ❌ 代码生成器
- ❌ UI 组件
- ❌ 命令处理器
- ❌ 特定功能模块

## 🧪 测试

每个工具类都应该有对应的单元测试：

```
tests/
└── core/
    └── utils/
        ├── test_file_generator.py
        └── test_project_config.py
```

## 📚 相关文档

- [架构文档](../../docs/ARCHITECTURE.md)
- [Generators 文档](../generators/README.md)
- [项目 README](../../README.md)

---

**原则：** 工具类应该是"无聊"的 - 它们只是提供功能，不包含任何有趣的业务逻辑。
