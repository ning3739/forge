"""Core Dependencies 生成器 - 生成 app/core/deps.py"""
from ..base import BaseTemplateGenerator


class CoreDepsGenerator(BaseTemplateGenerator):
    """生成 app/core/deps.py - 核心依赖注入函数"""
    
    def generate(self) -> None:
        """生成 app/core/deps.py"""
        if not self.config_reader.has_auth():
            return
        
        imports = [
            "from fastapi import Depends, HTTPException, status",
            "from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "",
            "from app.core.database import get_db",
            "from app.core.security import security_manager",
            "from app.crud.user import user_crud",
            "from app.models.user import User",
        ]
        
        content = '''# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前认证用户
    
    Args:
        credentials: HTTP Bearer 认证凭证
        db: 数据库会话
    
    Returns:
        User: 当前用户对象
    
    Raises:
        HTTPException: 401 - 未认证或认证失败
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 解码 token
    payload = security_manager.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户
    user = await user_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前超级用户
    
    Args:
        current_user: 当前用户
    
    Returns:
        User: 当前超级用户对象
    
    Raises:
        HTTPException: 403 - 权限不足
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
'''
        
        self.file_ops.create_python_file(
            file_path="app/core/deps.py",
            docstring="核心依赖注入函数",
            imports=imports,
            content=content,
            overwrite=True
        )
