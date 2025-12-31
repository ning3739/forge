"""API v1 路由聚合器生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class ApiV1Generator(BaseTemplateGenerator):
    """API v1 路由聚合器生成器"""
    
    def generate(self) -> None:
        """生成 API v1 路由聚合器"""
        # 只有启用认证才生成
        if not self.config_reader.has_auth():
            return
        
        self._generate_api_v1()
    
    def _generate_api_v1(self) -> None:
        """生成 API v1 聚合器"""
        imports = [
            "from .auth import router as auth_router",
            "from .users import router as user_router",
        ]
        
        content = '''# 导出所有路由
__all__ = ["auth_router", "user_router"]
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/__init__.py",
            docstring="API v1 路由模块",
            imports=imports,
            content=content,
            overwrite=True
        )
