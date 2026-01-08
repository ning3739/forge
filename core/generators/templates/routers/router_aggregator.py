"""Router aggregator generator - generates app/routers/v1/__init__.py"""
from core.decorators import Generator
from pathlib import Path
from ..base import BaseTemplateGenerator


@Generator(
    category="router",
    priority=82,
    requires=["AuthRouterGenerator", "UserRouterGenerator"],
    enabled_when=lambda c: c.has_auth(),
    description="Generate router aggregator file (app/routers/v1/__init__.py)"
)
class RouterAggregatorGenerator(BaseTemplateGenerator):
    """Router aggregator generator - exports all v1 routers"""
    
    def generate(self) -> None:
        """Generate router aggregator file"""
        # Only generate if authentication is enabled
        if not self.config_reader.has_auth():
            return
        
        self._generate_router_aggregator()
    
    def _generate_router_aggregator(self) -> None:
        """Generate app/routers/v1/__init__.py"""
        imports = [
            "from .auth import router as auth_router",
            "from .users import router as user_router",
        ]
        
        exports = ["auth_router", "user_router"]
        
        content = f'''# Export all routers
__all__ = {exports}
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/__init__.py",
            docstring="API v1 router module - aggregates all v1 routers",
            imports=imports,
            content=content,
            overwrite=True
        )
