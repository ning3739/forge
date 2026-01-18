# Adding New Features

This guide explains how to add new features to Forge, from configuration collection to code generation.

## Overview

Adding a feature involves these steps:

1. Add configuration collection in `commands/init.py`
2. Extend `ConfigReader` with helper methods
3. Create generators for the feature
4. Update dependencies in the pyproject generator
5. Add tests
6. Update documentation

## Example: Adding GraphQL Support

Let's walk through adding GraphQL support as an example.

### Step 1: Configuration Collection

Edit `commands/init.py` to add the interactive prompt:

```python
def collect_features() -> dict:
    # ... existing prompts ...
    
    # Add GraphQL prompt
    has_graphql = questionary.confirm(
        "Enable GraphQL support?",
        default=False,
        style=custom_style
    ).ask()
    
    return {
        # ... existing features ...
        "graphql": has_graphql,
    }
```

The configuration will be saved to `.forge/config.json`:

```json
{
  "features": {
    "graphql": true
  }
}
```

### Step 2: Extend ConfigReader

Edit `core/config_reader.py` to add a helper method:

```python
class ConfigReader:
    # ... existing methods ...
    
    def has_graphql(self) -> bool:
        """Check if GraphQL is enabled"""
        return self.config.get("features", {}).get("graphql", False)
```

### Step 3: Create Generators

Create a new directory for GraphQL generators:

```
core/generators/templates/graphql/
├── __init__.py
├── schema.py
└── router.py
```

#### GraphQL Schema Generator

```python
# core/generators/templates/graphql/schema.py
from core.decorators import Generator
from core.generators.templates.base import BaseTemplateGenerator


@Generator(
    category="graphql",
    priority=75,
    requires=["UserModelGenerator"],
    enabled_when=lambda c: c.has_graphql(),
    description="Generate GraphQL schema (app/graphql/schema.py)"
)
class GraphQLSchemaGenerator(BaseTemplateGenerator):
    """GraphQL schema generator"""
    
    def generate(self) -> None:
        imports = [
            "import strawberry",
            "from typing import List, Optional",
            "from app.models.user import User as UserModel",
        ]
        
        content = '''@strawberry.type
class User:
    """GraphQL User type"""
    id: int
    username: str
    email: str
    is_active: bool
    
    @classmethod
    def from_model(cls, model: UserModel) -> "User":
        return cls(
            id=model.id,
            username=model.username,
            email=model.email,
            is_active=model.is_active,
        )


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info) -> List[User]:
        """Get all users"""
        db = info.context["db"]
        from app.crud.user import user_crud
        users = await user_crud.get_all(db)
        return [User.from_model(u) for u in users]
    
    @strawberry.field
    async def user(self, info, user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = info.context["db"]
        from app.crud.user import user_crud
        user = await user_crud.get_by_id(db, user_id)
        return User.from_model(user) if user else None


schema = strawberry.Schema(query=Query)
'''
        
        # Create directory
        (self.project_path / "app" / "graphql").mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        self.file_ops.create_file(
            "app/graphql/__init__.py",
            content="",
            overwrite=False
        )
        
        # Create schema file
        self.file_ops.create_python_file(
            file_path="app/graphql/schema.py",
            docstring="GraphQL schema definition",
            imports=imports,
            content=content,
            overwrite=True
        )
```

#### GraphQL Router Generator

```python
# core/generators/templates/graphql/router.py
from core.decorators import Generator
from core.generators.templates.base import BaseTemplateGenerator


@Generator(
    category="graphql",
    priority=85,
    requires=["GraphQLSchemaGenerator"],
    enabled_when=lambda c: c.has_graphql(),
    description="Generate GraphQL router (app/routers/graphql.py)"
)
class GraphQLRouterGenerator(BaseTemplateGenerator):
    """GraphQL router generator"""
    
    def generate(self) -> None:
        imports = [
            "from fastapi import Depends",
            "from strawberry.fastapi import GraphQLRouter",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.database import get_db",
            "from app.graphql.schema import schema",
        ]
        
        content = '''async def get_context(db: AsyncSession = Depends(get_db)):
    """Provide database session to GraphQL resolvers"""
    return {"db": db}


graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
)
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/graphql.py",
            docstring="GraphQL router configuration",
            imports=imports,
            content=content,
            overwrite=True
        )
```

### Step 4: Update Dependencies

Edit `core/generators/configs/pyproject.py` to add GraphQL dependencies:

```python
def _get_dependencies(self) -> list:
    dependencies = [
        # ... existing dependencies ...
    ]
    
    # GraphQL dependencies
    if self.config_reader.has_graphql():
        dependencies.extend([
            'strawberry-graphql[fastapi]>=0.200.0',
        ])
    
    return dependencies
```

### Step 5: Update Main Generator

The main.py generator needs to include the GraphQL router. Edit `core/generators/templates/app/main.py`:

```python
def _generate_main_with_graphql(self) -> None:
    # Add import
    if self.config_reader.has_graphql():
        imports.append("from app.routers.graphql import graphql_router")
    
    # Add router
    if self.config_reader.has_graphql():
        app_content += '''
# GraphQL endpoint
app.include_router(graphql_router, prefix="/graphql")
'''
```

### Step 6: Add Tests

Create tests for the new feature:

```python
# tests/test_graphql_generator.py
import pytest
from pathlib import Path
from core.config_reader import ConfigReader
from core.generators.templates.graphql.schema import GraphQLSchemaGenerator


def test_graphql_generator_creates_files(tmp_path):
    """Test GraphQL generator creates schema file"""
    # Setup config
    config_dir = tmp_path / ".forge"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(
        '{"features": {"graphql": true, "auth": {"type": "basic"}}}'
    )
    
    # Create required directories
    (tmp_path / "app" / "graphql").mkdir(parents=True)
    
    # Run generator
    config_reader = ConfigReader(tmp_path)
    generator = GraphQLSchemaGenerator(tmp_path, config_reader)
    generator.generate()
    
    # Verify
    assert (tmp_path / "app" / "graphql" / "schema.py").exists()
```

### Step 7: Update Documentation

Add documentation for the new feature:

1. Create `docs/user-guide/graphql.md`
2. Add to `docs/index.rst` toctree
3. Update feature list in relevant docs

## Checklist for New Features

- [ ] Configuration prompt in `commands/init.py`
- [ ] Helper method in `ConfigReader`
- [ ] Generator(s) with proper decorator parameters
- [ ] Dependencies in pyproject generator
- [ ] Integration with main.py (if needed)
- [ ] Tests for generators
- [ ] Documentation

## Tips

1. **Start simple**: Create a minimal working generator first
2. **Follow patterns**: Look at existing generators for examples
3. **Test incrementally**: Run `forge init` frequently to verify output
4. **Check dependencies**: Ensure `requires` lists all prerequisites
5. **Use conditions**: Use `enabled_when` to skip generators when feature is disabled
