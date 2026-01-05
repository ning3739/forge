"""API v1 route aggregationgeneratorgenerategenerator"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class ApiV1Generator(BaseTemplateGenerator):
    """API v1 route aggregationgeneratorgenerategenerator"""
    
    def generate(self) -> None:
        """generate API v1 route aggregationgenerator"""
        # Only generate if authentication is enabled
        if not self.config_reader.has_auth():
            return
        
        self._generate_api_v1()
    
    def _generate_api_v1(self) -> None:
        """generate API v1 aggregationgenerator"""
        imports = [
            "from .auth import router as auth_router",
            "from .users import router as user_router",
        ]
        
        content = '''# exportallrouter
__all__ = ["auth_router", "user_router"]
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/__init__.py",
            docstring="API v1 routermodule",
            imports=imports,
            content=content,
            overwrite=True
        )
