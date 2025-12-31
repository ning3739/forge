"""用户路由生成器"""
from pathlib import Path
from ..base import BaseTemplateGenerator


class UserRouterGenerator(BaseTemplateGenerator):
    """用户路由文件生成器"""
    
    def generate(self) -> None:
        """生成用户路由文件"""
        # 只有启用认证才生成
        if not self.config_reader.has_auth():
            return
        
        self._generate_user_router()
    
    def _generate_user_router(self) -> None:
        """生成用户路由"""
        imports = [
            "from fastapi import APIRouter, Depends, HTTPException, status",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from typing import List",
            "",
            "from app.core.database import get_db",
            "from app.core.deps import get_current_user, get_current_superuser",
            "from app.models.user import User",
            "from app.schemas.user import UserResponse, UserUpdate",
            "from app.crud.user import user_crud",
        ]
        
        content = '''router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息
    
    Args:
        user_update: 用户更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的用户信息
        
    Raises:
        HTTPException: 更新失败
    """
    # 如果要更新用户名，检查是否已存在
    if user_update.username and user_update.username != current_user.username:
        existing_user = await user_crud.get_by_username(db, user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # 如果要更新邮箱，检查是否已存在
    if user_update.email and user_update.email != current_user.email:
        existing_user = await user_crud.get_by_email(db, user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    updated_user = await user_crud.update(db, current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除当前用户账户
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Raises:
        HTTPException: 删除失败
    """
    success = await user_crud.delete(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


# ========== 管理员路由 ==========

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（仅管理员）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        current_user: 当前登录的管理员用户
        db: 数据库会话
        
    Returns:
        用户列表
    """
    users = await user_crud.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """获取指定用户信息（仅管理员）
    
    Args:
        user_id: 用户 ID
        current_user: 当前登录的管理员用户
        db: 数据库会话
        
    Returns:
        用户信息
        
    Raises:
        HTTPException: 用户不存在
    """
    user = await user_crud.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """更新指定用户信息（仅管理员）
    
    Args:
        user_id: 用户 ID
        user_update: 用户更新数据
        current_user: 当前登录的管理员用户
        db: 数据库会话
        
    Returns:
        更新后的用户信息
        
    Raises:
        HTTPException: 用户不存在或更新失败
    """
    updated_user = await user_crud.update(db, user_id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """删除指定用户（仅管理员）
    
    Args:
        user_id: 用户 ID
        current_user: 当前登录的管理员用户
        db: 数据库会话
        
    Raises:
        HTTPException: 用户不存在或删除失败
    """
    # 防止管理员删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    success = await user_crud.delete(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
'''
        
        self.file_ops.create_python_file(
            file_path="app/routers/v1/users.py",
            docstring="用户管理路由",
            imports=imports,
            content=content,
            overwrite=True
        )
